"""
main.py — OmniBrief Orchestrator (V6.0 Agentic Engine)
"""

import asyncio
import traceback
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from config import (
    APP_BASE_URL,
    DATABASE_URL,
    MAX_BROADCAST_CONCURRENCY,
    NEWSLETTER_TOKEN_SECRET,
    OPENAI_API_KEY, RESEND_API_KEY,
    HN_MAX_ITEMS, ARXIV_MAX_ITEMS, GITHUB_TRENDING_MAX,
    RSS_MAX_PER_FEED, PRODUCTHUNT_MAX, REDDIT_MAX_ITEMS,
    ARXIV_CATEGORIES, RSS_FEEDS, GITHUB_QUERIES, GITHUB_TOKEN,
    REDDIT_SUBREDDITS, AI_ORGANIZATIONS
)
from src.fetchers.hackernews      import fetch_hackernews
from src.fetchers.arxiv           import fetch_arxiv
from src.fetchers.github_trending import fetch_github_trending
from src.fetchers.rss_feeds       import fetch_rss_feeds
from src.fetchers.producthunt     import fetch_producthunt
from src.fetchers.reddit          import fetch_reddit
from src.renderer                 import render_digest
from src.mailer                   import send_digest
from src.persistence              import (
    cleanup_history,
    cleanup_tokens,
    create_unsubscribe_link,
    ensure_default_subscriber,
    init_db,
    is_duplicate,
    list_active_subscribers_for_campaign,
    load_history,
    mark_sent,
    record_delivery,
)
from src.agent_graph              import create_graph


def validate_config() -> None:
    """Fail fast if required env vars are missing."""
    missing = []
    if not OPENAI_API_KEY: missing.append("OPENAI_API_KEY")
    if not RESEND_API_KEY: missing.append("RESEND_API_KEY")
    if not DATABASE_URL: missing.append("DATABASE_URL")
    if not APP_BASE_URL: missing.append("APP_BASE_URL")
    if not NEWSLETTER_TOKEN_SECRET: missing.append("NEWSLETTER_TOKEN_SECRET")
    if missing:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")


async def fetch_raw_data() -> tuple:
    """Runs all fast fetchers concurrently. Returns (data, stats)."""
    print("📡 Fetching content from all sources in parallel...\n")
    results = await asyncio.gather(
        fetch_hackernews(HN_MAX_ITEMS),
        fetch_rss_feeds(RSS_FEEDS, RSS_MAX_PER_FEED),
        fetch_arxiv(ARXIV_CATEGORIES, ARXIV_MAX_ITEMS),
        fetch_github_trending(GITHUB_QUERIES, GITHUB_TRENDING_MAX, GITHUB_TOKEN, organizations=AI_ORGANIZATIONS),
        fetch_producthunt(PRODUCTHUNT_MAX),
        fetch_reddit(REDDIT_SUBREDDITS, REDDIT_MAX_ITEMS),
        return_exceptions=True,
    )

    stats = {}
    def safe(result, label):
        if isinstance(result, Exception):
            print(f"  ⚠️  {label} fetch failed: {result}")
            stats[label] = "❌ Failed"
            return []
        print(f"  ✅ {label}: {len(result)} items")
        stats[label] = f"✅ {len(result)} items"
        return result

    data = {
        "hn":     safe(results[0], "Hacker News"),
        "news":   safe(results[1], "RSS News"),
        "arxiv":  safe(results[2], "ArXiv Papers"),
        "github": safe(results[3], "GitHub Trending"),
        "ph":     safe(results[4], "ProductHunt"),
        "reddit": safe(results[5], "Reddit"),
    }
    return data, stats


