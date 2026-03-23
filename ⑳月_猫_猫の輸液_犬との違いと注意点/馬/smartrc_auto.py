"""
SmartRc 自動印付け v11 — 高速ナビゲーション版
使い方:
  1. 下の DATA セクションにリストA/B/C のデータを貼り替える
  2. python smartrc_auto.py を実行 (会場名やレース名の事前設定は一切不要です)

前提:
  - robot_chrome_profile にログイン済み状態が残っていること
"""
import time
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

# ============================================
# 設定
# ============================================
LOGIN_EMAIL = "souhei1219@gmail.com"
LOGIN_PASS = "so1219"
PROFILE_DIR = r"C:\Users\souhe\Desktop\馬\robot_chrome_profile"

# ============================================
# DATA: リストA/B/C
# ============================================
LIST_A = {
    '中山1R': [(13, 'ニシノギャルズ')],
    '中山2R': [(3, 'グランドスウェル'), (4, 'デディカス'), (8, 'ロイヤルヤマト'), (11, 'ブルースパーダ'), (12, 'ライヴジントニック'), (13, 'ソルテソーロ'), (15, 'インスウィング')],
    '中山3R': [(4, 'フェイスリフト')],
    '中山5R': [(10, 'ウインターブレス'), (11, 'ミサダメキメル'), (18, 'ラスターヴァース')],
    '中山6R': [(12, 'イバラヒメ'), (16, 'ライトハウス')],
    '中山7R': [(4, 'ウォーターサグラダ'), (5, 'アンティミスト'), (9, 'ディープスリー'), (13, 'トップマジシャン'), (14, 'ロードストラダーレ'), (16, 'ジャスパーメルチェ')],
    '中山8R': [(2, 'プルメリアクヒオ'), (6, 'ディースプレマシー'), (10, 'サムワンライクユー')],
    '中山9R': [(4, 'ソワドリヨン'), (7, 'エーオーキング'), (10, 'ヴァイザーバルコ')],
    '中山10R': [(5, 'ゴールドアローン')],
    '中山11R': [(1, 'クリノメイ'), (2, 'ビヨンドザヴァレー'), (6, 'アンリーロード'), (8, 'レディーヴァリュー')],
    '中山12R': [(9, 'ランスロット'), (14, 'ウーバーストロング')],
    '阪神1R': [(1, 'アクシュラ'), (5, 'コイバナ'), (6, 'ニキータ'), (7, 'テイエムカミカゼ'), (9, 'サンタカリス'), (12, 'オルビスケリー'), (13, 'ストラーダ')],
    '阪神2R': [(10, 'ライゼシュトゥルム'), (15, 'ケイアイブラック')],
    '阪神3R': [(2, 'ハイドパーク'), (4, 'リオンサーガ'), (7, 'ジェラルリスト'), (8, 'テンマジックアワー'), (9, 'グランシャン'), (10, 'ブレイブメンロード'), (11, 'ポップアップ'), (13, 'タイセイゼスティ')],
    '阪神4R': [(1, 'ブルースプレイヤー'), (5, 'トコトコクマチ')],
    '阪神5R': [(6, 'アメリカンサクラ'), (7, 'テイクザスローン')],
    '阪神6R': [(1, 'エムフォー'), (2, 'アンプイットアップ'), (5, 'ジャンシ')],
    '阪神7R': [(5, 'メードス'), (7, 'レッドイステル')],
    '阪神8R': [(8, 'ジャルディニエ')],
    '阪神10R': [(6, 'ミユキアイラブユー'), (8, 'タカネノハナコサン'), (14, 'トーアジョウトウ'), (15, 'ビルカール')],
    '阪神11R': [(1, 'フルールジェンヌ'), (3, 'プレセピオ'), (9, 'タイセイフレッサ'), (10, 'ラスティングスノー'), (15, 'ローズカリス'), (16, 'ファニーバニー')],
    '阪神12R': [(4, 'アーロッタレット'), (6, 'ジュウオウ'), (12, 'フェルサイト'), (14, 'エンブレムボム'), (15, 'グランデスフィーダ'), (16, 'ジャスパーノベル')],
}

