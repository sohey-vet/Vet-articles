import os
import sys
import json
import time
import argparse
import logging
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# ----- パス設定 -----
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_DIR = os.path.join(SCRIPT_DIR, ".threads_session")
LOG_DIR = os.path.join(SCRIPT_DIR, "logs")
SCHEDULE_FILE = os.path.join(SCRIPT_DIR, "sns_schedule.json")
LATEST_URL_FILE = os.path.join(SCRIPT_DIR, "threads_latest_post_url.txt")

def get_latest_post_url_from_profile(page):
    """プロフィールから最新の投稿URLを取得する"""
    logger.info("🔍 プロフィールから最新の投稿URLを取得します...")
    page.goto("https://www.threads.net/@pawmedical_jp", wait_until="domcontentloaded", timeout=15000)
    time.sleep(4)
    try:
        # 投稿リンクを探す (最初のものを取得)
        link_elems = page.locator('a[href*="/post/"]').all()
        for link in link_elems:
            if link.is_visible():
                href = link.get_attribute("href")
                if href:
                    url = f"https://www.threads.net{href}" if href.startswith("/") else href
                    logger.info(f"✅ 最新の投稿URLを取得しました: {url}")
                    return url
    except Exception as e:
        logger.error(f"❌ プロフィールからのURL取得に失敗しました: {e}")
    logger.warning("⚠️ 投稿URLが見つかりませんでした。")
    return None


