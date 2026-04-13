import os
import sys
import time
import logging
from playwright.sync_api import sync_playwright

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_DIR = os.path.join(SCRIPT_DIR, ".x_session")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def main():
    logger.info("==================================================")
    logger.info("🗑️ VetEvidence X 予約投稿全自動削除スクリプト (Select All版)")
    logger.info("==================================================")

    if not os.path.exists(SESSION_DIR):
        logger.error("❌ セッションが見つかりません。")
        sys.exit(1)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=SESSION_DIR,
            headless=False,
            channel="msedge",
            locale="ja-JP",
            viewport={"width": 1280, "height": 900},
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = context.pages[0] if context.pages else context.new_page()

        logger.info("🌐 予約設定画面にアクセスしています...")
        page.goto("https://x.com/compose/post/unsent/scheduled", wait_until="domcontentloaded", timeout=20000)
        time.sleep(5)

        # 「編集」ボタンを探してクリック
        edit_btn = page.locator('button, [role="button"]').filter(has_text="編集").first
        if not edit_btn.is_visible(timeout=5000):
            logger.info("✅ 画面内に「編集」ボタンが見つかりません。予約投稿は空になったか、すべて削除されました！")
            context.close()
            return
            
        logger.info("🔍 「編集」ボタンをクリックします...")
        edit_btn.click()
        time.sleep(2)

        # 「すべて選択」ボタン
        select_all = page.locator('button, [role="button"], span').filter(has_text="すべて選択").first
        if select_all.is_visible():
            logger.info("✅ 「すべて選択」をクリックします...")
            select_all.click()
            time.sleep(1)
        else:
            logger.info("⚠️ 「すべて選択」が見つかりませんでした。手動での確認が必要です。")
            
        # 削除ボタン
        delete_btn = page.locator('button, [role="button"]').filter(has_text="削除").last
        if delete_btn.is_visible():
            logger.info(f"🗑️ 「削除」ボタンをクリックします...")
            delete_btn.click()
            time.sleep(1)
            
            # 確認ダイアログの削除
            confirm_btn = page.locator('[data-testid="confirmationSheetConfirm"]').first
            if confirm_btn.is_visible():
                confirm_btn.click()
            else:
                fallback_btn = page.locator('button, [role="button"]').filter(has_text="削除").last
                if fallback_btn.is_visible():
                    fallback_btn.click()
            
            logger.info(f"✅ 全ての削除が完了しました！")
        else:
            logger.info("⚠️ 削除ボタンが見つかりませんでした。")
            
        time.sleep(3)
        context.close()

if __name__ == "__main__":
    main()
