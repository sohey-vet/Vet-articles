import os
import sys
import time
import json
import logging
from playwright.sync_api import sync_playwright

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_DIR = os.path.join(SCRIPT_DIR, ".x_session")
GHOST_FILE = os.path.join(SCRIPT_DIR, "ghost_tweets.json")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def main():
    if not os.path.exists(SESSION_DIR):
        sys.exit(1)

    ghosts = []
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=SESSION_DIR,
            headless=False,
            channel="msedge"
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto("https://x.com/compose/post/unsent/scheduled", wait_until="domcontentloaded", timeout=20000)
        time.sleep(5)

        last_count = 0
        scroll_attempts = 0
        while scroll_attempts < 10:
            items = page.locator('[data-testid="cellInnerDiv"]').all()
            for item in items:
                try:
                    text = item.inner_text()
                    if text and text not in ghosts:
                        ghosts.append(text)
                except:
                    pass
            
            if len(ghosts) > last_count:
                last_count = len(ghosts)
                scroll_attempts = 0
            else:
                scroll_attempts += 1
                
            page.evaluate("window.scrollBy(0, 1000)")
            time.sleep(1)

        context.close()
        
    with open(GHOST_FILE, "w", encoding="utf-8") as f:
        json.dump(ghosts, f, indent=2, ensure_ascii=False)
        
    print(f"Extracted {len(ghosts)} ghost items")

if __name__ == "__main__":
    main()
