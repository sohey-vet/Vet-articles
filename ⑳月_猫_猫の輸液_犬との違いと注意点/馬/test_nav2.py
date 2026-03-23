import time
import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

sys.path.append(r"C:\Users\souhe\Desktop\馬")
from smartrc_auto_v12 import go_home, get_todays_venues, click_venue_by_idx, click_race, wait_runners

def test_next_race():
    PROFILE_DIR = r"C:\Users\souhe\Desktop\馬\robot_chrome_profile"
    options = Options()
    options.add_argument(f"--user-data-dir={PROFILE_DIR}")
    options.add_argument("--remote-debugging-port=9222")
    
    driver = webdriver.Chrome(options=options)
    try:
        driver.get("https://www.smartrc.jp/v3/")
        time.sleep(5)
        
        go_home(driver)
        # Verify we are on home
        time.sleep(3)
        print("Home Title:", driver.execute_script("return document.body.innerText.substring(0, 50).replace(/\\n/g, ' ');"))
        
        home_venues = get_todays_venues(driver)
        v_idx = next((v['idx'] for v in home_venues if '中山' in v['venue']), None)
        
        if v_idx is not None:
            print(f"Clicking venue index {v_idx}...")
            click_venue_by_idx(driver, v_idx)
            time.sleep(5)
            print("Venue Title:", driver.execute_script("return document.body.innerText.substring(0, 50).replace(/\\n/g, ' ');"))
            
            print("Clicking 3R...")
            click_race(driver, "3R")
            time.sleep(5)
            wait_runners(driver, timeout=10)
            
            print("Fetching the full HTML of the top toolbar to analyze button structure...")
            toolbar_html = driver.execute_script("""
                var tb = document.querySelector('.x-toolbar-dark');
                if(!tb) tb = document.querySelector('.x-titlebar');
                return tb ? tb.outerHTML : 'no toolbar found';
            """)
            with open("toolbar_dump.html", "w", encoding="utf-8") as f:
                f.write(toolbar_html)
            print("Wrote toolbar html to toolbar_dump.html")
            
            # Don't try to click, just quit.
            time.sleep(1)

        else:
            print("Venue not found")
            
    finally:
        driver.quit()

if __name__ == '__main__':
    test_next_race()
