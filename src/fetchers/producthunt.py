"""
src/fetchers/producthunt.py
Fetches top AI products launched on ProductHunt via their RSS feed.
No API key needed.
"""

import asyncio
import feedparser
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any
import re

PRODUCTHUNT_RSS = "https://www.producthunt.com/feed?category=artificial-intelligence"


def _parse_producthunt() -> List[Dict[str, Any]]:
    """Parses the ProductHunt AI RSS feed synchronously."""
    feed  = feedparser.parse(PRODUCTHUNT_RSS)
    items = []

    for entry in feed.entries:
        title   = entry.get("title", "").strip()
        url     = entry.get("link", "")
        summary = entry.get("summary", "") or entry.get("description", "")

        # Strip HTML
        summary = re.sub(r"<[^>]+>", "", summary).strip()
        if len(summary) > 300:
            summary = summary[:300] + "..."

        if not title or not url:
            continue

        published = ""
        if hasattr(entry, "published"):
            published = entry.published[:10] if entry.published else ""

        # Extract vote count if available in title (PH sometimes includes it)
        votes = 0
        vote_match = re.search(r"\((\d+)\s*votes?\)", title, re.IGNORECASE)
        if vote_match:
            votes = int(vote_match.group(1))
            title = title.replace(vote_match.group(0), "").strip()

        items.append({
            "title":     title,
            "url":       url,
            "summary":   summary,
            "votes":     votes,
            "published": published,
            "source":    "ProductHunt",
        })

    return items


async def fetch_producthunt(max_items: int = 5) -> List[Dict[str, Any]]:
    """Async wrapper around the sync feedparser call."""
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=2) as executor:
        items = await loop.run_in_executor(executor, _parse_producthunt)
    return items[:max_items]


if __name__ == "__main__":
    items = asyncio.run(fetch_producthunt(5))
    for i in items:
        print(f"🚀 {i['title']}")
        print(f"   {i['summary'][:100]}")
        print(f"   {i['url']}\n")
