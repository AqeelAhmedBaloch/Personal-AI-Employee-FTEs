#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Poster - Creates and posts business updates to LinkedIn.

This skill automates LinkedIn posting for business promotion and lead generation.
All posts require human approval before being published.

Usage:
    python linkedin_poster.py /path/to/vault --content "Your post content"
    python linkedin_poster.py /path/to/vault --template business_update
    python linkedin_poster.py /path/to/vault --schedule "2026-03-24T10:00:00" --content "..."

Requirements:
    pip install playwright
    playwright install chromium

Note: Be aware of LinkedIn's Terms of Service when using automation.
"""

import sys
import argparse
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import BaseWatcher, logging

# Playwright imports
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


# Post templates for business updates
POST_TEMPLATES = {
    'business_update': '''🚀 Business Update

We're excited to share some news!

Our team has been working hard to deliver great results for our clients.

#BusinessUpdate #Growth #Success''',

    'service_promotion': '''💼 Now Offering: New Services

Looking for professional solutions? We can help!

✅ Quality work
✅ Timely delivery  
✅ Great support

DM us to learn more!

#Services #Business #Solutions''',

    'client_success': '''🎉 Client Success Story

We helped our client achieve amazing results!

"Working with this team was a great experience."

Ready to get similar results? Let's talk!

#ClientSuccess #Testimonial #Results''',

    'motivation_monday': '''💪 Motivation Monday

Success is not final, failure is not fatal:
It is the courage to continue that counts.

What are you working on this week?

#MotivationMonday #Inspiration #Business''',

    'tip_tuesday': '''💡 Tip Tuesday

[Business tip related to your industry]

What's your best tip for [topic]?

#TipTuesday #BusinessTips #Learning'''
}


class LinkedInPoster:
    """
    Posts content to LinkedIn with human approval workflow.
    """
    
    LINKEDIN_URL = 'https://www.linkedin.com'
    
    def __init__(self, vault_path: str, session_path: str = 'linkedin_session'):
        """
        Initialize the LinkedIn poster.
        
        Args:
            vault_path: Path to the Obsidian vault
            session_path: Path to store browser session data
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError(
                "Playwright not installed. "
                "Install with: pip install playwright && playwright install chromium"
            )
        
        self.vault_path = Path(vault_path)
        self.session_path = Path(session_path)
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Directories
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        
        # Ensure directories exist
        for directory in [self.pending_approval, self.approved, self.done]:
            directory.mkdir(parents=True, exist_ok=True)
        
        self.session_path.mkdir(parents=True, exist_ok=True)
    
    def create_post_request(self, content: str, scheduled_time: str = None, 
                           template_name: str = None) -> Optional[Path]:
        """
        Create a post approval request file.
        
        Args:
            content: Post content
            scheduled_time: Optional scheduled time for posting
            template_name: Name of template used
            
        Returns:
            Path to created file or None
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"LINKEDIN_POST_{timestamp}.md"
        filepath = self.pending_approval / filename
        
        scheduled_str = scheduled_time if scheduled_time else "Immediate (upon approval)"
        
        content_md = f'''---
type: linkedin_post
action: post_to_linkedin
content: |
{chr(10).join('  ' + line for line in content.split(chr(10)))}
scheduled_time: {scheduled_str}
template: {template_name or 'custom'}
created: {datetime.now().isoformat()}
status: pending_approval
expires: {datetime.now().replace(hour=23, minute=59).isoformat()}
---

# LinkedIn Post for Approval

## Content

```
{content}
```

## Details

- **Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Scheduled:** {scheduled_str}
- **Template:** {template_name or 'Custom'}

## To Approve

Move this file to `/Approved` folder.

## To Reject

Move this file to `/Rejected` folder with comments.

---
*This post requires human approval before publishing to LinkedIn.*
'''
        
        filepath.write_text(content_md, encoding='utf-8')
        self.logger.info(f'Created post approval request: {filepath.name}')
        
        # Log the action
        self._log_action('post_created', {
            'content_preview': content[:100],
            'scheduled_time': scheduled_time,
            'template': template_name,
            'approval_file': str(filepath)
        })
        
        return filepath
    
    def execute_post(self, approval_file: Path) -> bool:
        """
        Execute a post after approval.
        
        Args:
            approval_file: Path to approved post file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Read the approved content
            content = approval_file.read_text(encoding='utf-8')
            
            # Extract post content from frontmatter
            post_content = self._extract_content(content)
            if not post_content:
                self.logger.error('Could not extract post content')
                return False
            
            self.logger.info(f'Posting to LinkedIn: {post_content[:50]}...')
            
            # Post to LinkedIn using Playwright
            success = self._post_to_linkedin(post_content)
            
            if success:
                # Move to Done
                done_path = self.done / approval_file.name
                approval_file.rename(done_path)
                self.logger.info(f'Post successful, moved to Done: {done_path.name}')
                
                # Log success
                self._log_action('post_published', {
                    'content_preview': post_content[:100],
                    'original_file': str(approval_file)
                })
                
                return True
            else:
                self.logger.error('Failed to post to LinkedIn')
                return False
                
        except Exception as e:
            self.logger.error(f'Error executing post: {e}', exc_info=True)
            return False
    
    def _extract_content(self, file_content: str) -> Optional[str]:
        """Extract post content from approval file."""
        try:
            in_content = False
            content_lines = []
            
            for line in file_content.split('\n'):
                if line.strip().startswith('content:'):
                    in_content = True
                    # Get content after the |
                    if '|' in line:
                        continue
                elif in_content:
                    if line.startswith('---'):
                        break
                    if line.startswith('  '):
                        content_lines.append(line[2:])
                    elif line.strip() == '':
                        content_lines.append('')
                    else:
                        break
            
            return '\n'.join(content_lines).strip()
        except Exception as e:
            self.logger.error(f'Error extracting content: {e}')
            return None
    
    def _post_to_linkedin(self, content: str) -> bool:
        """
        Post content to LinkedIn using browser automation.
        
        Args:
            content: Post content
            
        Returns:
            True if successful
        """
        try:
            with sync_playwright() as p:
                # Launch browser with persistent context
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path),
                    headless=False,  # Show browser for debugging
                    args=['--disable-blink-features=AutomationControlled']
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                # Navigate to LinkedIn
                page.goto(self.LINKEDIN_URL, timeout=30000)
                
                # Wait for page to load
                time.sleep(5)
                
                # Check if logged in
                try:
                    page.wait_for_selector('[data-control-name="nav_create_post"]', timeout=10000)
                except PlaywrightTimeout:
                    self.logger.error('Not logged in to LinkedIn. Please login manually.')
                    browser.close()
                    return False
                
                # Click create post button
                try:
                    create_post_btn = page.query_selector('[data-control-name="nav_create_post"]')
                    if create_post_btn:
                        create_post_btn.click()
                        time.sleep(2)
                    else:
                        # Try alternative selector
                        page.click('button[aria-label*="Start a post"]')
                        time.sleep(2)
                except Exception as e:
                    self.logger.error(f'Could not find create post button: {e}')
                    browser.close()
                    return False
                
                # Find and fill the post text area
                try:
                    # Wait for editor to appear
                    page.wait_for_selector('[role="textbox"]', timeout=5000)
                    
                    # Fill the content
                    textbox = page.query_selector('[role="textbox"]')
                    if textbox:
                        textbox.fill(content)
                        time.sleep(1)
                    else:
                        self.logger.error('Could not find text input')
                        browser.close()
                        return False
                        
                except Exception as e:
                    self.logger.error(f'Error filling content: {e}')
                    browser.close()
                    return False
                
                # Click Post button
                try:
                    post_button = page.query_selector('button[aria-label*="Post"]')
                    if post_button:
                        post_button.click()
                        time.sleep(3)
                        self.logger.info('Post button clicked')
                    else:
                        self.logger.error('Could not find Post button')
                        browser.close()
                        return False
                except Exception as e:
                    self.logger.error(f'Error clicking post button: {e}')
                    browser.close()
                    return False
                
                # Wait for confirmation
                time.sleep(3)
                
                browser.close()
                self.logger.info('LinkedIn post completed')
                return True
                
        except Exception as e:
            self.logger.error(f'Playwright error: {e}', exc_info=True)
            return False
    
    def _log_action(self, action_type: str, details: Dict):
        """Log an action to the logs directory."""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.vault_path / 'Logs' / f'{today}.json'
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'actor': 'linkedin_poster',
            **details
        }
        
        # Simple JSON array append
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
    
    def process_approved_posts(self):
        """Process all approved posts."""
        approved_files = list(self.approved.glob('LINKEDIN_POST_*.md'))
        
        if not approved_files:
            return
        
        self.logger.info(f'Found {len(approved_files)} approved post(s)')
        
        for filepath in approved_files:
            self.logger.info(f'Processing: {filepath.name}')
            success = self.execute_post(filepath)
            
            if not success:
                self.logger.error(f'Failed to post: {filepath.name}')


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='LinkedIn Poster for AI Employee')
    parser.add_argument('vault_path', type=str, help='Path to Obsidian vault')
    parser.add_argument('--content', '-c', type=str, help='Post content')
    parser.add_argument('--template', '-t', type=str, choices=list(POST_TEMPLATES.keys()),
                       help='Use a post template')
    parser.add_argument('--schedule', '-s', type=str, help='Schedule time (ISO format)')
    parser.add_argument('--execute', '-e', action='store_true', help='Execute approved posts')
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault_path)
    if not vault_path.exists():
        print(f'Error: Vault path does not exist: {vault_path}')
        sys.exit(1)
    
    poster = LinkedInPoster(str(vault_path))
    
    if args.execute:
        # Execute approved posts
        poster.process_approved_posts()
    elif args.content or args.template:
        # Create new post request
        if args.template:
            content = POST_TEMPLATES[args.template]
            template_name = args.template
        else:
            content = args.content
            template_name = None
        
        filepath = poster.create_post_request(content, args.schedule, template_name)
        if filepath:
            print(f'✓ Post approval request created: {filepath}')
            print('\nTo approve: Move file to /Approved folder')
            print('To reject: Move file to /Rejected folder')
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
