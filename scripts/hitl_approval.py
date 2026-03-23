#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HITL Approval - Human-in-the-Loop approval workflow manager.

Manages approval requests, handles expiry, and processes approved items.

Usage:
    python hitl_approval.py /path/to/vault --check-approved
    python hitl_approval.py /path/to/vault --process-expired
    python hitl_approval.py /path/to/vault --status
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import logging


class HITLApproval:
    """
    Human-in-the-Loop approval workflow manager.
    """
    
    DEFAULT_EXPIRY_HOURS = 24
    
    def __init__(self, vault_path: str):
        """
        Initialize the HITL approval manager.
        
        Args:
            vault_path: Path to the Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Directories
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'
        
        # Ensure directories exist
        for directory in [self.pending_approval, self.approved, 
                          self.rejected, self.done, self.logs]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def create_approval_request(self, action_type: str, details: Dict,
                               expires_in_hours: int = None) -> Optional[Path]:
        """
        Create a new approval request.
        
        Args:
            action_type: Type of action (payment, email, post, etc.)
            details: Dictionary of action details
            expires_in_hours: Hours until expiry (default: 24)
            
        Returns:
            Path to created approval file
        """
        expires_in_hours = expires_in_hours or self.DEFAULT_EXPIRY_HOURS
        now = datetime.now()
        expires = now + timedelta(hours=expires_in_hours)
        
        timestamp = now.strftime('%Y%m%d_%H%M%S')
        safe_type = action_type.upper().replace(' ', '_')
        filename = f"{safe_type}_{timestamp}.md"
        filepath = self.pending_approval / filename
        
        # Build details section
        details_md = '\n'.join(f'- **{k.replace("_", " ").title()}:** {v}' 
                               for k, v in details.items())
        
        content = f'''---
type: approval_request
action: {action_type}
created: {now.isoformat()}
expires: {expires.isoformat()}
status: pending
---

# {action_type.replace("_", " ").title()} Approval Request

## Details

{details_md}

## Created

{now.strftime('%Y-%m-%d %H:%M:%S')}

## Expires

{expires.strftime('%Y-%m-%d %H:%M:%S')}

## To Approve

Move this file to `/Approved` folder.

## To Reject

Move this file to `/Rejected` folder with comments.

---
*This action requires human approval before execution.*
'''
        
        filepath.write_text(content, encoding='utf-8')
        self.logger.info(f'Created approval request: {filepath.name}')
        
        self._log_action('approval_request_created', {
            'action_type': action_type,
            'expires': expires.isoformat(),
            'approval_file': str(filepath)
        })
        
        return filepath
    
    def get_approved_items(self) -> List[Path]:
        """Get list of approved items ready for execution."""
        return list(self.approved.glob('*.md'))
    
    def get_pending_items(self) -> List[Path]:
        """Get list of pending items."""
        return list(self.pending_approval.glob('*.md'))
    
    def get_expired_items(self) -> List[Path]:
        """Get list of expired approval requests."""
        expired = []
        now = datetime.now()
        
        for filepath in self.pending_approval.glob('*.md'):
            content = filepath.read_text(encoding='utf-8')
            expires_line = self._extract_frontmatter_value(content, 'expires')
            
            if expires_line:
                try:
                    expires = datetime.fromisoformat(expires_line)
                    if expires < now:
                        expired.append(filepath)
                except ValueError:
                    pass
        
        return expired
    
    def process_expired_items(self) -> int:
        """
        Move expired items to Rejected folder.
        
        Returns:
            Number of items processed
        """
        expired = self.get_expired_items()
        
        for filepath in expired:
            # Add expiry note
            content = filepath.read_text(encoding='utf-8')
            content = content.replace(
                'status: pending',
                'status: expired'
            )
            content += f'\n\n---\n*Expired at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*\n'
            filepath.write_text(content, encoding='utf-8')
            
            # Move to rejected
            new_path = self.rejected / filepath.name
            shutil.move(str(filepath), str(new_path))
            
            self.logger.info(f'Moved expired request to Rejected: {filepath.name}')
            self._log_action('approval_expired', {
                'original_file': str(filepath),
                'rejected_file': str(new_path)
            })
        
        return len(expired)
    
    def approve_request(self, filepath: Path) -> bool:
        """
        Move a request to Approved folder.
        
        Args:
            filepath: Path to approval request
            
        Returns:
            True if successful
        """
        if not filepath.exists():
            return False
        
        new_path = self.approved / filepath.name
        
        if filepath.parent == self.pending_approval:
            shutil.move(str(filepath), str(new_path))
            self.logger.info(f'Approved: {filepath.name}')
            self._log_action('approval_granted', {
                'file': str(filepath)
            })
            return True
        
        return False
    
    def reject_request(self, filepath: Path, reason: str = '') -> bool:
        """
        Move a request to Rejected folder with optional reason.
        
        Args:
            filepath: Path to approval request
            reason: Rejection reason
            
        Returns:
            True if successful
        """
        if not filepath.exists():
            return False
        
        # Add rejection reason
        content = filepath.read_text(encoding='utf-8')
        content = content.replace('status: pending', 'status: rejected')
        
        if reason:
            content += f'\n\n## Rejection Reason\n\n{reason}\n'
        
        # Write updated content
        filepath.write_text(content, encoding='utf-8')
        
        # Move to rejected
        new_path = self.rejected / filepath.name
        shutil.move(str(filepath), str(new_path))
        
        self.logger.info(f'Rejected: {filepath.name}')
        self._log_action('approval_rejected', {
            'file': str(filepath),
            'reason': reason
        })
        
        return True
    
    def _extract_frontmatter_value(self, content: str, key: str) -> Optional[str]:
        """Extract a value from YAML frontmatter."""
        for line in content.split('\n'):
            if line.startswith(f'{key}:'):
                return line.split(':', 1)[1].strip()
        return None
    
    def _log_action(self, action_type: str, details: Dict):
        """Log an action to the logs directory."""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs / f'{today}.json'
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'actor': 'hitl_approval',
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
    
    def get_status(self) -> Dict:
        """Get current approval status."""
        return {
            'pending': len(self.get_pending_items()),
            'approved': len(self.get_approved_items()),
            'rejected': len(list(self.rejected.glob('*.md'))),
            'done': len(list(self.done.glob('*.md'))),
            'expired': len(self.get_expired_items())
        }


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='HITL Approval Workflow Manager')
    parser.add_argument('vault_path', type=str, help='Path to Obsidian vault')
    parser.add_argument('--check-approved', action='store_true', 
                       help='List approved items')
    parser.add_argument('--process-expired', action='store_true',
                       help='Process expired requests')
    parser.add_argument('--status', action='store_true',
                       help='Show approval status')
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault_path)
    if not vault_path.exists():
        print(f'Error: Vault path does not exist: {vault_path}')
        sys.exit(1)
    
    hitl = HITLApproval(str(vault_path))
    
    if args.status:
        status = hitl.get_status()
        print('\n📊 HITL Approval Status')
        print('=' * 40)
        print(f"Pending:   {status['pending']}")
        print(f"Approved:  {status['approved']}")
        print(f"Rejected:  {status['rejected']}")
        print(f"Done:      {status['done']}")
        print(f"Expired:   {status['expired']}")
        print('=' * 40)
        
    elif args.check_approved:
        approved = hitl.get_approved_items()
        if approved:
            print(f'\n✓ Found {len(approved)} approved item(s):')
            for item in approved:
                print(f"  - {item.name}")
        else:
            print('\nNo approved items waiting.')
            
    elif args.process_expired:
        count = hitl.process_expired_items()
        print(f'\n✓ Processed {count} expired request(s)')
        
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
