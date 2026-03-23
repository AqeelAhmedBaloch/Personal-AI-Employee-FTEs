---
name: scheduler
description: |
  Scheduler skill for running recurring tasks via cron (Linux/Mac) or 
  Task Scheduler (Windows). Supports daily briefings, weekly audits,
  and custom scheduled tasks.
---

# Scheduler

Schedule recurring tasks for your AI Employee.

## Overview

The scheduler enables time-based automation:
- Daily briefings at 8 AM
- Weekly audits every Monday
- Monthly reports on the 1st
- Custom scheduled tasks

## Setup

### Windows (Task Scheduler)

#### Option 1: Using the Helper Script

```bash
python scripts/scheduler.py ../AI_Employee_Vault --install-windows
```

#### Option 2: Manual Setup

1. Open Task Scheduler
2. Create Basic Task
3. Name: "AI Employee Daily Briefing"
4. Trigger: Daily at 8:00 AM
5. Action: Start a program
   - Program: `python.exe`
   - Arguments: `scripts\scheduler.py path\to\vault --task daily_briefing`
   - Start in: `D:\hackathon-0\Personal-AI-Employee-FTEs`

### Linux/Mac (cron)

#### Option 1: Using the Helper Script

```bash
python scripts/scheduler.py ~/AI_Employee_Vault --install-cron
```

#### Option 2: Manual Setup

```bash
# Edit crontab
crontab -e

# Add daily briefing at 8 AM
0 8 * * * /usr/bin/python3 /path/to/scripts/scheduler.py /path/to/vault --task daily_briefing

# Add weekly audit every Monday at 9 AM
0 9 * * 1 /usr/bin/python3 /path/to/scripts/scheduler.py /path/to/vault --task weekly_audit
```

## Scheduled Tasks

### daily_briefing

Generates a daily summary every morning:

```bash
python scheduler.py ../AI_Employee_Vault --task daily_briefing
```

Output: `Briefings/YYYY-MM-DD_Briefing.md`

### weekly_audit

Comprehensive weekly business audit:

```bash
python scheduler.py ../AI_Employee_Vault --task weekly_audit
```

Output: `Briefings/YYYY-MM-DD_Weekly_Audit.md`

### process_pending

Processes all pending items:

```bash
python scheduler.py ../AI_Employee_Vault --task process_pending
```

### cleanup_old_files

Moves old completed tasks to archive:

```bash
python scheduler.py ../AI_Employee_Vault --task cleanup_old_files --days 30
```

## Configuration

Create `scheduler_config.json`:

```json
{
  "daily_briefing": {
    "enabled": true,
    "time": "08:00",
    "timezone": "UTC"
  },
  "weekly_audit": {
    "enabled": true,
    "day": "monday",
    "time": "09:00"
  },
  "cleanup": {
    "enabled": true,
    "days_old": 30,
    "frequency": "weekly"
  }
}
```

## Task Output

### Daily Briefing Template

```markdown
---
generated: 2026-03-23T08:00:00Z
type: daily_briefing
---

# Daily Briefing - March 23, 2026

## Yesterday's Summary

- Tasks completed: 5
- Emails processed: 12
- Pending items: 2

## Today's Priorities

1. Follow up with Client A
2. Review invoice requests
3. Post LinkedIn update

## Alerts

- Payment over $500 requires approval
```

### Weekly Audit Template

```markdown
---
generated: 2026-03-23T09:00:00Z
type: weekly_audit
period: 2026-03-17 to 2026-03-23
---

# Weekly Audit

## Revenue

- This week: $2,450
- MTD: $4,500
- Trend: On track

## Completed Tasks

- [x] Client invoices sent
- [x] Social media scheduled
- [x] Weekly reports generated

## Bottlenecks

| Task | Delay |
|------|-------|
| Client B proposal | +3 days |

## Recommendations

1. Cancel unused Notion subscription
2. Follow up on overdue invoices
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Task not running | Check scheduler logs |
| Python not found | Use full path to python.exe |
| Permission denied | Run as administrator |
| Wrong timezone | Update config timezone |

## Logs

Scheduler logs are written to:
- `Logs/scheduler.log`
- `Logs/YYYY-MM-DD.json`

## Best Practices

1. Start with daily briefings only
2. Add weekly audit after testing
3. Review scheduled task logs weekly
4. Adjust times based on your timezone
5. Keep tasks idempotent (safe to re-run)
