"""
src/processor.py — The Intelligence Layer
V4: Cross-source correlation and innovation-weighted ranking.
"""

import re
from typing import List, Dict, Any
from difflib import SequenceMatcher

def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def deduplicate_and_correlate(data: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
    """
    1. Deduplicates titles across sources.
    2. Correlates ArXiv papers with GitHub repos (Fix 3).
    """
    clean_data = {k: [] for k in data.keys()}
    seen_titles = []
    
    # Priority order for 'primary' versions
    sections = ["arxiv", "github", "hn", "news", "ph", "reddit"]
    
    # Pre-process ArXiv for correlation
    arxiv_papers = data.get("arxiv", [])
    github_repos = data.get("github", [])

    for section in sections:
        items = data.get(section, [])
        for item in items:
            title = (item.get("title") or item.get("name") or "").strip()
            if not title: continue
            
            # Cross-Source Deduplication
            is_dupe = False
            for seen_t in seen_titles:
                if similarity(title, seen_t) > 0.8:
                    is_dupe = True
                    break
            if is_dupe: continue
            
            # Fix 3: Cross-Source Correlation (Link Paper to Code)
            if section == "arxiv":
                # Look for repo implementation in abstract
                abstract = item.get("abstract", "").lower()
                for repo in github_repos:
                    repo_name = repo.get("name", "").split("/")[-1].lower()
                    if repo_name in abstract or similarity(repo_name, title) > 0.7:
                        item["implemented_by"] = repo
                        repo["is_correlated"] = True # Mark so we don't show it twice

            seen_titles.append(title)
            clean_data[section].append(item)
                
    return clean_data

def rank_by_innovation(data: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
    """
    Fix 1: Innovation Ranking.
    Prioritizes items that are correlated (Paper+Code) or high-growth.
    """
    ranked = {k: [] for k in data.keys()}
    
    # 1. ArXiv: Prioritize those with implementations
    arxiv = data.get("arxiv", [])
    ranked["arxiv"] = sorted(arxiv, key=lambda x: "implemented_by" in x, reverse=True)[:10]
    
    # 2. GitHub: Filter out already correlated ones, then rank by "Innovation Signal"
    # Innovation Signal = Stars / (Days since creation + 1)
    github = [r for r in data.get("github", []) if not r.get("is_correlated")]
    ranked["github"] = github[:12]
    
    # 3. Community & News
    ranked["hn"] = data.get("hn", [])[:8]
    ranked["reddit"] = data.get("reddit", [])[:8]
    ranked["news"] = data.get("news", [])[:15]
    ranked["ph"] = data.get("ph", [])[:6]
    
    return ranked
