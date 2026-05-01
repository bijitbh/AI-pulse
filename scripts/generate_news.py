#!/usr/bin/env python3
"""
AI Pulse — Multi-section news generation script.
Fetches articles per section, uses Claude to curate & summarise top 5 per section,
and writes index.html + 6 section detail pages under pages/.
"""

import os
import sys
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from html import escape

import feedparser
import anthropic

# ── Section Definitions ────────────────────────────────────────────────────────

SECTIONS = [
    {
        "id":          "finance",
        "title":       "AI in Finance",
        "description": "AI transforming banking, payments, trading and financial services",
        "color":       "#38bdf8",
        "output":      "pages/finance.html",
        "feeds": [
            ("FinExtra",         "https://www.finextra.com/rss/headlines.aspx"),
            ("American Banker",  "https://www.americanbanker.com/feeds/topic/technology-rss"),
            ("PYMNTS AI",        "https://www.pymnts.com/category/artificial-intelligence/feed/"),
            ("Reuters Business", "https://feeds.reuters.com/reuters/businessNews"),
        ],
        "focus": (
            "AI in banking, financial services, payments, trading, insurance, and fintech. "
            "Prioritise stories about AI product launches, deployments, and regulatory impact "
            "in the financial sector."
        ),
    },
    {
        "id":          "engineering",
        "title":       "Engineering Intelligence",
        "description": "AI tools, frameworks and breakthroughs for software and data engineers",
        "color":       "#4ade80",
        "output":      "pages/engineering.html",
        "feeds": [
            ("ArXiv cs.AI",          "http://arxiv.org/rss/cs.AI"),
            ("Towards Data Science", "https://towardsdatascience.com/feed"),
            ("InfoQ",                "https://feed.infoq.com/"),
            ("Stack Overflow Blog",  "https://stackoverflow.blog/feed/"),
            ("Dev.to AI",            "https://dev.to/feed/tag/ai"),
        ],
        "focus": (
            "AI tools and techniques for software engineering, data engineering, MLOps, "
            "and developer productivity. Prioritise practical, actionable stories for engineers."
        ),
    },
    {
        "id":          "github-copilot",
        "title":       "GitHub Copilot",
        "description": "Latest features, updates and news from GitHub Copilot",
        "color":       "#a78bfa",
        "output":      "pages/github-copilot.html",
        "feeds": [
            ("GitHub Blog",      "https://github.blog/feed/"),
            ("GitHub Changelog", "https://github.blog/changelog/feed/"),
            ("VS Code Blog",     "https://code.visualstudio.com/feed.xml"),
            ("The Verge AI",     "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml"),
            ("TechCrunch AI",    "https://techcrunch.com/category/artificial-intelligence/feed/"),
        ],
        "focus": (
            "GitHub Copilot news, feature releases, and updates. Include stories about "
            "AI coding assistants, GitHub AI features, VS Code AI integrations, and "
            "agentic coding tools. If dedicated Copilot articles are scarce, include the "
            "most relevant AI developer tooling stories."
        ),
    },
    {
        "id":          "m365-copilot",
        "title":       "Microsoft 365 Copilot",
        "description": "Updates, features and news from Microsoft 365 Copilot",
        "color":       "#fb923c",
        "output":      "pages/m365-copilot.html",
        "feeds": [
            ("Microsoft 365 Blog", "https://www.microsoft.com/en-us/microsoft-365/blog/feed/"),
            ("Windows Blog",       "https://blogs.windows.com/feed/"),
            ("VentureBeat AI",     "https://venturebeat.com/category/ai/feed/"),
            ("TechCrunch AI",      "https://techcrunch.com/category/artificial-intelligence/feed/"),
        ],
        "focus": (
            "Microsoft 365 Copilot news, feature releases, and updates. Include stories "
            "about AI in Word, Excel, Teams, Outlook, PowerPoint, and broader Microsoft "
            "AI strategy and products."
        ),
    },
    {
        "id":          "governance",
        "title":       "AI Governance & Safety",
        "description": "AI regulations, privacy, security and policy developments worldwide",
        "color":       "#f87171",
        "output":      "pages/governance.html",
        "feeds": [
            ("IAPP",                  "https://iapp.org/feed/"),
            ("Future of Life Inst.",  "https://futureoflife.org/feed/"),
            ("EFF",                   "https://www.eff.org/rss/updates.xml"),
            ("MIT Technology Review", "https://www.technologyreview.com/topic/artificial-intelligence/feed"),
            ("The Verge AI",          "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml"),
        ],
        "focus": (
            "AI regulations, policy, safety, privacy, and security. Prioritise legislative "
            "developments, regulatory decisions, ethical AI debates, and cybersecurity "
            "implications of AI systems."
        ),
    },
    {
        "id":          "trending",
        "title":       "Trending in AI",
        "description": "The most significant and talked-about AI stories right now",
        "color":       "#fbbf24",
        "output":      "pages/trending.html",
        "feeds": [
            ("TechCrunch AI",         "https://techcrunch.com/category/artificial-intelligence/feed/"),
            ("MIT Technology Review", "https://www.technologyreview.com/topic/artificial-intelligence/feed"),
            ("The Verge AI",          "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml"),
            ("VentureBeat AI",        "https://venturebeat.com/category/ai/feed/"),
            ("Wired AI",              "https://www.wired.com/feed/tag/ai/latest/rss"),
            ("The Register AI",       "https://www.theregister.com/emergent_tech/artificial_intelligence/headlines.atom"),
        ],
        "focus": (
            "The most broadly significant and trending AI stories across research, products, "
            "and industry. Focus on high-impact, novel stories generating wide discussion."
        ),
    },
]

