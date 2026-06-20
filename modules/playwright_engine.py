"""
Playwright engine for enhanced stealth and stability.
"""

import os
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from modules.helpers import print_lg, critical_error_log

def create_playwright_instance(headless: bool = False, user_data_dir: str = "playwright_profile"):
    """
    Creates a Playwright instance with stealth and persistent context.
    """
    try:
        pw = sync_playwright().start()
        
        # Ensure user data dir exists
        if not os.path.exists(user_data_dir):
            os.makedirs(user_data_dir)
            
        browser_context = pw.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-background-networking",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-breakpad",
                "--disable-client-side-phishing-detection",
                "--disable-component-update",
                "--disable-default-apps",
                "--disable-domain-reliability",
                "--disable-extensions",
                "--disable-features=AudioServiceOutOfProcess",
                "--disable-hang-monitor",
                "--disable-ipc-flooding-protection",
                "--disable-notifications",
                "--disable-offer-store-unmasked-wallet-cards",
                "--disable-popup-blocking",
                "--disable-print-preview",
                "--disable-prompt-on-repost",
                "--disable-renderer-backgrounding",
                "--disable-setuid-sandbox",
                "--disable-speech-api",
                "--disable-sync",
                "--hide-scrollbars",
                "--ignore-gpu-blacklist",
                "--metrics-recording-only",
                "--mute-audio",
                "--no-default-browser-check",
                "--no-first-run",
                "--no-pings",
                "--password-store=basic",
                "--use-gl=swiftshader",
                "--use-mock-keychain",
            ],
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        
        # Apply stealth to the entire context (all pages)
        stealth = Stealth()
        stealth.apply_stealth_sync(browser_context)
        
        page = browser_context.pages[0]
        
        print_lg("Playwright instance created with modern stealth mode.")
        return pw, browser_context, page
    except Exception as e:
        critical_error_log("Failed to initialize Playwright!", e)
        raise e

def playwright_login_ln(page, username, password):
    """
    Handles LinkedIn login using Playwright.
    """
    try:
        page.goto("https://www.linkedin.com/login")
        
        # Check if already logged in
        if page.url == "https://www.linkedin.com/feed/":
            print_lg("Already logged in to LinkedIn.")
            return True
            
        page.fill("#username", username)
        page.fill("#password", password)
        page.click('button[type="submit"]')
        
        # Wait for redirect or manual intervention
        page.wait_for_url("https://www.linkedin.com/feed/", timeout=30000)
        print_lg("Login successful via Playwright.")
        return True
    except Exception as e:
        print_lg(f"Login attempt failed via Playwright: {e}")
        return False
