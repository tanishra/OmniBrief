"""
src/fetchers/hackernews.py
Fetches top HN posts that are AI/ML related using the Algolia HN Search API.
No API key needed — completely free.
"""

import httpx
import asyncio
from typing import List, Dict, Any

# Keywords that indicate an AI/ML post
AI_KEYWORDS = [
    "ai", "ml", "llm", "gpt", "claude", "gemini", "openai", "anthropic",
    "machine learning", "deep learning", "neural", "transformer", "agent",
    "langchain", "rag", "vector", "embedding", "diffusion", "stable diffusion",
    "mistral", "llama", "model", "inference", "fine-tun", "multimodal",
    "autonomous", "copilot", "chatbot", "generative", "hugging face",
    "reinforcement learning", "rlhf", "alignment",
]

HN_API_BASE = "https://hacker-news.firebaseio.com/v0"
HN_ALGOLIA  = "https://hn.algolia.com/api/v1/search"


async def fetch_hackernews(max_items: int = 8) -> List[Dict[str, Any]]:
    """
    Fetches top HN stories and filters for AI-related ones.
    Returns a list of dicts: {title, url, points, comments, hn_link}
    """
    async with httpx.AsyncClient(timeout=15) as client:
        # Algolia search — search for AI directly, sorted by date/relevance
        params = {
            "query": "AI machine learning LLM agent",
            "tags": "story",
            "numericFilters": "points>50",
            "hitsPerPage": 50,
        }
        resp = await client.get(HN_ALGOLIA, params=params)
        resp.raise_for_status()
        data = resp.json()

    hits = data.get("hits", [])

    results = []
    seen_titles = set()

    for hit in hits:
        title = hit.get("title", "")
        url   = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
        points   = hit.get("points", 0)
        comments = hit.get("num_comments", 0)
        hn_link  = f"https://news.ycombinator.com/item?id={hit.get('objectID')}"

        if not title or title in seen_titles:
            continue

        title_lower = title.lower()
        if any(kw in title_lower for kw in AI_KEYWORDS):
            seen_titles.add(title)
            results.append({
                "title":    title,
                "url":      url,
                "points":   points,
                "comments": comments,
                "hn_link":  hn_link,
                "source":   "Hacker News",
            })

        if len(results) >= max_items:
            break

    return results


if __name__ == "__main__":
    items = asyncio.run(fetch_hackernews())
    for i in items:
        print(f"[{i['points']}pts] {i['title']}")
        print(f"  → {i['url']}\n")
