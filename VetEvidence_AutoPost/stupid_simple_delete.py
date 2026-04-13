import os
import sys
import time
from playwright.sync_api import sync_playwright

SESSION_DIR = r"C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts\VetEvidence_AutoPost\.x_session"

def main():
    print("STARTING")
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=SESSION_DIR,
            headless=False,
            channel="msedge",
            viewport={"width": 1280, "height": 900}
        )
        page = context.pages[0] if context.pages else context.new_page()
        
        page.goto("https://x.com/compose/post/unsent/scheduled", wait_until="networkidle", timeout=30000)
        time.sleep(5)
        
        print("Clicking Edit...")
        edit_btn = page.locator('button, [role="button"]').filter(has_text="編集").first
        if edit_btn.is_visible():
            edit_btn.click()
            time.sleep(2)
            
            rows = page.locator('[data-testid="cellInnerDiv"]').all()
            print(f"Found {len(rows)} rows to click.")
            
            for row in rows:
                try:
                    row.click()
                    time.sleep(0.2)
                except Exception as e:
                    print("Error clicking row:", e)
                    
            time.sleep(1)
            
            delete_btn = page.locator('button, [role="button"]').filter(has_text="削除").last
            print("Clicking Delete...")
            delete_btn.click()
            time.sleep(2)
            
            dialog = page.locator('[role="dialog"]').last
            print("Dialog text:", dialog.inner_text().replace('\n', ' '))
            
            confirm = page.locator('[data-testid="confirmationSheetConfirm"]').first
            if confirm.is_visible():
                confirm.click()
                print("Clicked confirm sheet!")
            else:
                fallback = dialog.locator('button, [role="button"]').filter(has_text="削除").last
                fallback.click()
                print("Clicked dialog fallback!")
                
            time.sleep(5)
        else:
            print("Edit button not visible!")
            
        context.close()
        print("DONE")

if __name__ == "__main__":
    main()
