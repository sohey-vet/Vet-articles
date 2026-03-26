from playwright.sync_api import sync_playwright
import time
import json
import os

print("Starting radar script...")
try:
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=r'C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts\VetEvidence_AutoPost\.note_session',
            channel='msedge',
            headless=False
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        print("Navigating to new note...")
        page.goto('https://note.com/notes/new')
        page.wait_for_url("**/edit**", timeout=15000)
        time.sleep(5)
        
        print("Scraping...")
        radar = page.evaluate('''() => {
            let results = [];
            let seen = new Set();
            for (let y = 50; y <= 350; y += 20) {
                for (let x = 100; x <= 1000; x += 40) {
                    let el = document.elementFromPoint(x, y);
                    if (el) {
                        let target = el.closest('button') || el.closest('svg') || el;
                        let key = target.tagName + target.className;
                        if (!seen.has(key)) {
                            seen.add(key);
                            let aria = target.getAttribute('aria-label') || '';
                            let text = target.innerText ? target.innerText.replace(/\\n/g, ' ').substring(0, 20) : '';
                            
                            if (aria || target.tagName === 'BUTTON' || target.tagName === 'SVG' || text.includes('画像') || text.includes('設定')) {
                                results.push(`X:${x} Y:${y} Tag:<${target.tagName}> Aria:[${aria}] Text:[${text}]`);
                            }
                        }
                    }
                }
            }
            return results;
        }''')
        
        out_path = r'C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts\VetEvidence_AutoPost\radar.json'
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(radar, f, ensure_ascii=False, indent=2)
            
        print(f"Successfully saved to {out_path} with {len(radar)} elements.")
        browser.close()
except Exception as e:
    print(f"ERROR: {e}")