LIST_B = {
    '中山2R': [(1, 'ジオストラテジー'), (3, 'グランドスウェル')],
    '中山3R': [(14, 'トヨサカエ')],
    '中山5R': [(8, 'ヤマメナイト'), (9, 'アイスアイスベイビ'), (12, 'ウィロークリーク'), (13, 'バッカステソーロ')],
    '中山7R': [(2, 'ノースブルースカイ')],
    '中山8R': [(1, 'ブリスフル'), (2, 'プルメリアクヒオ'), (13, 'カージオイド')],
    '中山9R': [(5, 'サラトガチップス'), (9, 'レーヴドロペラ')],
    '中山10R': [(3, 'ウィンドフォール'), (5, 'ゴールドアローン')],
    '阪神1R': [(1, 'アクシュラ'), (8, 'ウンナターシャ'), (10, 'ショコラ')],
    '阪神3R': [(13, 'タイセイゼスティ')],
    '阪神4R': [(1, 'ブルースプレイヤー'), (4, 'ラピス'), (9, 'ケンブリッジグレイ')],
    '阪神5R': [(8, 'リアライズアリス'), (10, 'ジリアート')],
    '阪神6R': [(2, 'アンプイットアップ'), (7, 'メイショウバルク')],
    '阪神7R': [(6, 'ダノンヴェステル')],
    '阪神8R': [(1, 'トーホウガレオン')],
    '阪神9R': [(5, 'ビッグデイメイク')],
    '阪神10R': [(8, 'タカネノハナコサン')],
    '阪神11R': [(1, 'フルールジェンヌ'), (7, 'アイニードユー'), (10, 'ラスティングスノー'), (11, 'クリエープキー'), (12, 'トワニ')],
}

LIST_C = {
    '中山1R': [(16, 'トモジャオーリー')],
    '阪神5R': [(3, 'ホワイトフレイムス')],
    '中山5R': [(12, 'ウィロークリーク')],
    '中山8R': [(12, 'キャストロペペ')],
    '阪神9R': [(3, 'クルミナーレ')],
    '中山9R': [(7, 'エーオーキング')],
    '阪神11R': [(2, 'ギリーズボール'), (10, 'ラスティングスノー'), (17, 'サンアントワーヌ')],
    '阪神12R': [(8, 'ダイヤモンド')],
    '中山12R': [(1, 'ティティナ'), (2, 'ライネリーベ'), (11, 'キャトルエピス'), (13, 'キアラメンテ')],
}

# ============================================
# ロジック
# ============================================

def normalize_race_key(key):
    key = key.strip().replace(" ", "")
    for venue in ["東京", "阪神", "小倉", "京都", "中山", "中京", "札幌", "函館", "福島", "新潟"]:
        if key.startswith(venue):
            rest = key[len(venue):]
            rest = rest.replace("R", "").replace("r", "")
            try:
                rno = int(rest)
                return (venue, rno)
            except:
                pass
    return None

def compute_marks(list_a, list_b, list_c):
    all_races = {}
    
    for key, horses in list_a.items():
        norm = normalize_race_key(key)
        if not norm: continue
        if norm not in all_races: all_races[norm] = {}
        for uno, hname in horses:
            if uno not in all_races[norm]:
                all_races[norm][uno] = {"sets": set(), "hname": hname}
            all_races[norm][uno]["sets"].add("A")
            all_races[norm][uno]["hname"] = hname

    for key, horses in list_b.items():
        norm = normalize_race_key(key)
        if not norm: continue
        if norm not in all_races: all_races[norm] = {}
        for uno, hname in horses:
            if uno not in all_races[norm]:
                all_races[norm][uno] = {"sets": set(), "hname": hname}
            all_races[norm][uno]["sets"].add("B")
            all_races[norm][uno]["hname"] = hname

    for key, horses in list_c.items():
        norm = normalize_race_key(key)
        if not norm: continue
        if norm not in all_races: all_races[norm] = {}
        for uno, hname in horses:
            if uno not in all_races[norm]:
                all_races[norm][uno] = {"sets": set(), "hname": hname}
            all_races[norm][uno]["sets"].add("C")
            all_races[norm][uno]["hname"] = hname

    result = {}
    for (venue, rno), horses in all_races.items():
        if venue not in result: result[venue] = {}
        if rno not in result[venue]: result[venue][rno] = []
        
        for uno, info in horses.items():
            s = info["sets"]
            hname = info["hname"]
            if "A" in s and "B" in s and "C" in s:
                result[venue][rno].append((uno, "m1", "注", hname))
            elif "A" in s and "B" in s:
                result[venue][rno].append((uno, "m1", "◎", hname))
            elif "A" in s and "C" in s:
                result[venue][rno].append((uno, "m1", "○", hname))
                result[venue][rno].append((uno, "m2", "○", hname))
            elif "B" in s and "C" in s:
                result[venue][rno].append((uno, "m1", "○", hname))
                result[venue][rno].append((uno, "m2", "◎", hname))
            elif s == {"A"}:
                result[venue][rno].append((uno, "m2", "○", hname))
            elif s == {"B"}:
                result[venue][rno].append((uno, "m2", "◎", hname))
            elif s == {"C"}:
                result[venue][rno].append((uno, "m2", "▲", hname))

    return result

