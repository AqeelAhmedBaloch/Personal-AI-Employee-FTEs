#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File System Watcher - Monitors a drop folder for new files.

This watcher monitors the /Inbox folder for any new files dropped by the user.
When a file is detected, it creates a corresponding action file in /Needs_Action.

Usage:
    python filesystem_watcher.py /path/to/vault

Requirements:
    pip install watchdog
"""

import sys
import time
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import BaseWatcher, logging


class DropFolderHandler(FileSystemEventHandler):
    """Handles file system events in the drop folder."""
    
    def __init__(self, watcher: 'FilesystemWatcher'):
        self.watcher = watcher
        self.logger = logging.getLogger(__name__)
        self.processed_hashes: set = set()
    
    def _get_file_hash(self, filepath: Path) -> str:
        """Calculate MD5 hash of file content."""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            self.logger.error(f'Error hashing file {filepath}: {e}')
            return ''
    
    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            return
        
        source = Path(event.src_path)
        
        # Skip hidden files and temporary files
        if source.name.startswith('.') or source.name.startswith('~'):
            return
        
        # Skip if already processed
        file_hash = self._get_file_hash(source)
        if file_hash in self.processed_hashes:
            return
        
        self.logger.info(f'New file detected: {source.name}')
        self.watcher.process_file(source, file_hash)
        self.processed_hashes.add(file_hash)


class FilesystemWatcher(BaseWatcher):
    """Watches the /Inbox folder for new files."""
    
    def __init__(self, vault_path: str, check_interval: int = 5):
        super().__init__(vault_path, check_interval)
        self.drop_folder = self.inbox
        
    def process_file(self, source: Path, file_hash: str):
        """Process a dropped file and create an action file."""
        try:
            file_size = source.stat().st_size
            file_ext = source.suffix.lower()
            created_time = datetime.fromtimestamp(source.stat().st_ctime)
            
            file_type = self._categorize_file(file_ext, source.name)
            
            safe_name = source.stem.replace(' ', '_').replace('-', '_')
            action_filename = f'FILE_DROP_{safe_name}_{created_time.strftime("%Y%m%d_%H%M%S")}.md'
            filepath = self.needs_action / action_filename
            
            content_preview = ''
            if file_ext in ['.txt', '.md', '.csv', '.json', '.log']:
                try:
                    content_preview = source.read_text(encoding='utf-8', errors='ignore')[:500]
                except:
                    pass
            
            action_content = f'''---
type: file_drop
original_name: {source.name}
file_hash: {file_hash}
size: {file_size}
size_formatted: {self._format_size(file_size)}
file_type: {file_type}
dropped_at: {created_time.isoformat()}
status: pending
priority: normal
---

# File Dropped for Processing

## File Information

- **Original Name:** {source.name}
- **File Type:** {file_type}
- **Size:** {self._format_size(file_size)}
- **Dropped At:** {created_time.strftime('%Y-%m-%d %H:%M:%S')}

## Content Preview

```
{content_preview if content_preview else '(Binary file or unable to read)'}
```

## Suggested Actions

- [ ] Review file content
- [ ] Categorize and file appropriately
- [ ] Take any required action
- [ ] Move to /Done when complete

## Notes

*This action file was automatically created by the File System Watcher.*
'''
            
            filepath.write_text(action_content, encoding='utf-8')
            
            self.log_action('file_dropped', {
                'file_name': source.name,
                'file_type': file_type,
                'file_size': file_size,
                'action_file': str(filepath)
            })
            
            self.logger.info(f'Created action file: {filepath.name}')
            return filepath
            
        except Exception as e:
            self.logger.error(f'Error processing file {source}: {e}', exc_info=True)
            return None
    
    def _categorize_file(self, ext: str, name: str) -> str:
        """Categorize file based on extension and name."""
        categories = {
            '.pdf': 'Document', '.doc': 'Document', '.docx': 'Document',
            '.txt': 'Text', '.md': 'Markdown',
            '.xls': 'Spreadsheet', '.xlsx': 'Spreadsheet',
            '.csv': 'Data', '.json': 'Data', '.xml': 'Data',
            '.jpg': 'Image', '.jpeg': 'Image', '.png': 'Image',
            '.mp3': 'Audio', '.wav': 'Audio',
            '.mp4': 'Video', '.avi': 'Video',
            '.zip': 'Archive', '.rar': 'Archive', '.7z': 'Archive',
        }
        
        name_lower = name.lower()
        if 'invoice' in name_lower:
            return 'Invoice'
        elif 'receipt' in name_lower:
            return 'Receipt'
        elif 'contract' in name_lower:
            return 'Contract'
        elif 'report' in name_lower:
            return 'Report'
        
        return categories.get(ext, 'Unknown')
    
    def _format_size(self, size: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f'{size:.1f} {unit}'
            size /= 1024
        return f'{size:.1f} TB'
    
    def check_for_updates(self) -> List:
        """Not used in event-driven approach."""
        return []
    
    def create_action_file(self, item) -> Optional[Path]:
        """Not used in event-driven approach."""
        return None
    
    def run(self):
        """Run the filesystem watcher using watchdog Observer."""
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Watching folder: {self.drop_folder}')
        
        self.drop_folder.mkdir(parents=True, exist_ok=True)
        
        event_handler = DropFolderHandler(self)
        observer = Observer()
        observer.schedule(event_handler, str(self.drop_folder), recursive=False)
        observer.start()
        
        self.logger.info(f'File System Watcher started. Drop files in: {self.drop_folder}')
        self.logger.info('Press Ctrl+C to stop')
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info('Stopping File System Watcher...')
            observer.stop()
        except Exception as e:
            self.logger.error(f'Fatal error: {e}', exc_info=True)
            observer.stop()
        
        observer.join()
        self.logger.info('File System Watcher stopped')


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        vault_path = Path(__file__).parent / 'AI_Employee_Vault'
        if not vault_path.exists():
            print(f'Usage: python {sys.argv[0]} <vault_path>')
            sys.exit(1)
    else:
        vault_path = Path(sys.argv[1])
    
    if not vault_path.exists():
        print(f'Error: Vault path does not exist: {vault_path}')
        sys.exit(1)
    
    watcher = FilesystemWatcher(str(vault_path))
    watcher.run()


if __name__ == '__main__':
    main()
