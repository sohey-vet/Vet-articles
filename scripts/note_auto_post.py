"""
note_auto_post.py
─────────────────────────────
Note への記事自動投稿スクリプト（1 記事ずつ投稿）

テキストのみ（画像なし）。テーブルはテキスト形式で変換済み。

使い方:
  python scripts/note_auto_post.py              # 次の未投稿記事を 1 本投稿
  python scripts/note_auto_post.py --draft       # 下書き保存のみ（テスト用）
"""

import os
import re
import sys
import json
import time
import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(r"c:\Users\souhe\Desktop\論文まとめ")
TOPICS_NOTE_DIR = PROJECT_ROOT / "topics_note"
DONE_DIR = TOPICS_NOTE_DIR / "done"
POST_LOG = PROJECT_ROOT / "note_post_log.json"
CHROME_USER_DATA = PROJECT_ROOT / "playwright_chrome_profile"


def load_post_log() -> list:
    if POST_LOG.exists():
        return json.loads(POST_LOG.read_text(encoding="utf-8"))
    return []


def save_post_log(log: list):
    POST_LOG.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")


def get_pending_articles() -> list:
    all_files = sorted(TOPICS_NOTE_DIR.glob("*_formatted.txt"))
    done_files = set()
    if DONE_DIR.exists():
        done_files = {f.name for f in DONE_DIR.glob("*_formatted.txt")}
    return [f for f in all_files if f.name not in done_files]


def parse_formatted_file(file_path: Path) -> dict:
    content = file_path.read_text(encoding="utf-8")
    parts = content.split("\n\nBODY\n", 1)
    if len(parts) < 2:
        raise ValueError(f"Invalid format: {file_path.name}")

    header, body = parts
    title = ""
    tags = []
    for line in header.splitlines():
        if line in ("TITLE", "TAGS"):
            continue
        if not title:
            title = line.strip()
        elif not tags:
            tags = [t.strip() for t in line.split(",") if t.strip()]

    return {
        "title": title,
        "tags": tags,
        "body": body.strip(),
        "source_file": file_path,
    }


def type_body_text(page, text: str):
    """
    本文テキストを Note の ProseMirror エディタに入力する。
    見出し（##）はキーボード入力、それ以外はクリップボードペーストで入力。
    """
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        if not line:
            page.keyboard.press("Enter")
            time.sleep(0.03)
            i += 1
            continue

        if line.startswith("## ") or line.startswith("### "):
            # 見出し → keyboard.type（ProseMirror が ## をH2に変換）
            page.keyboard.type(line + " ", delay=2)
            time.sleep(0.05)
            page.keyboard.press("Enter")
            time.sleep(0.05)
            i += 1
            continue

        # 通常テキスト → 連続する非空・非見出し行をまとめてペースト
        block_lines = []
        while i < len(lines):
            cur = lines[i].rstrip()
            if not cur or cur.startswith("## ") or cur.startswith("### "):
                break
            block_lines.append(cur)
            i += 1

        if block_lines:
            block_text = "\n".join(block_lines)
            # クリップボードペースト
            page.evaluate("""(text) => {
                navigator.clipboard.writeText(text);
            }""", block_text)
            time.sleep(0.15)
            page.keyboard.press("Control+v")
            time.sleep(0.3)
            page.keyboard.press("Enter")
            time.sleep(0.05)

    time.sleep(0.5)


def get_scheduled_articles(start_date: datetime.date) -> list:
    content_plan = PROJECT_ROOT / "CONTENT_PLAN.md"
    if not content_plan.exists():
        return []
    content = content_plan.read_text(encoding="utf-8")
    
    try:
        table_section = content.split("## 📅 最初の30本")[1].split("### 📊")[0]
    except IndexError:
        return []
        
    schedule = []
    for line in table_section.splitlines():
        if "| **" in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 4:
                week_str = parts[1].replace("**", "").strip()
                try:
                    week = int(week_str)
                except ValueError:
                    continue
                
                mon_title = re.sub(r'^[🚨❤️🫘💊🐱🛡️🧠🔬💧🦷⚖️😴🧪🩺👁️🏥🧬🦴]+\s*', '', parts[2].replace('✅', '')).strip()
                thu_title = re.sub(r'^[🚨❤️🫘💊🐱🛡️🧠🔬💧🦷⚖️😴🧪🩺👁️🏥🧬🦴]+\s*', '', parts[3].replace('✅', '')).strip()
                
                if mon_title:
                    days_offset = (week - 1) * 7
                    post_date = start_date + datetime.timedelta(days=days_offset)
                    post_time = datetime.datetime.combine(post_date, datetime.time(12, 0))
                    schedule.append({"title_key": mon_title, "time": post_time})
                
                if thu_title:
                    days_offset = (week - 1) * 7 + 3
                    post_date = start_date + datetime.timedelta(days=days_offset)
                    post_time = datetime.datetime.combine(post_date, datetime.time(12, 0))
                    schedule.append({"title_key": thu_title, "time": post_time})
                    
    return schedule[:10]

