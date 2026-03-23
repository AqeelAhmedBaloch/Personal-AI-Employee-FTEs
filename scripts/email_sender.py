#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Email Sender - Sends emails via Gmail API with approval workflow.

Usage:
    python email_sender.py /path/to/vault --to "email@example.com" --subject "Subject" --body "Body"
    python email_sender.py /path/to/vault --execute  # Execute approved emails

Requirements:
    pip install google-auth google-auth-oauthlib google-api-python-client

Note: Requires Gmail API credentials with full Gmail scope.
"""

import sys
import argparse
import base64
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import logging

# Gmail API imports
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False


class EmailSender:
    """
    Sends emails via Gmail API with human approval workflow.
    """
    
    # Full Gmail scope for sending
    SCOPES = ['https://www.googleapis.com/auth/gmail']
    
    def __init__(self, vault_path: str, credentials_path: str = 'credentials.json',
                 token_path: str = 'token.json'):
        """
        Initialize the email sender.
        
        Args:
            vault_path: Path to the Obsidian vault
            credentials_path: Path to Gmail API credentials.json
            token_path: Path to authentication token
        """
        if not GMAIL_AVAILABLE:
            raise ImportError(
                "Gmail API libraries not installed. "
                "Install with: pip install google-auth google-auth-oauthlib google-api-python-client"
            )
        
        self.vault_path = Path(vault_path)
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.service = None
        
        # Directories
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        
        # Ensure directories exist
        for directory in [self.pending_approval, self.approved, self.done]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Authenticate
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Gmail API."""
        creds = None
        
        if self.token_path.exists():
            with open(self.token_path, 'r') as f:
                creds = Credentials.from_authorized_user_file(f, self.SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not self.credentials_path.exists():
                    self.logger.error(f"Credentials not found: {self.credentials_path}")
                    raise FileNotFoundError("Credentials not found")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            with open(self.token_path, 'w') as f:
                pickle.dump(creds, f)
        
        self.service = build('gmail', 'v1', credentials=creds)
        self.logger.info("Authenticated with Gmail API")
    
    def create_send_request(self, to: str, subject: str, body: str,
                           cc: str = None, attachment: str = None) -> Optional[Path]:
        """
        Create an email send approval request.
        
        Args:
            to: Recipient email
            subject: Email subject
            body: Email body
            cc: CC recipient (optional)
            attachment: Path to attachment file (optional)
            
        Returns:
            Path to created approval file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"EMAIL_SEND_{timestamp}.md"
        filepath = self.pending_approval / filename
        
        content = f'''---
type: email_send
action: send_email
to: {to}
subject: {subject}
cc: {cc if cc else ''}
attachment: {attachment if attachment else ''}
created: {datetime.now().isoformat()}
status: pending_approval
---

# Email for Approval

## Details

- **To:** {to}
- **Subject:** {subject}
- **CC:** {cc if cc else 'N/A'}
- **Attachment:** {attachment if attachment else 'None'}
- **Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Content

```
{body}
```

## To Approve

Move this file to `/Approved` folder.

## To Reject

Move this file to `/Rejected` folder with comments.

---
*This email requires human approval before sending.*
'''
        
        filepath.write_text(content, encoding='utf-8')
        self.logger.info(f'Created email send request: {filepath.name}')
        
        self._log_action('email_draft_created', {
            'to': to,
            'subject': subject,
            'approval_file': str(filepath)
        })
        
        return filepath
    
    def execute_approved_emails(self) -> List[bool]:
        """
        Execute all approved email sends.
        
        Returns:
            List of success/failure results
        """
        approved_files = list(self.approved.glob('EMAIL_SEND_*.md'))
        results = []
        
        if not approved_files:
            self.logger.info('No approved emails to send')
            return results
        
        self.logger.info(f'Found {len(approved_files)} approved email(s)')
        
        for filepath in approved_files:
            success = self._send_from_file(filepath)
            results.append(success)
        
        return results
    
    def _send_from_file(self, filepath: Path) -> bool:
        """
        Send email from approval file.
        
        Args:
            filepath: Path to approval file
            
        Returns:
            True if successful
        """
        try:
            content = filepath.read_text(encoding='utf-8')
            
            # Extract email details
            email_data = self._extract_email_data(content)
            if not email_data:
                self.logger.error(f'Could not extract email data from {filepath.name}')
                return False
            
            # Send the email
            success = self._send_email(
                to=email_data['to'],
                subject=email_data['subject'],
                body=email_data['body'],
                cc=email_data.get('cc'),
                attachment=email_data.get('attachment')
            )
            
            if success:
                # Move to Done
                done_path = self.done / filepath.name
                filepath.rename(done_path)
                self.logger.info(f'Email sent, moved to Done: {done_path.name}')
                
                self._log_action('email_sent', {
                    'to': email_data['to'],
                    'subject': email_data['subject'],
                    'original_file': str(filepath)
                })
                
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f'Error sending email: {e}', exc_info=True)
            return False
    
    def _extract_email_data(self, file_content: str) -> Optional[Dict]:
        """Extract email data from approval file."""
        try:
            data = {}
            lines = file_content.split('\n')
            in_body = False
            body_lines = []
            
            for line in lines:
                if line.startswith('to:'):
                    data['to'] = line.split(':', 1)[1].strip()
                elif line.startswith('subject:'):
                    data['subject'] = line.split(':', 1)[1].strip()
                elif line.startswith('cc:'):
                    data['cc'] = line.split(':', 1)[1].strip()
                elif line.startswith('attachment:'):
                    att = line.split(':', 1)[1].strip()
                    data['attachment'] = att if att else None
                elif line.strip() == '```':
                    if in_body:
                        in_body = False
                    else:
                        in_body = True
                elif in_body:
                    body_lines.append(line)
            
            data['body'] = '\n'.join(body_lines).strip()
            return data if 'to' in data and 'subject' in data else None
            
        except Exception as e:
            self.logger.error(f'Error extracting email data: {e}')
            return None
    
    def _send_email(self, to: str, subject: str, body: str,
                   cc: str = None, attachment: str = None) -> bool:
        """
        Send email via Gmail API.
        
        Args:
            to: Recipient email
            subject: Email subject
            body: Email body
            cc: CC recipient
            attachment: Attachment file path
            
        Returns:
            True if successful
        """
        try:
            # Create message
            if attachment:
                message = MIMEMultipart()
                message.attach(MIMEText(body, 'plain'))
                
                # Add attachment
                with open(attachment, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename={Path(attachment).name}'
                    )
                    message.attach(part)
            else:
                message = MIMEText(body)
            
            message['to'] = to
            message['subject'] = subject
            if cc:
                message['cc'] = cc
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Send via Gmail API
            sent_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            self.logger.info(f'Email sent to {to}, message ID: {sent_message["id"]}')
            return True
            
        except HttpError as e:
            self.logger.error(f'Gmail API error: {e}')
            if e.resp.status == 401:
                self._authenticate()
            return False
        except Exception as e:
            self.logger.error(f'Error sending email: {e}', exc_info=True)
            return False
    
    def _log_action(self, action_type: str, details: Dict):
        """Log an action to the logs directory."""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.vault_path / 'Logs' / f'{today}.json'
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'actor': 'email_sender',
            **details
        }
        
        if log_file.exists():
            content = log_file.read_text(encoding='utf-8').strip()
            if content.endswith(']'):
                content = content[:-1].rstrip()
                if not content.endswith('['):
                    content += ','
                content += '\n  ' + str(log_entry).replace("'", '"') + '\n]'
        else:
            content = '[\n  ' + str(log_entry).replace("'", '"') + '\n]'
        
        log_file.write_text(content, encoding='utf-8')


# Import pickle at module level for authentication
import pickle


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Email Sender for AI Employee')
    parser.add_argument('vault_path', type=str, help='Path to Obsidian vault')
    parser.add_argument('--to', type=str, help='Recipient email')
    parser.add_argument('--subject', type=str, help='Email subject')
    parser.add_argument('--body', type=str, help='Email body')
    parser.add_argument('--cc', type=str, help='CC recipient')
    parser.add_argument('--attachment', type=str, help='Attachment file path')
    parser.add_argument('--execute', '-e', action='store_true', help='Execute approved emails')
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault_path)
    if not vault_path.exists():
        print(f'Error: Vault path does not exist: {vault_path}')
        sys.exit(1)
    
    credentials_path = Path(__file__).parent / 'credentials.json'
    
    try:
        sender = EmailSender(
            str(vault_path),
            credentials_path=str(credentials_path)
        )
        
        if args.execute:
            results = sender.execute_approved_emails()
            print(f'\n✓ Sent {sum(results)}/{len(results)} email(s)')
        elif args.to and args.subject and args.body:
            filepath = sender.create_send_request(
                to=args.to,
                subject=args.subject,
                body=args.body,
                cc=args.cc,
                attachment=args.attachment
            )
            if filepath:
                print(f'✓ Email approval request created: {filepath}')
                print('\nTo approve: Move file to /Approved folder')
                print('To reject: Move file to /Rejected folder')
        else:
            parser.print_help()
            
    except Exception as e:
        print(f'Error: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
