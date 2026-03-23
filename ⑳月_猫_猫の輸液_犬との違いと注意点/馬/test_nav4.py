import time
import sys
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
        home_venues = get_todays_venues(driver)
        v_idx = next((v['idx'] for v in home_venues if '中山' in v['venue']), None)
        
        if v_idx is not None:
            click_venue_by_idx(driver, v_idx)
            time.sleep(3)
            click_race(driver, "3R")
            time.sleep(5)
            wait_runners(driver, timeout=10)
            
            print("Detecting visually active top-left buttons using elementFromPoint...")
            clicked = driver.execute_script("""
                var buttons = document.querySelectorAll('.x-button, .x-icon');
                var candidates = [];
                for(var i=0; i<buttons.length; i++) {
                    var el = buttons[i];
                    var rect = el.getBoundingClientRect();
                    // Top left corner
                    if(rect.top >= 0 && rect.top < 100 && rect.left >= 0 && rect.left < 200 && rect.width > 10 && rect.height > 10) {
                        var centerX = rect.left + rect.width / 2;
                        var centerY = rect.top + rect.height / 2;
                        var topEl = document.elementFromPoint(centerX, centerY);
                        if(topEl && (el === topEl || el.contains(topEl) || topEl.contains(el))) {
                            candidates.push({el: el, left: rect.left, className: el.className, html: el.innerHTML || ''});
                        }
                    }
                }
                
                if(candidates.length > 0) {
                    for(var i=0; i<candidates.length; i++) {
                        var c = candidates[i];
                        if(c.html.indexOf('fa-arrow-down') !== -1) {
                            c.el.click();
                            return "clicked fa-arrow-down at x=" + Math.round(c.left);
                        }
                    }
                }
                return "fa-arrow-down_not_found";
            """)
            print(f"Click result: {clicked}")
            time.sleep(5)
            
            page_info = driver.execute_script("""
                var res = [];
                var all = document.querySelectorAll('*');
                for(var i=0; i<all.length; i++) {
                    var el = all[i];
                    if(el.children.length === 0 && el.innerText) {
                        var text = el.innerText.trim();
                        if(text.indexOf('3R') !== -1 || text.indexOf('4R') !== -1) {
                            res.push("Found in " + el.tagName + " cls=" + el.className + " -> " + text);
                        }
                    }
                }
                return res.join("\\n");
            """)
            print("Elements containing '3R' or '4R':")
            print(page_info)
            
    finally:
        driver.quit()

if __name__ == '__main__':
    test_next_race()
