---
name: email-sender
description: |
  Email sender skill using Gmail API. Sends emails with human approval workflow.
  Supports attachments, HTML content, and scheduled sending.
  All outgoing emails require approval before sending.
---

# Email Sender (Gmail)

Send emails via Gmail API with human-in-the-loop approval.

## Setup Requirements

### 1. Enable Gmail API

Same setup as Email Watcher:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Gmail API
3. Download `credentials.json`

### 2. Install Dependencies

```bash
pip install google-auth google-auth-oauthlib google-api-python-client
```

### 3. Update Authentication Scope

For sending emails, you need full Gmail scope:

```bash
# Delete old token.json if exists
rm token.json

# Update scope in script to:
SCOPES = ['https://www.googleapis.com/auth/gmail']

# Re-authenticate
python scripts/gmail_authenticate.py
```

## Usage

### Send Email (with Approval)

```bash
python scripts/email_sender.py ../AI_Employee_Vault \
  --to "client@example.com" \
  --subject "Invoice #123" \
  --body "Please find attached your invoice..."
```

### Send with Attachment

```bash
python scripts/email_sender.py ../AI_Employee_Vault \
  --to "client@example.com" \
  --subject "Invoice #123" \
  --body "Please find attached..." \
  --attachment "/path/to/invoice.pdf"
```

### Execute Approved Emails

```bash
python scripts/email_sender.py ../AI_Employee_Vault --execute
```

## Features

- Human-in-the-loop approval workflow
- Support for attachments
- HTML email support
- CC/BCC support
- Reply-to configuration
- Email logging and tracking

## Approval Workflow

1. AI creates email draft → `/Pending_Approval/EMAIL_SEND_*.md`
2. Human reviews content → Moves to `/Approved/`
3. Email sender executes → Sends via Gmail API
4. Result logged → Moves to `/Done/`

## Example Approval File

```markdown
---
type: email_send
action: send_email
to: client@example.com
subject: Invoice #123
body: |
  Dear Client,
  
  Please find attached your invoice...
attachment: /path/to/invoice.pdf
created: 2026-03-23T15:00:00
status: pending_approval
---

# Email for Approval

## Details

- **To:** client@example.com
- **Subject:** Invoice #123
- **Attachment:** invoice.pdf

## Content

Dear Client,

Please find attached your invoice for services rendered.

Best regards,
Your Company

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder with comments.
```

## Security Rules

| Rule | Description |
|------|-------------|
| Max recipients | 10 per email (avoid bulk) |
| Approval required | All outgoing emails |
| Attachment limit | 10MB per email |
| Rate limit | Max 20 emails/hour |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Authentication failed | Re-authenticate with full Gmail scope |
| Attachment too large | Use Google Drive link instead |
| Rate limited | Wait and reduce sending frequency |
| Token expired | Re-run authentication |
