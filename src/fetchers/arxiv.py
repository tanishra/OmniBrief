"""
src/fetchers/arxiv.py
Fetches latest AI research papers from ArXiv using their free Atom/XML API.
No API key needed. Uses HTTPS directly to avoid 301 redirect issues.
"""

import httpx
import asyncio
import xml.etree.ElementTree as ET
from typing import List, Dict, Any

# IMPORTANT: Use https:// directly — http:// causes a 301 redirect that httpx won't follow
ARXIV_API = "https://export.arxiv.org/api/query"
NS = {"atom": "http://www.w3.org/2005/Atom"}


async def fetch_arxiv(categories: List[str], max_items: int = 8) -> List[Dict[str, Any]]:
    """
    Fetches the latest papers from given ArXiv categories.
    Uses batching and retries to avoid 429 errors.
    """
    # Split categories into smaller batches of 5 to keep URL length safe
    batch_size = 5
    batches = [categories[i:i + batch_size] for i in range(0, len(categories), batch_size)]
    
    all_results = []
    seen = set()

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        for batch in batches:
            cat_query = " OR ".join(f"cat:{c}" for c in batch)
            params = {
                "search_query": cat_query,
                "sortBy":       "submittedDate",
                "sortOrder":    "descending",
                "max_results":  max_items,
            }

            for attempt in range(3):
                try:
                    resp = await client.get(ARXIV_API, params=params)
                    if resp.status_code == 429:
                        wait = (attempt + 1) * 5
                        print(f"  ⚠️  ArXiv 429 - Waiting {wait}s...")
                        await asyncio.sleep(wait)
                        continue
                    
                    resp.raise_for_status()
                    xml_text = resp.text
                    break
                except Exception as e:
                    if attempt == 2: raise e
                    await asyncio.sleep(2)

            root    = ET.fromstring(xml_text)
            entries = root.findall("atom:entry", NS)

            for entry in entries:
                title = _text(entry, "atom:title")
                if not title or title in seen: continue
                seen.add(title)
                
                abstract = _text(entry, "atom:summary")
                url      = _text(entry, "atom:id")
                pub      = _text(entry, "atom:published")
                authors  = [a.find("atom:name", NS).text for a in entry.findall("atom:author", NS) if a.find("atom:name", NS) is not None]
                cats     = [c.get("term", "") for c in entry.findall("atom:category", NS)]

                all_results.append({
                    "title":      title.strip(),
                    "authors":    authors[:3],
                    "abstract":   " ".join(abstract.split())[:450] + "...",
                    "url":        url.strip(),
                    "published":  pub[:10] if pub else "",
                    "categories": cats[:3],
                    "source":     "ArXiv",
                })

            # Small pause between batches to be polite
            await asyncio.sleep(1)

    # Sort combined results by published date and cap
    all_results.sort(key=lambda x: x["published"], reverse=True)
    return all_results[:max_items]


def _text(element, tag: str) -> str:
    node = element.find(tag, NS)
    return node.text.strip() if node is not None and node.text else ""


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from config import ARXIV_CATEGORIES, ARXIV_MAX_ITEMS
    items = asyncio.run(fetch_arxiv(ARXIV_CATEGORIES, ARXIV_MAX_ITEMS))
    for i in items:
        print(f"📄 {i['title']}")
        print(f"   Authors: {', '.join(i['authors'])}")
        print(f"   {i['url']}\n")