async def run() -> None:
    """Main pipeline: Fetch → Agentic Graph → Render → Send."""

    print("\n" + "="*58)
    print("  ⚡  OMNIBRIEF V6.0 — AGENTIC ENGINE ACTIVE")
    print("="*58 + "\n")

    # ── Step 1: Init ──────────────────────────────────────────
    validate_config()
    init_db()
    cleanup_tokens()
    ensure_default_subscriber()
    history = load_history()

    # ── Step 2: Parallel Fetch ────────────────────────────────
    raw_data, health_stats = await fetch_raw_data()
    
    # ── Step 3: Filter History ────────────────────────────────
    print("\n🧠 Filtering previously sent items...")
    filtered_data = {k: [] for k in raw_data.keys()}
    for section, items in raw_data.items():
        for item in items:
            if not is_duplicate(item.get("url", ""), history):
                filtered_data[section].append(item)
    
    # ── Step 4: Run LangGraph Engine ───────────────────────────
    graph = create_graph()

    initial_state = {
        "raw_data": filtered_data,
        "health_stats": health_stats,
        "ranked_data": {},
        "summarized_data": {},
        "synthesis": "",
        "iterations": 0
    }

    from datetime import datetime
    today_id = datetime.now().strftime("%Y-%m-%d")
    config = {"configurable": {"thread_id": today_id}}

    print(f"\n🚀 Executing Intelligence Graph (Thread: {today_id})...")
    final_state = await graph.ainvoke(initial_state, config=config)
    
    # ── Step 5: Render & Deliver ──────────────────────────────
    summarized = final_state["summarized_data"]
    total_items = sum(len(v) for v in summarized.values())
    
    if total_items == 0:
        print("📭 No new unique items found. Skipping email.")
        return

    from datetime import datetime

    campaign_key = datetime.now().strftime("%Y-%m-%d")
    subscribers = list_active_subscribers_for_campaign(campaign_key)
    if not subscribers:
        print("📭 No active subscribers found for this campaign. Skipping email.")
        return

    print(f"\n🎨 Rendering and Delivering {total_items} items to {len(subscribers)} subscribers...")

    semaphore = asyncio.Semaphore(MAX_BROADCAST_CONCURRENCY)

    async def deliver_to_subscriber(subscriber: dict) -> tuple[bool, str]:
        async with semaphore:
            unsubscribe_url = create_unsubscribe_link(subscriber["id"])
            html = render_digest(
                summarized,
                health_stats,
                final_state["synthesis"],
                unsubscribe_url=unsubscribe_url,
            )
            try:
                result = await send_digest(html, subscriber["email"])
                record_delivery(
                    subscriber["id"],
                    campaign_key,
                    status="sent",
                    resend_message_id=result.get("id"),
                )
                return True, subscriber["email"]
            except Exception as exc:
                record_delivery(
                    subscriber["id"],
                    campaign_key,
                    status="failed",
                    error=str(exc)[:1000],
                )
                print(f"  ⚠️ Delivery failed for {subscriber['email']}: {exc}")
                return False, subscriber["email"]

    delivery_results = await asyncio.gather(*(deliver_to_subscriber(s) for s in subscribers))
    sent_count = sum(1 for ok, _ in delivery_results if ok)
    failed_count = len(delivery_results) - sent_count

    print(f"📬 Broadcast complete: {sent_count} sent, {failed_count} failed.")
    if sent_count == 0:
        raise RuntimeError("Digest generation completed, but delivery failed for all subscribers.")
    
    # Commit to history
    for section, items in summarized.items():
        for item in items:
            mark_sent(
                item.get("url", ""),
                title=item.get("title") or item.get("name", ""),
                source=item.get("source", ""),
                section=section,
            )
    
    cleanup_history()
    
    # PRIVATE COST AUDIT (Step 7)
    from src.cost_tracker import tracker
    print(tracker.get_summary())

    print("\n" + "="*58)
    print("  ✅  OMNIBRIEF DELIVERED SUCCESSFULLY")
    print("="*58 + "\n")


async def main() -> None:
    try:
        await run()
    except Exception as e:
        print(f"\n❌ Fatal error:\n{traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
