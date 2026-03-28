import os
import sys
import json
import time
import glob
import argparse
import logging
from datetime import datetime
from playwright.sync_api import sync_playwright

# ----- パス設定 -----
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DRAFTS_ROOT = r"C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts"
SESSION_DIR = os.path.join(SCRIPT_DIR, ".x_session")
LOG_DIR = os.path.join(SCRIPT_DIR, "logs")
SCHEDULE_FILE = os.path.join(SCRIPT_DIR, "sns_schedule.json")

# ----- ログ設定 -----
os.makedirs(LOG_DIR, exist_ok=True)
log_file = os.path.join(LOG_DIR, f"x_schedule_1week_log_{datetime.now().strftime('%Y%m%d')}.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_schedule():
    if not os.path.exists(SCHEDULE_FILE):
        logger.error(f"❌ スケジュールファイルが見つかりません: {SCHEDULE_FILE}")
        return []
    try:
        with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
            schedule = json.load(f)
        posts = [p for p in schedule if p["platform"] == "X"]
        return posts
    except Exception as e:
        logger.error(f"❌ スケジュール読み込みエラー: {e}")
        return []

def safe_paste(pg, t):
    pg.evaluate("""(text) => {
        const dataTransfer = new DataTransfer();
        dataTransfer.setData('text/plain', text);
        // 現在フォーカスが当たっている要素（textbox.click()後なので入力欄）にペーストイベントを直接発火
        const el = document.activeElement;
        const pasteEvent = new ClipboardEvent('paste', {
            bubbles: true,
            cancelable: true,
            clipboardData: dataTransfer
        });
        el.dispatchEvent(pasteEvent);
    }""", t)
    time.sleep(1)

def find_image(source_folder):
    folder_path = os.path.join(DRAFTS_ROOT, source_folder)
    png_files = glob.glob(os.path.join(folder_path, "*.png"))
    if png_files:
        return png_files[0]
    return None

def split_text_for_x(full_text):
    text = full_text.replace("\r\n", "\n")
    if "詳細・エビデンスはNoteへ" in text or "https://note.com/" in text:
        parts = text.split("詳細・エビデンスはNoteへ", 1)
        if len(parts) == 2:
            main_text = parts[0].strip()
            reply_text = "詳細・エビデンスはNoteへ" + parts[1].strip()
            # 140文字超えの警告（URLはX側で23文字換算だが、単純な安全性のため）
            if len(main_text) > 138:
                logger.warning(f"⚠️ 1枚目の文字数が {len(main_text)} 文字です。（厳密な140字制限に抵触する恐れあり）")
            return main_text, reply_text
            
    # 分割マーカーがない場合は適当に改行で分割（予備）
    lines = text.split("\n")
    url_line_idx = -1
    for i, line in enumerate(lines):
        if "note.com" in line:
            url_line_idx = i
            break
            
    if url_line_idx != -1:
        main_text = "\n".join(lines[:url_line_idx]).strip()
        reply_text = "\n".join(lines[url_line_idx:]).strip()
        return main_text, reply_text
        
    return text.strip(), ""

def schedule_single_post(page, post, dry_run=False):
    post_date_str = post["date"]
    post_date = datetime.strptime(post_date_str, "%Y-%m-%d")
    
    # 予約時間は 12:00 固定
    post_time = "12:00"
    
    main_text, _ = split_text_for_x(post["content"])

    logger.info(f"\n{'='*50}")
    logger.info(f"📝 予約登録: {post_date_str} {post_time}")
    logger.info(f"   ソース: {post['source']}")
    
    image_path = find_image(post['source'])
    if image_path:
        logger.info(f"   📷 添付画像: {os.path.basename(image_path)}")
    else:
        logger.warning(f"   ⚠️ PNG画像が見つかりません: {post['source']}")

    try:
        page.goto("https://x.com/compose/post", wait_until="domcontentloaded", timeout=20000)
        time.sleep(4)

        # 1. 画像の添付
        if image_path:
            file_input = page.locator('input[data-testid="fileInput"]').first
            file_input.set_input_files(image_path)
            logger.info("   ✅ 画像を添付しました")
            time.sleep(2)

        # 2. テキストボックスの取得（ゴーストドラフト回避のため role=dialog 限定）
        tbs = page.locator('[role="dialog"] [data-testid^="tweetTextarea_"]').all()
        visible_tbs = [b for b in tbs if b.is_visible()]
        if not visible_tbs:
            logger.error("❌ 表示されているテキスト入力欄が見つかりません。")
            page.screenshot(path=os.path.join(LOG_DIR, "failed_state_schedule.png"))
            return False
            
        textbox = visible_tbs[0]
        textbox.evaluate("el => el.scrollIntoView({block: 'center'})")
        time.sleep(0.5)
        textbox.click()
        time.sleep(0.5)
        
        # 安全なペースト
        safe_paste(page, main_text)
        logger.info(f"   ✅ テキスト入力完了")
        time.sleep(2)

        if dry_run:
            logger.info(f"🔸 ドライラン: 予約カレンダーボタンはスキップします")
            return True

        # 3. カレンダーアイコン（予約ボタン）をクリック
        schedule_icon_clicked = page.evaluate("""() => {
            const btn = document.querySelector('[role="dialog"] [aria-label="ポストを予約"]') || 
                        document.querySelector('[role="dialog"] [aria-label="Schedule"]') || 
                        document.querySelector('[role="dialog"] [data-testid="scheduleOption"]');
            if (btn) {
                btn.scrollIntoView({ block: 'center' });
                btn.click();
                return true;
            }
            return false;
        }""")
        
        if not schedule_icon_clicked:
            logger.error("❌ 予約カレンダーアイコンが見つかりません。")
            return False
            
        time.sleep(2)

        # 4. 日時設定 (Reactネイティブ操作)
        target_year = str(post_date.year)
        target_month = str(post_date.month)
        target_day = str(post_date.day)
        target_hour = "12"
        target_minute = "0"

        # selects[0] = Month, [1] = Day, [2] = Year, [3] = Hour, [4] = Minute
        set_result = page.evaluate("""(params) => {
            const { month, day, year, hour, minute } = params;
            // React state change hook
            const nativeSetter = Object.getOwnPropertyDescriptor(
                window.HTMLSelectElement.prototype, 'value'
            ).set;

            const selects = document.querySelectorAll('select');
            if (selects.length < 5) return { success: false, error: 'selects not found' };

            const values = [month, day, year, hour, minute];

            for (let i = 0; i < 5; i++) {
                try {
                    nativeSetter.call(selects[i], values[i]);
                    selects[i].dispatchEvent(new Event('input', { bubbles: true }));
                    selects[i].dispatchEvent(new Event('change', { bubbles: true }));
                } catch (e) {
                    return { success: false, error: e.message };
                }
            }
            return { success: true };
        }""", {
            "month": target_month,
            "day": target_day,
            "year": target_year,
            "hour": target_hour,
            "minute": target_minute
        })
        time.sleep(1)

        if not set_result.get("success"):
            logger.error(f"❌ 日時変更コンボボックスの操作に失敗しました: {set_result}")
            return False

        logger.info(f"   📅 日時設定完了: {post_date_str} {target_hour}:{target_minute.zfill(2)}")

        # 5. 「確認する」（アップデート）ボタンのクリック
        confirm_clicked = page.evaluate("""() => {
            const btn = document.querySelector('[data-testid="scheduledConfirmationPrimaryAction"]');
            if(btn) { btn.click(); return true; }
            
            // Text fallback
            const buttons = document.querySelectorAll('[role="button"]');
            for(const b of buttons) {
                if(b.textContent.includes('確認する') || b.textContent.includes('Update')) {
                    b.click(); return true;
                }
            }
            return false;
        }""")
        
        if not confirm_clicked:
            logger.error("❌ スケッチュール確認用ダイアログの「確認する」ボタンが見つかりません。")
            return False
            
        time.sleep(2)

        # 6. 右上の「予約設定」送信ボタンのクリック
        schedule_btn_clicked = page.evaluate("""() => {
            // [data-testid="tweetButton"] はスレッド等の通常投稿ボタンだが、予約時はテキストが「予約設定」になる
            const btn = document.querySelector('[data-testid="tweetButton"]');
            if (btn && (btn.textContent.includes('予約設定') || btn.textContent.includes('Schedule'))) {
                btn.removeAttribute('disabled');
                btn.removeAttribute('aria-disabled');
                btn.click();
                return true;
            }
            return false;
        }""")

        if not schedule_btn_clicked:
            logger.error("❌ 最終の「予約設定」送信ボタンが見つかりません。文字数オーバー等の可能性があります。")
            page.screenshot(path=os.path.join(LOG_DIR, "failed_state_schedule_final.png"))
            return False

        logger.info("   🎉 完了: 予約設定送信ボタンをクリックしました！")
        time.sleep(3)
        return True

    except Exception as e:
        logger.error(f"❌ エラー発生: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="VetEvidence X 1週間分一括予約(1枚目のみ)")
    parser.add_argument("--dry-run", action="store_true", help="テスト実行（予約ボタンを押さない）")
    args = parser.parse_args()

    logger.info("=" * 50)
    logger.info("📅 VetEvidence X 1週間分一括予約(1枚目のみ) スクリプト")
    logger.info("=" * 50)

    # 先生の「ワンクリックで全部動かす」という要望に応え、スケジュール生成(extract_drafts.py)をここで自動的におこないます。
    logger.info("🔄 ステップ1: 1週間分の最新スケジュール(JSON)を抽出・生成しています...")
    import subprocess
    result = subprocess.run([sys.executable, "extract_drafts.py"], cwd=SCRIPT_DIR, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"❌ スケジュール生成(extract_drafts.py)に失敗しました:\n{result.stderr}")
        sys.exit(1)
    logger.info("✅ スケジュール生成完了！\n")

    logger.info("▶ ステップ2: Xへの予約投稿処理を開始します...")

    if not os.path.exists(SESSION_DIR):
        logger.error("❌ セッションが見つかりません。先にログインを済ませてください。")
        sys.exit(1)

    posts = load_schedule()
    if not posts:
        logger.info("予約対象の投稿がありません。終了します。")
        sys.exit(0)

    logger.info(f"📋 予約対象: 合計 {len(posts)} 件（※1枚目のみ処理します）")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=SESSION_DIR,
            headless=False,
            channel="msedge",
            locale="ja-JP",
            viewport={"width": 1280, "height": 900},
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = context.pages[0] if context.pages else context.new_page()

        # ログイン確認
        page.goto("https://x.com/home", wait_until="domcontentloaded", timeout=20000)
        time.sleep(3)
        if "login" in page.url.lower():
            logger.error("❌ Xセッションが無効です。再ログインしてください。")
            context.close()
            sys.exit(1)

        success_count = 0
        for i, post in enumerate(posts):
            logger.info(f"\n--- 予約処理 [{i+1}/{len(posts)}] ---")
            success = schedule_single_post(page, post, dry_run=args.dry_run)
            if success:
                success_count += 1
            time.sleep(5) 

        context.close()
        logger.info(f"\n{'='*50}")
        logger.info(f"✅ 全処理終了: 成功 {success_count}/{len(posts)}件")

if __name__ == "__main__":
    main()
