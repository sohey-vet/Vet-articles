import os
import sys
import time
from playwright.sync_api import sync_playwright

SESSION_DIR = r"C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts\VetEvidence_AutoPost\.x_session"

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=SESSION_DIR,
        headless=True,
        channel="msedge"
    )
    page = context.pages[0] if context.pages else context.new_page()
    page.goto("https://x.com/compose/post/unsent/scheduled", wait_until="networkidle")
    time.sleep(3)
    print("URL IS:", page.url)
    print("TITLE IS:", page.title())
    context.close()
