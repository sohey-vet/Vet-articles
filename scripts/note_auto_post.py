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


def post_to_note(page, article: dict, draft_only: bool = False) -> bool:
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

    # ── 即時公開 ──
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

        final_publish = page.locator('button').filter(has_text="投稿").last
        if final_publish.count() > 0:
            final_publish.click()
            time.sleep(5)
            print("  ✅ 公開完了！")
            return True

    return False


def main():
    draft_only = "--draft" in sys.argv

    pending = get_pending_articles()
    if not pending:
        print("📭 投稿する記事がありません。")
        return

    to_post = pending[:1]

    print(f"{'='*60}")
    print(f"  Note 自動投稿: {len(to_post)} 記事")
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

        for file_path in to_post:
            article_name = file_path.stem.replace("_formatted", "")
            print(f"\n{'─'*50}")
            print(f"  📄 {article_name}")
            print(f"{'─'*50}")

            try:
                article = parse_formatted_file(file_path)
                success = post_to_note(page, article, draft_only=draft_only)

                if success:
                    log.append({
                        "title": article["title"],
                        "file": article_name,
                        "posted_at": datetime.datetime.now().isoformat(),
                        "status": "draft" if draft_only else "published",
                    })
                    save_post_log(log)
                    os.makedirs(DONE_DIR, exist_ok=True)
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
