import os
import time
from playwright.sync_api import sync_playwright

SESSION_DIR = r"C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts\VetEvidence_AutoPost\.x_session"

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=SESSION_DIR,
        headless=True,
        channel="msedge",
        args=["--disable-blink-features=AutomationControlled"]
    )
    page = context.pages[0] if context.pages else context.new_page()
    page.goto("https://x.com/compose/post/unsent/scheduled", wait_until="domcontentloaded", timeout=20000)
    time.sleep(5)
    
    # Save a screenshot to see what it looks like
    page.screenshot(path="x_scheduled_screenshot.png")
    
    # Dump test ids
    elements = page.locator('button, [role="button"], span').all()
    count = 0
    for el in elements:
        try:
            if el.is_visible():
                text = el.inner_text().strip()
                if "編集" in text or "Edit" in text or "予約" in text or "削除" in text:
                    print(f"FOUND: text='{text}', testid='{el.get_attribute('data-testid')}'")
                count += 1
        except:
            pass
    print("Total elements checked:", count)
    context.close()
