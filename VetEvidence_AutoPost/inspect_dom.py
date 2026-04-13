import os
import time
from playwright.sync_api import sync_playwright

SESSION_DIR = r"C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts\VetEvidence_AutoPost\.x_session"

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=SESSION_DIR,
        headless=False,
        channel="msedge"
    )
    page = context.pages[0] if context.pages else context.new_page()
    page.goto("https://x.com/compose/post/unsent/scheduled", wait_until="domcontentloaded")
    time.sleep(5)
    
    # Click edit button
    edit_btn = page.locator('button, [role="button"]').filter(has_text="編集").first
    if edit_btn.is_visible():
        edit_btn.click()
        time.sleep(2)
        
    # Get the HTML of the main dialog
    dialog = page.locator('[role="dialog"]').first
    if dialog.is_visible():
        html = dialog.inner_html()
        with open("dialog_dom.txt", "w", encoding="utf-8") as f:
            f.write(html)
    else:
        print("No dialog found")
        
    context.close()
