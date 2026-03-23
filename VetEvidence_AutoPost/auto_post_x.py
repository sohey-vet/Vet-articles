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
HISTORY_FILE = os.path.join(SCRIPT_DIR, "x_post_history.json")

# ----- ログ設定 -----
os.makedirs(LOG_DIR, exist_ok=True)
log_file = os.path.join(LOG_DIR, f"x_post_log_{datetime.now().strftime('%Y%m')}.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_todays_x_post(target_date):
    if not os.path.exists(SCHEDULE_FILE):
        logger.error(f"❌ スケジュールファイルが見つかりません: {SCHEDULE_FILE}")
        return None

    try:
        with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
            schedule = json.load(f)
            
        date_str = target_date.strftime("%Y-%m-%d")
        todays_posts = [p for p in schedule if p["date"] == date_str and p["platform"] == "X"]
        
        if not todays_posts:
            logger.info(f"📭 今日 ({date_str}) のX投稿データはありません。")
            return None
            
        return todays_posts[0]
    except Exception as e:
        logger.error(f"❌ スケジュール読み込みエラー: {e}")
        return None

def check_history_duplicate(target_date_str):
    if not os.path.exists(HISTORY_FILE):
        return False
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
        return any(h.get("date") == target_date_str for h in history)
    except:
        return False
        
def save_post_history(post):
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        except:
            pass
            
    history.append({
        "date": post["date"],
        "source": post["source"],
        "type": post["type"],
        "posted_at": datetime.now().isoformat()
    })
    
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def post_to_x(page, text, dry_run=False):
    logger.info("📝 Xに投稿します...")
    
    try:
        page.goto("https://x.com/compose/tweet", wait_until="domcontentloaded", timeout=20000)
        time.sleep(5)
        
        # メインテキストとリプライ（リンク）の分離
        cta_marker = "詳細・エビデンスはNoteへ"
        main_text = text
        reply_text = ""
        if cta_marker in text:
            idx = text.rfind(cta_marker)
            main_text = text[:idx].strip()
            reply_text = text[idx:].strip()

        def safe_paste(pg, t):
            # Xの特殊なエディタで文字が重複・消失するバグを防ぐため、クリップボード経由でペースト
            pg.evaluate("text => navigator.clipboard.writeText(text)", t)
            # macOSの場合はMeta+V、Windowsの場合はControl+V
            modifier = "Meta" if sys.platform == "darwin" else "Control"
            pg.keyboard.press(f"{modifier}+V")
            time.sleep(1)

        # 最初のボックスにメインテキストを入力（長文制限突破済みのため一括）
        textbox = page.locator('[data-testid="tweetTextarea_0"]').last
        if not textbox.is_visible(timeout=5000):
            logger.error("❌ Xのテキスト入力欄が見つかりません。未ログインの可能性があります。")
            return False
            
        textbox.click(force=True)
        time.sleep(1)
        safe_paste(page, main_text)
        time.sleep(2)
        
        # リンク部分をリプライツリー化（アルゴリズム減点回避 ＋ OGP画像削除）
        if reply_text:
            add_btn = page.locator('[aria-label="ポストを追加"], [aria-label="Add post"]').last
            if add_btn.is_visible():
                add_btn.click(force=True)
                time.sleep(2)
                textboxes = page.locator('[data-testid="tweetTextarea_0"]').all()
                textboxes[-1].click(force=True)
                time.sleep(1)
                safe_paste(page, reply_text)
                
                # リンクプレビュー(OGP顔画像)の展開を待ち、確実に削除する
                logger.info("🔗 リンクプレビュー展開を待機します...")
                time.sleep(6) # プレビューが描画されるのをしっかり待つ
                remove_card_btn = page.locator('[data-testid="card.wrapper"] [aria-label="削除"], [aria-label="カードを削除"], [aria-label="Remove card"], [aria-label="リンクプレビューを削除"]').first
                if remove_card_btn.is_visible():
                    remove_card_btn.click(force=True)
                    logger.info("✅ リンクのプレビュー(顔画像)の削除に成功しました！")
                time.sleep(1)
        
        if dry_run:
            logger.info("🔸 ドライラン: 投稿ボタンは押しません")
            return True

        # 投稿ボタンをクリック (すべてポスト)
        post_btn = page.locator('[data-testid="tweetButton"]').last
        if post_btn.is_visible() and post_btn.get_attribute('aria-disabled') != 'true':
            post_btn.click(force=True)
            logger.info("✅ 投稿ボタンをクリックしました")
            time.sleep(8)  # 複数の投稿完了を待つ
            return True
        else:
            logger.error("❌ 有効な投稿ボタンが見つかりません（文字数オーバーの可能性など）")
            return False

    except Exception as e:
        logger.error(f"❌ エラー: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="VetEvidence X 自動投稿スクリプト")
    parser.add_argument("--dry-run", action="store_true", help="テスト実行（投稿ボタンを押さない）")
    parser.add_argument("--setup", action="store_true", help="初回ログイン用のブラウザを起動")
    parser.add_argument("--date", type=str, help="YYYY-MM-DD (指定日をテストしたい場合)")
    args = parser.parse_args()

    logger.info("=" * 50)
    logger.info("🐦 VetEvidence X 自動投稿スクリプト (Playwright版)")
    logger.info("=" * 50)

    # 1. ログインセットアップモード
    if args.setup:
        logger.info("🔧 初回セットアップ（ログイン）モードで起動します...")
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=SESSION_DIR,
                headless=False,
                channel="msedge",
                viewport={"width": 1280, "height": 900},
                args=["--disable-blink-features=AutomationControlled"]
            )
            page = context.pages[0] if context.pages else context.new_page()
            page.evaluate("() => Object.defineProperty(navigator, 'webdriver', { get: () => undefined })")
            page.goto("https://x.com/")
            print("\n" + "*"*50)
            print("👤 ブラウザが開きました。PawMedicalアカウントでX(Twitter)にログインしてください。")
            print("ログインが完了してホーム画面が表示されたら、このコンソールで Enter キーを押してください。")
            print("*"*50 + "\n")
            input()
            context.close()
            logger.info("✅ セッションを保存しました。通常実行が可能になります。")
        return

    # 2. 投稿モード
    target_date = datetime.strptime(args.date, "%Y-%m-%d").date() if args.date else datetime.now().date()
    target_date_str = target_date.strftime("%Y-%m-%d")
    
    if check_history_duplicate(target_date_str) and not args.dry_run and not args.date:
        logger.info(f"⏭️ {target_date_str} のX投稿は既に完了しているためスキップします。")
        sys.exit(0)
        
    post = load_todays_x_post(target_date)
    if not post:
        sys.exit(0)
        
    text = post["content"].replace("\r\n", "\n").strip()
    if not text:
        logger.error("❌ 投稿テキストが空です。")
        sys.exit(1)

    logger.info(f"📅 投稿対象: {target_date_str}")
    logger.info(f"📝 ソース: {post['source']}")
    logger.info(f"📄 内容プレビュー: {text[:50]}...")

    if not os.path.exists(SESSION_DIR):
        logger.error("❌ セッションが見つかりません。先に --setup オプションでログインしてください。")
        sys.exit(1)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=SESSION_DIR,
            headless=False, # XのBot検知を回避するためにHeaded推奨
            channel="msedge",
            locale="ja-JP",
            viewport={"width": 1280, "height": 900},
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.evaluate("() => Object.defineProperty(navigator, 'webdriver', { get: () => undefined })")

        success = post_to_x(page, text, dry_run=args.dry_run)
        
        if success and not args.dry_run:
            save_post_history(post)
            logger.info("🎉 処理が正常に完了しました！")
        else:
            if not success: logger.error("❌ 処理に失敗しました。")
            
        context.close()
        
        if not success:
            sys.exit(1)

if __name__ == "__main__":
    main()
