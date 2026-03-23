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
            
            print("Analyzing Active Toolbar...")
            clicked = driver.execute_script("""
                // The active screen is the one that has an ancestor that is NOT display:none or off-screen,
                // but simpler: find the x-titlebar that contains the text '中山' AND '3R'
                var titlebars = document.querySelectorAll('.x-titlebar, .x-toolbar-dark');
                var activeTb = null;
                for(var i=0; i<titlebars.length; i++) {
                    var tb = titlebars[i];
                    if(tb.offsetWidth > 0 && tb.innerText.indexOf('中山') !== -1 && tb.innerText.indexOf('3R') !== -1) {
                        activeTb = tb;
                        break;
                    }
                }
                
                if(!activeTb) return "active_toolbar_not_found";
                
                // Now inside this active toolbar, find the rightmost button in the left section (x < 200)
                var buttons = activeTb.querySelectorAll('.x-button, .x-icon');
                var candidates = [];
                for(var i=0; i<buttons.length; i++) {
                    var el = buttons[i];
                    if(el.offsetWidth > 0 && el.offsetHeight > 0) {
                        var rect = el.getBoundingClientRect();
                        if(rect.left < 200 && rect.width > 10) {
                            candidates.push({el: el, left: rect.left, html: el.outerHTML});
                        }
                    }
                }
                
                if(candidates.length > 0) {
                    // Sort descending by left coordinate (Right to Left)
                    candidates.sort(function(a, b) { return b.left - a.left; });
                    var target = candidates[0].el;
                    target.click();
                    return "clicked_arrow_at_left_" + Math.round(candidates[0].left) + " from " + candidates.length + " buttons." + 
                           " Classes: " + target.className;
                }
                return "no_buttons_in_active_toolbar";
            """)
            
            print(f"Click result: {clicked}")
            
            print("Waiting 5 seconds for page load...")
            time.sleep(5)
            
            page_text = driver.execute_script("""
                var els = document.querySelectorAll('.x-toolbar-dark .x-title, .x-panel-inner');
                for(var i=0;i<els.length;i++){
                    // check if URL or text changed
                    if(els[i].innerText && (els[i].innerText.indexOf('中山') !== -1 || els[i].innerText.indexOf('R') !== -1)) {
                        return els[i].innerText.replace(/\\n/g, ' ');
                    }
                }
                return document.title;
            """)
            print(f"New location after click: {page_text}")
        else:
            print("Venue not found")
            
    finally:
        driver.quit()

if __name__ == '__main__':
    test_next_race()
