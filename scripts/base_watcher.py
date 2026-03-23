#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base Watcher - Abstract base class for all watcher scripts.

All watchers follow this pattern:
1. Run continuously in the background
2. Monitor a specific input source (Gmail, WhatsApp, filesystem, etc.)
3. Create .md files in the /Needs_Action folder when something requires attention
4. Log all activity

Usage:
    Create a subclass implementing check_for_updates() and create_action_file()
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('watcher.log', encoding='utf-8')
    ]
)


class BaseWatcher(ABC):
    """
    Abstract base class for all watcher scripts.
    
    Subclasses must implement:
    - check_for_updates(): Return list of new items to process
    - create_action_file(item): Create .md file in Needs_Action folder
    """
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the watcher.
        
        Args:
            vault_path: Path to the Obsidian vault
            check_interval: Seconds between checks (default: 60)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.inbox = self.vault_path / 'Inbox'
        self.logs = self.vault_path / 'Logs'
        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.inbox.mkdir(parents=True, exist_ok=True)
        self.logs.mkdir(parents=True, exist_ok=True)
        
        # Track processed items to avoid duplicates
        self.processed_ids: set = set()
        
    @abstractmethod
    def check_for_updates(self) -> List[Any]:
        """
        Check for new items that require action.
        
        Returns:
            List of items to process
        """
        pass
    
    @abstractmethod
    def create_action_file(self, item: Any) -> Optional[Path]:
        """
        Create a .md action file for an item.
        
        Args:
            item: The item to process
            
        Returns:
            Path to created file, or None if failed
        """
        pass
    
    def log_action(self, action_type: str, details: dict):
        """
        Log an action to the logs directory.
        
        Args:
            action_type: Type of action
            details: Dictionary of action details
        """
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs / f'{today}.json'
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'actor': self.__class__.__name__,
            **details
        }
        
        # Append to log file
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
        
        # Count files in each directory
        needs_action_count = len(list(self.needs_action.glob('*.md')))
        pending_approval_count = len(list((self.vault_path / 'Pending_Approval').glob('*.md')))
        
        # Read current dashboard
        content = dashboard.read_text(encoding='utf-8')
        
        # Update timestamp
        content = content.replace(
            'last_updated: 2026-03-23T00:00:00Z',
            f'last_updated: {datetime.now().isoformat()}Z'
        )
        
        dashboard.write_text(content, encoding='utf-8')
        self.logger.debug('Dashboard updated')
    
    def run(self):
        """Main run loop. Continuously checks for updates and creates action files."""
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        
        try:
            while True:
                try:
                    items = self.check_for_updates()
                    if items:
                        self.logger.info(f'Found {len(items)} new item(s)')
                        for item in items:
                            filepath = self.create_action_file(item)
                            if filepath:
                                self.logger.info(f'Created action file: {filepath.name}')
                                self.update_dashboard()
                    time.sleep(self.check_interval)
                except Exception as e:
                    self.logger.error(f'Error checking for updates: {e}', exc_info=True)
                    time.sleep(self.check_interval)
        except KeyboardInterrupt:
            self.logger.info(f'{self.__class__.__name__} stopped by user')
        except Exception as e:
            self.logger.error(f'Fatal error: {e}', exc_info=True)
            raise


if __name__ == '__main__':
    print("BaseWatcher is an abstract class. Create a subclass to use.")