def js(d, code):
    try:
        return d.execute_script(f"return {code.strip()}")
    except:
        return None

def is_logged_in(driver):
    r = js(driver, """(function(){
        var btns = document.querySelectorAll('.x-button');
        for(var i=0;i<btns.length;i++){
            if(btns[i].innerText==='ログアウト' && btns[i].offsetWidth>0) return true;
        }
        return false;
    })()""")
    return r == True

def auto_login(driver):
    """自動ログイン（Selenium send_keys方式）"""
    print("🔑 自動ログイン中...")

    # 1. マイページ上のログインボタンクリック → 認証ダイアログを開く
    print("  📍 ログインダイアログを開く...")
    js(driver, """(function(){
        var btns = Ext.ComponentQuery.query('button');
        for(var i=0; i<btns.length; i++){
            var t = btns[i].getText ? btns[i].getText() : '';
            if(t === 'ログイン' && !btns[i].isHidden()){
                btns[i].fireEvent('tap', btns[i]);
                return;
            }
        }
    })()""")
    time.sleep(3)

    # 2. Seleniumでinputフィールドを探してsend_keysで入力
    print("  📍 ID/PW入力 (send_keys)...")
    email_field = None
    pass_field = None

    # テキストフィールド（メールアドレス）
    for el in driver.find_elements(By.CSS_SELECTOR, "input[type='text']"):
        try:
            if el.is_displayed() and el.size['width'] > 0:
                email_field = el
                break
        except:
            continue

    # パスワードフィールド
    for el in driver.find_elements(By.CSS_SELECTOR, "input[type='password']"):
        try:
            if el.is_displayed() and el.size['width'] > 0:
                pass_field = el
                break
        except:
            continue

    if not email_field or not pass_field:
        print(f"  ❌ フィールド未検出 (email={email_field is not None}, pass={pass_field is not None})")
        return False

    email_field.clear()
    email_field.send_keys(LOGIN_EMAIL)
    time.sleep(0.3)
    pass_field.clear()
    pass_field.send_keys(LOGIN_PASS)
    time.sleep(0.3)
    print("  ✅ ID/パスワード入力完了")

    # 3. ダイアログ内のログインボタン = 最後の可視ログインボタンをSeleniumクリック
    time.sleep(0.5)
    print("  📍 ログイン送信...")
    login_btns = []
    for el in driver.find_elements(By.CSS_SELECTOR, ".x-button"):
        try:
            if el.is_displayed() and el.size['width'] > 0:
                txt = el.text.strip()
                if txt == 'ログイン':
                    login_btns.append(el)
        except:
            continue

    if login_btns:
        target = login_btns[-1]  # 最後のログインボタン = ダイアログ内
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", target)
        time.sleep(0.3)
        ActionChains(driver).move_to_element(target).click().perform()
        print(f"  ✅ ログインボタンクリック ({len(login_btns)}個中最後)")
    else:
        print("  ❌ ログインボタン未検出")
        return False

    time.sleep(8)

    # 4. エラーチェック＆確認ダイアログ閉じ
    err_text = js(driver, """(function(){
        var el = document.querySelector('.x-messagebox');
        return el ? el.innerText : '';
    })()""")
    if err_text and '認証エラー' in str(err_text):
        print(f"  ❌ {err_text.strip()}")
        # 確認ボタンを押す
        for el in driver.find_elements(By.CSS_SELECTOR, ".x-button"):
            try:
                if el.is_displayed() and el.text.strip() == '確認':
                    ActionChains(driver).move_to_element(el).click().perform()
                    break
            except:
                continue
        return False

    # 5. お知らせ閉じる
    time.sleep(2)
    for el in driver.find_elements(By.XPATH, "//*[contains(text(), '閉じる') or contains(text(), '閉じ')]"):
        try:
            if el.is_displayed():
                ActionChains(driver).move_to_element(el).click().perform()
                print("  ✅ お知らせ等を閉じました")
                break
        except:
            continue
    time.sleep(1)

    # 6. ログイン確認
    js(driver, """(function(){
        var els = document.querySelectorAll('.x-tab');
        for(var i=0;i<els.length;i++){
            if((els[i].innerText||'').indexOf('マイページ')!==-1){ els[i].click(); return; }
        }
    })()""")
    time.sleep(3)

    if is_logged_in(driver):
        print("  ✅ ログイン成功！")
        return True
    else:
        print("  ❌ ログイン失敗")
        return False

