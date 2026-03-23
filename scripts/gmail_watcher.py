#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gmail Watcher - Monitors Gmail for new important emails.

This watcher uses the Gmail API to check for new unread and important emails.
When detected, it creates action files in /Needs_Action folder.

Usage:
    python gmail_watcher.py /path/to/vault

Requirements:
    pip install google-auth google-auth-oauthlib google-api-python-client

Setup:
    1. Make sure credentials.json exists in scripts/ folder
    2. Run: python gmail_authenticate.py
    3. Follow browser authentication flow
    4. Run this watcher
"""

import sys
import os
import pickle
import base64
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from email import message_from_bytes

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from base_watcher import BaseWatcher
except ImportError:
    print("Error: base_watcher.py not found")
    sys.exit(1)

# Gmail API imports
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GMAIL_AVAILABLE = True
except ImportError as e:
    print(f"Error: Gmail API libraries not installed: {e}")
    print("Install with: pip install google-auth google-auth-oauthlib google-api-python-client")
    GMAIL_AVAILABLE = False


class GmailWatcher(BaseWatcher):
    """
    Watches Gmail inbox for new important emails.
    """
    
    # Gmail API scopes
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    # Keywords that indicate high priority
    PRIORITY_KEYWORDS = ['urgent', 'asap', 'invoice', 'payment', 'meeting', 'deadline', 'important', 'action required']
    
    def __init__(self, vault_path: str, credentials_path: str = 'credentials.json', 
                 token_path: str = 'token.json', check_interval: int = 120):
        """
        Initialize the Gmail watcher.
        
        Args:
            vault_path: Path to the Obsidian vault
            credentials_path: Path to Gmail API credentials.json
            token_path: Path to store authentication token
            check_interval: Seconds between checks (default: 120)
        """
        if not GMAIL_AVAILABLE:
            raise ImportError("Gmail API libraries not installed")
        
        # Initialize with a dummy path first
        super().__init__(vault_path, check_interval)
        
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path)
        self.service = None
        self.label_ids = {}
        self.processed_ids: set = set()
        
        # Load or authenticate
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Gmail API."""
        creds = None
        
        # Load existing token
        if self.token_path.exists():
            try:
                with open(self.token_path, 'r') as f:
                    creds = Credentials.from_authorized_user_file(f, self.SCOPES)
                self.logger.info("Loaded existing token")
            except Exception as e:
                self.logger.warning(f"Could not load token: {e}")
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                self.logger.info("Refreshing expired token...")
                try:
                    creds.refresh(Request())
                    self._save_token(creds)
                except Exception as e:
                    self.logger.error(f"Token refresh failed: {e}")
                    creds = None
            else:
                if not self.credentials_path.exists():
                    self.logger.error(
                        f"Credentials file not found: {self.credentials_path}\n"
                        "Please run: python gmail_authenticate.py"
                    )
                    raise FileNotFoundError(f"Credentials not found: {self.credentials_path}")
                
                self.logger.info("Starting OAuth flow...")
                self.logger.info("Please complete authentication in browser...")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES
                )
                creds = flow.run_local_server(port=0)
                
                # Save token for future use
                self._save_token(creds)
        
        # Build Gmail service
        self.service = build('gmail', 'v1', credentials=creds)
        self.logger.info("Authenticated with Gmail API")
        
        # Get label IDs
        self._get_label_ids()
    
    def _save_token(self, creds):
        """Save token to file."""
        with open(self.token_path, 'w') as f:
            pickle.dump(creds, f)
        self.logger.info(f"Token saved to: {self.token_path}")
    
    def _get_label_ids(self):
        """Get Gmail label IDs for common labels."""
        try:
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            for label in labels:
                self.label_ids[label['name']] = label['id']
            self.logger.info(f"Loaded {len(labels)} Gmail labels")
        except Exception as e:
            self.logger.error(f"Error getting labels: {e}")
    
    def check_for_updates(self) -> List[Dict]:
        """
        Check for new unread emails.
        
        Returns:
            List of email dictionaries
        """
        if not self.service:
            return []
        
        try:
            # Search for unread emails
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=10
            ).execute()
            
            messages = results.get('messages', [])
            new_emails = []
            
            for msg in messages:
                if msg['id'] not in self.processed_ids:
                    email_data = self._get_email_details(msg['id'])
                    if email_data:
                        new_emails.append(email_data)
                        self.processed_ids.add(msg['id'])
            
            return new_emails
            
        except HttpError as e:
            self.logger.error(f"Gmail API error: {e}")
            if e.resp.status == 401:
                self._authenticate()
            return []
        except Exception as e:
            self.logger.error(f"Error checking emails: {e}")
            return []
    
    def _get_email_details(self, message_id: str) -> Optional[Dict]:
        """
        Get full email details.
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            Dictionary with email details or None
        """
        try:
            msg = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Extract headers
            headers = {h['name']: h['value'] for h in msg['payload']['headers']}
            
            # Get email body
            body = self._get_email_body(msg['payload'])
            
            # Check for priority keywords
            subject = headers.get('Subject', '').lower()
            from_email = headers.get('From', '').lower()
            priority = 'high' if any(kw in subject or kw in from_email 
                                     for kw in self.PRIORITY_KEYWORDS) else 'normal'
            
            return {
                'id': message_id,
                'from': headers.get('From', 'Unknown'),
                'to': headers.get('To', ''),
                'subject': headers.get('Subject', 'No Subject'),
                'date': headers.get('Date', ''),
                'snippet': msg.get('snippet', ''),
                'body': body,
                'priority': priority
            }
            
        except Exception as e:
            self.logger.error(f"Error getting email details: {e}")
            return None
    
    def _get_email_body(self, payload) -> str:
        """Extract email body from payload."""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                    data = part['body']['data']
                    body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    break
                elif part.get('mimeType') == 'text/html':
                    continue  # Skip HTML for now
        elif 'body' in payload and 'data' in payload['body']:
            data = payload['body']['data']
            body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        
        return body[:1000]  # Limit to 1000 chars
    
    def create_action_file(self, email: Dict) -> Optional[Path]:
        """
        Create action file for an email.
        
        Args:
            email: Email dictionary
            
        Returns:
            Path to created file or None
        """
        try:
            # Create safe filename
            safe_subject = email['subject'][:50].replace(' ', '_').replace('/', '_').replace('\\', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"EMAIL_{safe_subject}_{timestamp}.md"
            filepath = self.needs_action / filename
            
            content = f'''---
type: email
email_id: {email['id']}
from: {email['from']}
subject: {email['subject']}
to: {email['to']}
received: {email['date']}
detected_at: {datetime.now().isoformat()}
priority: {email['priority']}
status: pending
platform: gmail
---

# Email Received

## Sender Information

- **From:** {email['from']}
- **To:** {email['to']}
- **Received:** {email['date']}
- **Priority:** {email['priority'].upper()}
- **Detected:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Email Preview

{email['snippet']}

## Full Content

{email['body'] if email['body'] else '(No plain text content)'}

## Suggested Actions

- [ ] Read full email in Gmail
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Create task if action required
- [ ] Archive after processing

## Notes

*This action file was automatically created by the Gmail Watcher.*
'''
            
            filepath.write_text(content, encoding='utf-8')
            
            # Log the action
            self.log_action('email_received', {
                'email_id': email['id'],
                'from': email['from'],
                'subject': email['subject'],
                'priority': email['priority'],
                'action_file': str(filepath)
            })
            
            self.logger.info(f"Created action file: {filepath.name}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error creating action file: {e}")
            return None
    
    def mark_as_read(self, message_id: str):
        """
        Mark an email as read in Gmail.
        
        Args:
            message_id: Gmail message ID
        """
        if not self.service:
            return
        
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            self.logger.info(f"Marked email {message_id} as read")
        except Exception as e:
            self.logger.error(f"Error marking email as read: {e}")
    
    def run(self):
        """Main run loop."""
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        self.logger.info('Press Ctrl+C to stop')
        
        try:
            while True:
                try:
                    items = self.check_for_updates()
                    if items:
                        self.logger.info(f'Found {len(items)} new email(s)')
                        for item in items:
                            filepath = self.create_action_file(item)
                            if filepath:
                                self.logger.info(f'Created action file: {filepath.name}')
                                self.update_dashboard()
                    else:
                        self.logger.debug('No new emails')
                    
                    # Check token expiry
                    if hasattr(self, 'service') and self.service:
                        try:
                            self.service.users().getProfile().execute()
                        except HttpError as e:
                            if e.resp.status == 401:
                                self.logger.warning("Token expired, re-authenticating...")
                                self._authenticate()
                    
                    time.sleep(self.check_interval)
                except Exception as e:
                    self.logger.error(f'Error checking for updates: {e}', exc_info=True)
                    time.sleep(self.check_interval)
        except KeyboardInterrupt:
            self.logger.info(f'{self.__class__.__name__} stopped by user')
        except Exception as e:
            self.logger.error(f'Fatal error: {e}', exc_info=True)
            raise


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        vault_path = Path(__file__).parent.parent / 'AI_Employee_Vault'
        if not vault_path.exists():
            print(f'Usage: python {sys.argv[0]} <vault_path>')
            print(f'\nDefault vault not found: {vault_path}')
            sys.exit(1)
    else:
        vault_path = Path(sys.argv[1])
    
    if not vault_path.exists():
        print(f'Error: Vault path does not exist: {vault_path}')
        sys.exit(1)
    
    # Check for credentials
    credentials_path = Path(__file__).parent / 'credentials.json'
    if not credentials_path.exists():
        print(f'Error: credentials.json not found at {credentials_path}')
        print('Please run: python gmail_authenticate.py')
        sys.exit(1)
    
    watcher = GmailWatcher(
        vault_path=str(vault_path),
        credentials_path=str(credentials_path)
    )
    watcher.run()


if __name__ == '__main__':
    main()
