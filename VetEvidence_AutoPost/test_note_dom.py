from playwright.sync_api import sync_playwright
import time
import sys

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=".note_session",
            channel="msedge",
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        page = browser.pages[0]
        
        # Grant clipboard-read and clipboard-write permissions
        browser.grant_permissions(["clipboard-read", "clipboard-write"])
        
        print("▶️ Note エディタを開きます...")
        page.goto("https://note.com/notes/new", wait_until="networkidle")
        time.sleep(3)
        
        print("▶️ テストテキストを入力します...")
        try:
            page.locator('textarea[placeholder*="タイトル"], textarea').first.click(timeout=3000)
            page.keyboard.insert_text("テストタイトル")
            time.sleep(1)
            page.locator('[contenteditable="true"]').last.click(timeout=3000)
            page.keyboard.insert_text("テスト本文")
            time.sleep(2)
        except Exception as e:
            print("テキスト入力エラー:", e)
            
        # DOMとスクリーンショットを保存 (クリック前に保存)
        with open("note_before_pub.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        page.screenshot(path="note_publish.png")
        print("✅ DOMとスクリーンショットを保存しました。")
        
        print("▶️ 公開設定ボタンをクリックします...")
        try:
            # 汎用的なセレクタで公開設定ボタンを探す
            page.click("button:has-text('公開に進む')", timeout=5000)
            time.sleep(3)
            page.click("text='詳細設定'", timeout=5000)
            time.sleep(1)
            
            page.click("text='日時の設定'", timeout=5000)
            time.sleep(2)
            page.screenshot(path="note_publish_date.png")
            print("✅ 日時設定のスクリーンショットを保存しました！")
            
            html = page.inner_html("body")
            with open("note_dom.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("✅ DOMを note_dom.html に保存しました！")
            
            # Save Screenshot
            page.screenshot(path="note_publish.png")
            print("✅ スクリーンショットを保存しました！")
        except Exception as e:
            print("❌ 公開設定ボタンが見つかりませんでした")
            
        browser.close()

if __name__ == "__main__":
    main()
