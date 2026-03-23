import time
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

sys.path.append(r"C:\Users\souhe\Desktop\馬")
from smartrc_auto import go_home, get_todays_venues, click_venue_by_idx, click_race, wait_runners

def test_next_race():
    PROFILE_DIR = r"C:\Users\souhe\Desktop\馬\robot_chrome_profile"
    options = Options()
    options.add_argument(f"--user-data-dir={PROFILE_DIR}")
    options.add_argument("--remote-debugging-port=9222")
    
    print("ブラウザを起動しています...")
    driver = webdriver.Chrome(options=options)
    try:
        driver.get("https://www.smartrc.jp/v3/")
        time.sleep(5)
        
        print("ホーム画面へ...")
        go_home(driver)
        home_venues = get_todays_venues(driver)
        
        v_idx = None
        for v in home_venues:
            if '中山' in v['venue']:
                v_idx = v['idx']
                break
        
        if v_idx is not None:
            print(f"中山（index:{v_idx}）をクリック...")
            click_venue_by_idx(driver, v_idx)
            time.sleep(2)
            print("1Rをクリック...")
            click_race(driver, "1R")
            time.sleep(5)
            wait_runners(driver, timeout=10)
            
            print("中山1Rに到着。現在の可視ボタンをダンプします:")
            html_snippet = driver.execute_script("""
                var btns = document.querySelectorAll('.x-button');
                var res = [];
                for(var i=0; i<btns.length; i++){
                    if(btns[i].offsetWidth > 0) {
                        res.push(btns[i].className + " | " + btns[i].innerHTML.replace(/\\n/g, '').replace(/\s+/g, ' '));
                    }
                }
                return res;
            """)
            for idx, h in enumerate(html_snippet):
                print(f"  Btn {idx}: {h}")

            print("↓ボタン（arrow_down）をクリックして2Rへ移動テスト...")
            clicked = driver.execute_script("""
                // Ext JSのボタン要素の中に iconCls='arrow_down' みたいなものがあるか調べる
                var btns = document.querySelectorAll('.x-button');
                for(var i=0; i<btns.length; i++) {
                    var html = btns[i].innerHTML;
                    if(html.indexOf('arrow_down') !== -1 && btns[i].offsetWidth > 0) {
                        btns[i].click();
                        return true;
                    }
                }
                // 別のクラス名も試す
                var icons = document.querySelectorAll('.x-icon-arrow_down, .x-icon-arrow-down');
                for(var i=0; i<icons.length; i++) {
                    if(icons[i].offsetWidth > 0) {
                        icons[i].click();
                        return true;
                    }
                }
                return false;
            """)
            print(f"↓矢印ボタンをクリックしましたか？: {clicked}")
            
            time.sleep(5)
            wait_runners(driver, timeout=10)
            
            print("次レース（2R）遷移後の画面上部のテキスト取得:")
            page_text = driver.execute_script("""
                var els = document.querySelectorAll('.x-toolbar-dark .x-title, .x-panel-inner');
                var txt = "";
                for(var i=0;i<els.length;i++){
                    if(els[i].innerText && els[i].innerText.indexOf('中山') !== -1) {
                        txt += els[i].innerText + " ";
                    }
                }
                return txt || document.body.innerText.substring(0, 100);
            """)
            print(page_text.strip()[:100])
        else:
            print("「中山」が見つかりませんでした")
            
    finally:
        driver.quit()

if __name__ == '__main__':
    test_next_race()
