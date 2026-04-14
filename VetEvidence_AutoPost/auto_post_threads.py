import os
import sys
import json
import time
import argparse
import logging
import glob
import random
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

def find_image(source_folder):
    """指定されたフォルダからPNG画像を検索する"""
    DRAFTS_ROOT = r"C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts"
    folder_path = os.path.join(DRAFTS_ROOT, source_folder)
    png_files = glob.glob(os.path.join(folder_path, "*.png"))
    if png_files:
        return png_files[0]
    return None

def generate_quote_text(text):
    """記事の内容からキーワードを抽出し、適切なニュアンスのリマインド文を10パターンから選択・生成する"""
    categories = []
    if any(k in text for k in ["救急", "緊急", "ショック", "重症", "ICU", "心肺蘇生", "呼吸困難", "出血"]):
        categories.append('emergency')
    if any(k in text for k in ["猫", "ねこ", "Feline", "キャット"]):
        categories.append('cat')
    if any(k in text for k in ["犬", "いぬ", "Canine", "ドッグ"]):
        categories.append('dog')
    if any(k in text for k in ["ガイドライン", "エビデンス", "最新", "JCVIM", "ACVIM", "WSAVA", "論文"]):
        categories.append('evidence')

    # 基本の10バリエーション
    texts = [
        "この記事、臨床現場で非常に遭遇しやすいケースなので再掲します。詳細はツリーの案内から👇",
        "診断や治療方針で迷った際に役立つエビデンスです。日々の臨床のヒントになれば幸いです💡詳細はツリーの案内から👇",
        "知っているか知らないかで予後が変わる重要なトピックなので再シェアします。具体的な案内は下のツリーから👇",
        "教科書的な知識から一歩踏み込んだ、臨床向けのリアルな解説です。おさらいとして再掲します。詳細へのアクセスはツリーにて👇",
        "この疾患の管理において、特に注意すべきポイントをまとめた記事です。さらに詳しいエビデンスの確認はツリーの案内からどうぞ👇",
        "ご家族への説明や、スタッフ間の知識共有にも役立つ内容なので再投稿します📝実践的なアプローチへのアクセスはツリーへ👇",
        "このケース、実際に直面した時に焦らないように再シェアしておきます。さらに専門的な解説の確認方法はツリーから👇",
        "よくある主訴ですが、意外と落とし穴が多い疾患です。見逃し防止のチェックリスト、詳細はツリーから👇",
        "治療の引き出しを増やすための実践的なアプローチです。明日の診療からすぐ使えるエビデンスの詳細は下のツリーから👇",
        "忙しい診察の合間にサクッと復習できる内容です。より深い病態生理や推奨薬の詳細へのアクセスはツリーにて解説しています👇"
    ]
    
    # 記事内容に合わせた特化バージョンの優先適用
    if 'emergency' in categories:
        return "救急対応や初期診療で絶対に迷いたくない知識なので、振り返りとしてシェアします🚑より詳しいエビデンスへのアクセスはツリーへ👇"
    if 'cat' in categories and 'dog' not in categories:
        return "猫の特異的な病態について、非常に重要なポイントなので再シェアします🐈具体的な管理法など詳細へのアクセスはツリーにて解説しています👇"
    if 'dog' in categories and 'cat' not in categories:
        return "犬の診療で知っておくべき最新の知見です🐕アップデートのために再掲します。さらに詳しい解説への案内はツリーから👇"
    if 'evidence' in categories:
        return "一次診療でも知っておきたい重要なガイドライン・最新知見のおさらいです📚治療水準のアップデートに関する詳細はツリーから👇"
        
    return random.choice(texts)

def normalize_text(text):
    """テキストの改行を正規化する"""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text

