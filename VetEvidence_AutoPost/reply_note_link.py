import os
import sys
import json
import time
import argparse
import logging
from datetime import datetime
from playwright.sync_api import sync_playwright

# ----- パス設定 -----
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_DIR = os.path.join(SCRIPT_DIR, ".x_session")
LOG_DIR = os.path.join(SCRIPT_DIR, "logs")
SCHEDULE_FILE = os.path.join(SCRIPT_DIR, "sns_schedule.json")

# ----- ログ設定 -----
os.makedirs(LOG_DIR, exist_ok=True)
log_file = os.path.join(LOG_DIR, f"x_reply_log_{datetime.now().strftime('%Y%m%d')}.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_todays_post(target_date):
    if not os.path.exists(SCHEDULE_FILE):
        logger.error(f"❌ スケジュールファイルが見つかりません: {SCHEDULE_FILE}")
        return None
    try:
        with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
            schedule = json.load(f)
        date_str = target_date.strftime("%Y-%m-%d")
        todays_posts = [p for p in schedule if p["date"] == date_str and p["platform"] == "X"]
        if not todays_posts:
            logger.info(f"📭 今日 ({date_str}) のX投稿スケジュールはありません。")
            return None
        return todays_posts[0]
    except Exception as e:
        logger.error(f"❌ スケジュール読み込みエラー: {e}")
        return None

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

def split_text_for_x(full_text):
    text = full_text.replace("\r\n", "\n")
    if "詳細・エビデンスはNoteへ" in text or "https://note.com/" in text:
        parts = text.split("詳細・エビデンスはNoteへ", 1)
        if len(parts) == 2:
            return parts[0].strip(), "詳細・エビデンスはNoteへ" + parts[1].strip()
            
    lines = text.split("\n")
    url_line_idx = -1
    for i, line in enumerate(lines):
        if "note.com" in line:
            url_line_idx = i
            break
            
    if url_line_idx != -1:
        return "\n".join(lines[:url_line_idx]).strip(), "\n".join(lines[url_line_idx:]).strip()
    return text.strip(), ""


def execute_reply(page, post, dry_run=False):
    _, reply_text = split_text_for_x(post["content"])
    if not reply_text:
        logger.warning("⚠️ 2枚目のテキスト（リプライ内容）が見つかりません。終了します。")
        return False

    try:
        # 1. 自分のプロフィールURLへ移動（固定: pawmedical_jp）
        # ※もしアカウント名が異なる場合はここを修正してください
        profile_url = "https://x.com/pawmedical_jp"
        logger.info(f"🔍 プロフィール画面へ移動します: {profile_url}")
        page.goto(profile_url, wait_until="domcontentloaded", timeout=20000)
        time.sleep(5)

        # 2. 最新のポストを探す
        # <article> タグがポスト一つ一つを指す。最初のarticleを探す。
        article = page.locator('article[data-testid="tweet"]').first
        if not article.is_visible(timeout=10000):
            logger.error("❌ プロフィール画面にツイートが見つかりません。")
            return False

        # 現在のXは、各ツイート内の <time> タグがそのツイートの個別URLへのリンクになっている
        time_link = article.locator('a:has(time)').first
        if not time_link.is_visible():
            logger.error("❌ ツイートの個別リンクが見つかりません。")
            return False

        tweet_url = "https://x.com" + time_link.get_attribute("href")
        logger.info(f"🔗 個別ツイートへ移動します: {tweet_url}")
        
        # 3. リプライ対象の個別画面へ遷移
        page.goto(tweet_url, wait_until="domcontentloaded", timeout=15000)
        time.sleep(5)

        # 4. インラインの返信テキストボックスを取得
        # ツイートの単体画面では、リプライ枠は role="dialog" ではなくページに直置きされている
        # ただし、ダイアログが開くこともあるので両方探す
        tbs = page.locator('[data-testid^="tweetTextarea_"]').all()
        visible_tbs = [b for b in tbs if b.is_visible()]
        if not visible_tbs:
            logger.error("❌ 返信用テキストボックスが見つかりません。")
            page.screenshot(path=os.path.join(LOG_DIR, "failed_state_reply.png"))
            return False

        textbox = visible_tbs[0]
        textbox.evaluate("el => el.scrollIntoView({block: 'center'})")
        time.sleep(1)
        textbox.click()
        time.sleep(1)

        # 5. テキストをペースト
        safe_paste(page, reply_text)
        logger.info("   ✅ リプライテキスト（URL）を入力しました")
        time.sleep(2)

        # 6. OGPリンクプレビュー（顔写真等）の監視と削除
        logger.info("🔗 リンクプレビュー（顔写真等）が生成されるのを待機・監視します...")
        card_removed = False
        for _ in range(15):
            card_removed = page.evaluate("""() => {
                // 返信画面ではダイアログかどうか不明なため、全体からボタンを拾う
                const btns = Array.from(document.querySelectorAll('[role="button"], button'));
                for(const b of btns) {
                    const label = (b.getAttribute('aria-label') || '').toLowerCase();
                    const testid = (b.getAttribute('data-testid') || '').toLowerCase();
                    
                    if(testid.includes('removephoto') || testid.includes('removemedia') || label.includes('メディア')) {
                        continue;
                    }
                    
                    if(label.includes('リンクプレビューを削除') || label.includes('プレビューを削除') || label.includes('remove link preview') ||
                       testid.includes('removelinkpreview') || testid.includes('remove-card') || testid.includes('removecard')) {
                        b.click();
                        return true;
                    }
                }
                return false;
            }""")
            
            if card_removed:
                break
            time.sleep(1)
        
        if card_removed:
            logger.info("✅ リンクのプレビュー（写真カード）の削除に成功しました！")
        else:
            logger.info("⚠️ リンクプレビュー削除ボタンが見つかりませんでした。(プレビューが出ない仕様か、遅延の可能性)")
        time.sleep(2)

        if dry_run:
            logger.info("🔸 ドライラン: 返信ボタンは押しません")
            return True

        # 7. 返信（送信）ボタンのクリック
        reply_btn_clicked = page.evaluate("""() => {
            const btn = document.querySelector('[data-testid="tweetButtonInline"]') || 
                        document.querySelector('[data-testid="tweetButton"]');
            if (btn && !btn.disabled) {
                btn.removeAttribute('disabled');
                btn.removeAttribute('aria-disabled');
                btn.click();
                return true;
            }
            return false;
        }""")

        if not reply_btn_clicked:
            logger.error("❌ 送信（返信）ボタンが見つからないか、無効になっています。（文字数エラー等）")
            page.screenshot(path=os.path.join(LOG_DIR, "failed_state_reply_final.png"))
            return False

        logger.info("🎉 返信投稿完了！")
        time.sleep(3)
        return True

    except Exception as e:
        logger.error(f"❌ リプライ実行中にエラーが発生しました: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="VetEvidence X 追尾自動リプライスクリプト")
    parser.add_argument("--dry-run", action="store_true", help="テスト実行（返信ボタンを押さない）")
    parser.add_argument("--date", type=str, help="YYYY-MM-DD (指定日をテストしたい場合)")
    args = parser.parse_args()

    logger.info("=" * 50)
    logger.info("🐦 VetEvidence X 追尾自動リプライ スクリプト")
    logger.info("=" * 50)

    target_date = datetime.strptime(args.date, "%Y-%m-%d") if args.date else datetime.now()
    post = load_todays_post(target_date)
    
    if not post:
        sys.exit(0)

    logger.info(f"📝 対象: {post['source']}")

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

        page.goto("https://x.com/home", wait_until="domcontentloaded", timeout=20000)
        time.sleep(3)
        if "login" in page.url.lower():
            logger.error("❌ Xセッションが無効です。再ログインが必要です。")
            context.close()
            sys.exit(1)

        execute_reply(page, post, dry_run=args.dry_run)
        context.close()
        
    logger.info("✅ 処理終了")

if __name__ == "__main__":
    main()
