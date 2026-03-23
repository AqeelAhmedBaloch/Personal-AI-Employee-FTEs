# Personal AI Employee FTEs 🤖

> **Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.**

Build an **Autonomous AI Employee (Digital FTE)** that works 24/7 to manage your personal and business affairs using **Claude Code** + **Obsidian** + **Python Watchers**.

---

## 🎯 What is a Digital FTE?

A **Digital Full-Time Equivalent (FTE)** is an AI agent that replaces human employees:

| Feature | Human FTE | Digital FTE |
|---------|-----------|-------------|
| Availability | 40 hours/week | **168 hours/week (24/7)** |
| Monthly Cost | $4,000 – $8,000+ | **$500 – $2,000** |
| Ramp-up Time | 3 – 6 months | **Instant** |
| Cost per Task | ~$5.00 | **~$0.50** |
| Annual Hours | ~2,000 | **~8,760** |

**💡 85-90% cost savings** compared to hiring humans!

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL SOURCES                         │
│         Gmail │ WhatsApp │ LinkedIn │ File System            │
└────────────────┬────────────────┬───────────────────────────┘
                 │                │
                 ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│              PERCEPTION LAYER (Python Watchers)             │
│    Gmail Watcher │ WhatsApp Watcher │ Filesystem Watcher    │
└─────────────────┬─────────────────┬─────────────────────────┘
                  │                 │
                  ▼                 ▼
┌─────────────────────────────────────────────────────────────┐
│                    OBSIDIAN VAULT                           │
│  /Needs_Action → /Plans → /Pending_Approval → /Approved     │
│  Dashboard.md | Company_Handbook.md | Business_Goals.md     │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              REASONING LAYER (Claude Code)                  │
│                    Orchestrator + Qwen                      │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                 ACTION LAYER (MCP Servers)                  │
│         Email │ Browser │ Calendar │ Payments                │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| **The Brain** | Claude Code | Reasoning engine, task execution |
| **The Memory/GUI** | Obsidian | Dashboard, knowledge base (local Markdown) |
| **The Senses** | Python Watchers | Monitor Gmail, WhatsApp, filesystems 24/7 |
| **The Hands** | MCP Servers | External actions (email, browser, payments) |
| **Persistence** | Ralph Wiggum Loop | Keep agent working until task complete |

---

## 📁 Project Structure

```
Personal-AI-Employee-FTEs/
├── AI_Employee_Vault/          # Obsidian vault
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
├── scripts/                    # Python scripts
│   ├── base_watcher.py         # Base class for all watchers
│   ├── filesystem_watcher.py   # File system monitor
│   ├── gmail_watcher.py        # Gmail API monitor
│   ├── linkedin_watcher.py     # LinkedIn auto-poster
│   ├── orchestrator.py         # Main orchestration process
│   ├── hitl_approval.py        # Human-in-the-loop workflow
│   ├── scheduler.py            # Task scheduler
│   ├── gmail_authenticate.py   # Gmail OAuth setup
│   └── email_sender.py         # Email sending helper
├── .qwen/skills/               # Qwen Code agent skills
│   ├── browsing-with-playwright/
│   ├── email-watcher/
│   ├── whatsapp-watcher/
│   ├── linkedin-poster/
│   ├── email-sender/
│   ├── hitl-approval/
│   └── scheduler/
├── README.md                   # This file
├── QWEN.md                     # Project context
└── .gitignore                  # Git ignore rules
```

---

## 🚀 Quick Start

### Prerequisites

