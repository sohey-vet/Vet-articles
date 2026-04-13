import os
import sys
import time
from playwright.sync_api import sync_playwright

SESSION_DIR = r"C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts\VetEvidence_AutoPost\.x_session"

def log(m):
    with open("headless_delete2.log", "a", encoding="utf-8") as f:
        f.write(m + "\n")

def main():
    if os.path.exists("headless_delete2.log"): os.remove("headless_delete2.log")
    log("STARTING HEADLESS DELETE 2")
    try:
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=SESSION_DIR,
                headless=True,
                channel="msedge",
                viewport={"width": 1280, "height": 900}
            )
            page = context.pages[0] if context.pages else context.new_page()
            
            for bidx in range(50):
                log(f"\n--- BATCH {bidx} ---")
                try:
                    page.goto("https://x.com/compose/post/unsent/scheduled", wait_until="domcontentloaded", timeout=20000)
                except:
                    pass
                    
                time.sleep(5)
                
                edit_btn = page.locator('button, [role="button"]').filter(has_text="編集").first
                if edit_btn.is_visible():
                    edit_btn.click()
                    time.sleep(2)
                    
                    rows = page.locator('[data-testid="cellInnerDiv"]').all()
                    log(f"Found {len(rows)} rows to click.")
                    
                    if len(rows) == 0:
                        log("No rows found. Breaking.")
                        break
                    
                    for row in rows:
                        try:
                            row.scroll_into_view_if_needed()
                            row.click(force=True)
                            time.sleep(0.2)
                        except:
                            pass
                            
                    time.sleep(1)
                    
                    delete_btn = page.locator('button, [role="button"]').filter(has_text="削除").last
                    log(f"Clicking Delete... disabled? {delete_btn.get_attribute('aria-disabled')}")
                    delete_btn.click(force=True)
                    time.sleep(2)
                    
                    confirm = page.locator('[data-testid="confirmationSheetConfirm"]').first
                    if confirm.is_visible():
                        confirm.click(force=True)
                        log("Clicked confirm sheet!")
                    else:
                        dialog = page.locator('[role="dialog"]').last
                        fallback = dialog.locator('button, [role="button"]').filter(has_text="削除").last
                        fallback.click(force=True)
                        log("Clicked dialog fallback!")
                        
                    time.sleep(5) # wait for API
                else:
                    log("Edit button not visible! ALL DONE!")
                    break
                
            context.close()
            log("DONE")
    except Exception as ex:
        log(f"CRASH: {ex}")

if __name__ == "__main__":
    main()