def get_todays_venues(driver):
    """ホーム画面から本日の開催会場名を抽出し、ボタンにdata-venue-idx属性を付ける"""
    return driver.execute_script("""
        var today = new Date();
        var todayStr = (today.getMonth()+1) + '/' + today.getDate();
        
        // 前回のマークをクリア
        var allBtns = document.querySelectorAll('[data-venue-idx]');
        for(var k=0; k<allBtns.length; k++) allBtns[k].removeAttribute('data-venue-idx');
        
        var els = document.querySelectorAll('.x-layout-hbox');
        var results = [];
        var venuesList = ["東京", "中山", "京都", "阪神", "小倉", "新潟", "福島", "中京", "札幌", "函館"];
        
        for (var i = 0; i < els.length; i++) {
            var row = els[i];
            var text = row.innerText || '';
            
            // 本日の日付 (例: "2/28") に一致する行を探す
            if (text.indexOf(todayStr) !== -1) {
                var hasVenue = false;
                for(var v=0; v<venuesList.length; v++) {
                    if (text.indexOf(venuesList[v]) !== -1) { hasVenue = true; break; }
                }
                
                if (hasVenue) {
                    var btns = row.querySelectorAll('.x-button, .x-tab');
                    var idx = 0;
                    for (var j = 0; j < btns.length; j++) {
                        var bText = btns[j].innerText || '';
                        for(var v=0; v<venuesList.length; v++) {
                            if (bText.indexOf(venuesList[v]) !== -1 && bText.indexOf("一覧") === -1) {
                                btns[j].setAttribute('data-venue-idx', idx.toString());
                                results.push({
                                    venue: venuesList[v], 
                                    click_text: bText.replace(/\\n/g, ' ').trim(),
                                    idx: idx
                                });
                                idx++;
                                break;
                            }
                        }
                    }
                    if(results.length > 0) return results;
                }
            }
        }
        return results;
    """)

def click_venue_by_idx(driver, idx):
    """data-venue-idx属性でマークされたボタンをSeleniumクリック"""
    els = driver.find_elements(By.CSS_SELECTOR, f"[data-venue-idx='{idx}']")
    if els:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", els[0])
        time.sleep(0.3)
        if els[0].is_displayed():
            ActionChains(driver).move_to_element(els[0]).click().perform()
        time.sleep(5)
        return True
    return False

def click_exact_text(driver, text):
    """指定された完全一致テキストを持つボタン（タブ）を探してクリックする"""
    r = js(driver, f"""(function(){{
        var btns = document.querySelectorAll('.x-button, .x-tab');
        for(var i=0; i<btns.length; i++) {{
            btns[i].removeAttribute('data-target-click');
            var txt = (btns[i].innerText||'').replace(/\\n/g, ' ').trim();
            if(txt === '{text}' && btns[i].offsetWidth > 0) {{
                btns[i].setAttribute('data-target-click', 'true');
                return "found";
            }}
        }}
        return "not_found";
    }})()""")
    if r == "found":
        els = driver.find_elements(By.CSS_SELECTOR, "[data-target-click='true']")
        if els:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", els[0])
            time.sleep(0.3)
            if els[0].is_displayed():
                ActionChains(driver).move_to_element(els[0]).click().perform()
            driver.execute_script("arguments[0].removeAttribute('data-target-click');", els[0])
            time.sleep(3)
            return True
    return False

