# ⚡ AI Pulse

A static website that displays the **top 10 AI news stories**, automatically curated and summarised by Claude (Anthropic). The site refreshes every 15 days via a scheduled GitHub Actions workflow and is hosted on GitHub Pages.

## Live Site

> `https://bijitbh.github.io/ai-pulse/`

---

## What It Does

- Fetches articles from **12 curated RSS feeds** covering broad AI, AI engineering, and AI in banking/finance
- Sends all candidate articles to **Claude (claude-sonnet-4-6)** which selects and ranks the top 10 by impact, significance, and engagement
- For each story, Claude generates:
  - A summary (up to 10 sentences)
  - 3–5 impact takeaways as bullet points
- Outputs a fully self-contained `index.html` with a dark-mode design and serves it via GitHub Pages

---

## News Sources

| Category | Source |
|---|---|
| General AI | TechCrunch AI, MIT Technology Review, The Verge AI, VentureBeat AI, Wired AI, The Register AI |
| AI Engineering / Research | ArXiv cs.AI, Towards Data Science, InfoQ |
| Banking / Finance AI | FinExtra, American Banker, PYMNTS AI |

### Ranking Priority
1. **Impact & significance** — breakthroughs, major launches, policy changes
2. **Engagement signals** — stories trending across multiple outlets
3. **Topic weighting** — AI for engineering and AI in banking/finance are prioritised

---

## Project Structure

```
ai-pulse/
├── index.html                    # Generated static site (committed by the workflow)
├── requirements.txt              # Python dependencies
├── scripts/
│   ├── generate_news.py          # Fetches RSS → calls Claude → writes index.html
│   └── template.html             # HTML template populated by the script
└── .github/
    └── workflows/
        └── refresh.yml           # Scheduled GitHub Actions workflow
```

---

## How It Works

```
┌─────────────────────────────────────────────────┐
│  GitHub Actions (cron: 1st & 16th of each month) │
│                                                   │
│  1. Fetch up to 8 articles from each RSS feed    │
│  2. Send all articles to Claude API              │
│  3. Claude returns top 10 as JSON                │
│     (ranked, summarised, tagged)                 │
│  4. Inject JSON into template.html               │
│  5. Commit index.html to main                    │
│  6. GitHub Pages serves updated site             │
└─────────────────────────────────────────────────┘
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
- Wait ~1–2 minutes
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
| Frontend | Vanilla HTML/CSS (no framework) |

---

## Customisation

**Change refresh frequency** — edit the cron in `.github/workflows/refresh.yml`:
```yaml
cron: '0 6 1,16 * *'  # 1st and 16th of each month
```

**Add/remove RSS feeds** — edit `RSS_FEEDS` in `scripts/generate_news.py`

**Change ranking priorities** — edit the system prompt in `curate_with_claude()` in `scripts/generate_news.py`

---

## License

MIT
