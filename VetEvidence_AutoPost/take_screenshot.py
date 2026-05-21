import sys
from playwright.sync_api import sync_playwright

def main():
    url = "https://www.threads.net/@pawmedical_jp/post/DYTagCPGL2I"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.goto(url, wait_until="networkidle")
        page.screenshot(path="threads_error_investigation.png", full_page=True)
        browser.close()
        print("Screenshot saved to threads_error_investigation.png")

if __name__ == "__main__":
    main()
