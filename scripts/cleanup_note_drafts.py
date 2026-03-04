"""
cleanup_note_drafts.py
─────────────────────────────
Note に溜まった過去のテスト用下書きを一括削除するスクリプト。
最新の CPR 記事（1件）だけを残して他をすべて削除します。
"""

import os
import sys
import time
from playwright.sync_api import sync_playwright

CHROME_USER_DATA = r"C:\Users\souhe\AppData\Local\Google\Chrome\User Data"

def cleanup_drafts():
    print("🚀 Note 下書き一括削除ツール起動...")
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=CHROME_USER_DATA,
                headless=False,
                channel="chrome",
                args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
            )
            page = browser.new_page()

            print("➡️  Note にアクセス中...")
            page.goto("https://note.com/notes/drafts", wait_until="domcontentloaded")
            time.sleep(3)
            
            # 手動ログインが必要か確認
            if "login" in page.url or page.locator('a[href*="/login"]').is_visible():
                print("⚠️  ログインが必要です。ブラウザでログインを完了してください。")
                print("    ※ ログイン完了後、自動的に再開します。そのままお待ちください...")
                page.wait_for_url("https://note.com/notes/drafts", timeout=300000)
                time.sleep(3)

            print("\n🧹 削除処理を開始します...")

            while True:
                # 記事リストの親要素を取得
                articles = page.locator("div.mu-articleListItem")
                count = articles.count()
                
                if count <= 1:
                    print(f"✅ 残り {count} 件です。削除を終了します。")
                    break

                # 2記事目以降を順次削除 (1記事目は保持する想定)
                # NoteのDOM構造的にインデックスアクセスより、最後の要素から消していくのが安全
                target = articles.nth(count - 1)
                
                try:
                    title = target.locator("h3").inner_text(timeout=2000)
                    print(f"  🗑️  削除中: {title}")
                except:
                    print(f"  🗑️  削除中: (タイトル取得不可)")

                # 「･･･」メニューボタンをクリック
                menu_btn = target.locator('button[aria-label="記事メニューを開く"], button.fn-menu-button')
                if not menu_btn.is_visible():
                    print("  ⚠️ メニューボタンが見つかりません。")
                    break
                    
                menu_btn.first.click()
                time.sleep(1)

                # 「削除」をクリック
                delete_btn = page.locator('button:has-text("削除")')
                if not delete_btn.is_visible():
                    print("  ⚠️ 削除ボタンが見つかりません。")
                    break
                
                delete_btn.first.click()
                time.sleep(1)

                # モーダルの「削除する」をクリック
                confirm_btn = page.locator('button.o-modalButtons__button.-danger')
                if not confirm_btn.is_visible():
                    confirm_btn = page.locator('button:has-text("削除する")')
                
                if confirm_btn.is_visible():
                    confirm_btn.first.click()
                    time.sleep(2)  # 削除完了を待つ
                else:
                    print("  ⚠️ 確認ボタンが見つかりません。")
                    break
                    
                # 画面更新を確実にするため少し待つ
                time.sleep(1)

            print("\n🎉 クリーンアップ完了！")
            time.sleep(2)
            
        except Exception as e:
            print(f"\n❌ エラー発生: {e}")
        finally:
            if 'browser' in locals():
                browser.close()

if __name__ == "__main__":
    cleanup_drafts()