def post_to_note(page, article: dict, draft_only: bool = False, schedule_time: datetime.datetime = None, test_schedule: bool = False) -> bool:
    title = article["title"]
    tags = article["tags"]
    body = article["body"]

    print(f"  📝 タイトル: {title}")
    print(f"  🏷️  タグ: {', '.join(tags)}")
    print(f"  📄 本文: {len(body)} 文字")

    # ── Note にアクセス ──
    print("  ➡️  Note にアクセス中...")
    page.goto("https://note.com/", wait_until="networkidle", timeout=30000)
    time.sleep(3)

    if "login" in page.url:
        print("  ⚠️  ログイン必要。ブラウザでログインしてください...")
        for attempt in range(60):
            time.sleep(5)
            if "login" not in page.url:
                break
        else:
            return False

    print("  ➡️  エディタへ移動中...")
    page.goto("https://editor.note.com/new", wait_until="networkidle", timeout=30000)
    time.sleep(3)

    if "editor" not in page.url:
        print(f"  ❌ エディタに到達できません")
        return False

    # ── タイトル入力 ──
    print("  ✏️  タイトル入力中...")
    title_el = page.locator("textarea").first
    title_el.click()
    title_el.fill(title)
    time.sleep(0.5)

    # ── 本文入力 ──
    print("  ✏️  本文入力中...")
    editor = page.locator('div[role="textbox"]').first
    editor.click()
    time.sleep(0.5)

    type_body_text(page, body)

    # 入力されたテキストの確認
    char_count = page.evaluate("""() => {
        const ed = document.querySelector('div[role="textbox"]');
        return ed ? ed.innerText.length : 0;
    }""")
    print(f"  📊 入力文字数: {char_count} 文字")

    time.sleep(2)

    if draft_only:
        print("  💾 下書き保存中...")
        draft_btn = page.locator('button').filter(has_text="下書き保存")
        if draft_btn.count() > 0:
            draft_btn.first.click()
            time.sleep(3)
            print("  ✅ 下書き保存完了！")
            return True
        return False

    # ── 即時公開 / 予約投稿 ──
    print("  📤 公開設定へ...")
    publish_btn = page.locator('button').filter(has_text="公開に進む")
    if publish_btn.count() > 0:
        publish_btn.first.click()
        time.sleep(3)

        if tags:
            tag_input = page.locator('input[placeholder*="ハッシュタグ"]').or_(
                page.locator('input[placeholder*="タグ"]')
            )
            if tag_input.count() > 0:
                for tag in tags[:5]:
                    tag_input.first.fill(tag)
                    time.sleep(0.5)
                    page.keyboard.press("Enter")
                    time.sleep(0.5)
                    
        # 予約設定のアテンプト
        if schedule_time:
            print(f"  ⏰ 予約設定: {schedule_time.strftime('%Y/%m/%d %H:%M')}")
            schedule_label = page.locator('label').filter(has_text=re.compile(r"日時指定|日時を設定|予約"))
            if schedule_label.count() > 0:
                schedule_label.first.click()
                time.sleep(1)
                
                try:
                    # Input the date by name targeting
                    page.locator('input[name="year"]').fill(str(schedule_time.year))
                    page.locator('input[name="month"]').fill(str(schedule_time.month))
                    page.locator('input[name="day"]').fill(str(schedule_time.day))
                    page.locator('input[name="hour"]').fill(str(schedule_time.hour))
                    page.locator('input[name="minute"]').fill(str(schedule_time.minute))
                    time.sleep(1)
                except Exception as e:
                    print(f"  ⚠️ 日時指定UIへの入力に失敗しました。下書きとして保存します: {e}")
                    page.locator('button').filter(has_text="下書き保存").first.click()
                    return True

        final_publish = page.locator('button').filter(has_text=re.compile(r"投稿|予約")).last
        if final_publish.count() > 0:
            if test_schedule:
                print("  🧪 テストモードのため、最終投稿ボタンは押さずに下書きとして保存します。")
                page.locator('button').filter(has_text="下書き保存").first.click()
                return True
            final_publish.click()
            time.sleep(5)
            print("  ✅ 投稿・予約完了！")
            return True

    return False


