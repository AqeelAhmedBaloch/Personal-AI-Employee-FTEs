# Silver Tier Setup Guide

## Overview

Silver Tier builds on Bronze Tier with:
- **Gmail Watcher** - Monitor emails in real-time
- **LinkedIn Watcher** - Auto-post business updates
- **HITL Approval** - Human-in-the-loop workflow
- **Scheduler** - Automated daily/weekly tasks
- **Qwen Code Integration** - AI reasoning engine

## Prerequisites

✅ Bronze Tier completed
✅ Python 3.13+
✅ Qwen Code installed
✅ Gmail API credentials (credentials.json)

---

## Step 1: Install Dependencies

```bash
cd scripts
pip install -r requirements.txt
```

### Requirements include:
- `watchdog` - File system monitoring
- `google-auth`, `google-api-python-client` - Gmail API
- `playwright` - Browser automation (LinkedIn)

---

## Step 2: Authenticate Gmail

Your `credentials.json` is already in place. Now authenticate:

```bash
cd scripts
python gmail_authenticate.py
```

**What happens:**
1. Browser opens automatically
2. Sign in to your Google account
3. Click "Allow" for permissions
4. Token saved to `token.json`

**Verify authentication:**
```bash
python gmail_authenticate.py --test
```

Expected output:
```
✓ Gmail API access confirmed!
  Email: your-email@gmail.com
  Messages Total: 1234
```

---

## Step 3: Install Playwright (for LinkedIn)

```bash
pip install playwright
playwright install chromium
```

---

## Step 4: Start Silver Tier

### Option A: Quick Start (Windows)

```bash
cd scripts
start-silver-tier.bat
```

This starts all services:
- File System Watcher
- Gmail Watcher
- LinkedIn Watcher
- Orchestrator

### Option B: Manual Start

**Terminal 1 - File System Watcher:**
```bash
cd scripts
python filesystem_watcher.py ../AI_Employee_Vault
```

**Terminal 2 - Gmail Watcher:**
```bash
cd scripts
python gmail_watcher.py ../AI_Employee_Vault
```

**Terminal 3 - LinkedIn Watcher:**
```bash
cd scripts
python linkedin_watcher.py ../AI_Employee_Vault
```

**Terminal 4 - Orchestrator:**
```bash
cd scripts
python orchestrator.py ../AI_Employee_Vault
```

---

## Step 5: Test the System

### Test Gmail Watcher

1. **Send yourself an email** with subject "Test Invoice"
2. **Wait 2 minutes** (Gmail Watcher check interval)
3. **Check** `AI_Employee_Vault/Needs_Action/` for new email action file
4. **View Dashboard.md** - pending count should increase

### Test File System Watcher

1. **Drop a file** in `AI_Employee_Vault/Inbox/`
2. **Wait 5 seconds**
3. **Check** `Needs_Action/` for FILE_DROP_*.md file

### Test LinkedIn Watcher

1. **Create a test post:**
   ```bash
   python linkedin_watcher.py ../AI_Employee_Vault
   ```

2. **Check** `AI_Employee_Vault/Pending_Approval/` for new post

3. **Approve the post:**
   - Move the file from `Pending_Approval/` to `Approved/`

4. **LinkedIn Watcher will:**
   - Open browser
   - Navigate to LinkedIn
   - Post the content
   - Move file to `Done/`

---

## Step 6: Configure Scheduler (Optional)

### Windows Task Scheduler

**Daily Briefing at 8 AM:**
```bash
python scheduler.py ../AI_Employee_Vault --install-windows
```

Follow the displayed commands to create scheduled tasks.

### Manual Setup

1. Open **Task Scheduler** (taskschd.msc)
2. Create Basic Task
3. Name: "AI Employee Daily Briefing"
4. Trigger: Daily at 8:00 AM
5. Action: Start a program
   - Program: `python.exe`
   - Arguments: `scripts\scheduler.py path\to\vault --task daily_briefing`

---

## Folder Structure

```
AI_Employee_Vault/
├── Dashboard.md              # Real-time status
├── Company_Handbook.md       # Rules of engagement
├── Business_Goals.md         # Your objectives
├── Inbox/                    # Drop files here
├── Needs_Action/             # Pending items (auto-created)
├── Plans/                    # Multi-step task plans
├── Pending_Approval/         # Awaiting your approval
├── Approved/                 # Approved, ready to execute
├── Done/                     # Completed tasks
├── Rejected/                 # Rejected items
├── Logs/                     # Activity logs
└── Briefings/                # Daily/Weekly reports
```

---

## Troubleshooting

### Gmail Watcher Not Working

**Problem:** No emails detected

**Solutions:**
1. Check token exists: `dir token.json`
2. Re-authenticate: `python gmail_authenticate.py`
3. Check Gmail API enabled in Google Cloud Console
4. Verify credentials.json is valid

### LinkedIn Watcher Not Posting

**Problem:** Browser opens but doesn't post

**Solutions:**
1. Login to LinkedIn manually first in the browser
2. Check session folder exists
3. Increase check_interval in linkedin_watcher.py
4. Review logs for specific errors

### Orchestrator Not Processing

**Problem:** Files stay in Needs_Action

**Solutions:**
1. Check orchestrator.log for errors
2. Verify Qwen Code is installed: `qwen --version`
3. Restart orchestrator process
4. Check file permissions in vault

---

## Silver Tier Verification

Run the verification script:

```bash
python verify_silver.py
```

Expected output:
```
✓ All Silver Tier Requirements Met!
```

---

## Daily Workflow

### Morning (8 AM)
1. Open Obsidian vault
2. Check Dashboard.md
3. Review Daily Briefing in Briefings/
4. Process any Pending_Approval items

### During Day
- Gmail Watcher monitors emails
- File System Watcher monitors Inbox
- Drop files for processing anytime

### Evening
- Review completed tasks in Done/
- Check Logs for activity summary
- Plan next day's priorities

---

## Next Steps (Gold Tier)

To upgrade to Gold Tier:
1. Add WhatsApp Watcher
2. Integrate Odoo Accounting
3. Weekly CEO Briefing automation
4. Multiple MCP servers
5. Error recovery system

---

## Support

- **Documentation:** See `Personal AI Employee Hackathon 0_...md`
- **Weekly Meetings:** Wednesdays 10:00 PM PKT
- **Zoom:** Link in hackathon document

---

*Silver Tier - Functional Assistant*
*Built with Qwen Code + Obsidian + Python*