def go_home(driver):
    """ホームタブに戻る"""
    r = js(driver, """(function(){
        var btns = document.querySelectorAll('.x-button, .x-tab');
        for(var i=0; i<btns.length; i++){
            var t = (btns[i].innerText||'').replace(/\\n/g, ' ').trim();
            if(t.indexOf('ホーム') !== -1 && btns[i].offsetWidth > 0) {
                btns[i].setAttribute('data-target-click', 'true');
                return "found";
            }
        }
        return "not_found";
    })()""")
    if r == "found":
        els = driver.find_elements(By.CSS_SELECTOR, "[data-target-click='true']")
        if els:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", els[0])
            time.sleep(0.3)
            if els[0].is_displayed():
                ActionChains(driver).move_to_element(els[0]).click().perform()
            driver.execute_script("arguments[0].removeAttribute('data-target-click');", els[0])
            time.sleep(3)
            return True
    return False

def go_back_to_race_list(driver):
    """出馬表画面からアプリ内の←ボタンでレース一覧に戻る"""
    # アプリ内の「←」戻るボタンをクリック
    clicked = driver.execute_script("""
        // Ext JSの戻る矢印ボタンを探す
        var arrows = document.querySelectorAll('.x-icon-arrow_left, .x-button-back');
        for(var i=0; i<arrows.length; i++) {
            if(arrows[i].offsetWidth > 0 && arrows[i].offsetHeight > 0) {
                arrows[i].click();
                return true;
            }
        }
        // 左上のボタン全般を試す
        var btns = document.querySelectorAll('.x-button');
        for(var i=0; i<btns.length; i++) {
            var el = btns[i];
            if(el.offsetWidth > 0 && el.offsetHeight > 0) {
                var rect = el.getBoundingClientRect();
                if(rect.left < 50 && rect.top < 50) {
                    el.click();
                    return true;
                }
            }
        }
        return false;
    """)
    if not clicked:
        # フォールバック: ブラウザバック
        print("    ⚠️ アプリ戻るボタン未検出、ブラウザバック使用")
        driver.back()
    time.sleep(5)
    # スクロールを先頭に戻す
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(2)
    return True

def click_race(driver, rno_str):
    """「1R」といった前方一致するレース行をクリックする（スクロール対応）"""
    for attempt in range(5):
        r = js(driver, f"""(function(){{
            var prevMarked = document.querySelectorAll('[data-target-click]');
            for(var k=0; k<prevMarked.length; k++) prevMarked[k].removeAttribute('data-target-click');
            
            var all = document.querySelectorAll('*');
            for(var i=0; i<all.length; i++) {{
                var el = all[i];
                if(el.offsetWidth === 0 || el.offsetHeight === 0) continue;
                var ownText = '';
                for(var n=0; n<el.childNodes.length; n++){{
                    if(el.childNodes[n].nodeType === 3) ownText += el.childNodes[n].textContent;
                }}
                var txt = (el.innerText||'').trim();
                if(txt.indexOf('{rno_str}') === 0 && txt.length < 200) {{
                    el.setAttribute('data-target-click', 'true');
                    return "found:" + txt.substring(0,30);
                }}
            }}
            return "not_found";
        }})()""")
        if r and str(r).startswith("found"):
            print(f"    レース: {r}")
            els = driver.find_elements(By.CSS_SELECTOR, "[data-target-click='true']")
            if els:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", els[0])
                time.sleep(0.3)
                if els[0].is_displayed():
                    ActionChains(driver).move_to_element(els[0]).click().perform()
                driver.execute_script("arguments[0].removeAttribute('data-target-click');", els[0])
                time.sleep(5)
                return True
        # 見つからなかった場合、スクロールダウンして再試行
        driver.execute_script("window.scrollBy(0, 400);")
        time.sleep(1)
    return False

def wait_runners(driver, expected_hname=None, timeout=20):
    for _ in range(timeout):
        c = js(driver, "(function(){try{var s=Ext.data.StoreManager.lookup('runners');return s?s.getCount():0;}catch(e){return 0;}})()")
        if c and int(c) > 0:
            if expected_hname:
                found = js(driver, f"(function(){{var s=Ext.data.StoreManager.lookup('runners');for(var i=0;i<s.getCount();i++){{if(s.getAt(i).get('hname')==='{expected_hname}')return true;}}return false;}})()")
                if found == True: return int(c)
            else:
                return int(c)
        time.sleep(1)
    return 0