MAX_ARTICLES_PER_FEED = 10


# ── Fetching ───────────────────────────────────────────────────────────────────

def fetch_articles(feeds: list[tuple]) -> list[dict]:
    articles = []
    for source_name, url in feeds:
        try:
            feed = feedparser.parse(url)
            count = 0
            for entry in feed.entries:
                if count >= MAX_ARTICLES_PER_FEED:
                    break
                title = entry.get("title", "").strip()
                link  = entry.get("link",  "").strip()
                if not title or not link:
                    continue
                summary = (
                    entry.get("summary", "")
                    or entry.get("description", "")
                    or ""
                ).strip()
                summary = re.sub(r"<[^>]+>", " ", summary).strip()
                summary = re.sub(r"\s+", " ", summary)[:600]
                published = entry.get("published", entry.get("updated", ""))
                articles.append({
                    "source":    source_name,
                    "title":     title,
                    "link":      link,
                    "summary":   summary,
                    "published": published,
                })
                count += 1
        except Exception as e:
            print(f"  [warn] Failed to fetch {source_name}: {e}", file=sys.stderr)
    return articles


# ── Claude Curation ────────────────────────────────────────────────────────────

def curate_section(client: anthropic.Anthropic, articles: list[dict], section: dict) -> list[dict]:
    if not articles:
        print(f"  [warn] No articles for {section['title']}, skipping Claude call.", file=sys.stderr)
        return []

    article_lines = []
    for i, a in enumerate(articles, 1):
        article_lines.append(
            f"[{i}] SOURCE: {a['source']}\n"
            f"    TITLE: {a['title']}\n"
            f"    SNIPPET: {a['summary'][:400]}\n"
            f"    LINK: {a['link']}\n"
            f"    DATE: {a['published']}\n"
        )
    articles_text = "\n".join(article_lines)

    system_prompt = f"""You are the editor of AI Pulse, a professional AI news digest.
Select the 5 most important articles for the section "{section['title']}".

FOCUS: {section['focus']}

SELECTION CRITERIA (in order):
1. Relevance to this section's specific topic
2. Impact and significance for professionals
3. Recency

OUTPUT: A JSON array of exactly 5 objects. Raw JSON only — no markdown fences, no extra text.

Each object must have these exact keys:
{{
  "rank": <1-5>,
  "title": "<original headline, do not rewrite>",
  "source": "<source name>",
  "link": "<URL>",
  "published": "<date string>",
  "short_summary": "<2-3 sentence preview for homepage card>",
  "summary": "<10-11 sentence detailed summary for the section page>",
  "takeaways": ["<impact point 1>", "<impact point 2>", "<impact point 3>"]
}}

Rules:
- short_summary: concise, 2-3 sentences, suitable for a card preview
- summary: detailed, 10-11 sentences, factual and informative
- takeaways: 3-5 bullet points on real-world impact for practitioners
- If fewer than 5 relevant articles exist, still return 5 using the best available"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        system=system_prompt,
        messages=[{
            "role": "user",
            "content": f"Articles for '{section['title']}':\n\n{articles_text}\n\nReturn top 5 as JSON."
        }],
    )

    raw = message.content[0].text.strip()
    raw = re.sub(r"^```[a-z]*\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)

    try:
        items = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"  [error] JSON parse failed for {section['title']}: {e}", file=sys.stderr)
        print(f"  [debug] Raw tail: {raw[-300:]}", file=sys.stderr)
        raise

    return items


# ── HTML Rendering ─────────────────────────────────────────────────────────────

def render_section_card(section: dict, items: list[dict]) -> str:
    stories_html = ""
    for item in items:
        stories_html += f"""
        <div class="story-item">
          <span class="story-rank">{str(item['rank']).zfill(2)}</span>
          <div class="story-body">
            <h3 class="story-headline">
              <a href="{section['output']}#story-{item['rank']}">{escape(item['title'])}</a>
            </h3>
            <p class="story-short">{escape(item.get('short_summary', ''))}</p>
          </div>
        </div>"""

    return f"""
    <div class="section-card" style="--c: {section['color']}">
      <div class="section-card-top">
        <div class="section-label">
          <span class="section-dot"></span>
          <h2 class="section-title">{escape(section['title'])}</h2>
        </div>
        <p class="section-desc">{escape(section['description'])}</p>
      </div>
      <div class="story-list">{stories_html}
      </div>
      <a class="view-all-link" href="{section['output']}">View all 5 stories →</a>
    </div>"""


def render_article(item: dict) -> str:
    takeaways_html = "".join(
        f"<li>{escape(t)}</li>" for t in item.get("takeaways", [])
    )
    return f"""
    <article class="article-card" id="story-{item['rank']}">
      <div class="article-number">#{item['rank']}</div>
      <h2 class="article-title">
        <a href="{escape(item['link'])}" target="_blank" rel="noopener noreferrer">
          {escape(item['title'])}
        </a>
      </h2>
      <div class="article-meta">
        <span class="article-source">{escape(item.get('source', ''))}</span>
        <span class="article-date">{escape(item.get('published', ''))}</span>
      </div>
      <p class="article-summary">{escape(item.get('summary', ''))}</p>
      <div class="article-impact">
        <h4>Impact Takeaways</h4>
        <ul>{takeaways_html}</ul>
      </div>
    </article>"""


def build_homepage(sections_data: list[tuple], now: str) -> str:
    template = (Path(__file__).parent / "template_home.html").read_text(encoding="utf-8")
    sections_html = "\n".join(
        render_section_card(section, items)
        for section, items in sections_data
    )
    return template.replace("{{LAST_UPDATED}}", now).replace("{{SECTIONS_HTML}}", sections_html)


def build_section_page(section: dict, items: list[dict], now: str) -> str:
    template = (Path(__file__).parent / "template_section.html").read_text(encoding="utf-8")
    articles_html = "\n".join(render_article(item) for item in items)
    return (
        template
        .replace("{{SECTION_TITLE}}",       escape(section["title"]))
        .replace("{{SECTION_DESCRIPTION}}", escape(section["description"]))
        .replace("{{SECTION_COLOR}}",       section["color"])
        .replace("{{ARTICLES_HTML}}",       articles_html)
        .replace("{{LAST_UPDATED}}",        now)
    )


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    now    = datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M UTC")
    root   = Path(__file__).parent.parent

    (root / "pages").mkdir(exist_ok=True)

    sections_data = []

    for section in SECTIONS:
        print(f"\n[{section['title']}]")
        articles = fetch_articles(section["feeds"])
        print(f"  Fetched {len(articles)} articles from {len(section['feeds'])} feeds")

        items = curate_section(client, articles, section)
        print(f"  Claude selected {len(items)} stories")

        sections_data.append((section, items))

        page_html  = build_section_page(section, items, now)
        page_path  = root / section["output"]
        page_path.write_text(page_html, encoding="utf-8")
        print(f"  Written → {page_path}")

    index_html = build_homepage(sections_data, now)
    (root / "index.html").write_text(index_html, encoding="utf-8")
    print(f"\nHomepage written → {root / 'index.html'}")


if __name__ == "__main__":
    main()
