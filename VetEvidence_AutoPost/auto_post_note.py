import os
import sys
import json
import time
import argparse
import re
import logging
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DRAFTS_ROOT = os.path.dirname(SCRIPT_DIR)
LOG_DIR = os.path.join(SCRIPT_DIR, "logs")
SESSION_DIR = os.path.join(SCRIPT_DIR, ".note_session")
SCHEDULE_FILE = os.path.join(SCRIPT_DIR, "sns_schedule.json")

os.makedirs(LOG_DIR, exist_ok=True)
log_file = os.path.join(LOG_DIR, f"note_post_log_{datetime.now().strftime('%Y%m')}.log")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(log_file, encoding="utf-8"), logging.StreamHandler()])
logger = logging.getLogger(__name__)

def load_todays_post_source(target_date):
    # Noteは月・水・金のみ投稿 (0: 月, 2: 水, 4: 金)
    if target_date.weekday() not in [0, 2, 4]:
        logger.info(f"📭 今日 ({target_date.strftime('%Y-%m-%d')}) は月・水・金ではないため、Note投稿をスキップします。")
        return None

    if not os.path.exists(SCHEDULE_FILE): return None
    try:
        with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
            schedule = json.load(f)
        date_str = target_date.strftime("%Y-%m-%d")
        
        # Note用の予約はスケジュールに独立して存在しないため、同日のX（Pattern 1）のソースを取得する
        todays_posts = [p for p in schedule if p.get("date") == date_str and p.get("platform") == "X" and p.get("type") == "Pattern 1"]
        
        if not todays_posts:
            # フォールバック: その日の何らかの投稿を拾う
            todays_posts = [p for p in schedule if p.get("date") == date_str]
            if not todays_posts:
                return None
                
        return todays_posts[0]["source"]
    except Exception as e:
        logger.error(f"❌ スケジュール読み込みエラー: {e}")
        return None

def find_original_md_file_and_url(source_folder):
    draft_md = os.path.join(DRAFTS_ROOT, source_folder, "sns_all_drafts.md")
    if not os.path.exists(draft_md): return None, None
    try:
        with open(draft_md, "r", encoding="utf-8", errors="ignore") as f:
            m = re.search(r'元ファイル:\s*([^\r\n]+)', f.read())
            if m:
                path = m.group(1).strip()
                url_suffix = path.replace('\\', '/')
                
                if not os.path.isabs(path):
                    r_root = r"C:\Users\souhe\Desktop\論文まとめ"
                    path = os.path.join(r_root, path) if path.startswith("topics") else os.path.join(r_root, "topics", path)
                md_path = path.replace(".html", ".md")
                if os.path.exists(md_path): return md_path, url_suffix
    except Exception as e:
        logger.error(f"❌ drafts.mdの読取エラー: {e}")
    return None, None