def set_marks(driver, marks_list):
    ok = 0; ng = 0
    for uno, field, mark, hname in marks_list:
        fl = "主" if field == "m1" else "仮"
        print(f"    {uno}番{hname}→[{fl}]{mark}", end=" ")
        mc = None
        for xp in [
            f"//tr[.//td[contains(text(),'{hname}')]]//td[contains(@class,'mark')]",
            f"//*[contains(text(),'{hname}')]/ancestor::tr//*[contains(@class,'mark')]",
        ]:
            els = driver.find_elements(By.XPATH, xp)
            if els: mc = els[0]; break
        if not mc: print("❌セル"); ng += 1; continue
        
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", mc)
        time.sleep(0.3)
        ActionChains(driver).move_to_element(mc).click().perform()
        time.sleep(0.8)
        
        ti = 1 if field == "m1" else 2; fc = 0; done = False
        for btn in driver.find_elements(By.CSS_SELECTOR, ".x-button-flat"):
            try:
                if btn.text.strip() == mark:
                    fc += 1
                    if fc == ti:
                        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
                        time.sleep(0.3)
                        ActionChains(driver).move_to_element(btn).click().perform()
                        done = True; break
            except: continue
            
        if done: print("✅"); ok += 1
        else: print("❌UI"); ng += 1
        time.sleep(0.3)
        
        try:
            for c in driver.find_elements(By.XPATH, "//*[contains(text(),'確認') or contains(text(),'OK')]"):
                if c.is_displayed() and c.size['width'] > 0:
                    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", c)
                    time.sleep(0.3)
                    ActionChains(driver).move_to_element(c).click().perform()
                    break
        except: pass
        try:
            ActionChains(driver).move_by_offset(500,10).click().perform()
            ActionChains(driver).move_by_offset(-500,-10).perform()
        except: pass
        time.sleep(0.3)
    return ok, ng

