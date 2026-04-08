"""
src/renderer.py
Renders the Jinja2 HTML email template with all digest sections.
V5: Added executive synthesis and hybrid scraping support.
"""

import os
from typing import Dict, List, Any
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")


def render_digest(
    summarized_data: Dict[str, List[Dict[str, Any]]],
    health_stats: Dict = None,
    synthesis: str = "",
    unsubscribe_url: str = "",
) -> str:
    """
    Takes the summarized digest data and renders it into the HTML email template.
    """
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(["html"]),
    )
    template = env.get_template("digest.html")

    hn_items     = summarized_data.get("hn", [])
    news_items   = summarized_data.get("news", [])
    arxiv_items  = summarized_data.get("arxiv", [])
    github_items = summarized_data.get("github", [])
    ph_items     = summarized_data.get("ph", [])
    reddit_items = summarized_data.get("reddit", [])

    total_items   = sum(len(v) for v in summarized_data.values())
    
    stats = {
        "papers":   len(arxiv_items),
        "repos":    len(github_items),
        "news":     len(hn_items) + len(news_items),
        "products": len(ph_items),
        "reddit":   len(reddit_items),
    }

    date_str = datetime.now().strftime("%A, %B %d, %Y")

    html = template.render(
        date          = date_str,
        total_items   = total_items,
        stats         = stats,
        hn_items      = hn_items,
        news_items    = news_items,
        arxiv_items   = arxiv_items,
        github_items  = github_items,
        ph_items      = ph_items,
        reddit_items  = reddit_items,
        health        = health_stats or {},
        synthesis     = synthesis,
        unsubscribe_url = unsubscribe_url,
    )

    return html