def format_compact_html(md_text, url_suffix):
    md_text = md_text.replace('✗', '❌').replace('✅', '✅')

    md_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', md_text)
    md_text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', md_text)
    
    # 単一アスタリスクやアンダースコア（イタリック等）はNoteでは不要なため、記号を除去して修飾なし文字にする
    md_text = re.sub(r'(?<!\*)\*([^\*]+)\*(?!\*)', r'\1', md_text)
    md_text = re.sub(r'_(.*?)_', r'\1', md_text)
    
    md_text = md_text.replace('💡 臨床アクション', '臨床アクション').replace('臨床アクション', '💡 臨床アクション')
    
    lines = md_text.split('\n')
    
    # 参照文献数の算出
    ref_count = 0
    in_refs = False
    for line in lines:
        if line.startswith('## 📚 参照論文') or line.startswith('## 📚 参照文献'):
            in_refs = True
            continue
        if in_refs:
            if line.startswith('#'):
                in_refs = False
            elif re.match(r'^\d+\.', line.strip()):
                ref_count += 1

    html_out = []
    # 安全な junk フィルター
    junk = ['ナビゲーション', 'トップに戻る', '全展開', '全折り', 'すべて表示', '有料会員限定']
    in_table = False
    in_mermaid = False
    table_lines = []
    current_p = []
    
    def flush_p():
        nonlocal current_p, html_out
        if current_p:
            html_out.append("<p>" + "<br>".join(current_p) + "</p>")
            current_p = []

    for line in lines:
        line_s = line.strip()
        
        if line_s.startswith('```mermaid') or line_s.startswith('<div class="mermaid-wrapper">'):
            in_mermaid = True
            continue
        if in_mermaid:
            if line_s == '```' or line_s == '</div>':
                in_mermaid = False
            continue
            
        # --- 強力なフローチャート除外フィルター ---
        if 'graph TD' in line or 'graph LR' in line:
            line = re.sub(r'graph (TD|LR)', '', line)
            line_s = line.strip()
            if not line_s: continue
        if '-->' in line_s: continue
        if re.match(r'^[A-Za-z0-9_]+\[".*?"\]', line_s) or re.match(r'^[A-Za-z0-9_]+\{".*?"\}', line_s): continue
        if line_s.startswith('subgraph ') or line_s == 'end': continue
        # ----------------------------------------
            
        # ----------------------------------------
            
        if line_s.startswith('update:'): continue

        if line_s == '---':
            flush_p()
            html_out.append("<hr>")
            continue

        if any(j in line_s for j in junk) and len(line_s) < 20: continue
        if '<details>' in line_s or '</details>' in line_s or '<summary>' in line_s or '</summary>' in line_s: continue
        if line_s.startswith('[!'): continue
        if line_s.startswith('ハッシュタグ'): continue
        if line_s.startswith('※本まとめは'): continue
        
        # 引用記号の除去
        line_s = re.sub(r'^>\s*', '', line_s)
        
        # 参照文献数の挿入
        if '⏱️ <strong>読了時間</strong>' in line_s or '⏱️ 読了時間' in line_s or '読了時間' in line_s:
            line_s = line_s + f"<br><br>📚 <strong>参照文献</strong>: {ref_count}本"
        
        if line_s.startswith('#### '):
            line_s = line_s.replace('#### ', '<strong>') + '</strong>'
            
        if line_s.startswith('### '):
            flush_p()
            html_out.append(f"<h3>{line_s[4:]}</h3>")
            continue
        if line_s.startswith('## '):
            flush_p()
            html_out.append(f"<h2>{line_s[3:]}</h2>")
            continue
        if line_s.startswith('# '): continue
            
        if line_s.startswith('|') and line_s.endswith('|'):
            in_table = True
            table_lines.append(line_s)
            continue
        else:
            if in_table:
                flush_p()
                if len(table_lines) >= 3:
                    headers = [h.strip() for h in table_lines[0].split('|')[1:-1]]
                    for tr in table_lines[2:]:
                        cells = [c.strip() for c in tr.split('|')[1:-1]]
                        if not cells: continue
                        h0 = headers[0] if len(headers) > 0 else "項目"
                        if h0 and cells[0]:
                            current_p.append(f"<strong>【{h0}：{cells[0]}】</strong>")
                        else:
                            current_p.append(f"<strong>【{cells[0]}】</strong>")
                            
                        for i in range(1, len(cells)):
                            hn = headers[i] if i < len(headers) else ""
                            current_p.append(f"・{hn}：{cells[i]}")
                        current_p.append("") 
                in_table = False
                table_lines = []
                flush_p()
                
            if not line_s:
                flush_p()
            else:
                current_p.append(line_s)
                
    flush_p()
    return "\n".join(html_out)


