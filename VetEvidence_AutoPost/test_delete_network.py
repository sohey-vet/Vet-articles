import os
import time
from playwright.sync_api import sync_playwright

SESSION_DIR = r"C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts\VetEvidence_AutoPost\.x_session"

def main():
    print("=== STARTING NETWORK TRACE ===")
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=SESSION_DIR,
            headless=True,
            channel="msedge",
            viewport={"width": 1280, "height": 900}
        )
        page = context.pages[0] if context.pages else context.new_page()

        # Listen for the graphql delete endpoint
        def on_response(response):
            if "graphql" in response.url and "Delete" in response.url:
                print(f"DEL RESP: {response.status} {response.url}")
                try:
                    print("BODY:", response.text()[:200])
                except:
                    pass

        page.on("response", on_response)

        page.goto("https://x.com/compose/post/unsent/scheduled", wait_until="domcontentloaded")
        time.sleep(5)
        
        edit_btn = page.locator('button, [role="button"]').filter(has_text="編集").first
        if edit_btn.is_visible():
            edit_btn.click(force=True)
            time.sleep(2)
            
            cbs = page.locator('[role="checkbox"]').all()
            if cbs:
                cbs[0].scroll_into_view_if_needed()
                cbs[0].click(force=True)
                time.sleep(1)
                
                delete_btn = page.locator('button, [role="button"]').filter(has_text="削除").last
                delete_btn.click(force=True)
                time.sleep(2)
                
                confirm_btn = page.locator('[data-testid="confirmationSheetConfirm"]').first
                if confirm_btn.is_visible():
                    confirm_btn.click(force=True)
                    print("CONFIRM CLICKED!")
                else:
                    dialog = page.locator('[role="dialog"]').last
                    dialog.get_by_role("button", name="削除").last.click()
                    print("CONFIRM FALLBACK CLICKED!")
                    
                time.sleep(5) # Wait for network
            else:
                print("No checkboxes found.")
        else:
            print("No edit button found.")
            
        context.close()
        print("=== END TRACE ===")

if __name__ == "__main__":
    main()
