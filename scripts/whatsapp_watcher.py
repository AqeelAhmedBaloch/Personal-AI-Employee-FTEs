#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WhatsApp Watcher - Monitors WhatsApp Web for important messages.

This watcher uses Playwright to automate WhatsApp Web and check for
messages containing priority keywords.

Usage:
    python whatsapp_watcher.py /path/to/vault

Requirements:
    pip install playwright
    playwright install chromium

Note: Be aware of WhatsApp's Terms of Service when using automation.
"""

import sys
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import BaseWatcher, logging

# Playwright imports
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class WhatsAppWatcher(BaseWatcher):
    """
    Watches WhatsApp Web for messages containing priority keywords.
    """
    
    # Keywords that indicate important messages
    DEFAULT_KEYWORDS = ['urgent', 'asap', 'invoice', 'payment', 'help', 'meeting', 'deadline']
    
    # WhatsApp Web URL
    WHATSAPP_WEB_URL = 'https://web.whatsapp.com'
    
    def __init__(self, vault_path: str, session_path: str = 'whatsapp_session',
                 keywords: List[str] = None, check_interval: int = 30):
        """
        Initialize the WhatsApp watcher.
        
        Args:
            vault_path: Path to the Obsidian vault
            session_path: Path to store browser session data
            keywords: List of keywords to monitor (default: common business keywords)
            check_interval: Seconds between checks (default: 30)
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError(
                "Playwright not installed. "
                "Install with: pip install playwright && playwright install chromium"
            )
        
        super().__init__(vault_path, check_interval)
        
        self.session_path = Path(session_path)
        self.keywords = keywords or self.DEFAULT_KEYWORDS
        self.processed_chats: set = set()
        self.logger.info(f"Monitoring keywords: {self.keywords}")
    
    def check_for_updates(self) -> List[Dict]:
        """
        Check WhatsApp Web for new messages with priority keywords.
        
        Returns:
            List of message dictionaries
        """
        messages = []
        
        try:
            with sync_playwright() as p:
                # Launch browser with persistent context
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path),
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox'
                    ]
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                # Navigate to WhatsApp Web
                try:
                    page.goto(self.WHATSAPP_WEB_URL, timeout=30000)
                    
                    # Wait for chat list to load
                    try:
                        page.wait_for_selector('[data-testid="chat-list"]', timeout=10000)
                    except PlaywrightTimeout:
                        self.logger.warning("WhatsApp Web not loaded (QR code may need scanning)")
                        browser.close()
                        return []
                    
                    # Give time for messages to load
                    time.sleep(3)
                    
                    # Find all chat items
                    chat_items = page.query_selector_all('[role="row"]')
                    
                    for chat in chat_items[:10]:  # Check top 10 chats
                        try:
                            # Get chat name
                            name_elem = chat.query_selector('[dir="auto"]')
                            if not name_elem:
                                continue
                            chat_name = name_elem.inner_text()
                            
                            # Get last message
                            msg_elem = chat.query_selector('span[dir="auto"]')
                            if not msg_elem:
                                continue
                            message_text = msg_elem.inner_text().lower()
                            
                            # Check for keywords
                            if any(kw in message_text for kw in self.keywords):
                                chat_id = f"{chat_name}_{datetime.now().strftime('%Y%m%d')}"
                                
                                if chat_id not in self.processed_chats:
                                    messages.append({
                                        'chat_name': chat_name,
                                        'chat_id': chat_id,
                                        'message': message_text,
                                        'timestamp': datetime.now().isoformat()
                                    })
                                    self.processed_chats.add(chat_id)
                                    self.logger.info(f"Found keyword message from: {chat_name}")
                            
                        except Exception as e:
                            self.logger.debug(f"Error processing chat: {e}")
                            continue
                    
                    browser.close()
                    
                except Exception as e:
                    self.logger.error(f"Error on WhatsApp Web: {e}")
                    browser.close()
                    return []
                    
        except Exception as e:
            self.logger.error(f"Playwright error: {e}")
        
        return messages
    
    def create_action_file(self, message: Dict) -> Optional[Path]:
        """
        Create action file for a WhatsApp message.
        
        Args:
            message: Message dictionary
            
        Returns:
            Path to created file or None
        """
        try:
            safe_name = message['chat_name'].replace(' ', '_').replace('/', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"WHATSAPP_{safe_name}_{timestamp}.md"
            filepath = self.needs_action / filename
            
            content = f'''---
type: whatsapp
chat_name: {message['chat_name']}
chat_id: {message['chat_id']}
received: {message['timestamp']}
priority: high
status: pending
platform: whatsapp_web
---

# WhatsApp Message Received

## Sender Information

- **Chat:** {message['chat_name']}
- **Received:** {message['timestamp']}
- **Platform:** WhatsApp Web
- **Priority:** HIGH (keyword detected)

## Message Content

```
{message['message']}
```

## Suggested Actions

- [ ] Read full message on WhatsApp Web
- [ ] Reply to sender
- [ ] Take required action (invoice, meeting, etc.)
- [ ] Mark as processed

## Notes

*This action file was automatically created by the WhatsApp Watcher.*
*Keyword detected in message triggered this alert.*
'''
            
            filepath.write_text(content, encoding='utf-8')
            
            # Log the action
            self.log_action('whatsapp_message', {
                'chat_name': message['chat_name'],
                'chat_id': message['chat_id'],
                'message_preview': message['message'][:100],
                'action_file': str(filepath)
            })
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error creating action file: {e}")
            return None
    
    def run(self):
        """
        Main run loop with session persistence check.
        """
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Session path: {self.session_path}')
        self.logger.info(f'Keywords: {", ".join(self.keywords)}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        
        # Ensure session path exists
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        self.logger.info('Press Ctrl+C to stop')
        
        try:
            while True:
                try:
                    items = self.check_for_updates()
                    if items:
                        self.logger.info(f'Found {len(items)} message(s) with keywords')
                        for item in items:
                            filepath = self.create_action_file(item)
                            if filepath:
                                self.logger.info(f'Created action file: {filepath.name}')
                                self.update_dashboard()
                    time.sleep(self.check_interval)
                except Exception as e:
                    self.logger.error(f'Error checking WhatsApp: {e}', exc_info=True)
                    time.sleep(self.check_interval)
        except KeyboardInterrupt:
            self.logger.info(f'{self.__class__.__name__} stopped by user')
        except Exception as e:
            self.logger.error(f'Fatal error: {e}', exc_info=True)
            raise


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        vault_path = Path(__file__).parent / 'AI_Employee_Vault'
        if not vault_path.exists():
            print(f'Usage: python {sys.argv[0]} <vault_path>')
            print(f'\nDefault vault not found: {vault_path}')
            sys.exit(1)
    else:
        vault_path = Path(sys.argv[1])
    
    if not vault_path.exists():
        print(f'Error: Vault path does not exist: {vault_path}')
        sys.exit(1)
    
    watcher = WhatsAppWatcher(
        vault_path=str(vault_path),
        session_path=str(Path(__file__).parent / 'whatsapp_session')
    )
    watcher.run()


if __name__ == '__main__':
    main()
