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

def find_image(source_folder):
    """指定されたフォルダからPNG画像を検索する"""
    DRAFTS_ROOT = r"C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts"
    folder_path = os.path.join(DRAFTS_ROOT, source_folder)
    png_files = glob.glob(os.path.join(folder_path, "*.png"))
    if png_files:
        return png_files[0]
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

def assassinate_ghost_tweets(page, main_text):
    logger.info("🕵️‍♂️ 二重投稿バグ（同じ記事が2回連続で投稿される現象）がないかパトロールします...")
    try:
        # 今投稿した記事の最初の1行（見出し）をシグネチャとする
        lines = main_text.strip().split('\n')
        signature = lines[0].strip()
        if not signature or len(signature) < 5:
            return

        # プロフィールへアクセス
        page.goto("https://x.com/pawmedical_jp", wait_until="domcontentloaded", timeout=20000)
        time.sleep(5)
        
        for _ in range(3):
            tweets = page.locator('article[data-testid="tweet"]').all()
            ghost_assassinated = False
            matching_tweets = []
            
            for tweet in tweets:
                try:
                    tweet_text = tweet.locator('[data-testid="tweetText"]').inner_text()
                    
                    # 直近の投稿のみに絞る
                    time_elem = tweet.locator('time').first
                    if not time_elem.is_visible():
                        continue
                    time_txt = time_elem.inner_text()
                    is_recent = ("秒" in time_txt) or ("分" in time_txt) or ("時間" in time_txt and int(time_txt.replace("時間", "").strip()) <= 2)
                    
                    if not is_recent:
                        continue
                        
                    # サイン（見出し）が含まれているか？
                    if signature in tweet_text:
                        matching_tweets.append({"element": tweet, "text": tweet_text})
                except Exception:
                    continue
                    
            # もし同じ見出しのツイートが2個以上あった場合、二重投稿バグが発生している！
            if len(matching_tweets) >= 2:
                logger.warning(f"🚨 同じ記事の二重投稿バグを発見しました！（検出数: {len(matching_tweets)}）不要な方を暗殺します...")
                
                # 削除すべきゴーストを特定する
                protected = False
                for item in matching_tweets:
                    # 本物（完全一致に近いもの）をまだ保護していない場合は保護
                    # （Xの改行の違いを吸収するために適度に判定）
                    if not protected and main_text[:30].strip() in item["text"]:
                        protected = True
                        logger.info("🛡️ 直近の正しい投稿を保護対象としてマークしました。")
                        continue
                        
                    # それ以外は削除対象（古いゴースト）
                    logger.info(f"🗑️ ゴーストを削除します: {item['text'][:30]}...")
                    more_btn = item["element"].locator('[data-testid="caret"]').first
                    if more_btn.is_visible():
                        more_btn.click()
                        time.sleep(1)
                        
                        delete_menu = page.locator('[role="menuitem"]').filter(has_text="削除").first
                        if delete_menu.is_visible():
                            delete_menu.click()
                            time.sleep(1)
                            
                            confirm_btn = page.locator('[data-testid="confirmationSheetConfirm"]').first
                            if confirm_btn.is_visible():
                                confirm_btn.click()
                                logger.info("✅ ゴースト二重投稿を自動削除（暗殺）しました！")
                                ghost_assassinated = True
                                time.sleep(3)
                                break  # 1つ消したら一旦終了
                        else:
                            page.mouse.click(0, 0)
            else:
                logger.info("ℹ️ 二重投稿は検出されませんでした（健全です）。")
                break
                
            if ghost_assassinated:
                break
                
            page.evaluate("window.scrollBy(0, 500)")
            time.sleep(1)
            
    except Exception as e:
        logger.error(f"⚠️ ゴースト投稿パトロール中にエラーが発生しました: {e}")

