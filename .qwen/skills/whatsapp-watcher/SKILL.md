---
name: whatsapp-watcher
description: |
  WhatsApp Web watcher that monitors messages for keywords.
  Uses Playwright to automate WhatsApp Web and detect important messages.
  Creates action files in /Needs_Action folder when keywords detected.
---

# WhatsApp Watcher

Monitor WhatsApp Web for important messages using browser automation.

## ⚠️ Important Notice

This skill uses WhatsApp Web automation. Be aware of:
- WhatsApp's Terms of Service
- Rate limiting to avoid account bans
- Never use for spam or bulk messaging

## Setup Requirements

### 1. Install Dependencies

```bash
pip install playwright
playwright install chromium
```

### 2. First-Time WhatsApp Web Login

```bash
python scripts/whatsapp_login.py
```

This will open a browser for you to scan QR code and login.

## Usage

### Start WhatsApp Watcher

```bash
cd scripts
python whatsapp_watcher.py ../AI_Employee_Vault
```

### Configuration

```python
# In whatsapp_watcher.py
watcher = WhatsAppWatcher(
    vault_path='../AI_Employee_Vault',
    session_path='./whatsapp_session',
    check_interval=30,  # Check every 30 seconds
    keywords=['urgent', 'asap', 'invoice', 'payment', 'help']
)
```

## Features

- Monitors WhatsApp Web for unread messages
- Filters messages by keywords
- Creates action files for important messages
- Persistent browser session (stays logged in)
- Updates Dashboard.md with pending count

## Default Keywords

Messages containing these keywords trigger action files:
- urgent
- asap
- invoice
- payment
- help
- meeting
- deadline

## Action File Format

```markdown
---
type: whatsapp
from: +1234567890
chat: John Doe
received: 2026-03-23T10:30:00
priority: high
status: pending
---

## Message Content

{message text}

## Suggested Actions

- [ ] Reply on WhatsApp
- [ ] Create invoice if requested
- [ ] Schedule meeting if needed
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| QR code expired | Re-run whatsapp_login.py |
| No messages detected | Check WhatsApp Web is open |
| Session expired | Delete session folder and re-login |
| Browser crashes | Reduce check_interval |

## Security Notes

- Session data stored locally
- Never commit session files to git
- Use dedicated business number for automation
- Monitor for unusual account activity

## Integration with Orchestrator

1. Watcher detects keyword message → Creates action file
2. Orchestrator reads action file → Triggers Qwen Code
3. Qwen processes message → Creates reply draft
4. Human approves reply → Sent via WhatsApp MCP
5. Action moved to /Done when complete
