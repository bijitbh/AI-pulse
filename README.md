# ⚡ AI Pulse

A static website displaying **top AI news across 6 curated sections**, automatically selected and summarised by Claude (Anthropic). The site refreshes every 15 days via a scheduled GitHub Actions workflow and is hosted on GitHub Pages.

> **Idea by Bijit Bhattacherjee, curated by Claude**

## Live Site

> `https://bijitbh.github.io/ai-pulse/`

---

## What It Does

- Fetches articles from **curated RSS feeds** across 6 topic sections
- Sends candidate articles to **Claude (claude-sonnet-4-6)** which selects and ranks the top 5 per section by impact, significance, and recency
- For each story, Claude generates:
  - A 2–3 sentence preview for the homepage card
  - A 10–11 sentence detailed summary on the section page
  - 3–5 impact takeaways as bullet points
- Outputs a multi-page static site (`index.html` + 6 section detail pages) with a dark-mode design, served via GitHub Pages

---

## Sections

| # | Section | Focus |
|---|---|---|
| 1 | 🏦 **AI in Finance** | Wholesale banking, capital markets, trading, treasury, major bank AI adoption (JPMC, Goldman, HSBC, etc.) |
| 2 | ⚙️ **Engineering Intelligence** | AI tools, frameworks, MLOps, and developer productivity |
| 3 | 🛡️ **AI Governance & Safety** | EU AI Act, US regulation, global policy, safety, privacy |
| 4 | 🔥 **Trending in AI** | The most significant and widely discussed AI stories right now |
| 5 | 🤖 **GitHub Copilot** | Copilot features, updates, and AI coding assistant news |
| 6 | 💼 **Microsoft 365 Copilot** | M365 Copilot updates across Word, Excel, Teams, Outlook |

---

## News Sources

### 🏦 AI in Finance
FinExtra, American Banker, PYMNTS AI, Reuters Business, The Banker, Waters Technology, Global Finance, Risk.net

### ⚙️ Engineering Intelligence
ArXiv cs.AI, Towards Data Science, InfoQ, Stack Overflow Blog, Dev.to AI

### 🛡️ AI Governance & Safety
IAPP, Future of Life Institute, EFF, MIT Technology Review, AlgorithmWatch, Access Now, The Verge AI

### 🔥 Trending in AI
TechCrunch AI, MIT Technology Review, The Verge AI, VentureBeat AI, Wired AI, The Register AI

### 🤖 GitHub Copilot
GitHub Blog, GitHub Changelog, VS Code Blog, The Verge AI, TechCrunch AI

### 💼 Microsoft 365 Copilot
Microsoft 365 Blog, Windows Blog, VentureBeat AI, TechCrunch AI

---

## Project Structure

```
ai-pulse/
├── index.html                      # Generated homepage (committed by the workflow)
├── pages/
│   ├── finance.html                # AI in Finance detail page
│   ├── engineering.html            # Engineering Intelligence detail page
│   ├── governance.html             # AI Governance & Safety detail page
│   ├── trending.html               # Trending in AI detail page
│   ├── github-copilot.html         # GitHub Copilot detail page
│   └── m365-copilot.html           # Microsoft 365 Copilot detail page
├── requirements.txt                # Python dependencies (anthropic, feedparser)
├── scripts/
│   ├── generate_news.py            # Fetches RSS → calls Claude → writes all HTML
│   ├── template_home.html          # Homepage template
│   └── template_section.html       # Section detail page template
└── .github/
    └── workflows/
        └── refresh.yml             # Scheduled GitHub Actions workflow
```

---

## How It Works

```
┌────────────────────────────────────────────────────────┐
│  GitHub Actions (cron: 1st & 16th of each month)        │
│                                                          │
│  For each of the 6 sections:                             │
│    1. Fetch up to 10 articles per RSS feed               │
│    2. Send all candidate articles to Claude API          │
│    3. Claude returns top 5 as structured JSON            │
│       (title, source, summary, short_summary, takeaways) │
│    4. Render section detail page  (pages/*.html)         │
│                                                          │
│  5. Render homepage (index.html) with all 6 section cards│
│  6. Commit index.html + pages/ to main                   │
│  7. GitHub Pages serves updated site                     │
└────────────────────────────────────────────────────────┘
```

---

## Schedule

The workflow runs automatically at **6:00 AM UTC** on the **1st and 16th of every month** (approximately every 15 days).

You can also trigger it manually at any time:
1. Go to the **Actions** tab in this repository
2. Click **Refresh AI Pulse**
3. Click **Run workflow**

---

## Setup Guide

### 1. Fork / Clone the repository

```bash
git clone https://github.com/bijitbh/ai-pulse.git
cd ai-pulse
```

### 2. Get a Claude API key

- Sign up at [console.anthropic.com](https://console.anthropic.com)
- Create an API key under **API Keys**

### 3. Add the GitHub Actions secret

Go to **Settings → Secrets and variables → Actions → New repository secret**:

| Secret name | Value |
|---|---|
| `ANTHROPIC_API_KEY` | Your Claude API key (`sk-ant-...`) |

### 4. Enable GitHub Pages

- Go to **Settings → Pages**
- Source: **Deploy from a branch**
- Branch: `main`, folder: `/ (root)`
- Save

### 5. Run the workflow for the first time

- Go to **Actions → Refresh AI Pulse → Run workflow**
- Wait ~2–3 minutes for all 6 Claude API calls to complete
- Visit your Pages URL to see the stories

---

## Running Locally

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python scripts/generate_news.py
open index.html
```

---

## Tech Stack

| Component | Technology |
|---|---|
| Hosting | GitHub Pages (static) |
| CI/CD | GitHub Actions |
| AI curation | Claude claude-sonnet-4-6 (Anthropic) |
| News fetching | Python + feedparser |
| Frontend | Vanilla HTML/CSS (no framework, dark mode) |
| Fonts | Google Fonts — Inter |

---

## Customisation

**Change refresh frequency** — edit the cron in `.github/workflows/refresh.yml`:
```yaml
cron: '0 6 1,16 * *'  # 1st and 16th of each month
```

**Add/remove RSS feeds** — edit the `feeds` list inside each section in `SECTIONS` in `scripts/generate_news.py`

**Change what Claude focuses on per section** — edit the `focus` string inside each section in `SECTIONS`

**Add a new section** — add a new dict to `SECTIONS` following the existing pattern (`id`, `title`, `description`, `color`, `icon`, `output`, `feeds`, `focus`)

---

## License

MIT
