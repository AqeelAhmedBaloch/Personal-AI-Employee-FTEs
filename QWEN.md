# Personal AI Employee FTEs - Project Context

## Project Overview

This is a **hackathon project** for building **Autonomous AI Employees (Digital FTEs)** - AI agents that work 24/7 to manage personal and business affairs. The project uses **Qwen Code** as the reasoning engine and **Obsidian** (local Markdown) as the dashboard/memory system.

**Core Concept:** A "Digital Full-Time Equivalent" (FTE) that costs ~$500-2000/month vs $4000-8000/month for a human, works 168 hours/week (vs 40), and provides 85-90% cost savings per task.

---

## ✅ Bronze Tier - COMPLETED

The Bronze Tier foundation has been fully implemented:

| Requirement | Status | Location |
|-------------|--------|----------|
| Obsidian vault | ✅ | `AI_Employee_Vault/` |
| Dashboard.md | ✅ | `AI_Employee_Vault/Dashboard.md` |
| Company_Handbook.md | ✅ | `AI_Employee_Vault/Company_Handbook.md` |
| Business_Goals.md | ✅ | `AI_Employee_Vault/Business_Goals.md` |
| File System Watcher | ✅ | `scripts/filesystem_watcher.py` |
| Base Watcher Template | ✅ | `scripts/base_watcher.py` |
| Orchestrator | ✅ | `scripts/orchestrator.py` |
| Folder Structure | ✅ | All 11 folders created |
| Qwen Integration | ✅ | Via orchestrator.py |

---

## ✅ Silver Tier - COMPLETED

The Silver Tier functional assistant has been fully implemented:

| Requirement | Status | Location |
|-------------|--------|----------|
| Gmail Watcher | ✅ | `scripts/gmail_watcher.py` |
| LinkedIn Watcher | ✅ | `scripts/linkedin_watcher.py` |
| HITL Approval | ✅ | `scripts/hitl_approval.py` |
| Scheduler | ✅ | `scripts/scheduler.py` |
| Plan.md Creation | ✅ | In orchestrator.py |
| Agent Skills (7) | ✅ | `.qwen/skills/` |
| Gmail Auth | ✅ | `scripts/gmail_authenticate.py` |

**Verification:** Run `python scripts/verify_silver.py` to confirm all requirements.

## Architecture

### The Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **The Brain** | Claude Code | Reasoning engine, task execution |
| **The Memory/GUI** | Obsidian | Dashboard, knowledge base (local Markdown) |
| **The Senses** | Python Watchers | Monitor Gmail, WhatsApp, filesystems |
| **The Hands** | MCP Servers | External actions (email, browser automation, payments) |
| **Persistence** | Ralph Wiggum Loop | Keep agent working until task complete |

### Key Patterns

1. **Watcher Architecture:** Lightweight Python scripts run continuously, monitoring inputs and creating `.md` files in `/Needs_Action` folder
2. **File-Based Handoff:** Agents communicate by writing/reading Markdown files (no complex messaging)
3. **Human-in-the-Loop:** Sensitive actions require approval via file movement (`/Pending_Approval` → `/Approved`)
4. **Ralph Wiggum Loop:** Stop hook that keeps Claude iterating until multi-step tasks are complete

## Directory Structure

```
Personal-AI-Employee-FTEs/
├── AI_Employee_Vault/          # Obsidian vault (Bronze Tier)
│   ├── Dashboard.md            # Real-time status dashboard
│   ├── Company_Handbook.md     # Rules of engagement
│   ├── Business_Goals.md       # Objectives and metrics
│   ├── Inbox/                  # Drop zone for files
│   ├── Needs_Action/           # Pending items requiring action
│   ├── Plans/                  # Multi-step task plans
│   ├── Done/                   # Completed tasks
│   ├── Approved/               # Approved actions
│   ├── Pending_Approval/       # Awaiting human approval
│   ├── Rejected/               # Rejected actions
│   ├── Logs/                   # Activity logs
│   ├── Accounting/             # Financial records
│   ├── Briefings/              # CEO briefings
│   └── Invoices/               # Invoice files
├── scripts/
│   ├── base_watcher.py         # Base class for all watchers
│   ├── filesystem_watcher.py   # File system monitor (Bronze)
│   ├── orchestrator.py         # Main orchestration process
│   ├── verify_bronze.py        # Bronze tier verification
│   ├── requirements.txt        # Python dependencies
│   └── start-ai-employee.bat   # Windows quick start
├── README.md                   # Setup and usage guide
├── QWEN.md                     # This context file
└── Personal AI Employee Hackathon 0_...md  # Full hackathon guide
```

