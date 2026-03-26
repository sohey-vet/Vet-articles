import os
import sys
import json
import time
import argparse
import re
import logging
from datetime import datetime
from playwright.sync_api import sync_playwright

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DRAFTS_ROOT = os.path.dirname(SCRIPT_DIR)
LOG_DIR = os.path.join(SCRIPT_DIR, "logs")
SESSION_DIR = os.path.join(SCRIPT_DIR, ".note_session")
SCHEDULE_FILE = os.path.join(SCRIPT_DIR, "sns_schedule.json")

os.makedirs(LOG_DIR, exist_ok=True)
log_file = os.path.join(LOG_DIR, f"note_drafts_publish_log_{datetime.now().strftime('%Y%m')}.log")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(log_file, encoding="utf-8"), logging.StreamHandler()])
logger = logging.getLogger(__name__)

def load_todays_post_source(target_date):
    if not os.path.exists(SCHEDULE_FILE): return None
    try:
        with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
            schedule = json.load(f)
        date_str = target_date.strftime("%Y-%m-%d")
        todays_posts = [p for p in schedule if p["date"] == date_str]
        if not todays_posts: return None
        return todays_posts[0]["source"]
    except Exception as e:
        logger.error(f"❌ スケジュール読み込みエラー: {e}")
        return None

def find_original_md_file(source_folder):
    draft_md = os.path.join(DRAFTS_ROOT, source_folder, "sns_all_drafts.md")
    if not os.path.exists(draft_md): return None
    try:
        with open(draft_md, "r", encoding="utf-8", errors="ignore") as f:
            m = re.search(r'元ファイル:\s*([^\r\n]+)', f.read())
            if m:
                path = m.group(1).strip()
                if not os.path.isabs(path):
                    r_root = r"C:\Users\souhe\Desktop\論文まとめ"
                    path = os.path.join(r_root, path) if path.startswith("topics") else os.path.join(r_root, "topics", path)
                md_path = path.replace(".html", ".md")
                if os.path.exists(md_path): return md_path
    except Exception as e:
        logger.error(f"❌ drafts.mdの読取エラー: {e}")
    return None

def get_title_from_md(md_path):
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith('# '):
                return line.lstrip('#').strip()
    return os.path.basename(md_path).replace('.md', '')

def publish_existing_draft(page, search_title, dry_run=False):
    logger.info(f"🔍 記事一覧(下書き)から対象を探します: {search_title}")
    try:
        page.goto("https://note.com/notes", wait_until="networkidle", timeout=30000)
        time.sleep(3)
        
        # ユーザーが編集してタイトルが多少変わっている可能性を考慮し、前半の文字を抽出（最大15文字）
        # ただし、絵文字（先頭の1文字目）などのみだと重複するため、英数字や日本語部分を長めに取る
        short_title = search_title[:15].strip()
        logger.info(f"👉 検索キーワード: {short_title}")
        # Note.comはカード全体を覆う編集ボタン(aria-label="〇〇を編集")を持っています
        draft_link = page.locator(f'button[aria-label*="{short_title}"]').first
        
        try:
            draft_link.wait_for(state="visible", timeout=10000)
        except:
            logger.error(f"❌ 記事一覧に「{short_title}」に一致する下書きが見つかりませんでした。")
            return False
            
        logger.info("✅ 対象の下書きを発見しました。エディタを開きます...")
        draft_link.click()
        
        try:
            page.wait_for_url("**/edit**", timeout=15000)
            time.sleep(3)
        except:
            logger.warning("※URL遷移の待機をスキップしました")
            
        # === 公開手順 ===
        pub_btn = page.locator("button", has_text="公開に進む").first
        if not pub_btn.is_visible(timeout=5000):
            logger.error("❌ 「公開に進む」ボタンが見つかりません。エディタが正しく読み込まれていないか、仕様変更の可能性があります。")
            return False
            
        if dry_run:
            logger.info("✅ 【Dry-Run】下書きを正常に開くことに成功しました。テスト完了のため公開は行いません。")
            return True
            
        pub_btn.click(force=True, timeout=10000)
        time.sleep(5)
        
        # NOTE.comの最終公開ボタン
        final_pub_btn = page.locator('button:has-text("公開"), button:has-text("投稿")').last
        if not final_pub_btn.is_visible(timeout=5000):
            logger.error("❌ 「公開(投稿)」ボタンが見つかりません。")
            return False
            
        final_pub_btn.click(force=True, timeout=15000)
        logger.info("🎉 既存の下書きの定刻公開(Publish)に成功しました！")
        time.sleep(5)
        return True

    except Exception as e:
        logger.error(f"❌ 投稿処理中にエラー発生: {e}")
        return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str, help="対象日付 (YYYY-MM-DD)。省略時は実行日の日付となる。")
    parser.add_argument("--dry-run", action="store_true", help="公開ボタンを押さずに終了する")
    args = parser.parse_args()

    logger.info("=" * 50)
    logger.info("📓 Note 定刻・下書き公開スクリプト")
    logger.info("=" * 50)

    target_date = datetime.strptime(args.date, "%Y-%m-%d").date() if args.date else datetime.now().date()
    source_folder = load_todays_post_source(target_date)
    
    if not source_folder:
        logger.info(f"📅 {target_date} に予定されているNoteの投稿はありません。")
        sys.exit(0)

    md_path = find_original_md_file(source_folder)
    if not md_path:
        logger.error(f"❌ 元のMarkdownファイルが見つかりません: {source_folder}")
        sys.exit(1)

    title = get_title_from_md(md_path)
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=SESSION_DIR,
            channel="msedge",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.bring_to_front()
        success = publish_existing_draft(page, title, dry_run=args.dry_run)
        browser.close()
        
        if not success:
            sys.exit(1)

if __name__ == "__main__":
    main()
