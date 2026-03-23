@echo off
echo =========================================
echo Note Login Setup (Playwright)
echo =========================================
echo.
echo Please login to Note.com in the opened browser.
echo After login is complete, return to this black window and press Enter.
echo.

python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); browser = p.chromium.launch_persistent_context(user_data_dir='.note_session', channel='msedge', headless=False); page = browser.pages[0]; page.goto('https://note.com/login'); input('\n[OK] Press Enter here after login is complete...'); browser.close(); p.stop()"

echo.
echo Setup Complete! You can close this window now.
pause