def post_to_threads(page, text, target_date, dry_run=False, image_path=None):
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

        # 2. テキストを入力・処理
        import re
        
        # リンク部分と誘導部分を分離する内部関数
        def extract_link_reply(t):
            import random
            konkyo_marker = "📄 根拠:"
            if konkyo_marker in t:
                t = t[:t.rfind(konkyo_marker)].strip()
                
            blocks = re.split(r'\n\s*\n', t)
            split_index = len(blocks)
            for i in range(len(blocks) - 1, -1, -1):
                block = blocks[i]
                if "http:" in block or "https:" in block or "note.com" in block:
                    split_index = i
                    while split_index > 0:
                        prev_block = blocks[split_index - 1]
                        if any(k in prev_block for k in ["詳細", "Note", "プロフ", "リンク", "💡", "🔗", "👇", "こちら"]):
                            split_index -= 1
                        else:
                            break
                    break
                    
            if split_index == len(blocks):
                cta_marker = "詳細・エビデンスはNoteへ"
                if cta_marker in t:
                    idx = t.rfind(cta_marker)
                    main_t = t[:idx].strip()
                else:
                    main_t = t
            else:
                main_t = "\n\n".join(blocks[:split_index]).strip()
            
            if not main_t:
                return t, ""
                
            # メイン投稿側の余計な誘導文(CTA)を完全に削除（これがあると長文時にツリーが2重分割されるため）
            if main_t.endswith("👇") or main_t.endswith("💡"):
                main_t = main_t[:-1].strip()
                
            # ツリー部分のプロフ誘導文（4パターンをご指定通りに修正）
            pattern_general = "💡 疾患の詳細や、明日から使える最新エビデンスは、プロフィール欄のNoteリンクから解説記事をチェックしてみてください🐾"
            pattern_paper = "📚 今回のトピックの完全版（論文リファレンス付き）は、プロフィールのURLからNote記事を参照してください"
            pattern_clinic = "🏥 診療で使えるガイドラインや推奨薬の詳細は、プロフのリンク先にある記事の中でさらに深堀りしています"
            pattern_pathology = "📝 「さらに掘り下げた細かい病態生理や鑑別も知りたい！」という方は、プロフィールにあるリンクからNote全編をぜひご覧ください"
            
            check_text = main_t.lower()
            if any(k in check_text for k in ["論文", "リファレンス", "文献", "ガイドライン", "aaha", "wsava", "jvim"]):
                reply_t = pattern_paper
            elif any(k in check_text for k in ["薬", "投与", "用量", "救急", "ショック", "治療", "麻酔", "初期対応"]):
                reply_t = pattern_clinic
            elif any(k in check_text for k in ["病態", "生理", "機序", "メカニズム", "ホルモン", "鑑別", "原因"]):
                reply_t = pattern_pathology
            else:
                reply_t = pattern_general
            
            return main_t, reply_t

        # メインテキストとプロフ誘導(ツリー)を抽出
        main_text, reply_text = extract_link_reply(text)
        
        if quote_mode_active:
            # 引用ポストの場合、元投稿がカード化するので画像は不要
            image_path = None

        # テキストを500文字以内のチャンクに分割 (Threadsの文字数制限対応)
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

        chunks = split_text(main_text, 480)
        # リンクや誘導文があれば、スレッドの「次のチャンク」として強制的に分ける
        if reply_text:
            chunks.extend(split_text(reply_text, 480))

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
                time.sleep(6)
                try:
                    # OGPプレビューの削除ボタンをクリック
                    removed = page.evaluate("""() => {
                        const svgs = Array.from(document.querySelectorAll('svg'));
                        for (let i = svgs.length - 1; i >= 0; i--) {
                            const svg = svgs[i];
                            const label = (svg.getAttribute('aria-label') || '');
                            // Threadsのリンクプレビュー削除や一般的な削除ボタンを探す
                            // OGPは最後の方のDOMに生成されるため後ろから探す
                            if (label.includes('添付ファイルを削除') || label.includes('Remove attachment') || label === '削除' || label === 'Remove') {
                                const btn = svg.closest('div[role="button"]') || svg.closest('button');
                                if (btn) {
                                    btn.click();
                                    return true;
                                }
                            }
                        }
                        return false;
                    }""")
                    if removed:
                        logger.info("✅ 巨大なリンクプレビュー(OGP画像)の削除に成功しました！")
                    else:
                        logger.warning("⚠️ プレビュー削除ボタンが見つかりませんでした。プレビューが残る可能性があります。")
                except Exception as e:
                    logger.warning(f"⚠️ OGPプレビュー削除処理でエラー: {e}")

        text_areas[0].focus()
        page.keyboard.insert_text(chunks[0].strip())
        time.sleep(2)
        
        # 初回のメイン投稿ボックスに画像アップロードを追加（通常投稿時のみ）
        if image_path and os.path.exists(image_path) and not quote_mode_active:
            try:
                import base64
                with open(image_path, "rb") as f:
                    img_data = base64.b64encode(f.read()).decode("utf-8")
                
                # JavaScriptを通じてClipboardEvent(paste)をシミュレートし、画像をアタッチする（UIに確実に反映させる最強の手法）
                page.evaluate("""([imgData, filename]) => {
                    const byteChars = atob(imgData);
                    const byteArr = new Uint8Array(byteChars.length);
                    for (let i = 0; i < byteChars.length; i++) byteArr[i] = byteChars.charCodeAt(i);
                    const blob = new Blob([byteArr], {type: 'image/png'});
                    const file = new File([blob], filename, {type: 'image/png'});
                    
                    const dt = new DataTransfer();
                    dt.items.add(file);
                    
                    const el = document.activeElement;
                    const pasteEvent = new ClipboardEvent('paste', {
                        bubbles: true,
                        cancelable: true,
                        clipboardData: dt
                    });
                    el.dispatchEvent(pasteEvent);
                }""", [img_data, os.path.basename(image_path)])
                logger.info(f"📸 画像をクリップボード経由でアタッチしました: {os.path.basename(image_path)}")
                time.sleep(5) # 画像のレンダリングを長めに待つ
            except Exception as e:
                logger.warning(f"⚠️ 画像の添付(Paste)に失敗しました: {e}")
                
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
            logger.info("🔸 ドライラン: 投稿ボタンは押しません。プレビュー用のスクリーンショットを保存します。")
            try:
                page.evaluate("""() => {
                    const firstTextbox = document.querySelectorAll('div[contenteditable="true"]')[0];
                    if (firstTextbox) firstTextbox.scrollIntoView({block: 'center'});
                }""")
            except:
                pass
            time.sleep(3) # レンダリング待機
            screenshot_name = f"threads_preview_{int(time.time())}.png"
            page.screenshot(path=screenshot_name, full_page=True)
            logger.info(f"✅ スクリーンショットを保存しました: {screenshot_name}")
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
        
    image_path = find_image(post['source'])
    if image_path:
        logger.info(f"📷 添付候補のサムネイル画像: {os.path.basename(image_path)}")

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

        success = post_to_threads(page, text, target_date, dry_run=args.dry_run, image_path=image_path)
        
        if success:
            logger.info("🎉 処理が正常に完了しました！")
        else:
            logger.error("❌ 処理に失敗しました。")
            
        context.close()
        
        if not success:
            sys.exit(1)

if __name__ == "__main__":
    main()
