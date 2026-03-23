---
name: linkedin-poster
description: |
  LinkedIn automation skill for posting business updates to generate sales.
  Uses Playwright to automate LinkedIn posting with human approval workflow.
  Creates scheduled posts and tracks engagement.
---

# LinkedIn Poster

Automate LinkedIn posts for business promotion and lead generation.

## ⚠️ Important Notice

This skill uses LinkedIn automation. Be aware of:
- LinkedIn's Terms of Service
- Rate limiting (max 3-5 posts per day recommended)
- Never use for spam or excessive posting
- Always require human approval before posting

## Setup Requirements

### 1. Install Dependencies

```bash
pip install playwright
playwright install chromium
```

### 2. First-Time LinkedIn Login

```bash
python scripts/linkedin_login.py
```

This will open a browser for you to login to LinkedIn.

## Usage

### Post to LinkedIn (with Approval)

```bash
cd scripts
python linkedin_poster.py ../AI_Employee_Vault "Your post content here"
```

### Schedule a Post

```bash
python linkedin_poster.py ../AI_Employee_Vault --schedule "2026-03-24T10:00:00" --content "Post content"
```

### Create Post from Template

```bash
python linkedin_poster.py ../AI_Employee_Vault --template business_update
```

## Features

- Create and schedule LinkedIn posts
- Human-in-the-loop approval workflow
- Post templates for common business updates
- Track post engagement
- Auto-generate posts from business milestones

## Post Templates

### business_update
```
🚀 Business Update

We're excited to share that [achievement]!

Our team has been working hard to [description].

#BusinessUpdate #Growth #Success
```

### service_promotion
```
💼 Now Offering: [Service Name]

Looking for [solution]? We can help!

✅ [Benefit 1]
✅ [Benefit 2]
✅ [Benefit 3]

DM us to learn more!

#Services #Business #Solutions
```

### client_success
```
🎉 Client Success Story

We helped [client] achieve [result]!

"Testimonial from client about the experience."

Ready to get similar results? Let's talk!

#ClientSuccess #Testimonial #Results
```

## Approval Workflow

1. AI creates post draft → `/Pending_Approval/LINKEDIN_POST_*.md`
2. Human reviews content → Moves to `/Approved/`
3. Poster executes → Posts to LinkedIn
4. Result logged → Moves to `/Done/`

## Example Approval File

```markdown
---
type: linkedin_post
content: |
  🚀 Exciting news!
  
  We just completed a major project...
  
  #Business #Growth
scheduled_time: 2026-03-24T10:00:00
status: pending_approval
created: 2026-03-23T15:00:00
---

# LinkedIn Post for Approval

## Content

{post content}

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder with comments.
```

## Best Practices

- Post during business hours (9 AM - 5 PM)
- Use 3-5 relevant hashtags
- Include engaging visuals when possible
- Respond to comments within 24 hours
- Mix content types (updates, tips, success stories)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Login failed | Re-run linkedin_login.py |
| Post not appearing | Check LinkedIn session |
| Rate limited | Wait 24 hours before next post |
| Session expired | Delete session folder and re-login |

## Security Notes

- Session data stored locally
- Never commit session files to git
- Always use approval workflow
- Monitor account for unusual activity
