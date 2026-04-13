import os
import sys
import time
from playwright.sync_api import sync_playwright

SESSION_DIR = r"C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts\VetEvidence_AutoPost\.x_session"

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=SESSION_DIR,
        headless=True,
        channel="msedge",
        viewport={"width": 1280, "height": 900}
    )
    page = context.pages[0] if context.pages else context.new_page()
    
    responses = []
    page.on("response", lambda response: responses.append(response) if "graphql" in response.url or "delete" in response.url else None)

    page.goto("https://x.com/compose/post/unsent/scheduled", wait_until="domcontentloaded", timeout=20000)
    time.sleep(5)

    edit_btn = page.locator('button, [role="button"]').filter(has_text="編集").first
    if edit_btn.is_visible():
        edit_btn.click()
        time.sleep(2)
        
    select_all = page.locator('button, [role="button"], span').filter(has_text="すべて選択").first
    if select_all.is_visible():
        select_all.click()
        time.sleep(2)

    delete_btn = page.locator('button, [role="button"]').filter(has_text="削除").last
    if delete_btn.is_visible():
        delete_btn.click()
        time.sleep(2)
        
        # Dumpt everything visible in the dialog!
        dialog = page.locator('[role="dialog"]').first
        if dialog.is_visible():
            print("DIALOG TEXT:", dialog.inner_text())
            buttons = dialog.locator('button, [role="button"]').all()
            for i, b in enumerate(buttons):
                print(f"DIALOG BUTTON {i}:", b.inner_text(), "| testid:", b.get_attribute("data-testid"))
                
            # Click the one that says 削除
            for b in buttons:
                if "削除" in b.inner_text():
                    b.click()
                    print("CLICKED CONFIRM DELETE!")
                    break
        else:
            print("NO DIALOG VISIBLE!")
            
    time.sleep(5)
    
    print("--- NETWORK RESPONSES ---")
    for r in responses:
        if "Delete" in r.url or "Scheduled" in r.url:
            print(f"{r.status} {r.url}")
            try:
                print(r.text()[:200])
            except:
                pass
                
    context.close()
