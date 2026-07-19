"""
src/fetchers/producthunt.py
Fetches top AI products launched on ProductHunt via their RSS feed.
Uses httpx + xml.etree.ElementTree — no feedparser dependency.
"""

import asyncio
import re
import xml.etree.ElementTree as ET
from typing import Any, Dict, List

import httpx

from src.logger import logger

PRODUCTHUNT_RSS = "https://www.producthunt.com/feed?category=artificial-intelligence"


async def fetch_producthunt(max_items: int = 5) -> List[Dict[str, Any]]:
    """Fetches and parses the ProductHunt AI RSS feed asynchronously."""
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(PRODUCTHUNT_RSS)
            resp.raise_for_status()

        root = ET.fromstring(resp.text)
        channel = root.find("channel")
        entries = channel.findall("item") if channel is not None else []
        items = []

        for entry in entries[:max_items]:
            title = _tag_text(entry, "title")
            url = _tag_text(entry, "link")
            description = _tag_text(entry, "description")
            published = _tag_text(entry, "pubDate")[:10] if _tag_text(entry, "pubDate") else ""

            if not title or not url:
                continue

            description = re.sub(r"<[^>]+>", "", description).strip()
            if len(description) > 300:
                description = description[:300] + "..."

            votes = 0
            vote_match = re.search(r"\((\d+)\s*votes?\)", title, re.IGNORECASE)
            if vote_match:
                votes = int(vote_match.group(1))
                title = title.replace(vote_match.group(0), "").strip()

            items.append({
                "title":     title,
                "url":       url,
                "summary":   description,
                "votes":     votes,
                "published": published,
                "source":    "ProductHunt",
            })

        return items
    except Exception as e:
        logger.warning(f"  ⚠️  Error fetching ProductHunt: {e}")
        return []


def _tag_text(parent: ET.Element, tag: str) -> str:
    el = parent.find(tag)
    return el.text.strip() if el is not None and el.text else ""


if __name__ == "__main__":
    items = asyncio.run(fetch_producthunt(5))
    for i in items:
        logger.info(f"🚀 {i['title']}")
        logger.info(f"   {i['summary'][:100]}")
        logger.info(f"   {i['url']}\n")
