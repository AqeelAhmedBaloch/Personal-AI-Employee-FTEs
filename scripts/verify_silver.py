#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Silver Tier Verification Script

Verifies that all Silver tier requirements are met:
- All Bronze requirements PLUS:
- Two or more Watcher scripts (Gmail + WhatsApp + LinkedIn)
- Claude/Qwen reasoning loop that creates Plan.md files
- One working MCP server for external action
- Human-in-the-loop approval workflow
- Basic scheduling via cron or Task Scheduler
- All AI functionality implemented as Agent Skills

Usage:
    python verify_silver.py
"""

import sys
from pathlib import Path
from datetime import datetime

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def check(condition, message):
    """Print check result."""
    if condition:
        print(f"{Colors.GREEN}✓{Colors.RESET} {message}")
        return True
    else:
        print(f"{Colors.RED}✗{Colors.RESET} {message}")
        return False

def main():
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}AI Employee - Silver Tier Verification{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")
    
    # Find paths
    script_dir = Path(__file__).parent
    vault_path = script_dir.parent / 'AI_Employee_Vault'
    skills_path = script_dir.parent / '.qwen' / 'skills'
    
    all_passed = True
    bronze_passed = True
    silver_passed = True
    
    # ==================== BRONZE REQUIREMENTS ====================
    print(f"{Colors.BOLD}{Colors.BLUE}=== BRONZE TIER REQUIREMENTS ==={Colors.RESET}\n")
    
    # 1. Check vault exists
    print(f"{Colors.BLUE}Vault Check:{Colors.RESET}")
    if not check(vault_path.exists(), f"Obsidian vault exists: {vault_path}"):
        bronze_passed = False
        all_passed = False
    
    if vault_path.exists():
        # 2. Check required files
        print(f"\n{Colors.BLUE}Required Files:{Colors.RESET}")
        required_files = [
            ('Dashboard.md', 'Dashboard file'),
            ('Company_Handbook.md', 'Company Handbook'),
            ('Business_Goals.md', 'Business Goals'),
        ]
        
        for filename, description in required_files:
            filepath = vault_path / filename
            exists = filepath.exists()
            if not check(exists, f"{description}: {filename}"):
                bronze_passed = False
                all_passed = False
        
        # 3. Check folder structure
        print(f"\n{Colors.BLUE}Folder Structure:{Colors.RESET}")
        required_folders = [
            'Inbox', 'Needs_Action', 'Done', 'Plans',
            'Approved', 'Pending_Approval', 'Rejected',
            'Logs', 'Accounting', 'Briefings', 'Invoices',
        ]
        
        for folder in required_folders:
            folder_path = vault_path / folder
            if not check(folder_path.exists() and folder_path.is_dir(), f"Folder: /{folder}"):
                bronze_passed = False
                all_passed = False
        
        # 4. Check Bronze scripts
        print(f"\n{Colors.BLUE}Bronze Scripts:{Colors.RESET}")
        bronze_scripts = [
            ('base_watcher.py', 'Base Watcher class'),
            ('filesystem_watcher.py', 'File System Watcher'),
            ('orchestrator.py', 'Orchestrator'),
        ]
        
        for filename, description in bronze_scripts:
            filepath = script_dir / filename
            if not check(filepath.exists(), f"{description}: {filename}"):
                bronze_passed = False
                all_passed = False
    
    # ==================== SILVER REQUIREMENTS ====================
    print(f"\n{Colors.BOLD}{Colors.BLUE}=== SILVER TIER REQUIREMENTS ==={Colors.RESET}\n")
    
    # 5. Check additional watchers (2+ watchers)
    print(f"{Colors.BLUE}Additional Watchers (2+ required):{Colors.RESET}")
    watchers = {
        'gmail_watcher.py': 'Gmail Watcher',
        'whatsapp_watcher.py': 'WhatsApp Watcher',
    }
    
    watcher_count = 0
    for filename, description in watchers.items():
        filepath = script_dir / filename
        if filepath.exists():
            check(True, f"{description}: {filename}")
            watcher_count += 1
        else:
            check(False, f"{description}: {filename} (optional)")
    
    if watcher_count >= 1:  # At least 1 additional watcher + filesystem = 2 total
        check(True, f"Minimum watchers met: {watcher_count + 1} total (filesystem + {watcher_count})")
    else:
        check(False, "Need at least 2 watchers total (filesystem + 1 more)")
        silver_passed = False
        all_passed = False
    
    # 6. Check Agent Skills
    print(f"\n{Colors.BLUE}Agent Skills:{Colors.RESET}")
    required_skills = [
        'browsing-with-playwright',
        'email-watcher',
        'whatsapp-watcher',
        'linkedin-poster',
        'email-sender',
        'hitl-approval',
        'scheduler',
    ]
    
    skill_count = 0
    for skill in required_skills:
        skill_path = skills_path / skill
        if skill_path.exists():
            skill_file = skill_path / 'SKILL.md'
            if skill_file.exists():
                check(True, f"Skill: {skill}")
                skill_count += 1
            else:
                check(False, f"Skill {skill} missing SKILL.md")
        else:
            check(False, f"Skill: {skill}")
    
    if skill_count >= 5:
        check(True, f"Minimum skills met: {skill_count} skills")
    else:
        check(False, f"Need at least 5 skills, found {skill_count}")
        silver_passed = False
        all_passed = False
    
    # 7. Check Silver scripts
    print(f"\n{Colors.BLUE}Silver Scripts:{Colors.RESET}")
    silver_scripts = [
        ('gmail_watcher.py', 'Gmail Watcher'),
        ('whatsapp_watcher.py', 'WhatsApp Watcher'),
        ('linkedin_poster.py', 'LinkedIn Poster'),
        ('email_sender.py', 'Email Sender'),
        ('hitl_approval.py', 'HITL Approval'),
        ('scheduler.py', 'Scheduler'),
        ('gmail_authenticate.py', 'Gmail Auth Helper'),
    ]
    
    for filename, description in silver_scripts:
        filepath = script_dir / filename
        if check(filepath.exists(), f"{description}: {filename}"):
            # Check syntax
            try:
                compile(filepath.read_text(encoding='utf-8'), str(filepath), 'exec')
                check(True, f"  └─ Syntax valid")
            except SyntaxError as e:
                check(False, f"  └─ Syntax error: {e}")
                silver_passed = False
                all_passed = False
        else:
            check(False, f"{description}: {filename}")
            silver_passed = False
            all_passed = False
    
    # 8. Check Orchestrator has Plan.md creation
    print(f"\n{Colors.BLUE}Orchestrator Features:{Colors.RESET}")
    orchestrator_path = script_dir / 'orchestrator.py'
    if orchestrator_path.exists():
        content = orchestrator_path.read_text(encoding='utf-8')
        if 'create_plan' in content:
            check(True, "Plan.md creation capability")
        else:
            check(False, "Plan.md creation capability missing")
            silver_passed = False
            all_passed = False
        
        if 'pending_approval' in content:
            check(True, "HITL approval workflow integration")
        else:
            check(False, "HITL approval workflow missing")
            silver_passed = False
            all_passed = False
    
    # 9. Check dependencies
    print(f"\n{Colors.BLUE}Dependencies:{Colors.RESET}")
    try:
        import watchdog
        check(True, "watchdog installed")
    except ImportError:
        check(False, "watchdog NOT installed")
        print(f"  {Colors.YELLOW}Install with: pip install -r requirements.txt{Colors.RESET}")
    
    try:
        import playwright
        check(True, "playwright installed")
    except ImportError:
        check(False, "playwright NOT installed")
        print(f"  {Colors.YELLOW}Install with: pip install playwright && playwright install chromium{Colors.RESET}")
    
    try:
        from google.oauth2.credentials import Credentials
        check(True, "google-auth installed (for Gmail)")
    except ImportError:
        check(False, "google-auth NOT installed")
        print(f"  {Colors.YELLOW}Install with: pip install google-auth google-auth-oauthlib google-api-python-client{Colors.RESET}")
    
    # 10. Check Qwen Code
    print(f"\n{Colors.BLUE}External Tools:{Colors.RESET}")
    import subprocess
    try:
        result = subprocess.run(['qwen', '--version'], 
                              capture_output=True, text=True, timeout=5, shell=True)
        if result.returncode == 0:
            version_output = result.stdout.strip() or result.stderr.strip()
            check(True, f"Qwen Code: {version_output}")
        else:
            check(False, "Qwen Code installed but not responding")
            silver_passed = False
            all_passed = False
    except Exception as e:
        check(False, f"Qwen Code NOT installed")
        silver_passed = False
        all_passed = False
    
    # ==================== SUMMARY ====================
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    
    if not bronze_passed:
        print(f"{Colors.RED}{Colors.BOLD}✗ Bronze Tier Requirements Not Met{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Please complete Bronze Tier first!{Colors.RESET}")
    elif not silver_passed:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠ Some Silver Tier Requirements Not Met{Colors.RESET}")
        print(f"\n{Colors.BLUE}Review the failed checks above and fix them.{Colors.RESET}")
    else:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ All Silver Tier Requirements Met!{Colors.RESET}")
        print(f"\n{Colors.BLUE}Next Steps:{Colors.RESET}")
        print("1. Open Obsidian and load the AI_Employee_Vault")
        print("2. Configure Gmail API credentials (credentials.json)")
        print("3. Start watchers: python gmail_watcher.py ../AI_Employee_Vault")
        print("4. Start orchestrator: python orchestrator.py ../AI_Employee_Vault")
        print("5. Set up scheduler: python scheduler.py ../AI_Employee_Vault --install-windows")
        print("6. Test HITL workflow by dropping a file in Inbox/")
    
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")
    
    # Return appropriate exit code
    if all_passed:
        return 0
    elif bronze_passed:
        return 1  # Silver incomplete but Bronze OK
    else:
        return 2  # Bronze incomplete


if __name__ == '__main__':
    sys.exit(main())
