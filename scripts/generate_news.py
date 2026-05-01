#!/usr/bin/env python3
"""
AI Pulse — News generation script.
Fetches articles from RSS feeds, uses Claude to curate & summarize the top 10,
and writes index.html from the template.
"""

import os
import sys
import json
import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from html import escape

import feedparser
import anthropic

# ── RSS Feeds ──────────────────────────────────────────────────────────────────
# Broad AI coverage + engineering + banking/finance AI
RSS_FEEDS = [
    # General AI
    ("TechCrunch AI",       "https://techcrunch.com/category/artificial-intelligence/feed/"),
    ("MIT Technology Review","https://www.technologyreview.com/topic/artificial-intelligence/feed"),
    ("The Verge AI",         "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml"),
    ("VentureBeat AI",       "https://venturebeat.com/category/ai/feed/"),
    ("Wired AI",             "https://www.wired.com/feed/tag/ai/latest/rss"),
    ("The Register AI",      "https://www.theregister.com/emergent_tech/artificial_intelligence/headlines.atom"),
    # AI for Engineering / Research
    ("ArXiv cs.AI",          "http://arxiv.org/rss/cs.AI"),
    ("Towards Data Science", "https://towardsdatascience.com/feed"),
    ("InfoQ AI",             "https://feed.infoq.com/"),
    # Banking / Finance AI
    ("FinExtra",             "https://www.finextra.com/rss/headlines.aspx"),
    ("American Banker",      "https://www.americanbanker.com/feeds/topic/technology-rss"),
    ("PYMNTS AI",            "https://www.pymnts.com/category/artificial-intelligence/feed/"),
]

MAX_ARTICLES_PER_FEED = 8   # cap per feed to keep prompt size reasonable
MAX_TOTAL_ARTICLES    = 80  # upper limit passed to Claude


def fetch_articles() -> list[dict]:
    """Fetch articles from all RSS feeds, return list of dicts."""
    articles = []
    for source_name, url in RSS_FEEDS:
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
                # Strip HTML tags from summary
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

    return articles[:MAX_TOTAL_ARTICLES]


def curate_with_claude(articles: list[dict]) -> list[dict]:
    """Send articles to Claude; receive top 10 with summaries and takeaways."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    # Build compact article list for the prompt
    article_lines = []
    for i, a in enumerate(articles, 1):
        article_lines.append(
            f"[{i}] SOURCE: {a['source']}\n"
            f"    TITLE: {a['title']}\n"
            f"    SNIPPET: {a['summary'][:300]}\n"
            f"    LINK: {a['link']}\n"
            f"    DATE: {a['published']}\n"
        )
    articles_text = "\n".join(article_lines)

    system_prompt = """You are the editor of AI Pulse, a daily AI news digest aimed at professionals.
Your job: select and enrich the 10 most important AI stories from the provided list.

SELECTION CRITERIA (apply in order):
1. Impact & significance — breakthrough research, major product launches, policy changes, funding rounds that shift the industry
2. Engagement signals — stories likely trending across multiple outlets
3. Topical priority — give extra weight to (a) AI for software/data engineering and (b) AI in banking/financial services; cover broad AI otherwise

TAGGING: For each story assign one or more tags from: ["AI Engineering", "Finance & Banking", "Research", "Products & Tools", "Policy & Ethics", "Industry"]

OUTPUT: Return a JSON array of exactly 10 objects. No markdown fences, no extra text — raw JSON only.
Each object:
{
  "rank": <1-10>,
  "title": "<original headline — do not rewrite>",
  "source": "<source name>",
  "link": "<URL>",
  "published": "<date string>",
  "tags": ["<tag>", ...],
  "summary": "<AI-written summary, maximum 10 sentences, factual and concise>",
  "takeaways": [
    "<impact takeaway 1>",
    "<impact takeaway 2>",
    "<impact takeaway 3>"
  ]
}
takeaways must focus on real-world impact and what it means for practitioners. 3–5 bullet points."""

    user_prompt = f"Here are today's candidate articles:\n\n{articles_text}\n\nReturn the top 10 as JSON."

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw = message.content[0].text.strip()
    # Strip optional markdown code fences
    raw = re.sub(r"^```[a-z]*\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)

    try:
        top10 = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"  [error] JSON parse failed: {e}", file=sys.stderr)
        print(f"  [debug] Raw response tail: {raw[-300:]}", file=sys.stderr)
        raise

    return top10


def tag_class(tag: str) -> str:
    t = tag.lower()
    if "engineer" in t:
        return "tag-engineering"
    if "financ" in t or "bank" in t:
        return "tag-finance"
    return "tag-ai"


def render_news_items(top10: list[dict]) -> str:
    html_parts = []
    for item in top10:
        tags_html = "".join(
            f'<span class="tag {tag_class(tag)}">{escape(tag)}</span>'
            for tag in item.get("tags", [])
        )

        takeaways_html = "".join(
            f"<li>{escape(t)}</li>"
            for t in item.get("takeaways", [])
        )

        html_parts.append(f"""
      <article class="news-card">
        <div class="card-rank">#{item['rank']}</div>
        <div class="card-tags">{tags_html}</div>
        <h2 class="card-headline">
          <a href="{escape(item['link'])}" target="_blank" rel="noopener noreferrer">
            {escape(item['title'])}
          </a>
        </h2>
        <div class="card-meta">
          <span class="source">{escape(item['source'])}</span>
          <span>{escape(item.get('published', ''))}</span>
        </div>
        <p class="card-summary">{escape(item['summary'])}</p>
        <div class="card-takeaways">
          <h4>Impact Takeaways</h4>
          <ul>{takeaways_html}</ul>
        </div>
      </article>""")

    return "\n".join(html_parts)


def build_html(top10: list[dict]) -> str:
    template_path = Path(__file__).parent / "template.html"
    template = template_path.read_text(encoding="utf-8")

    now = datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M UTC")
    news_items = render_news_items(top10)

    return (
        template
        .replace("{{LAST_UPDATED}}", now)
        .replace("{{NEWS_ITEMS}}", news_items)
    )


def main():
    print("AI Pulse — fetching articles...")
    articles = fetch_articles()
    print(f"  Fetched {len(articles)} articles from {len(RSS_FEEDS)} feeds")

    if not articles:
        print("ERROR: No articles fetched. Check feed URLs or network.", file=sys.stderr)
        sys.exit(1)

    print("  Sending to Claude for curation...")
    top10 = curate_with_claude(articles)
    print(f"  Claude selected {len(top10)} stories")

    output_path = Path(__file__).parent.parent / "index.html"
    output_path.write_text(build_html(top10), encoding="utf-8")
    print(f"  Written to {output_path}")


if __name__ == "__main__":
    main()