def main():
    draft_only = "--draft" in sys.argv
    schedule_mode = "--schedule" in sys.argv
    test_schedule = "--test-schedule" in sys.argv

    if schedule_mode:
        today = datetime.date.today()
        # 次の月曜を計算
        days_ahead = 0 - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        next_monday = today + datetime.timedelta(days=days_ahead)
        
        schedule_plan = get_scheduled_articles(next_monday)
        if not schedule_plan:
            print("スケジュールの取得に失敗しました。")
            return
            
        all_files = sorted(TOPICS_NOTE_DIR.glob("*_formatted.txt"))
        
        to_post = []
        for s in schedule_plan:
            key = s["title_key"]
            core_key = key.split('─')[0].split('—')[0].strip()
            clean_key = re.sub(r'[\sのとい・]', '', core_key)
            
            matched_file = None
            for f in all_files:
                f_name = f.stem.replace('_formatted', '')
                core_f = f_name.split('_')[0].strip()
                clean_f = re.sub(r'[\sのとい・]', '', core_f)
                if clean_key in clean_f or clean_f in clean_key:
                    matched_file = f
                    break
                    
            if matched_file:
                to_post.append({"file": matched_file, "time": s["time"]})
            else:
                print(f"⚠️ スケジュール上の記事 {key} に対応するファイルが見つかりません。")
                
        if not to_post:
            print("📭 予約投稿する記事ファイルが見つかりません。")
            return
    else:
        pending = get_pending_articles()
        if not pending:
            print("📭 投稿する記事がありません。")
            return
        to_post = [{"file": pending[0], "time": None}]

    print(f"{'='*60}")
    print(f"  Note 自動投稿: {len(to_post)} 記事")
    if schedule_mode:
        print("  🗓️  スケジュール予約モード（10記事まとめ投稿）")
    if draft_only:
        print("  ⚠️  テストモード（下書き保存のみ）")
    print(f"{'='*60}")

    with sync_playwright() as p:
        print("  🌐 ブラウザ起動中...")
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(CHROME_USER_DATA),
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        browser.grant_permissions(["clipboard-read", "clipboard-write"])

        log = load_post_log()
        success_count = 0

        for item in to_post:
            file_path = item["file"]
            schedule_time = item["time"]
            article_name = file_path.stem.replace("_formatted", "")
            print(f"\n{'─'*50}")
            print(f"  📄 {article_name}")
            print(f"{'─'*50}")

            try:
                article = parse_formatted_file(file_path)
                success = post_to_note(page, article, draft_only=draft_only, schedule_time=schedule_time, test_schedule=test_schedule)

                if success:
                    log.append({
                        "title": article["title"],
                        "file": article_name,
                        "posted_at": datetime.datetime.now().isoformat(),
                        "scheduled_for": schedule_time.isoformat() if schedule_time else None,
                        "status": "draft" if draft_only else ("scheduled" if schedule_time else "published"),
                    })
                    save_post_log(log)
                    os.makedirs(DONE_DIR, exist_ok=True)
                    # For scheduled posts, immediately move to done to prevent duplicate processing
                    file_path.rename(DONE_DIR / file_path.name)
                    success_count += 1
            except Exception as e:
                print(f"  ❌ エラー: {e}")
                import traceback
                traceback.print_exc()

            time.sleep(3)

        browser.close()

    print(f"\n{'='*60}")
    print(f"  完了: {success_count}/{len(to_post)} 記事")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
