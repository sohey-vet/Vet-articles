import os
import time
from playwright.sync_api import sync_playwright

SESSION_DIR = r"C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts\VetEvidence_AutoPost\.x_session"

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=SESSION_DIR,
        headless=False,
        channel="msedge",
        viewport={"width": 1280, "height": 900}
    )
    page = context.pages[0] if context.pages else context.new_page()
    page.goto("https://x.com/compose/post/unsent/scheduled", wait_until="networkidle")
    time.sleep(5)
    
    # Dump all buttons and their texts/labels on the screen
    buttons = page.locator('button, [role="button"], [role="checkbox"]').all()
    for i, b in enumerate(buttons):
        try:
            aria_label = b.get_attribute("aria-label") or ""
            text = b.inner_text() or ""
            data_testid = b.get_attribute("data-testid") or ""
            role = b.get_attribute("role") or ""
            print(f"[{i}] role={role}, text={repr(text)}, aria_label={repr(aria_label)}, testid={repr(data_testid)}")
        except:
            pass
            
    context.close()
