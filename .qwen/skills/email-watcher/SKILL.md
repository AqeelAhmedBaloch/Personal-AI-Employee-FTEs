---
name: email-watcher
description: |
  Gmail watcher that monitors your inbox for new important emails.
  Creates action files in /Needs_Action folder when new emails arrive.
  Uses Gmail API for real-time email monitoring.
---

# Email Watcher (Gmail)

Monitor Gmail inbox and create action files for new important emails.

## Setup Requirements

### 1. Enable Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download `credentials.json`

### 2. Install Dependencies

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 3. Authenticate First Time

```bash
python scripts/gmail_authenticate.py
```

This will create `token.json` for future authentication.

## Usage

### Start Email Watcher

```bash
cd scripts
python gmail_watcher.py ../AI_Employee_Vault
```

### Configuration

```python
# In gmail_watcher.py
watcher = GmailWatcher(
    vault_path='../AI_Employee_Vault',
    credentials_path='credentials.json',
    check_interval=120  # Check every 2 minutes
)
```

## Features

- Monitors unread and important emails
- Creates action files with email metadata
- Tracks processed email IDs to avoid duplicates
- Logs all activity to /Logs folder
- Updates Dashboard.md with pending count

## Action File Format

```markdown
---
type: email
from: client@example.com
subject: Invoice Request
received: 2026-03-23T10:30:00
priority: high
status: pending
---

## Email Content

{email snippet}

## Suggested Actions

- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing
```

## Keywords for Priority

Emails containing these keywords are marked as high priority:
- urgent
- asap
- invoice
- payment
- meeting
- deadline

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Authentication failed | Re-run `gmail_authenticate.py` |
| No emails detected | Check Gmail API is enabled |
| Token expired | Delete `token.json` and re-authenticate |
| Rate limit | Increase check_interval |

## Security Notes

- Never commit `credentials.json` or `token.json` to git
- Store credentials in secure location
- Use app-specific passwords if 2FA enabled
- Review Gmail API permissions regularly

## Example: Full Setup

```bash
# 1. Install dependencies
pip install google-auth google-auth-oauthlib google-api-python-client

# 2. Download credentials.json from Google Cloud Console
# Save to scripts/credentials.json

# 3. Authenticate
cd scripts
python gmail_authenticate.py

# 4. Start watcher
python gmail_watcher.py ../AI_Employee_Vault
```

## Integration with Orchestrator

The Email Watcher works with the Orchestrator:

1. Watcher detects new email → Creates action file
2. Orchestrator reads action file → Triggers Qwen Code
3. Qwen processes email → Creates reply or plan
4. Action moved to /Done when complete
