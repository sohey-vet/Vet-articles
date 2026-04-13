import os
import sys
import time
from playwright.sync_api import sync_playwright

SESSION_DIR = r"C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts\VetEvidence_AutoPost\.x_session"

def log(m):
    with open("stupid.log", "a", encoding="utf-8") as f:
        f.write(m + "\n")

def main():
    if os.path.exists("stupid.log"): os.remove("stupid.log")
    log("STARTING 2")
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=SESSION_DIR,
            headless=False,
            channel="msedge",
            viewport={"width": 1280, "height": 900}
        )
        page = context.pages[0] if context.pages else context.new_page()
        
        try:
            page.goto("https://x.com/compose/post/unsent/scheduled", wait_until="domcontentloaded", timeout=20000)
        except Exception as e:
            log(f"Goto err: {e}")
            
        time.sleep(5)
        
        # Loop for batches
        for bidx in range(10):
            log(f"--- BATCH {bidx} ---")
            log("Clicking Edit...")
            edit_btn = page.locator('button, [role="button"]').filter(has_text="編集").first
            if edit_btn.is_visible():
                edit_btn.click()
                time.sleep(2)
                
                rows = page.locator('[data-testid="cellInnerDiv"]').all()
                log(f"Found {len(rows)} rows to click.")
                
                if len(rows) == 0:
                    log("Rows 0, breaking.")
                    break
                
                for row in rows:
                    try:
                        # Click slightly inside the row
                        row.click(position={"x": 50, "y": 20})
                        time.sleep(0.5)
                    except Exception as e:
                        log(f"Error clicking row: {e}")
                        
                time.sleep(1)
                
                delete_btn = page.locator('button, [role="button"]').filter(has_text="削除").last
                log(f"Delete disabled attr: {delete_btn.get_attribute('aria-disabled')}")
                log("Clicking Delete...")
                delete_btn.click()
                time.sleep(2)
                
                dialog = page.locator('[role="dialog"]').last
                log(f"Dialog text: {dialog.inner_text().replace(chr(10), ' ')}")
                
                confirm = page.locator('[data-testid="confirmationSheetConfirm"]').first
                if confirm.is_visible():
                    confirm.click()
                    log("Clicked confirm sheet!")
                else:
                    fallback = dialog.locator('button, [role="button"]').filter(has_text="削除").last
                    fallback.click()
                    log("Clicked dialog fallback!")
                    
                time.sleep(5)
            else:
                log("Edit button not visible! ALL DONE!")
                break
            
        context.close()
        log("DONE")

if __name__ == "__main__":
    main()