# ----- ログ設定 -----
os.makedirs(LOG_DIR, exist_ok=True)
log_file = os.path.join(LOG_DIR, f"threads_post_log_{datetime.now().strftime('%Y%m')}.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_todays_threads_post(target_date):
    """スケジュールから今日のThreads投稿を取得"""
    if not os.path.exists(SCHEDULE_FILE):
        logger.error(f"❌ スケジュールファイルが見つかりません: {SCHEDULE_FILE}")
        return None

    try:
        with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
            schedule = json.load(f)
            
        date_str = target_date.strftime("%Y-%m-%d")
        todays_posts = [p for p in schedule if p["date"] == date_str and p["platform"] == "Threads"]
        
        if not todays_posts:
            logger.info(f"📭 今日 ({date_str}) のThreads投稿データはありません。")
            return None
            
        return todays_posts[0]
        
    except Exception as e:
        logger.error(f"❌ スケジュール読み込みエラー: {e}")
        return None

def normalize_text(text):
    """テキストの改行を正規化する"""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text

def post_to_threads(page, text, target_date, dry_run=False):
    """PlaywrightでThreadsにテキストを投稿する"""
    logger.info("📝 Threadsに投稿します...")
    
    is_quote_day = target_date.weekday() in [1, 3, 5]  # 火(1) 木(3) 土(5)
    quote_mode_active = False

    try:
        # 1. 投稿ダイアログを開く (ThreadsのWeb UI構成に依存)
        
        if is_quote_day:
            logger.info("🔄 本日は引用投稿（火・木・土）の日です。引用元のURLを探します...")
            quote_url = None
            if os.path.exists(LATEST_URL_FILE):
                try:
                    with open(LATEST_URL_FILE, "r", encoding="utf-8") as f:
                        quote_url = f.read().strip()
                    logger.info(f"📄 保存されていたURLを使用します: {quote_url}")
                except Exception as e:
                    logger.error(f"❌ URLファイルの読み込みに失敗しました: {e}")
            
            if not quote_url:
                logger.warning("⚠️ 保存されたURLが見つからないため、プロフィールから取得を試みます...")
                quote_url = get_latest_post_url_from_profile(page)
                
            if quote_url:
                logger.info(f"🔗 引用元URLを開きます: {quote_url}")
                page.goto(quote_url, wait_until="domcontentloaded", timeout=15000)
                time.sleep(5)
                
                # 再投稿（Repost）ボタンを探す
                repost_trigger = None
                repost_selectors = [
                    'svg[aria-label="再投稿"]',
                    'svg[aria-label="Repost"]',
                    '[aria-label="再投稿"]',
                    '[aria-label="Repost"]'
                ]
                for selector in repost_selectors:
                    try:
                        elem = page.locator(selector).first
                        if elem.is_visible(timeout=2000):
                            repost_trigger = elem
                            break
                    except:
                        pass
                
                if repost_trigger:
                    repost_trigger.click(force=True)
                    time.sleep(2) # メニュー展開待ち
                    
                    # 「引用」メニューを探す
                    quote_trigger = None
                    quote_selectors = [
                        'text="引用"',
                        'text="Quote"',
                        '[aria-label="引用"]',
                        '[aria-label="Quote"]',
                        'div[role="button"]:has-text("引用")'
                    ]
                    for selector in quote_selectors:
                        try:
                            elem = page.locator(selector).first
                            if elem.is_visible(timeout=2000):
                                quote_trigger = elem
                                break
                        except:
                            pass
                            
                    if quote_trigger:
                        quote_trigger.click(force=True)
                        time.sleep(2)
                        logger.info("✅ 引用ダイアログを開きました")
                        quote_mode_active = True
                    else:
                        logger.error("❌ 引用メニューが見つかりませんでした。通常の新規投稿に切り替えます。")
                else:
                    logger.error("❌ 再投稿ボタンが見つかりませんでした。通常の新規投稿に切り替えます。")
            else:
                logger.error("❌ 引用対象のURLがどうしても取得できなかったため、通常の新規投稿に切り替えます。")

        if not quote_mode_active:
            # 通常の投稿（月水金、または引用フロー失敗時）
            page.goto("https://www.threads.net/", wait_until="domcontentloaded", timeout=15000)
            time.sleep(3)
        
        # 通常の投稿ダイアログを開くためのボタン探し
        if not quote_mode_active:
            compose_trigger = None
            selectors = [
                'text="今なにしてる？"',
                'text="Start a thread..."',
                '[aria-label="新しいスレッドを開始"]',
                '[aria-label="Start a thread"]',
                'svg[aria-label="新しいスレッドを開始"]',
                'svg[aria-label="Start a thread"]',
                'div[role="button"]:has-text("スレッドを開始")'
            ]
            
            for selector in selectors:
                try:
                    elem = page.locator(selector).first
                    if elem.is_visible(timeout=2000):
                        compose_trigger = elem
                        break
                except Exception:
                    pass
                    
            if not compose_trigger:
                # フォールバック: テキストエリア自体が最初から見えている場合
                compose_trigger = page.locator('div[contenteditable="true"]').first
                
            if compose_trigger and compose_trigger.is_visible():
                compose_trigger.click(force=True)
                time.sleep(2)
            else:
                logger.error("❌ 投稿開始ボタンまたは入力欄が見つかりません")
                return False

        # 2. テキストを入力
        # テキストを500文字以内のチャンクに分割
        def split_text(t, limit=480):
            chunks = []
            while len(t) > limit:
                # 1. 見出し（【）の前での分割を最優先
                split_idx = t.rfind("\n【", 0, limit)
                if split_idx == -1:
                    split_idx = t.rfind("\n・", 0, limit)
                # 2. 見出しがない場合は段落の切れ目
                if split_idx == -1:
                    split_idx = t.rfind("\n\n", 0, limit)
                # 3. 通常の改行
                if split_idx == -1:
                    split_idx = t.rfind("\n", 0, limit)
                # 4. 改行もない場合は句点
                if split_idx == -1:
                    split_idx = t.rfind("。", 0, limit)
                
                if split_idx == -1:
                    split_idx = limit
                else:
                    if t[split_idx] == "。":
                        split_idx += 1 # 句点は含める
                    
                chunks.append(t[:split_idx].strip())
                t = t[split_idx:].strip()
            if t:
                chunks.append(t)
            return chunks

        chunks = split_text(text, 480)

        # 最初のボックス
        text_areas = page.locator('div[contenteditable="true"]').all()
        if not text_areas:
            logger.error("❌ テキスト入力欄が見つかりません")
            return False
            
        text_areas[0].click(force=True)
        time.sleep(1)
        # プレビューカードを削除する内部関数
        def remove_link_preview_if_needed(chunk_text):
            if "http" in chunk_text:
                logger.info("🔗 URLが含まれているため、リンクプレビュー展開を待機します...")
                time.sleep(5)
                remove_selectors = [
                    'div[role="button"]:has(svg[aria-label="削除情報を追加"])',
                    'div[role="button"]:has(svg[aria-label="Remove attachment"])',
                    'div[role="button"]:has(svg[aria-label="削除"])'
                ]
                removed = False
                for s in remove_selectors:
                    btn = page.locator(s).first
                    if btn.is_visible(timeout=1000):
                        btn.click(force=True)
                        logger.info("✅ 巨大なリンクプレビュー(OGP画像)の削除に成功しました！")
                        removed = True
                        time.sleep(1)
                        break
                if not removed:
                    logger.warning("⚠️ プレビュー削除ボタンが見つかりませんでした。プレビューが残る可能性があります。")

        text_areas[0].focus()
        page.keyboard.insert_text(chunks[0].strip())
        time.sleep(2)
        remove_link_preview_if_needed(chunks[0])

        # 2つ目以降のブロックがあれば「スレッドに追加」
        for i in range(1, len(chunks)):
            add_thread_btn = page.locator('text="スレッドに追加"').last
            if add_thread_btn.is_visible():
                add_thread_btn.click(force=True)
                time.sleep(1)
            
            text_areas = page.locator('div[contenteditable="true"]').all()
            if text_areas:
                text_areas[-1].focus()
                page.keyboard.insert_text(chunks[i].strip())
                time.sleep(1)
                remove_link_preview_if_needed(chunks[i])
        
        if dry_run:
            logger.info("🔸 ドライラン: 投稿ボタンは押しません")
            return True

        # 3. 投稿ボタンをクリック
        # 3. 投稿ボタンをクリック (最後のものを優先)
        post_btn = None
        btns = page.locator('div[role="button"]:has-text("投稿")').all()
        for b in reversed(btns):
            if b.is_visible() and b.get_attribute('aria-disabled') != 'true':
                post_btn = b
                break
                
        if post_btn:
            post_btn.click(force=True)
            logger.info("✅ 投稿ボタンをクリックしました")
            time.sleep(6)  # 投稿完了を待つ

            # 月水金（通常投稿）の場合はURLを保存して次回（火木土）の引用に備える
            if not is_quote_day:
                latest_url = get_latest_post_url_from_profile(page)
                if latest_url:
                    try:
                        with open(LATEST_URL_FILE, "w", encoding="utf-8") as f:
                            f.write(latest_url)
                        logger.info(f"💾 次回（火木土）のために投稿URLを保存しました: {latest_url}")
                    except Exception as e:
                        logger.error(f"❌ URLファイルの保存に失敗しました: {e}")

            return True
        else:
            logger.error("❌ 有効な投稿ボタンが見つかりません")
            return False

    except PlaywrightTimeout as e:
        logger.error(f"❌ タイムアウト: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ エラー: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Threads 自動投稿スクリプト")
    parser.add_argument("--dry-run", action="store_true", help="テスト実行（投稿ボタンを押さない）")
    parser.add_argument("--headless", action="store_true", help="ヘッドレスモードで実行")
    parser.add_argument("--setup", action="store_true", help="初回ログイン用のブラウザを起動")
    parser.add_argument("--date", type=str, help="YYYY-MM-DD (指定日をテストしたい場合)")
    args = parser.parse_args()

    logger.info("=" * 50)
    logger.info("🧵 Threads 自動投稿スクリプト")
    logger.info("=" * 50)

    # 1. ログインセットアップモード
    if args.setup:
        logger.info("🔧 初回セットアップ（ログイン）モードで起動します...")
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=SESSION_DIR,
                headless=False,
                viewport={"width": 1280, "height": 900}
            )
            page = context.pages[0] if context.pages else context.new_page()
            page.goto("https://www.threads.net/login")
            print("\n" + "*"*50)
            print("👤 ブラウザが開きました。Threads (Instagramアカウント) でログインしてください。")
            print("認証が完了してホーム画面が表示されたら、このコンソールで Enter キーを押してください。")
            print("*"*50 + "\n")
            input()
            context.close()
            logger.info("✅ セッションを保存しました。通常実行が可能です。")
        return

    # 2. 投稿モード
    target_date = datetime.strptime(args.date, "%Y-%m-%d").date() if args.date else datetime.now().date()
    
    post = load_todays_threads_post(target_date)
    if not post:
        sys.exit(0)
        
    text = normalize_text(post["content"])
    if not text.strip():
        logger.error("❌ 投稿テキストが空です。")
        sys.exit(1)

    logger.info(f"📅 投稿対象: {target_date.isoformat()}")
    logger.info(f"📝 ソース: {post['source']}")
    logger.info(f"📄 内容プレビュー: {text[:50]}...")

    if not os.path.exists(SESSION_DIR):
        logger.error("❌ セッションが見つかりません。先に --setup オプションでログインしてください。")
        sys.exit(1)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=SESSION_DIR,
            headless=False,  # Instagram/Threads detects headless mode and forces logout, so must run headed
            locale="ja-JP",
            timezone_id="Asia/Tokyo",
            viewport={"width": 1280, "height": 900},
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = context.pages[0] if context.pages else context.new_page()
        
        # Webdriver検知回避
        page.evaluate("() => Object.defineProperty(navigator, 'webdriver', { get: () => undefined })")

        success = post_to_threads(page, text, target_date, dry_run=args.dry_run)
        
        if success:
            logger.info("🎉 処理が正常に完了しました！")
        else:
            logger.error("❌ 処理に失敗しました。")
            
        context.close()
        
        if not success:
            sys.exit(1)

if __name__ == "__main__":
    main()
