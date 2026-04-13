import os
import sys
import time
from playwright.sync_api import sync_playwright

SESSION_DIR = r"C:\Users\souhe\Desktop\VetEvidence_SNS_Drafts\VetEvidence_AutoPost\.x_session"

def main():
    print("=== STARTING ABSOLUTE FINAL ===")
    with open("absolute.log", "w", encoding="utf-8") as f:
        def log(msg):
            print(msg)
            f.write(msg + "\n")
            f.flush()
            
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=SESSION_DIR,
                headless=True,
                channel="msedge",
                viewport={"width": 1280, "height": 900}
            )
            page = context.pages[0] if context.pages else context.new_page()
            
            for i in range(50):
                log(f"\n--- BATCH {i+1} ---")
                try:
                    page.goto("https://x.com/compose/post/unsent/scheduled", wait_until="domcontentloaded", timeout=20000)
                except Exception as e:
                    log(f"Goto timeout: {e}")
                    
                time.sleep(5)
                
                # Check directly in JS
                result = page.evaluate("""async () => {
                    const sleep = ms => new Promise(r => setTimeout(r, ms));
                    
                    // Click Edit
                    let editBtn = Array.from(document.querySelectorAll('[role="button"], button')).find(b => b.innerText && b.innerText.includes("編集"));
                    if (!editBtn) return "NO_EDIT_BUTTON";
                    editBtn.click();
                    await sleep(2000);
                    
                    // Click Select All
                    let selectAll = Array.from(document.querySelectorAll('button, [role="button"], span')).find(b => b.innerText && b.innerText.includes("すべて選択"));
                    if (selectAll) {
                        selectAll.click();
                        await sleep(1500);
                    } else {
                        // Fallback click all checkboxes
                        let cbs = document.querySelectorAll('[role="checkbox"]');
                        if (cbs.length === 0) return "NO_CHECKBOXES";
                        for (let cb of cbs) {
                            cb.scrollIntoView({block: "center"});
                            if (cb.getAttribute('aria-checked') !== 'true') cb.click();
                        }
                        await sleep(1500);
                    }
                    
                    // Click Delete
                    let deleteBtns = Array.from(document.querySelectorAll('button, [role="button"]')).filter(b => b.innerText && b.innerText.includes("削除"));
                    if (deleteBtns.length === 0) return "NO_DELETE_BUTTON";
                    let mainDelete = deleteBtns[deleteBtns.length - 1]; // bottom
                    if (mainDelete.getAttribute("aria-disabled") === "true") return "DELETE_DISABLED";
                    
                    mainDelete.click();
                    await sleep(2000);
                    
                    // Confirm Dialog
                    let confirmBtn = document.querySelector('[data-testid="confirmationSheetConfirm"]');
                    if (confirmBtn) {
                        confirmBtn.click();
                        await sleep(3000);
                        return "DELETED_VIA_TESTID";
                    }
                    
                    let dialog = document.querySelector('[role="dialog"]:last-child');
                    if (dialog) {
                        let fallback = Array.from(dialog.querySelectorAll('button, [role="button"]')).find(b => b.innerText && b.innerText.includes("削除"));
                        if(fallback) {
                            fallback.click();
                            await sleep(3000);
                            return "DELETED_VIA_FALLBACK";
                        }
                    }
                    return "NO_CONFIRM_DIALOG";
                }""")
                
                log(f"Result: {result}")
                
                if result in ["NO_EDIT_BUTTON", "NO_CHECKBOXES"]:
                    # Wait and check if the page really has no posts
                    posts = page.locator('[data-testid="cellInnerDiv"]').all()
                    log(f"Double check posts visible: {len(posts)}")
                    if len(posts) == 0:
                        log("All deleted.")
                        break
                        
                time.sleep(3)
                
            context.close()
            log("=== DONE ===")

if __name__ == "__main__":
    main()