## Available Skills

### browsing-with-playwright

Browser automation via Playwright MCP server for web scraping, form submission, UI testing.

**Start Server:**
```bash
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh
# Or: npx @playwright/mcp@latest --port 8808 --shared-browser-context &
```

**Stop Server:**
```bash
bash .qwen/skills/browsing-with-playwright/scripts/stop-server.sh
```

**Verify:**
```bash
python .qwen/skills/browsing-with-playwright/scripts/verify.py
```

**Key Tools Available:**
- `browser_navigate`, `browser_snapshot`, `browser_click`, `browser_type`
- `browser_fill_form`, `browser_select_option`, `browser_take_screenshot`
- `browser_evaluate`, `browser_run_code`, `browser_wait_for`

See `SKILL.md` for detailed usage examples.

## Hackathon Tiers

| Tier | Time | Deliverables |
|------|------|--------------|
| **Bronze** | 8-12 hrs | Obsidian vault, 1 Watcher, basic folder structure |
| **Silver** | 20-30 hrs | 2+ Watchers, MCP server, HITL workflow, scheduling |
| **Gold** | 40+ hrs | Full integration, Odoo accounting, social media, weekly audit |
| **Platinum** | 60+ hrs | Cloud deployment, domain specialization, A2A upgrade |

## Key Files

| File | Purpose |
|------|---------|
| `Personal AI Employee Hackathon 0_...md` | Complete architectural blueprint, templates, code examples |
| `skills-lock.json` | Tracks installed Qwen skills and their versions |
| `.qwen/skills/browsing-with-playwright/SKILL.md` | Browser automation skill documentation |
| `.qwen/skills/browsing-with-playwright/scripts/mcp-client.py` | Universal MCP client for any MCP server |

## Development Conventions

1. **All AI functionality as Agent Skills:** Use the [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) pattern
2. **Local-first:** Keep data in local Obsidian vault, sync via Git
3. **File-based communication:** Agents write `.md` files to signal work needed
4. **Human approval for sensitive actions:** Never auto-execute payments, sends without approval

## Prerequisites (from documentation)

- **Claude Code:** Active subscription
- **Obsidian:** v1.10.6+
- **Python:** 3.13+
- **Node.js:** v24+ LTS
- **GitHub Desktop:** For version control

## Usage Patterns

### Quick Start (Windows)

```bash
# Run the quick start script
cd scripts
start-ai-employee.bat
```

### Manual Start

```bash
# Terminal 1: Start File System Watcher
cd scripts
python filesystem_watcher.py ../AI_Employee_Vault

# Terminal 2: Start Orchestrator
python orchestrator.py ../AI_Employee_Vault
```

### Testing the System

1. **Drop a file** in `AI_Employee_Vault/Inbox/`
2. **Watcher detects** it and creates action file in `Needs_Action/`
3. **Orchestrator triggers** Claude Code to process
4. **Claude creates** a plan or takes action
5. **Check Dashboard.md** for status updates

### Creating a Watcher Task
1. Watcher detects event (email, WhatsApp message, file drop)
2. Creates `.md` file in `/Needs_Action/` with metadata header
3. Claude Code reads folder, creates `Plan.md` with checkboxes
4. Ralph Wiggum loop keeps Claude working until complete
5. Move file to `/Done` when finished

### Human-in-the-Loop Approval
1. Claude creates `/Pending_Approval/ACTION_Description.md`
2. User reviews and moves file to `/Approved` or `/Rejected`
3. Orchestrator detects approval and executes MCP action

### Browser Automation Workflow
1. Start Playwright MCP server
2. Use `mcp-client.py` to call browser tools
3. Navigate → Snapshot → Interact → Screenshot
4. Stop server when complete

## Research Meetings

Weekly meetings every Wednesday at 10:00 PM PKT on Zoom for teaching and collaboration.
