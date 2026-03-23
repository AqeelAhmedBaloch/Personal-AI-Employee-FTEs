---
name: hitl-approval
description: |
  Human-in-the-Loop (HITL) approval workflow for sensitive actions.
  Manages approval requests in /Pending_Approval folder.
  Supports auto-expiry, notifications, and audit logging.
---

# Human-in-the-Loop (HITL) Approval

Approval workflow for sensitive actions requiring human review.

## Overview

The HITL system ensures that sensitive actions (payments, emails, posts) 
require human approval before execution.

## Folder Structure

```
AI_Employee_Vault/
├── Pending_Approval/     # Awaiting human review
├── Approved/             # Approved, ready to execute
├── Rejected/             # Rejected with comments
└── Done/                 # Executed and completed
```

## Approval Workflow

### Step 1: AI Creates Approval Request

```markdown
---
type: approval_request
action: payment
amount: 500.00
recipient: Client A
created: 2026-03-23T10:00:00
expires: 2026-03-24T10:00:00
status: pending
---

# Payment Approval Request

## Details
- Amount: $500.00
- To: Client A
- Reason: Invoice #1234

## To Approve
Move to /Approved folder.

## To Reject
Move to /Rejected folder with comments.
```

### Step 2: Human Reviews

1. Open Obsidian vault
2. Navigate to `Pending_Approval/`
3. Review the request details
4. **Approve:** Move file to `/Approved/`
5. **Reject:** Move file to `/Rejected/` with comment

### Step 3: System Executes

1. Orchestrator detects file in `/Approved/`
2. Executes the approved action
3. Moves file to `/Done/`
4. Logs the action

## Approval Types

| Type | Auto-Approve Threshold | Always Requires Approval |
|------|----------------------|-------------------------|
| Payment | < $50 (recurring) | > $50 or new recipient |
| Email | - | All outgoing emails |
| Social Post | - | All posts |
| File Delete | - | All deletions |
| API Call | Read-only | Write operations |

## Expiry Handling

Approval requests expire after 24 hours by default:

```python
# In approval request frontmatter
expires: 2026-03-24T10:00:00
status: expired  # Auto-set after expiry
```

Expired requests are:
1. Moved to `/Rejected/` with expiry note
2. Logged as expired
3. AI notified to recreate if still needed

## Notification Options

### File-based (Default)
- Human checks `Pending_Approval/` folder

### Email Notification (Optional)
```python
notify_via_email: true
notification_email: human@example.com
```

### Desktop Notification (Optional)
```python
notify_desktop: true
```

## Audit Logging

All approval actions are logged:

```json
{
  "timestamp": "2026-03-23T10:30:00",
  "action_type": "approval_granted",
  "actor": "human_user",
  "request_type": "payment",
  "request_id": "PAYMENT_20260323_100000",
  "decision": "approved"
}
```

## Usage Examples

### Create Approval Request

```python
from hitl_approval import create_approval_request

filepath = create_approval_request(
    vault_path='../AI_Employee_Vault',
    action_type='payment',
    details={
        'amount': 500.00,
        'recipient': 'Client A',
        'reason': 'Invoice #1234'
    },
    expires_in_hours=24
)
```

### Check for Approved Items

```bash
python scripts/hitl_approval.py ../AI_Employee_Vault --check-approved
```

### Process Expired Requests

```bash
python scripts/hitl_approval.py ../AI_Employee_Vault --process-expired
```

## Security Rules

1. **Never auto-approve payments** to new recipients
2. **Always require approval** for deletions
3. **Log all decisions** with timestamps
4. **Expire stale requests** after 24 hours
5. **Notify human** for high-value actions

## Best Practices

- Set appropriate expiry times (not too short, not too long)
- Include clear action details in approval requests
- Add context for why action is needed
- Provide reject reason when declining
- Review approval logs weekly