| Software | Version | Purpose |
|----------|---------|---------|
| [Claude Code](https://claude.com/product/claude-code) | Active subscription | Primary reasoning engine |
| [Obsidian](https://obsidian.md/download) | v1.10.6+ | Knowledge base & dashboard |
| [Python](https://www.python.org/downloads/) | 3.13+ | Sentinel scripts & orchestration |
| [Node.js](https://nodejs.org/) | v24+ LTS | MCP servers & automation |
| [GitHub Desktop](https://desktop.github.com/download/) | Latest | Version control |

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Personal-AI-Employee-FTEs
   ```

2. **Install Python dependencies:**
   ```bash
   cd scripts
   pip install -r requirements.txt
   ```

3. **Set up Gmail API (for email watching):**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a project and enable Gmail API
   - Download `credentials.json` to `scripts/` folder
   - Run authentication:
     ```bash
     python gmail_authenticate.py
     ```

4. **Open Obsidian vault:**
   - Open Obsidian
   - Click "Open folder as vault"
   - Select `AI_Employee_Vault/` folder

---

## 🎓 Hackathon Tiers

### 🥉 Bronze Tier (8-12 hours)

**Foundation - Minimum Viable Product**

- ✅ Obsidian vault with Dashboard.md, Company_Handbook.md, Business_Goals.md
- ✅ One working Watcher script (File System or Gmail)
- ✅ Claude Code reading/writing to vault
- ✅ Basic folder structure: `/Inbox`, `/Needs_Action`, `/Done`
- ✅ All AI functionality as Agent Skills

### 🥈 Silver Tier (20-30 hours)

**Functional Assistant**

- ✅ All Bronze requirements
- ✅ **2+ Watchers** (Gmail + LinkedIn + WhatsApp)
- ✅ Auto-post to LinkedIn for business updates
- ✅ Plan.md creation for multi-step tasks
- ✅ One MCP server for external actions
- ✅ Human-in-the-loop approval workflow
- ✅ Basic scheduling (daily briefings, weekly audits)

### 🥇 Gold Tier (40+ hours)

**Autonomous Employee**

- ✅ All Silver requirements
- ✅ Full cross-domain integration (Personal + Business)
- ✅ **Odoo Accounting Integration** via MCP
- ✅ Facebook/Instagram/Twitter integration
- ✅ Multiple MCP servers
- ✅ Weekly Business Audit with CEO Briefing
- ✅ Error recovery and graceful degradation
- ✅ Comprehensive audit logging
- ✅ Ralph Wiggum loop for autonomous tasks

### 💎 Platinum Tier (60+ hours)

**Production-Ready Cloud + Local**

- ✅ All Gold requirements
- ✅ **24/7 Cloud Deployment** (Oracle/AWS VM)
- ✅ Work-Zone Specialization (Cloud drafts, Local approves)
- ✅ Synced Vault via Git/Syncthing
- ✅ Odoo on Cloud VM with HTTPS + backups
- ✅ A2A (Agent-to-Agent) communication upgrade

---

## 📖 Usage

### Start All Watchers (Windows)

```bash
cd scripts
start-silver-tier.bat
```

### Manual Start (Individual Components)

**Terminal 1 - File System Watcher:**
```bash
cd scripts
python filesystem_watcher.py ../AI_Employee_Vault
```

**Terminal 2 - Gmail Watcher:**
```bash
python gmail_watcher.py ../AI_Employee_Vault
```

**Terminal 3 - LinkedIn Watcher:**
```bash
python linkedin_watcher.py ../AI_Employee_Vault
```

**Terminal 4 - Orchestrator:**
```bash
python orchestrator.py ../AI_Employee_Vault
```

### Testing the System

#### Test File System Watcher
1. Drop a file in `AI_Employee_Vault/Inbox/`
2. Wait 5 seconds
3. Check `Needs_Action/` for new action file
4. View `Dashboard.md` for status update

#### Test Gmail Watcher
1. Send yourself an email with subject "Test Invoice"
2. Wait 2 minutes (check interval)
3. Check `Needs_Action/` for new email file
4. View `Dashboard.md` - pending count should increase

#### Test HITL Approval
1. Create a test approval request in `Pending_Approval/`
2. Move file to `Approved/` folder
3. Watcher will execute the approved action

---

## 🔧 Available Agent Skills

| Skill | Description |
|-------|-------------|
| **browsing-with-playwright** | Browser automation for web scraping, form submission |
| **email-watcher** | Gmail monitoring with priority detection |
| **whatsapp-watcher** | WhatsApp message monitoring |
| **linkedin-poster** | Auto-post business updates to LinkedIn |
| **email-sender** | Send emails via Gmail API |
| **hitl-approval** | Human-in-the-loop workflow manager |
| **scheduler** | Daily briefings and weekly audits |

---

## 📝 Key Patterns

### 1. Watcher Architecture
Lightweight Python scripts run continuously, creating `.md` files in `/Needs_Action/` when events occur.

### 2. File-Based Handoff
Agents communicate by writing/reading Markdown files (no complex messaging system).

### 3. Human-in-the-Loop
Sensitive actions require approval:
```
/Pending_Approval/ → /Approved/ → Execute Action
                     → /Rejected/ → Skip Action
```

### 4. Ralph Wiggum Loop
Stop hook that keeps Claude working until multi-step tasks are complete.

---

## 📅 Research Meetings

**Weekly meetings every Wednesday at 10:00 PM PKT**

- **Zoom:** [Join Meeting](https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1)
- **Meeting ID:** 871 8870 7642
- **Passcode:** 744832
- **YouTube:** [@panaversity](https://www.youtube.com/@panaversity)

---

## 🔒 Security Notes

- Never commit `credentials.json` or `token.json` to Git (already in `.gitignore`)
- Store API credentials securely
- Use app-specific passwords if 2FA enabled
- Review MCP server permissions regularly
- Keep `.env` files out of version control

---

## 📚 Documentation

| File | Description |
|------|-------------|
| [`Personal AI Employee Hackathon 0_...md`](./Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md) | Complete architectural blueprint |
| [`QWEN.md`](./QWEN.md) | Project context and setup |
| [`SILVER_TIER_COMPLETE.md`](./SILVER_TIER_COMPLETE.md) | Silver tier verification |
| `.qwen/skills/*/SKILL.md` | Individual skill documentation |

---

## 🤝 Contributing

This is a hackathon project. Contributions welcome!

1. Fork the repository
2. Create a feature branch
3. Test your changes
4. Submit a pull request

---

## 📄 License

This project is part of the Personal AI Employee Hackathon 2026.

---

**Built with ❤️ using Claude Code + Obsidian + Python**

*Silver Tier Complete - March 2026*
