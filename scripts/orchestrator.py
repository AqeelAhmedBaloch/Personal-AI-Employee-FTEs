#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orchestrator - Master process for the AI Employee (Silver Tier).

The orchestrator:
1. Monitors /Needs_Action folder for pending items
2. Triggers Qwen Code to process pending items
3. Creates Plan.md files for multi-step tasks
4. Manages Human-in-the-Loop approval workflow
5. Coordinates between watchers and Qwen Code

Usage:
    python orchestrator.py /path/to/vault

Silver Tier Features:
- Creates Plan.md for complex tasks
- HITL approval workflow integration
- Multi-step task tracking
"""

import sys
import subprocess
import time
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('orchestrator.log', encoding='utf-8')
    ]
)


class Orchestrator:
    """
    Main orchestrator for the AI Employee system (Silver Tier).
    """
    
    # Actions that always require approval
    ALWAYS_REQUIRE_APPROVAL = ['payment', 'send_email', 'delete_file', 'linkedin_post']
    
    # Payment threshold for approval
    PAYMENT_APPROVAL_THRESHOLD = 50.00
    
    def __init__(self, vault_path: str, check_interval: int = 30):
        """
        Initialize the orchestrator.
        
        Args:
            vault_path: Path to the Obsidian vault
            check_interval: Seconds between checks (default: 30)
        """
        self.vault_path = Path(vault_path)
        self.check_interval = check_interval
        self.logger = logging.getLogger(__name__)
        
        # Directories
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done = self.vault_path / 'Done'
        self.plans = self.vault_path / 'Plans'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.logs = self.vault_path / 'Logs'
        self.briefings = self.vault_path / 'Briefings'
        
        # Ensure directories exist
        for directory in [self.needs_action, self.done, self.plans, 
                          self.pending_approval, self.approved, self.rejected, 
                          self.logs, self.briefings]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Track processed files
        self.processed_files: set = set()
        
        # Qwen Code configuration
        self.qwen_command = 'qwen'
    
    def get_pending_files(self) -> List[Path]:
        """Get list of pending files in /Needs_Action."""
        pending = []
        for filepath in self.needs_action.glob('*.md'):
            if filepath not in self.processed_files:
                pending.append(filepath)
        return sorted(pending, key=lambda f: f.stat().st_ctime)
    
    def get_approved_files(self) -> List[Path]:
        """Get list of approved files ready for action."""
        return sorted(self.approved.glob('*.md'), key=lambda f: f.stat().st_ctime)
    
    def read_file_content(self, filepath: Path) -> str:
        """Read content of a file."""
        try:
            return filepath.read_text(encoding='utf-8')
        except Exception as e:
            self.logger.error(f'Error reading {filepath}: {e}')
            return ''
    
    def extract_frontmatter(self, content: str) -> Dict:
        """Extract YAML frontmatter from content."""
        frontmatter = {}
        in_frontmatter = False
        
        for line in content.split('\n'):
            if line.strip() == '---':
                if not in_frontmatter:
                    in_frontmatter = True
                else:
                    break
                continue
            
            if in_frontmatter and ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()
        
        return frontmatter
    
    def analyze_task_complexity(self, content: str, frontmatter: Dict) -> Tuple[bool, List[str]]:
        """
        Analyze if a task requires a plan (multi-step) or can be done directly.
        
        Returns:
            Tuple of (is_complex, suggested_steps)
        """
        action_type = frontmatter.get('type', '').lower()
        
        # Check for complex action types
        complex_types = ['invoice_request', 'client_onboarding', 'project_setup']
        if any(t in action_type for t in complex_types):
            return True, self._get_suggested_steps(action_type)
        
        # Check content for multi-step indicators
        content_lower = content.lower()
        multi_step_keywords = ['invoice', 'payment', 'client', 'project', 'multiple']
        if any(kw in content_lower for kw in multi_step_keywords):
            return True, self._get_suggested_steps('general')
        
        return False, []
    
    def _get_suggested_steps(self, action_type: str) -> List[str]:
        """Get suggested steps for an action type."""
        steps = {
            'invoice_request': [
                'Review client details and amount',
                'Check if client exists in records',
                'Generate invoice document',
                'Create email send request for approval',
                'Send invoice after approval',
                'Log transaction in Accounting'
            ],
            'email_request': [
                'Read email content and recipient',
                'Check Company Handbook for rules',
                'Create email send approval request',
                'Send email after approval',
                'Log action'
            ],
            'payment_request': [
                'Verify payment details',
                'Check payment threshold',
                'Create payment approval request',
                'Process payment after approval',
                'Log transaction'
            ],
            'general': [
                'Review the request details',
                'Check Company Handbook for applicable rules',
                'Determine required actions',
                'Create approval requests if needed',
                'Execute approved actions',
                'Move to Done when complete'
            ]
        }
        return steps.get(action_type, steps['general'])
    
    def create_plan(self, task_name: str, steps: List[str], context: str = '',
                   action_type: str = '') -> Optional[Path]:
        """
        Create a Plan.md file for a multi-step task.
        
        Args:
            task_name: Name of the task
            steps: List of step descriptions
            context: Additional context
            action_type: Type of action
            
        Returns:
            Path to created plan file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = task_name.replace(' ', '_').replace('/', '_')[:30]
        plan_path = self.plans / f'PLAN_{safe_name}_{timestamp}.md'
        
        checkboxes = '\n'.join(f'- [ ] {step}' for step in steps)
        
        content = f'''---
created: {datetime.now().isoformat()}
task_name: {task_name}
action_type: {action_type}
status: in_progress
total_steps: {len(steps)}
completed_steps: 0
---

# Plan: {task_name}

## Context

{context if context else 'No additional context provided.'}

## Steps

{checkboxes}

## Notes

*This plan was automatically generated by the Orchestrator.*

## Completion

- [ ] All steps completed
- [ ] Moved to /Done

---
*Created: {timestamp}*
'''
        
        plan_path.write_text(content, encoding='utf-8')
        self.logger.info(f'Created plan: {plan_path.name}')
        return plan_path
    
    def create_approval_request(self, action_type: str, details: Dict, 
                               content: str) -> Optional[Path]:
        """
        Create an approval request file.
        
        Args:
            action_type: Type of action requiring approval
            details: Dictionary of action details
            content: Additional content/description
            
        Returns:
            Path to created approval file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_type = action_type.upper().replace(' ', '_')
        filename = f"{safe_type}_{timestamp}.md"
        filepath = self.pending_approval / filename
        
        details_md = '\n'.join(f'- **{k.replace("_", " ").title()}:** {v}' 
                               for k, v in details.items())
        
        expires = datetime.now().replace(hour=23, minute=59)
        
        content_md = f'''---
type: approval_request
action: {action_type}
created: {datetime.now().isoformat()}
expires: {expires.isoformat()}
status: pending
---

# {action_type.replace("_", " ").title()} Approval Request

## Details

{details_md}

## Description

{content}

## To Approve

Move this file to `/Approved` folder.

## To Reject

Move this file to `/Rejected` folder with comments.

---
*This action requires human approval before execution.*
'''
        
        filepath.write_text(content_md, encoding='utf-8')
        self.logger.info(f'Created approval request: {filepath.name}')
        
        self._log_action('approval_request_created', {
            'action_type': action_type,
            'approval_file': str(filepath)
        })
        
        return filepath
    
    def trigger_qwen(self, prompt: str, working_dir: Optional[Path] = None) -> bool:
        """
        Trigger Qwen Code to process a task.
        
        Args:
            prompt: The prompt to give Qwen
            working_dir: Working directory for Qwen
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cmd = [self.qwen_command, '--prompt', prompt]
            
            if working_dir:
                result = subprocess.run(
                    cmd,
                    cwd=str(working_dir),
                    capture_output=True,
                    text=True,
                    timeout=300
                )
            else:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
            
            if result.returncode == 0:
                self.logger.info('Qwen Code completed successfully')
                self.logger.debug(f'Output: {result.stdout[:500]}')
                return True
            else:
                self.logger.error(f'Qwen Code failed: {result.stderr}')
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error('Qwen Code timed out after 5 minutes')
            return False
        except FileNotFoundError:
            self.logger.error('Qwen Code not found. Make sure it\'s installed and in PATH.')
            return False
        except Exception as e:
            self.logger.error(f'Error triggering Qwen Code: {e}')
            return False
    
    def process_needs_action(self):
        """Process all files in /Needs_Action folder."""
        pending_files = self.get_pending_files()
        
        if not pending_files:
            return
        
        self.logger.info(f'Found {len(pending_files)} pending file(s)')
        
        for filepath in pending_files:
            try:
                content = self.read_file_content(filepath)
                frontmatter = self.extract_frontmatter(content)
                
                action_type = frontmatter.get('type', 'unknown')
                
                # Check if this requires a plan (multi-step task)
                is_complex, steps = self.analyze_task_complexity(content, frontmatter)
                
                if is_complex and steps:
                    # Create a plan for complex tasks
                    plan_path = self.create_plan(
                        task_name=filepath.stem,
                        steps=steps,
                        context=content[:500],
                        action_type=action_type
                    )
                    self.logger.info(f'Created plan for complex task: {plan_path.name}')
                
                # Check if this requires approval
                requires_approval = self._check_requires_approval(frontmatter, content)
                
                if requires_approval:
                    # Extract details for approval request
                    details = self._extract_approval_details(frontmatter, content)
                    approval_path = self.create_approval_request(
                        action_type=action_type,
                        details=details,
                        content=content[:300]
                    )
                    
                    if approval_path:
                        # Move original file to Done with note
                        done_path = self.done / filepath.name
                        filepath.rename(done_path)
                        self.logger.info(f'Moved to Done after creating approval: {filepath.name}')
                        self.processed_files.add(filepath)
                        continue
                
                # For simple tasks, trigger Qwen to process directly
                prompt = self._create_process_prompt(filepath, content, frontmatter)
                success = self.trigger_qwen(prompt, self.vault_path)
                
                if success:
                    self.processed_files.add(filepath)
                    self.logger.info(f'Marked file as processed: {filepath.name}')
                    
            except Exception as e:
                self.logger.error(f'Error processing {filepath.name}: {e}', exc_info=True)
    
    def _check_requires_approval(self, frontmatter: Dict, content: str) -> bool:
        """Check if action requires human approval."""
        action_type = frontmatter.get('type', '').lower()
        action = frontmatter.get('action', '').lower()
        
        # Check if action type always requires approval
        if any(t in action_type for t in self.ALWAYS_REQUIRE_APPROVAL):
            return True
        if any(t in action for t in self.ALWAYS_REQUIRE_APPROVAL):
            return True
        
        # Check for payment over threshold
        if 'payment' in action_type or 'payment' in action:
            amount_str = frontmatter.get('amount', '0')
            try:
                amount = float(amount_str.replace('$', '').replace(',', ''))
                if amount > self.PAYMENT_APPROVAL_THRESHOLD:
                    return True
            except ValueError:
                pass
        
        return False
    
    def _extract_approval_details(self, frontmatter: Dict, content: str) -> Dict:
        """Extract details for approval request."""
        details = {}
        
        # Common fields to extract
        for key in ['amount', 'recipient', 'to', 'subject', 'from', 'priority']:
            if key in frontmatter:
                details[key] = frontmatter[key]
        
        return details
    
    def _create_process_prompt(self, filepath: Path, content: str, frontmatter: Dict) -> str:
        """Create prompt for Qwen Code to process a file."""
        return f'''You are processing a pending action in the AI Employee vault.

Vault Path: {self.vault_path}

## File: {filepath.name}

{content}

## Your Tasks

1. Review the file content and frontmatter
2. Determine what action is required based on Company_Handbook.md rules
3. For simple items: Process directly and move to /Done
4. For items requiring approval: Approval request has been created in /Pending_Approval
5. Update Dashboard.md with current status

## Rules

- Always follow the Company_Handbook.md
- Flag payments over $50 for approval
- Log all actions to /Logs/
- Move completed items to /Done

Begin processing now.
'''
    
    def process_approved(self):
        """Process approved files and execute actions."""
        approved_files = self.get_approved_files()
        
        if not approved_files:
            return
        
        self.logger.info(f'Found {len(approved_files)} approved file(s)')
        
        for filepath in approved_files:
            content = self.read_file_content(filepath)
            frontmatter = self.extract_frontmatter(content)
            
            action_type = frontmatter.get('action', frontmatter.get('type', 'unknown'))
            
            self.logger.info(f'Processing approved: {filepath.name} (type: {action_type})')
            
            # Log the action (Silver tier - just logs, doesn't execute)
            self._log_action('approved_action', {
                'file': filepath.name,
                'type': action_type,
                'status': 'logged_silver_tier'
            })
            
            # Move to Done
            done_path = self.done / filepath.name
            filepath.rename(done_path)
            self.logger.info(f'Moved to Done: {done_path.name}')
    
    def _log_action(self, action_type: str, details: Dict):
        """Log an action to the logs directory."""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs / f'{today}.json'
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'actor': 'orchestrator',
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
    
    def update_dashboard(self):
        """Update the Dashboard.md with current counts."""
        dashboard = self.vault_path / 'Dashboard.md'
        if not dashboard.exists():
            return
        
        # Count files
        needs_action_count = len(list(self.needs_action.glob('*.md')))
        pending_approval_count = len(list(self.pending_approval.glob('*.md')))
        plans_count = len(list(self.plans.glob('*.md')))
        done_count = len(list(self.done.glob('*.md')))
        
        # Read and update
        content = dashboard.read_text(encoding='utf-8')
        
        # Update counts
        content = re.sub(
            r'\| \*\*Pending Actions\*\* \| \d+ \|',
            f'| **Pending Actions** | {needs_action_count} |',
            content
        )
        content = re.sub(
            r'\| \*\*Pending Approvals\*\* \| \d+ \|',
            f'| **Pending Approvals** | {pending_approval_count} |',
            content
        )
        
        # Update timestamp
        content = re.sub(
            r'last_updated: .*Z',
            f'last_updated: {datetime.now().isoformat()}Z',
            content
        )
        
        dashboard.write_text(content, encoding='utf-8')
        self.logger.debug('Dashboard updated')
    
    def run(self):
        """Main run loop."""
        self.logger.info('=' * 50)
        self.logger.info('AI Employee Orchestrator (Silver Tier) Starting')
        self.logger.info('=' * 50)
        self.logger.info(f'Vault Path: {self.vault_path}')
        self.logger.info(f'Check Interval: {self.check_interval}s')
        self.logger.info(f'Needs Action: {self.needs_action}')
        self.logger.info(f'Approved: {self.approved}')
        self.logger.info('Press Ctrl+C to stop')
        self.logger.info('=' * 50)
        
        try:
            while True:
                try:
                    # Process pending items
                    self.process_needs_action()
                    
                    # Process approved items
                    self.process_approved()
                    
                    # Update dashboard
                    self.update_dashboard()
                    
                    time.sleep(self.check_interval)
                    
                except Exception as e:
                    self.logger.error(f'Error in main loop: {e}', exc_info=True)
                    time.sleep(self.check_interval)
                    
        except KeyboardInterrupt:
            self.logger.info('Orchestrator stopped by user')
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
    
    orchestrator = Orchestrator(str(vault_path))
    orchestrator.run()


if __name__ == '__main__':
    main()
