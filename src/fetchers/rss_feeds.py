from src.logger import logger
"""
src/fetchers/rss_feeds.py
Parses multiple RSS/Atom feeds to pull AI news articles.
Uses httpx + xml.etree.ElementTree — no feedparser dependency.
"""

import asyncio
import re
import xml.etree.ElementTree as ET
from typing import List, Dict, Any

import httpx

ATOM_NS = "http://www.w3.org/2005/Atom"


async def _parse_single_feed(feed_config: Dict, max_items: int) -> List[Dict[str, Any]]:
    """Async fetch + parse a single RSS or Atom feed."""
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(feed_config["url"])
            resp.raise_for_status()

        root = ET.fromstring(resp.text)
        source = feed_config["name"]
        cat = feed_config.get("category", "news")
        items = []

        if root.tag == "rss":
            channel = root.find("channel")
            entries = channel.findall("item") if channel is not None else []
            for entry in entries[:max_items]:
                title = _tag_text(entry, "title")
                url = _tag_text(entry, "link")
                description = _tag_text(entry, "description")
                published = _tag_text(entry, "pubDate")[:10] if _tag_text(entry, "pubDate") else ""
                parsed = _make_item(title, url, description, source, cat, published)
                if parsed:
                    items.append(parsed)
        elif root.tag == f"{{{ATOM_NS}}}feed":
            entries = root.findall(f"{{{ATOM_NS}}}entry")
            for entry in entries[:max_items]:
                title = _tag_text(entry, f"{{{ATOM_NS}}}title")
                link_el = entry.find(f"{{{ATOM_NS}}}link")
                url = link_el.get("href", "") if link_el is not None else ""
                content_el = entry.find(f"{{{ATOM_NS}}}content") or entry.find(f"{{{ATOM_NS}}}summary")
                description = content_el.text or "" if content_el is not None else ""
                pub_el = entry.find(f"{{{ATOM_NS}}}published") or entry.find(f"{{{ATOM_NS}}}updated")
                published = (pub_el.text or "")[:10] if pub_el is not None else ""
                parsed = _make_item(title, url, description, source, cat, published)
                if parsed:
                    items.append(parsed)

        return items
    except Exception as e:
        logger.warning(f"  ⚠️  Error parsing {feed_config['name']}: {e}")
        return []


def _tag_text(parent: ET.Element, tag: str) -> str:
    el = parent.find(tag)
    if el is None:
        return ""
    return "".join(el.itertext()).strip()


def _make_item(title: str, url: str, description: str, source: str, category: str, published: str) -> Dict[str, Any] | None:
    title = title.strip()
    url = url.strip()
    if not title or not url:
        return None
    description = re.sub(r"<[^>]+>", "", description).strip()
    if len(description) > 350:
        description = description[:350] + "..."
    return {
        "title": title,
        "url": url,
        "summary": description,
        "source": source,
        "category": category,
        "published": published,
    }


async def fetch_rss_feeds(
    feeds: List[Dict],
    max_per_feed: int = 5,
) -> List[Dict[str, Any]]:
    """
    Fetches all RSS feeds concurrently using async HTTP.
    Returns combined list capped at max_per_feed per source.
    """
    tasks = [_parse_single_feed(feed, max_per_feed) for feed in feeds]
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
        logger.info(f"[{i['source']}] {i['title']}")
