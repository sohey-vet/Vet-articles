import os
import sys
import time
from playwright.sync_api import sync_playwright

SESSION_DIR = r"C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts\VetEvidence_AutoPost\.x_session"

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=SESSION_DIR,
        headless=True,
        channel="msedge",
        locale="ja-JP"
    )
    page = context.pages[0] if context.pages else context.new_page()
    page.goto("https://x.com/compose/post/unsent/drafts", wait_until="domcontentloaded")
    time.sleep(5)
    
    # Click 予約済み
    tab = page.locator('[role="tab"]').filter(has_text="予約済み").first
    if tab.is_visible():
        tab.click()
        time.sleep(3)
    else:
        print("Tab not found, maybe direct URL works.")
        page.goto("https://x.com/compose/post/unsent/scheduled")
        time.sleep(5)
        
    print("--- DUMPING SCHEDULED POSTS ---")
    # Scheduled posts are usually in [data-testid="cellInnerDiv"]
    posts = page.locator('[data-testid="cellInnerDiv"]').all()
    count = 0
    for p in posts:
        text = p.inner_text().strip()
        if text:
            print(f"POST {count}:", text.replace('\n', ' ')[:100])
            count += 1
            
    if count == 0:
        print("NO POSTS FOUND IN DOM! IT IS TRULY EMPTY.")

    context.close()
