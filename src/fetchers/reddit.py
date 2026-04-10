"""
src/fetchers/reddit.py
Fetches top AI posts from Reddit using the public JSON API.
Uses endpoint fallbacks because Reddit may block one hostname while allowing another.
"""

import httpx
import asyncio
from typing import List, Dict, Any

REDDIT_JSON_ENDPOINTS = [
    "https://www.reddit.com/r/{subreddit}/top.json",
    "https://old.reddit.com/r/{subreddit}/top.json",
]

HEADERS = {
    # Reddit is stricter on VPS/cloud IPs, so use a descriptive UA and explicit JSON accept header.
    "User-Agent": "linux:omnibrief:v1.0 (by /u/omnibrief)",
    "Accept": "application/json",
}

# Keywords to filter for relevance in mixed subreddits
AI_KEYWORDS = [
    "ai", "llm", "gpt", "claude", "gemini", "model", "agent", "openai",
    "anthropic", "deepmind", "mistral", "llama", "hugging", "transformer",
    "neural", "machine learning", "deep learning", "diffusion", "rag",
    "embedding", "inference", "fine-tun", "multimodal", "autonomous",
    "benchmark", "paper", "research", "china", "alibaba", "baidu", "tencent",
    "qwen", "deepseek", "kimi", "moonshot",
]


async def fetch_reddit(
    subreddits: List[str],
    max_items: int = 6,
    time_filter: str = "day",   # "hour", "day", "week"
) -> List[Dict[str, Any]]:
    """
    Fetches top posts from given subreddits, filtered for AI relevance.
    Returns: [{title, url, subreddit, score, comments, reddit_url}]
    """
    all_posts = []
    seen_urls = set()

    async with httpx.AsyncClient(timeout=20, headers=HEADERS, follow_redirects=True) as client:
        for subreddit in subreddits:
            try:
                posts = await _fetch_subreddit_posts(client, subreddit, time_filter)
                if not posts:
                    continue

                for post in posts:
                    p = post.get("data", {})

                    title      = p.get("title", "").strip()
                    link       = p.get("url", "")
                    reddit_url = f"https://reddit.com{p.get('permalink', '')}"
                    score      = p.get("score", 0)
                    comments   = p.get("num_comments", 0)
                    selftext   = p.get("selftext", "")[:300]
                    is_self    = p.get("is_self", False)

                    if not title or link in seen_urls:
                        continue

                    if subreddit not in ("MachineLearning", "LocalLLaMA"):
                        title_lower = title.lower()
                        if not any(kw in title_lower for kw in AI_KEYWORDS):
                            continue

                    if score < 50:
                        continue

                    seen_urls.add(link)
                    all_posts.append({
                        "title":      title,
                        "url":        reddit_url if is_self else link,
                        "reddit_url": reddit_url,
                        "subreddit":  f"r/{subreddit}",
                        "score":      score,
                        "comments":   comments,
                        "summary":    selftext if selftext else title,
                        "source":     "Reddit",
                    })

            except (httpx.HTTPStatusError, httpx.RequestError) as e:
                print(f"  ⚠️  Reddit r/{subreddit} fetch failed after fallbacks: {e}")
                continue

            await asyncio.sleep(0.5)   # Be polite to Reddit

    # Sort by score, take top N
    all_posts.sort(key=lambda x: x["score"], reverse=True)
    return all_posts[:max_items]


async def _fetch_subreddit_posts(
    client: httpx.AsyncClient,
    subreddit: str,
    time_filter: str,
) -> List[Dict[str, Any]]:
    params = {
        "limit": 20,
        "t": time_filter,
        "raw_json": 1,
    }

    last_error: Exception | None = None
    for endpoint in REDDIT_JSON_ENDPOINTS:
        url = endpoint.format(subreddit=subreddit)
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", {}).get("children", [])
        except (httpx.HTTPStatusError, httpx.RequestError) as exc:
            last_error = exc
            continue

    if last_error:
        raise last_error
    return []


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from config import REDDIT_SUBREDDITS, REDDIT_MAX_ITEMS
    items = asyncio.run(fetch_reddit(REDDIT_SUBREDDITS, REDDIT_MAX_ITEMS))
    for i in items:
        print(f"[{i['subreddit']}] ▲{i['score']}  {i['title']}")
        print(f"   {i['url']}\n")
