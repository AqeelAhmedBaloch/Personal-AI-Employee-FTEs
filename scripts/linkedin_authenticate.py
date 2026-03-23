#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Authentication Helper

Run this script to manually login to LinkedIn and save session.

Usage:
    python linkedin_authenticate.py

Instructions:
    1. Script opens browser
    2. Login to LinkedIn manually
    3. Wait 60 seconds after login
    4. Session saved automatically
    5. Close browser
"""

import sys
import time
from pathlib import Path

# Add parent directory
sys.path.insert(0, str(Path(__file__).parent))

# Playwright imports
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


def authenticate():
    """Authenticate with LinkedIn and save session."""
    
    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Playwright not installed!")
        print("\nInstall with:")
        print("  pip install playwright")
        print("  playwright install chromium")
        return False
    
    session_path = Path(__file__).parent / 'linkedin_session'
    session_path.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("LinkedIn Authentication")
    print("=" * 60)
    print()
    print("Instructions:")
    print("1. Browser will open in 3 seconds...")
    print("2. Login to LinkedIn with your credentials")
    print("3. Wait for homepage to load completely")
    print("4. Session will be saved automatically")
    print("5. Browser will close after 60 seconds")
    print()
    print("Session will be saved to:")
    print(f"  {session_path.absolute()}")
    print()
    
    try:
        with sync_playwright() as p:
            # Launch browser with persistent context
            print("Opening browser...")
            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(session_path),
                headless=False,  # Show browser for login
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--start-maximized'
                ],
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = browser.pages[0] if browser.pages else browser.new_page()
            
            # Navigate to LinkedIn
            print("Navigating to LinkedIn...")
            page.goto('https://www.linkedin.com/login', timeout=30000)
            
            print("\n" + "=" * 60)
            print("PLEASE LOGIN NOW")
            print("=" * 60)
            print()
            print("Enter your email and password on the LinkedIn login page.")
            print("Complete any 2FA if enabled.")
            print()
            
            # Wait for user to login (up to 5 minutes)
            print("Waiting for login (5 minutes max)...")
            
            # Wait for feed page (indicates successful login)
            try:
                page.wait_for_url('https://www.linkedin.com/feed/*', timeout=300000)
                print("\n✓ Login detected!")
            except:
                print("\n⚠ Timeout waiting for login. Continuing anyway...")
            
            # Wait additional time to ensure session is saved
            print("\nSaving session...")
            print("Please wait 10 seconds...")
            time.sleep(10)
            
            # Verify we're logged in
            page.goto('https://www.linkedin.com/feed/', timeout=30000)
            time.sleep(5)
            
            # Check if still on feed (not redirected to login)
            current_url = page.url
            if 'feed' in current_url or 'linkedin.com' in current_url:
                print("\n" + "=" * 60)
                print("✓ AUTHENTICATION SUCCESSFUL!")
                print("=" * 60)
                print(f"\nSession saved to: {session_path.absolute()}")
                print("\nYou can now run:")
                print("  python linkedin_watcher.py ../AI_Employee_Vault")
            else:
                print("\n" + "=" * 60)
                print("⚠ AUTHENTICATION MAY HAVE FAILED")
                print("=" * 60)
                print(f"\nCurrent URL: {current_url}")
                print("Please try again.")
            
            # Wait a bit more then close
            print("\nClosing browser in 5 seconds...")
            time.sleep(5)
            
            browser.close()
            
            return True
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure Playwright is installed: pip install playwright")
        print("2. Install Chromium: playwright install chromium")
        print("3. Check internet connection")
        print("4. Try again")
        return False


def test_session():
    """Test if saved session works."""
    session_path = Path(__file__).parent / 'linkedin_session'
    
    if not session_path.exists():
        print("❌ No session found. Please run authentication first.")
        return False
    
    print("Testing saved session...")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(session_path),
                headless=True,  # Run headless for test
                args=['--disable-blink-features=AutomationControlled']
            )
            
            page = browser.pages[0] if browser.pages else browser.new_page()
            
            # Go to LinkedIn
            page.goto('https://www.linkedin.com/feed/', timeout=30000)
            time.sleep(5)
            
            # Check if logged in
            current_url = page.url
            
            browser.close()
            
            if 'feed' in current_url or 'linkedin.com' in current_url:
                print("✓ Session is valid!")
                print(f"  Current URL: {current_url}")
                return True
            else:
                print("⚠ Session may be invalid")
                print(f"  Redirected to: {current_url}")
                return False
                
    except Exception as e:
        print(f"❌ Session test failed: {e}")
        return False


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        test_session()
    else:
        if authenticate():
            print("\n" + "=" * 60)
            print("Next Steps:")
            print("=" * 60)
            print("1. Run: python linkedin_watcher.py ../AI_Employee_Vault")
            print("2. Create post requests in Inbox/")
            print("3. Approve posts in Pending_Approval/")
            print("=" * 60)
