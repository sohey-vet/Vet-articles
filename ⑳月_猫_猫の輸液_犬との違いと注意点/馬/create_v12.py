import time

with open(r"C:\Users\souhe\Desktop\馬\smartrc_auto.py", "r", encoding="utf-8") as f:
    text = f.read()

# バージョン番号置換
text = text.replace("v11 — 高速ナビゲーション版", "v12 — 超高速ナビゲーション（次レース矢印）版")

# 新規関数の追加
new_funcs = """
def click_next_arrow(driver):
    \"\"\"ヘッダの↓矢印（次のレースへ）ボタンをクリックする\"\"\"
    return driver.execute_script('''
        var icons = document.querySelectorAll('.x-icon-arrow_down, .x-icon-arrow-down');
        for(var i=0; i<icons.length; i++) {
            var btn = icons[i].closest('.x-button') || icons[i];
            if(btn.offsetWidth > 0) { btn.click(); return true; }
        }
        var btns = document.querySelectorAll('.x-button');
        for(var i=0; i<btns.length; i++) {
            var html = btns[i].innerHTML;
            if(html.indexOf('arrow_down') !== -1 && btns[i].offsetWidth > 0) {
                btns[i].click(); return true;
            }
        }
        return false;
    ''')

def navigate_to_target_race_by_arrow(driver, venue_name, target_rno, timeout=15):
    \"\"\"現在開いているレース画面から↓矢印を使って目的のレース（target_rno）まで進む\"\"\"
    start_time = time.time()
    while time.time() - start_time < timeout:
        current_rno_str = driver.execute_script('''
            var els = document.querySelectorAll('.x-toolbar-dark .x-title, .x-panel-inner');
            for(var i=0;i<els.length;i++){
                var text = els[i].innerText;
                if(text && text.indexOf('R') !== -1 && text.indexOf("''' + venue_name + '''") !== -1) {
                    var match = text.match(/(\\\\d+)R/);
                    if(match) return match[1];
                }
            }
            return null;
        ''')
        if current_rno_str and current_rno_str.isdigit():
            curr_rno = int(current_rno_str)
            if curr_rno == target_rno:
                return True
            elif curr_rno < target_rno:
                if not click_next_arrow(driver): return False
                time.sleep(2)
            else:
                return False
        else:
            time.sleep(1)
    return False

"""

text = text.replace("def wait_runners(", new_funcs + "def wait_runners(")

# メインループの置換
old_loop = """                else:
                    # 2レース目以降：ブラウザバックでレース一覧に戻り、少し待つ
                    go_back_to_race_list(driver)
                
                target_rno_str = f"{rno}R"
                if not click_race(driver, target_rno_str):
                    print(f"  ❌ レース {target_rno_str} クリック失敗")
                    grand_ng += len(marks); continue
                time.sleep(5)"""

new_loop = """                else:
                    # 2レース目以降：現状のレース画面から↓矢印を使って目的のレースまで高速移動
                    print(f"    ↓矢印で {venue_name}{rno}R へ移動中...")
                    if not navigate_to_target_race_by_arrow(driver, venue_name, rno):
                        print(f"    ⚠️ 矢印ナビゲーション失敗、一覧からフォールバックします")
                        go_back_to_race_list(driver)
                        target_rno_str = f"{rno}R"
                        click_race(driver, target_rno_str)
                        time.sleep(5)"""

text = text.replace(old_loop, new_loop)

with open(r"C:\Users\souhe\Desktop\馬\smartrc_auto_v12.py", "w", encoding="utf-8") as f:
    f.write(text)

print("smartrc_auto_v12.py source generation completed!")
