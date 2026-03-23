#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Watcher - Monitors for business update requests and posts to LinkedIn.

This watcher uses Playwright to automate LinkedIn posting for business promotion.
All posts require human approval before being published.

Usage:
    python linkedin_watcher.py /path/to/vault

Requirements:
    pip install playwright
    playwright install chromium

Note: Be aware of LinkedIn's Terms of Service when using automation.
"""

import sys
import time
import random
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from base_watcher import BaseWatcher
except ImportError:
    print("Error: base_watcher.py not found")
    sys.exit(1)

# Playwright imports
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


# Business post templates
POST_TEMPLATES = {
    'business_update': '''🚀 Business Update

We're excited to share some news!

Our team has been working hard to deliver great results for our clients.

#BusinessUpdate #Growth #Success''',

    'service_promotion': '''💼 Now Offering: Professional Services

Looking for expert solutions? We can help!

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

Pro tip: Consistency is key in business.

Small daily improvements lead to massive results over time.

What's one thing you're improving today?

#TipTuesday #BusinessTips #Growth''',

    'throwback_thursday': '''📅 Throwback Thursday

Looking back at how far we've come!

From humble beginnings to serving amazing clients.

Grateful for the journey!

#TBT #ThrowbackThursday #BusinessJourney'''
}


class LinkedInWatcher(BaseWatcher):
    """
    Watches for LinkedIn posting opportunities and creates approval requests.
    """
    
    LINKEDIN_URL = 'https://www.linkedin.com'
    
    # Keywords that indicate a LinkedIn post opportunity
    POST_KEYWORDS = [
        'post on linkedin', 'linkedin post', 'share on linkedin',
        'business update', 'company news', 'achievement',
        'milestone', 'client win', 'new service'
    ]
    
    def __init__(self, vault_path: str, session_path: str = 'linkedin_session',
                 check_interval: int = 300):  # Check every 5 minutes
        """
        Initialize the LinkedIn watcher.
        
        Args:
            vault_path: Path to the Obsidian vault
            session_path: Path to store browser session data
            check_interval: Seconds between checks (default: 300)
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError(
                "Playwright not installed. "
                "Install with: pip install playwright && playwright install chromium"
            )
        
        super().__init__(vault_path, check_interval)
        
        self.session_path = Path(session_path)
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        
        # Ensure directories exist
        self.pending_approval.mkdir(parents=True, exist_ok=True)
        self.approved.mkdir(parents=True, exist_ok=True)
        
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Session path: {self.session_path}")
    
    def check_for_updates(self) -> List[Dict]:
        """
        Check vault for LinkedIn post requests.
        
        Returns:
            List of post request dictionaries
        """
        posts = []
        
        # Check Needs_Action for post requests
        for filepath in self.needs_action.glob('*.md'):
            try:
                content = filepath.read_text(encoding='utf-8')
                content_lower = content.lower()
                
                # Check if this is a LinkedIn post request
                if any(kw in content_lower for kw in self.POST_KEYWORDS):
                    post_data = self._extract_post_request(content, filepath)
                    if post_data:
                        posts.append(post_data)
                
            except Exception as e:
                self.logger.error(f"Error checking file {filepath}: {e}")
        
        return posts
    
    def _extract_post_request(self, content: str, filepath: Path) -> Optional[Dict]:
        """Extract post request details from file content."""
        try:
            # Extract frontmatter values
            frontmatter = {}
            in_frontmatter = False
            for line in content.split('\n'):
                if line.strip() == '---':
                    in_frontmatter = not in_frontmatter
                    continue
                if in_frontmatter and ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip()
            
            # Get post content
            post_content = frontmatter.get('content', '')
            if not post_content:
                # Try to extract from body
                post_content = content[content.find('##'):content.find('##', content.find('##') + 1)]
            
            return {
                'source_file': filepath,
                'type': frontmatter.get('type', 'linkedin_post'),
                'content': post_content,
                'template': frontmatter.get('template', 'custom'),
                'priority': frontmatter.get('priority', 'normal')
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting post request: {e}")
            return None
    
    def create_action_file(self, post: Dict) -> Optional[Path]:
        """
        Create approval request for a LinkedIn post.
        
        Args:
            post: Post request dictionary
            
        Returns:
            Path to created file or None
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"LINKEDIN_POST_{timestamp}.md"
            filepath = self.pending_approval / filename
            
            content = f'''---
type: linkedin_post
action: post_to_linkedin
content: |
{chr(10).join('  ' + line for line in post.get('content', '').split(chr(10)))}
template: {post.get('template', 'custom')}
created: {datetime.now().isoformat()}
status: pending_approval
priority: {post.get('priority', 'normal')}
---

# LinkedIn Post for Approval

## Details

- **Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Template:** {post.get('template', 'Custom')}
- **Priority:** {post.get('priority', 'Normal')}

## Content

```
{post.get('content', '')}
```

## To Approve

Move this file to `/Approved` folder to publish this post.

## To Reject

Move this file to `/Rejected` folder with comments.

---
*This post requires human approval before publishing to LinkedIn.*
'''
            
            filepath.write_text(content, encoding='utf-8')
            
            self.logger.info(f"Created LinkedIn post approval: {filepath.name}")
            
            # Log the action
            self.log_action('linkedin_post_request', {
                'template': post.get('template', 'custom'),
                'approval_file': str(filepath)
            })
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error creating action file: {e}")
            return None
    
    def create_scheduled_post(self, template_name: str = None, custom_content: str = None) -> Optional[Path]:
        """
        Create a scheduled post request.
        
        Args:
            template_name: Name of post template to use
            custom_content: Custom post content
            
        Returns:
            Path to created approval file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"LINKEDIN_SCHEDULED_{timestamp}.md"
        filepath = self.pending_approval / filename
        
        if template_name and template_name in POST_TEMPLATES:
            content = POST_TEMPLATES[template_name]
        elif custom_content:
            content = custom_content
        else:
            # Pick random template
            template_name = random.choice(list(POST_TEMPLATES.keys()))
            content = POST_TEMPLATES[template_name]
        
        content_md = f'''---
type: linkedin_post
action: post_to_linkedin
template: {template_name or 'custom'}
content: |
{chr(10).join('  ' + line for line in content.split(chr(10)))}
created: {datetime.now().isoformat()}
status: pending_approval
scheduled: false
---

# LinkedIn Post for Approval

## Template Used

{template_name or 'Custom'}

## Content

```
{content}
```

## To Approve

Move this file to `/Approved` folder to publish.

## To Reject

Move this file to `/Rejected` folder with comments.

---
*Generated by LinkedIn Watcher*
'''
        
        filepath.write_text(content_md, encoding='utf-8')
        self.logger.info(f"Created scheduled post: {filepath.name}")
        
        return filepath
    
    def execute_approved_post(self, filepath: Path) -> bool:
        """
        Execute an approved LinkedIn post.
        
        Args:
            filepath: Path to approved post file
            
        Returns:
            True if successful
        """
        try:
            content = filepath.read_text(encoding='utf-8')
            
            # Extract post content
            post_content = self._extract_content(content)
            if not post_content:
                self.logger.error('Could not extract post content')
                return False
            
            self.logger.info(f'Posting to LinkedIn: {post_content[:50]}...')
            
            # Post to LinkedIn using Playwright
            success = self._post_to_linkedin(post_content)
            
            if success:
                # Move to Done
                done_path = self.done / filepath.name
                filepath.rename(done_path)
                self.logger.info(f'Post successful, moved to Done: {done_path.name}')
                
                self.log_action('linkedin_post_published', {
                    'content_preview': post_content[:100],
                    'original_file': str(filepath)
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
                self.logger.info("Waiting for LinkedIn to load...")
                time.sleep(5)
                
                # Check if logged in
                try:
                    page.wait_for_selector('[data-control-name="nav_create_post"]', timeout=15000)
                    self.logger.info("Found create post button - logged in")
                except PlaywrightTimeout:
                    self.logger.error('Not logged in to LinkedIn. Please login manually in the browser.')
                    self.logger.info('You have 60 seconds to login...')
                    time.sleep(60)
                    
                    # Check again
                    try:
                        page.wait_for_selector('[data-control-name="nav_create_post"]', timeout=5000)
                    except PlaywrightTimeout:
                        browser.close()
                        return False
                
                # Click create post button
                try:
                    create_post_btn = page.query_selector('[data-control-name="nav_create_post"]')
                    if create_post_btn:
                        create_post_btn.click()
                        self.logger.info("Clicked create post button")
                        time.sleep(3)
                    else:
                        browser.close()
                        return False
                except Exception as e:
                    self.logger.error(f'Could not find create post button: {e}')
                    browser.close()
                    return False
                
                # Find and fill the post text area
                try:
                    # Wait for editor to appear
                    page.wait_for_selector('[role="textbox"]', timeout=10000)
                    
                    # Fill the content
                    textbox = page.query_selector('[role="textbox"]')
                    if textbox:
                        textbox.fill(content)
                        self.logger.info("Filled post content")
                        time.sleep(2)
                    else:
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
                        self.logger.info("Clicked Post button")
                        time.sleep(5)
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
                self.logger.info('LinkedIn post completed successfully')
                return True
                
        except Exception as e:
            self.logger.error(f'Playwright error: {e}', exc_info=True)
            return False
    
    def process_approved_posts(self):
        """Process all approved posts."""
        approved_files = list(self.approved.glob('LINKEDIN_*.md'))
        
        if not approved_files:
            return
        
        self.logger.info(f'Found {len(approved_files)} approved post(s)')
        
        for filepath in approved_files:
            self.logger.info(f'Processing: {filepath.name}')
            success = self.execute_approved_post(filepath)
            
            if not success:
                self.logger.error(f'Failed to post: {filepath.name}')
    
    def run(self):
        """Main run loop."""
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        self.logger.info('Press Ctrl+C to stop')
        
        try:
            while True:
                try:
                    # Check for new post requests
                    items = self.check_for_updates()
                    if items:
                        self.logger.info(f'Found {len(items)} post request(s)')
                        for item in items:
                            filepath = self.create_action_file(item)
                            if filepath:
                                self.logger.info(f'Created approval: {filepath.name}')
                                self.update_dashboard()
                    
                    # Process approved posts
                    self.process_approved_posts()
                    
                    time.sleep(self.check_interval)
                except Exception as e:
                    self.logger.error(f'Error in main loop: {e}', exc_info=True)
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
            sys.exit(1)
    else:
        vault_path = Path(sys.argv[1])
    
    if not vault_path.exists():
        print(f'Error: Vault path does not exist: {vault_path}')
        sys.exit(1)
    
    watcher = LinkedInWatcher(
        vault_path=str(vault_path),
        check_interval=300  # Check every 5 minutes
    )
    watcher.run()


if __name__ == '__main__':
    main()
