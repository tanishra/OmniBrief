"""
src/fetchers/rss_feeds.py
Parses multiple RSS/Atom feeds to pull AI news articles.
Uses feedparser — no API keys needed.
"""

import asyncio
import feedparser
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any


def _parse_single_feed(feed_config: Dict, max_items: int) -> List[Dict[str, Any]]:
    """
    Synchronously parses a single RSS feed (feedparser is sync).
    Returns list of article dicts capped at max_items.
    """
    try:
        feed   = feedparser.parse(feed_config["url"])
        items  = []
        source = feed_config["name"]
        cat    = feed_config.get("category", "news")

        for entry in feed.entries[:max_items]:
            title   = entry.get("title", "").strip()
            url     = entry.get("link", "")
            summary = entry.get("summary", "") or entry.get("description", "")

            # Strip basic HTML tags from summary
            import re
            summary = re.sub(r"<[^>]+>", "", summary).strip()
            if len(summary) > 350:
                summary = summary[:350] + "..."

            if not title or not url:
                continue

            published = ""
            if hasattr(entry, "published"):
                published = entry.published[:10] if entry.published else ""

            items.append({
                "title":     title,
                "url":       url,
                "summary":   summary,
                "source":    source,
                "category":  cat,
                "published": published,
            })

        return items
    except Exception as e:
        print(f"  ⚠️  Error parsing {feed_config['name']}: {e}")
        return []


async def fetch_rss_feeds(
    feeds: List[Dict],
    max_per_feed: int = 5,
) -> List[Dict[str, Any]]:
    """
    Fetches all RSS feeds concurrently using a thread pool.
    Returns combined list capped at max_per_feed per source.
    """
    loop = asyncio.get_event_loop()

    with ThreadPoolExecutor(max_workers=10) as executor:
        tasks = [
            loop.run_in_executor(executor, _parse_single_feed, feed, max_per_feed)
            for feed in feeds
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    all_items = []
    for feed_items in results:
        if isinstance(feed_items, Exception):
            continue
        all_items.extend(feed_items)

    return all_items


if __name__ == "__main__":
    from config import RSS_FEEDS
    items = asyncio.run(fetch_rss_feeds(RSS_FEEDS, 3))
    for i in items:
        print(f"[{i['source']}] {i['title']}")