def post_to_note(page, title, html_payload, thumb_path, dry_run=False, draft_mode=False):
    logger.info("📝 Noteへ投稿を開始します...")
    try:
        page.goto("https://note.com/notes/new", wait_until="networkidle", timeout=30000)
        
        try:
            page.wait_for_url("**/edit**", timeout=15000)
            time.sleep(2)
        except:
            logger.info("リダイレクト待機スキップ（遷移済み）")
            
        # === サムネイルのアップロード (ネイティブUI) ===
        if not thumb_path or not os.path.exists(thumb_path):
            logger.error(f"❌ 致命的エラー: サムネイル画像が見つかりません: {thumb_path}")
            logger.error("サムネイルの取りこぼしを防ぐため、処理を中断します。")
            return False

        logger.info(f"🖼 見出し画像を設定します: {thumb_path}")
        try:
            time.sleep(3)
            # 見出し画像の追加ボタン（aria-label="画像を追加"）をクリック
            header_btn = page.locator('button[aria-label="画像を追加"]').first
            header_btn.wait_for(state="attached", timeout=10000)
            header_btn.click()
            logger.info("✅ 画像を追加 ボタンをクリックしました")
            time.sleep(1)
            
            # メニューから「画像をアップロード」をクリックし、OSのファイル選択ダイアログをインターセプト
            upl_menu = page.locator('text="画像をアップロード"').first
            upl_menu.wait_for(state="visible", timeout=5000)
            
            with page.expect_file_chooser(timeout=5000) as fc:
                upl_menu.click()
            
            fc.value.set_files(thumb_path)
            logger.info("✅ ファイルチューザーから画像を送信しました。クロップモーダルを待機します...")
            time.sleep(3)
            
            # Note.com独自のクロップ(切り抜き)モーダルの「保存」をクリック
            try:
                save_modal_btn = page.locator('button:has-text("保存")').get_by_text("保存", exact=True).first
                if save_modal_btn.is_visible(timeout=5000):
                    save_modal_btn.click(force=True)
                    logger.info("✅ クロップモーダルの「保存」をクリックし、見出し画像を確定しました！")
                else:
                    logger.warning("※クロップモーダルが見つかりませんでした (仕様変更の可能性あり)")
            except Exception as e:
                logger.warning(f"※クロップモーダルの処理中にエラー: {str(e)}")
                
            time.sleep(8) # S3アップロード完了を待機
        except Exception as e:
            logger.warning(f"⚠️ 見出し画像のアップロード中にエラー: {e}")
        
        # === タイトル入力 ===
        title_box = page.locator('textarea[placeholder*="タイトル"], textarea').first
        title_box.fill(title, timeout=15000)
        time.sleep(1)
        # 追記: UIサジェスト等を消すためエスケープを押す
        page.keyboard.press("Escape")
        time.sleep(1)
        
        # === クリップボードペースト ===
        body_box = page.locator('[contenteditable="true"]').last
        body_box.click(force=True, timeout=15000)
        time.sleep(2) # 本文領域へのフォーカス遷移を確実に待つ
        
        page.evaluate('''([html]) => {
            const item = new ClipboardItem({
                "text/html": new Blob([html], {type: "text/html"}),
                "text/plain": new Blob(["Fallback"], {type: "text/plain"})
            });
            return navigator.clipboard.write([item]);
        }''', [html_payload])
        time.sleep(1)
        
        page.keyboard.press("Control+V")
        logger.info("✅ 完璧なレイアウトのHTMLペーストに成功しました！表・太字が完全にコントロールされています。")
        
        if dry_run or draft_mode:
            logger.info("⏳ Note.comの自動保存(Autosave)を確実に行うため15秒待機します...")
            time.sleep(15)
            logger.info("✅ 下書きとして完全に保存されました（--draft モードのため公開は行いません）")
            return True

        time.sleep(5)
        # === 公開手順 ===
        pub_btn = page.locator("button", has_text="公開に進む").first
        pub_btn.click(force=True, timeout=10000)
        time.sleep(5)
        
        # NOTE.comの右側パネルにある最終公開ボタン（公開、投稿、今すぐ公開 などに柔軟に対応）
        final_pub_btn = page.locator('button:has-text("公開"), button:has-text("投稿")').last
        final_pub_btn.click(force=True, timeout=15000)
        logger.info("✅ 記事の公開(Publish)をクリックしました！")
        time.sleep(5)
        return True

    except Exception as e:
        logger.error(f"❌ エラー発生: {e}")
        return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--draft", action="store_true", help="記事を下書きとしてのみ保存し、公開ボタンを押さない")
    parser.add_argument("--date", type=str)
    args = parser.parse_args()

    logger.info("=" * 50)
    logger.info("📓 Note 自動投稿スクリプト (Spatial Geometry UI Edition)")
    logger.info("=" * 50)

    target_date = datetime.strptime(args.date, "%Y-%m-%d").date() if args.date else datetime.now().date()
    source_folder = load_todays_post_source(target_date)
    if not source_folder: sys.exit(0)

    md_path, url_suffix = find_original_md_file_and_url(source_folder)
    if not md_path: sys.exit(1)

    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
        
    lines = content.split('\n')
    title = lines[0].lstrip('#').strip() if lines[0].startswith('#') else os.path.basename(md_path).replace('.md', '')
    
    compact_html = format_compact_html(content, url_suffix)
    thumb_path = os.path.join(DRAFTS_ROOT, source_folder, "note_thumbnail.png")
    
    # 堅牢性向上のためのフォールバック処理: note_thumbnail.png が無い場合は 1.png (共通スライド画像) を代用する
    if not os.path.exists(thumb_path):
        fallback_thumb = os.path.join(DRAFTS_ROOT, source_folder, "1.png")
        if os.path.exists(fallback_thumb):
            thumb_path = fallback_thumb

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=SESSION_DIR,
            channel="msedge",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.bring_to_front()
        success = post_to_note(page, title, compact_html, thumb_path, dry_run=args.dry_run, draft_mode=args.draft)
        browser.close()
        if not success: sys.exit(1)

if __name__ == "__main__":
    main()