def main():
    # 完了済みレースをスキップ（再実行時に使用）
    SKIP_RACES = set()
    
    marks_by_venue = compute_marks(LIST_A, LIST_B, LIST_C)
    
    if not marks_by_venue:
        print("❌ データが空です！LIST_A/B/Cにデータを入力してください。")
        return

    print("=" * 60)
    print(f"🏇 SmartRc 自動印付け v11 — 高速ナビゲーション版")
    print("=" * 60)

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument(f"--user-data-dir={PROFILE_DIR}")
    options.add_argument("--remote-debugging-port=9222")
    try:
        driver = webdriver.Chrome(options=options)
    except Exception as e:
        print("❌ robot_chrome_profile が別のプロセスに使われています。終了してください。")
        return

    try:
        driver.get("https://www.smartrc.jp/v3/")
        time.sleep(5)

        # ログイン確認
        js(driver, """(function(){
            var els = document.querySelectorAll('.x-tab');
            for(var i=0;i<els.length;i++) if((els[i].innerText||'').indexOf('マイページ')!==-1){els[i].click();return;}
        })()""")
        time.sleep(3)
        if is_logged_in(driver):
            print("✅ ログイン済み\\n")
        else:
            print("⚠️ ログインされていません。自動ログインを試みます...")
            if not auto_login(driver):
                print("❌ 自動ログインに失敗しました。")
                return
            print("✅ ログイン完了\\n")

        start = time.time()
        grand_ok = 0; grand_ng = 0

        # ホーム画面から本日の開催会場リストを表示されている順に取得
        go_home(driver)
        home_venues = get_todays_venues(driver)
        
        if not home_venues:
            print("❌ 本日の開催会場がホーム画面に見つかりませんでした。")
            return
            
        print(f"📌 {len(home_venues)}つの開催会場を自動検出しました:")
        for v in home_venues:
            print(f"  - {v['venue']} (クリック文字: '{v['click_text']}')")

        for v_info in home_venues:
            venue_name = v_info['venue']
            click_text = v_info['click_text']
            venue_idx = v_info.get('idx', 0)
            
            if venue_name not in marks_by_venue:
                print(f"\\n⚠️  {venue_name} には印付け対象データがないためスキップします。")
                continue

            races = marks_by_venue[venue_name]
            sorted_races = sorted(races.keys())
            print(f"\\n{'='*60}")
            print(f"🏟️  {venue_name} ({len(sorted_races)}レース)")
            print(f"{'='*60}")

            for idx, rno in enumerate(sorted_races):
                # スキップ判定
                if (venue_name, rno) in SKIP_RACES:
                    print(f"\\n  [{idx+1}/{len(sorted_races)}] {venue_name}{rno}R → スキップ（完了済み）")
                    continue
                
                marks = races[rno]
                first_hname = marks[0][3]
                print(f"\\n  [{idx+1}/{len(sorted_races)}] {venue_name}{rno}R ({len(marks)}頭)")
                
                # この会場で初めて処理するレースかどうか
                is_first_in_venue = all((venue_name, r) in SKIP_RACES for r in sorted_races[:idx]) if idx > 0 else True
                
                if is_first_in_venue:
                    # 会場の最初のレースのみフルナビ（ホーム→会場→レース）
                    go_home(driver)
                    # ホームでdata属性を再マーク
                    driver.execute_script(f"""
                        var today = new Date();
                        var todayStr = (today.getMonth()+1) + '/' + today.getDate();
                        var els = document.querySelectorAll('.x-layout-hbox');
                        for(var i=0; i<els.length; i++){{
                            var text = els[i].innerText || '';
                            if(text.indexOf(todayStr) !== -1){{
                                var btns = els[i].querySelectorAll('.x-button, .x-tab');
                                var venuesList = ["東京","中山","京都","阪神","小倉","新潟","福島","中京","札幌","函館"];
                                var vidx = 0;
                                for(var j=0; j<btns.length; j++){{
                                    var bText = btns[j].innerText || '';
                                    for(var v=0; v<venuesList.length; v++){{
                                        if(bText.indexOf(venuesList[v]) !== -1 && bText.indexOf('一覧') === -1){{
                                            btns[j].setAttribute('data-venue-idx', vidx.toString());
                                            vidx++;
                                            break;
                                        }}
                                    }}
                                }}
                                break;
                            }}
                        }}
                    """)
                    time.sleep(0.5)
                    if not click_venue_by_idx(driver, venue_idx):
                        print(f"  ❌ 会場ナビ失敗")
                        grand_ng += len(marks); continue
                else:
                    # 2レース目以降：ブラウザバックでレース一覧に戻り、少し待つ
                    go_back_to_race_list(driver)
                
                target_rno_str = f"{rno}R"
                if not click_race(driver, target_rno_str):
                    print(f"  ❌ レース {target_rno_str} クリック失敗")
                    grand_ng += len(marks); continue
                time.sleep(5)
                
                count = wait_runners(driver, expected_hname=first_hname, timeout=20)
                if count == 0:
                    count = wait_runners(driver, timeout=10)
                    if count == 0:
                        print(f"  ❌ 出馬表ロード失敗")
                        grand_ng += len(marks); continue
                print(f"  ✅ 出馬表 ({count}頭)")
                
                ok, ng = set_marks(driver, marks)
                grand_ok += ok; grand_ng += ng
                print(f"  → {ok}頭OK" + (f", {ng}頭NG" if ng > 0 else ""))

        elapsed = time.time() - start
        m, s = int(elapsed // 60), int(elapsed % 60)
        print(f"\\n{'='*60}")
        print(f"🎉 全完了！ {grand_ok}頭OK, {grand_ng}頭NG")
        print(f"⏱️  所要時間: {m}分{s}秒")
        print(f"{'='*60}")
        # 自動実行で止まらないようにinputを削除、またはタイムアウト付きにするなどがあるが、
        # もともとあった `input("Enterで終了...")` は削除しておくか、そのままにしておく。
        # 今回はバックグラウンド実行のため、標準入力を待たれると固まるので `input` は削除する。

    except KeyboardInterrupt:
        print("\\n中断")
    except Exception as e:
        print(f"❌ {e}"); import traceback; traceback.print_exc()
    finally:
        try: driver.quit()
        except: pass

if __name__ == "__main__":
    main()