def post_to_x(page, text, dry_run=False, image_path=None, target_date_str=None):
    logger.info("📝 Xに投稿します...")
    
    try:
        # Xの表示状態（下書き復元など）を一旦リセットするため、ホームを経由する
        page.goto("https://x.com/home", wait_until="domcontentloaded", timeout=20000)
        time.sleep(2)
        page.goto("https://x.com/compose/tweet", wait_until="domcontentloaded", timeout=20000)
        time.sleep(5)
        
        # 1. ハッシュタグの完全削除
        import re
        text = re.sub(r'#\S+', '', text).strip()

        # 2. メインテキストとリプライ（リンクのみ化）の分離
        konkyo_marker = "📄 根拠:"
        if konkyo_marker in text:
            # 根拠部分は破棄
            text = text[:text.rfind(konkyo_marker)].strip()

        # インプレッション低下を防ぐため、外部リンクやNote誘導を完全に分離してツリーへ回す
        blocks = re.split(r'\n\s*\n', text)
        split_index = len(blocks)
        
        for i in range(len(blocks) - 1, -1, -1):
            block = blocks[i]
            # 外部リンク文字が含まれるブロックを見つける
            if "http:" in block or "https:" in block or "note.com" in block:
                split_index = i
                # その直前のブロックが誘導文なら遡ってツリーに含める
                while split_index > 0:
                    prev_block = blocks[split_index - 1]
                    if any(k in prev_block for k in ["詳細", "Note", "プロフ", "リンク", "💡", "🔗", "👇", "こちら"]):
                        split_index -= 1
                    else:
                        break
                break
                
        # リンクが見つからなかった場合のフォールバック（旧形式対応）
        if split_index == len(blocks):
            cta_marker = "詳細・エビデンスはNoteへ"
            if cta_marker in text:
                idx = text.rfind(cta_marker)
                main_text = text[:idx].strip()
                reply_text = text[idx:].strip()
            else:
                main_text = text
                reply_text = ""
        else:
            main_text = "\n\n".join(blocks[:split_index]).strip()
            reply_text = "\n\n".join(blocks[split_index:]).strip()
            
        # 安全策：すべてがツリーに行ってしまった場合は元に戻す
        if not main_text:
            main_text = text
            reply_text = ""

        # 4月中はリンクの投稿をストップする（リプライ部分を破棄）
        if target_date_str and target_date_str.startswith("2026-04"):
            logger.info("🚫 4月中はNoteリンク設定が無効になっているため、リンク誘導リプライを削除します。")
            reply_text = ""


        def safe_paste(pg, t):
            pg.evaluate("""(text) => {
                const dataTransfer = new DataTransfer();
                dataTransfer.setData('text/plain', text);
                const el = document.activeElement;
                const pasteEvent = new ClipboardEvent('paste', {
                    bubbles: true,
                    cancelable: true,
                    clipboardData: dataTransfer
                });
                el.dispatchEvent(pasteEvent);
            }""", t)
            time.sleep(1)

        # 1. 画像の添付 (メインツイート)
        if image_path:
            file_input = page.locator('input[data-testid="fileInput"]').first
            file_input.set_input_files(image_path)
            logger.info("✅ 画像を添付しました")
            time.sleep(2)

        # 最初のボックスにメインテキストを入力（長文制限突破済みのため一括）
        textbox = page.locator('[data-testid="tweetTextarea_0"]').last
        if not textbox.is_visible(timeout=5000):
            logger.error("❌ Xのテキスト入力欄が見つかりません。未ログインの可能性があります。")
            return False
            
        textbox.click(force=True)
        time.sleep(1)
        
        # 既存の下書きが残っていた場合は全消去する
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        time.sleep(1)
        
        def safe_paste(pg, t):
            pg.evaluate("""(text) => {
                const dataTransfer = new DataTransfer();
                dataTransfer.setData('text/plain', text);
                const el = document.activeElement;
                const pasteEvent = new ClipboardEvent('paste', {
                    bubbles: true,
                    cancelable: true,
                    clipboardData: dataTransfer
                });
                el.dispatchEvent(pasteEvent);
            }""", t)
            time.sleep(1)

        # 再度フォーカスを確実にする
        # 画面に確実に見えているものだけを抽出（バックグラウンドのゴースト要素を無視する）
        tbs = page.locator('[role="dialog"] [data-testid^="tweetTextarea_"]').all()
        visible_tbs = [b for b in tbs if b.is_visible()]
        if not visible_tbs:
            logger.error("❌ 表示されているテキスト入力欄が見つかりません。")
            return False
        textbox = visible_tbs[0]
        # 背景誤爆を防ぐため確実に画面中央へ
        textbox.evaluate("el => el.scrollIntoView({block: 'center'})")
        time.sleep(0.5)
        textbox.click()
        time.sleep(0.5)
        
        # クリップボード経由で安全にペースト（改行やURLの不具合回避）
        safe_paste(page, main_text)
        time.sleep(2)
        
        # リンク部分をリプライツリー化（アルゴリズム減点回避 ＋ OGP画像削除）
        if reply_text:
            add_btn_clicked = page.evaluate("""() => {
                const btn = document.querySelector('[role="dialog"] [aria-label="ポストを追加"]') || document.querySelector('[role="dialog"] [aria-label="Add post"]');
                if(btn) {
                    btn.scrollIntoView({block: 'center'});
                    btn.click();
                    return true;
                }
                return false;
            }""")
            
            if add_btn_clicked:
                logger.info("➕ ツリー追加ボタンをクリックしました。2つ目の入力欄を待機します。")
                time.sleep(3) # レンダリングを長めに待機
                
                # 新しいテキストボックス群を再度取得
                tbs_thread = page.locator('[role="dialog"] [data-testid^="tweetTextarea_"]').all()
                visible_tbs_thread = [b for b in tbs_thread if b.is_visible()]
                
                if len(visible_tbs_thread) > 1:
                    logger.info("✅ 2つ目のテキストボックスを検出しました。ペースト処理へ移行します。")
                    text_box_2 = visible_tbs_thread[-1]
                    
                    # 完全に画面中央にスクロールさせる（これがないと画面外判定で背景をクリックしてしまう）
                    text_box_2.evaluate("el => el.scrollIntoView({block: 'center'})")
                    time.sleep(1)
                    
                    # ネイティブフォーカス
                    text_box_2.evaluate("el => el.focus()")
                    time.sleep(1)
                    
                    # 安全なクリック（force=Trueは絶対に使わない。背景誤爆の原因になる）
                    text_box_2.click()
                    time.sleep(1)
                    
                    safe_paste(page, reply_text)
                else:
                    logger.error("❌ 2つ目のテキストボックスが生成されませんでした。")
                
                # リンクプレビュー(OGP顔画像)の展開を待ち、確実に削除する
                logger.info("🔗 リンクプレビュー（顔写真等）が生成されるのを待機・監視します...")
                
                card_removed = False
                for _ in range(15):
                    card_removed = page.evaluate("""() => {
                        const btns = Array.from(document.querySelectorAll('[role="dialog"] [role="button"], [role="dialog"] button'));
                        for(const b of btns) {
                            const label = (b.getAttribute('aria-label') || '').toLowerCase();
                            const testid = (b.getAttribute('data-testid') || '').toLowerCase();
                            
                            // 画像添付の削除ボタンには絶対に触らない
                            if(testid.includes('removephoto') || testid.includes('removemedia') || label.includes('メディア')) {
                                continue;
                            }
                            
                            // リンクプレビュー用の削除ボタンを検知
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
            logger.info("🔸 ドライラン: 投稿ボタンは押しません")
            return True

        # 投稿ボタンをクリック (すべてポスト)
        post_btn_clicked = False
        logger.info("⏳ 投稿ボタンの有効化（画像アップロード完了）を待機しています...")
        
        for _ in range(15):
            is_active = page.evaluate("""() => {
                const btns = Array.from(document.querySelectorAll('[data-testid="tweetButton"]'));
                const activeBtns = btns.filter(b => !b.hasAttribute('disabled') && b.getAttribute('aria-disabled') !== 'true');
                if(activeBtns.length > 0) {
                    activeBtns[activeBtns.length - 1].scrollIntoView({block: 'center'});
                    activeBtns[activeBtns.length - 1].click();
                    return true;
                }
                return false;
            }""")
            if is_active:
                post_btn_clicked = True
                break
            time.sleep(1)
        
        if post_btn_clicked:
            logger.info("✅ 投稿ボタンをクリックしました")
            time.sleep(8)  # 複数の投稿完了を待つ

            # 注: assassinate_ghost_tweets()は正常な親ツイートを削除してしまう重大なバグ（リプだけ孤立する原因）があったため機能を停止しました。

            return True
        else:
            logger.error("❌ 有効な投稿ボタンが見つかりません（文字数制限エラー、またはネットワーク遅延・画像容量オーバーの疑い）")
            # デバッグ用にスクリーンショットを保存
            page.screenshot(path="C:\\Users\\souhe\\Desktop\\VetEvidence_SNS_Drafts\\VetEvidence_AutoPost\\failed_state.png", full_page=True)
            logger.info("📸 エラー時の画面状態を 'failed_state.png' に保存しました。")
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
    
    # 4月13日〜19日まではXの投稿をストップする（20日から再開）
    if "2026-04-13" <= target_date_str <= "2026-04-19":
        logger.info(f"⏸️ シャドウバン回復期間のため、{target_date_str} のX自動投稿をスキップします。")
        sys.exit(0)

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
    
    image_path = find_image(post['source'])
    if image_path:
        logger.info(f"📷 添付画像: {os.path.basename(image_path)}")
        
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

        success = post_to_x(page, text, dry_run=args.dry_run, image_path=image_path, target_date_str=target_date_str)
        
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
