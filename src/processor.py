import re
from typing import List, Dict, Any

def get_tokens(text: str) -> set:
    text = re.sub(r'[^a-z0-9\s]', '', text.lower())
    return set(text.split())

def similarity(a: str, b: str) -> float:
    # Jaccard similarity for speed
    tokens_a = get_tokens(a)
    tokens_b = get_tokens(b)
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = tokens_a.intersection(tokens_b)
    union = tokens_a.union(tokens_b)
    return len(intersection) / len(union)

def deduplicate_and_correlate(data: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
    """
    1. Deduplicates titles across sources.
    2. Correlates ArXiv papers with GitHub repos (Fix 3).
    """
    clean_data = {k: [] for k in data.keys()}
    seen_titles_tokens = []
    
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
            
            # Cross-Source Deduplication using Jaccard Similarity
            is_dupe = False
            title_tokens = get_tokens(title)

            for seen_tokens in seen_titles_tokens:
                if not title_tokens or not seen_tokens:
                    continue
                intersection = title_tokens.intersection(seen_tokens)
                union = title_tokens.union(seen_tokens)
                if union and len(intersection) / len(union) > 0.65: # Adjusted threshold for Jaccard
                    is_dupe = True
                    break

            if is_dupe: continue
            
            # Fix 3: Cross-Source Correlation (Link Paper to Code)
            if section == "arxiv":
                # Look for repo implementation in abstract
                abstract = item.get("abstract", "").lower()
                for repo in github_repos:
                    repo_name = repo.get("name", "").split("/")[-1].lower()
                    if repo_name in abstract or similarity(repo_name, title) > 0.5: # Adjusted threshold
                        item["implemented_by"] = repo
                        repo["is_correlated"] = True # Mark so we don't show it twice

            seen_titles_tokens.append(title_tokens)
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
