"""
src/fetchers/github_trending.py
V7.3: Authority-Based Scouting & Velocity Tracking.
"""

import httpx
import asyncio
from typing import List, Dict, Any
from datetime import datetime, timedelta

GITHUB_SEARCH_API = "https://api.github.com/search/repositories"

async def fetch_github_trending(
    queries: List[str],
    max_items: int = 15,
    github_token: str = "",
    organizations: List[str] = None
) -> List[Dict[str, Any]]:
    """
    Searches GitHub using three strategies:
    1. Trending (High Stars)
    2. Innovative (Recently Created)
    3. Authority Scout (Elite Labs like DeepSeek, HKUST, Microsoft)
    """
    since_date = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"

    all_repos = []
    seen_urls = set()

    async with httpx.AsyncClient(timeout=25, headers=headers) as client:
        # Strategy 1 & 2: General Keywords
        for strategy in ["pushed", "created"]:
            sort_by = "stars" if strategy == "pushed" else "updated"
            for query in queries:
                q = f"{query} language:python {strategy}:>{since_date}"
                params = {"q": q, "sort": sort_by, "order": "desc", "per_page": 5}
                try:
                    resp = await client.get(GITHUB_SEARCH_API, params=params)
                    if resp.status_code == 200:
                        for item in resp.json().get("items", []):
                            url = item.get("html_url", "")
                            if url not in seen_urls:
                                seen_urls.add(url)
                                all_repos.append(_format_repo(item, strategy))
                except Exception: continue
                await asyncio.sleep(0.2)

        # Strategy 3: Authority Scout (Top Labs)
        if organizations:
            print(f"    🔎 Scouting {len(organizations)} top AI labs...")
            for org in organizations:
                # Search for ANY AI-related python repo pushed in this org recently
                q = f"org:{org} language:python pushed:>{since_date}"
                params = {"q": q, "sort": "updated", "order": "desc", "per_page": 3}
                try:
                    resp = await client.get(GITHUB_SEARCH_API, params=params)
                    if resp.status_code == 200:
                        for item in resp.json().get("items", []):
                            url = item.get("html_url", "")
                            if url not in seen_urls:
                                seen_urls.add(url)
                                all_repos.append(_format_repo(item, "authority"))
                except Exception: continue
                await asyncio.sleep(0.2)

    # Final Sort: Prioritize Authority and Innovation over just raw Stars
    def rank_score(r):
        score = 0
        if r["strategy"] == "authority": score += 1000 # Boost labs
        if r["strategy"] == "created": score += 500   # Boost new innovation
        score += min(r["stars"] / 10, 1000)           # Normalize stars
        return score

    all_repos.sort(key=rank_score, reverse=True)
    return all_repos[:max_items]

def _format_repo(item: dict, strategy: str) -> dict:
    desc = item.get("description") or "No description provided."
    return {
        "name":        item.get("full_name", ""),
        "title":       item.get("full_name", ""),
        "description": desc[:220] + "..." if len(desc) > 220 else desc,
        "url":         item.get("html_url", ""),
        "stars":       item.get("stargazers_count", 0),
        "language":    item.get("language") or "Python",
        "topics":      item.get("topics", [])[:4],
        "strategy":    strategy,
        "source":      "GitHub",
    }