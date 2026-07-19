"""
src/agent_graph.py
The LangGraph Intelligence Engine.
V7.2: LLM-based Ranking, Routing, and Cost Tracking.
"""

import json
import os
from typing import Any, Dict, List, TypedDict

from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from config import (
    ARXIV_MAX_ITEMS,
    GITHUB_TRENDING_MAX,
    HN_MAX_ITEMS,
    OPENAI_API_KEY,
    PRODUCTHUNT_MAX,
    REDDIT_MAX_ITEMS,
)
from src.cost_tracker import tracker
from src.logger import logger


class AgentState(TypedDict):
    raw_data: Dict[str, List[Dict[str, Any]]]
    ranked_data: Dict[str, List[Dict[str, Any]]]
    summarized_data: Dict[str, List[Dict[str, Any]]]
    synthesis: str
    health_stats: Dict[str, str]
    revision_needed: bool
    iterations: int
    flagged_items: List[str]

# Intelligence Routing
cheap_llm = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-4o-mini", temperature=0)

# ─── NODES ──────────────────────────────────────────────────────────────────

def curation_node(state: AgentState):
    logger.info("  🧠 Graph: Initial curation and deduplication...")
    from src.processor import deduplicate_and_correlate
    processed = deduplicate_and_correlate(state["raw_data"])
    counts = {k: len(v) for k, v in processed.items()}
    logger.info(f"    ✅ Curation complete. Counts: {counts}")
    return {"raw_data": processed, "iterations": 0}

async def ranking_node(state: AgentState):
    """Personalized technical novelty ranking using PROFILE.md."""
    logger.info("  ⭐ Graph: AI performing personalized novelty ranking...")

    # Load Profile for Nuance
    profile_path = os.path.join(os.path.dirname(__file__), "..", "PROFILE.md")
    try:
        with open(profile_path, "r") as f:
            profile_content = f.read()
    except Exception:
        profile_content = "Prioritize innovative AI research and Python code."

    all_candidates = []
    for section, items in state["raw_data"].items():
        for i in items:
            title = i.get("title") or i.get("name")
            desc = i.get("description") or i.get("abstract") or i.get("summary") or ""
            all_candidates.append({"id": i.get("url"), "section": section, "content": f"{title}: {desc[:200]}"})

    if not all_candidates:
        return {"ranked_data": {k: [] for k in state["raw_data"].keys()}}

    # Comprehensive Prompt with Profile
    prompt = f"""You are an elite technical curator. Score these {len(all_candidates)} AI items from 1-10.
User Interest Profile:
{profile_content}

Scoring Rules:
1. High Score (9-10) for breakthrough innovation matching the user's focus (Agents, Efficiency, Implementation).
2. Medium Score (5-7) for solid technical news or trending repositories.
3. Low Score (1-3) for marketing fluff, generic 'top list' tools, or off-topic items.

Return ONLY a JSON list of IDs and their scores like: [{{"id": "url", "score": 9.5}}, ...]
Items:
{json.dumps(all_candidates[:50])}"""

    score_map = {}
    try:
        resp = await cheap_llm.ainvoke(prompt)
        # TRACK COST
        if resp.usage_metadata:
            tracker.log_usage("gpt-4o-mini", resp.usage_metadata.get("input_tokens", 0), resp.usage_metadata.get("output_tokens", 0))

        raw_content = resp.content.strip()
        if "```json" in raw_content:
            raw_content = raw_content.split("```json")[1].split("```")[0].strip()
        scores_list = json.loads(raw_content)
        score_map = {item['id']: item['score'] for item in scores_list}
    except Exception as e:
        logger.warning(f"    ⚠️ Ranking LLM failed, falling back to heuristic: {e}")

    # Heuristic fallback for unranked items (stars/score/votes)
    for section, items in state["raw_data"].items():
        for item in items:
            url = item.get("url")
            if url and url not in score_map:
                score_map[url] = item.get("stars", 0) or item.get("score", 0) or item.get("votes", 0) or 0

    ranked_final = {k: [] for k in state["raw_data"].keys()}
    for section, items in state["raw_data"].items():
        sorted_items = sorted(items, key=lambda x: score_map.get(x.get("url"), 0), reverse=True)
        section_limit = {
            "hn": HN_MAX_ITEMS, "arxiv": ARXIV_MAX_ITEMS, "github": GITHUB_TRENDING_MAX,
            "ph": PRODUCTHUNT_MAX, "reddit": REDDIT_MAX_ITEMS,
        }
        limit = section_limit.get(section, 8)
        ranked_final[section] = sorted_items[:limit]

    picks = {k: len(v) for k, v in ranked_final.items()}
    logger.info(f"    ✅ Ranking complete. Picks: {picks}")
    return {"ranked_data": ranked_final}

async def analyst_node(state: AgentState):
    logger.info(f"  🤖 Graph: Generating technical summaries (Attempt {state.get('iterations', 0) + 1})...")
    from src.scraper import enrich_items
    from src.summarizer import summarize_all

    ranked = state["ranked_data"]
    flagged = state.get("flagged_items", [])
    iterations = state.get("iterations", 0)

    if iterations == 0:
        logger.info("    🔍 Scraping full text for top items...")
        ranked["news"]   = await enrich_items(ranked.get("news", []), max_scrape=8)
        ranked["github"] = await enrich_items(ranked.get("github", []), max_scrape=8)

    if iterations > 0 and flagged:
        flagged_set = set(flagged)
        prev = state["summarized_data"]
        to_rerun = {s: [i for i in items if i.get("url") in flagged_set] for s, items in ranked.items()}
        kept = {s: [i for i in items if i.get("url") not in flagged_set] for s, items in prev.items()}
        new_summaries = await summarize_all(to_rerun)
        merged = {}
        for s in set(list(kept.keys()) + list(new_summaries.keys())):
            merged[s] = kept.get(s, []) + new_summaries.get(s, [])
        return {"summarized_data": merged, "iterations": iterations + 1}

    summarized = await summarize_all(ranked)
    return {"summarized_data": summarized, "iterations": iterations + 1}

async def critic_node(state: AgentState):
    logger.info("  ⚖️  Graph: Critic reviewing summaries...")
    all_items = []
    for items in state["summarized_data"].values():
        all_items.extend(items)
    if not all_items:
        return {"revision_needed": False, "flagged_items": []}
    poor_quality = []
    for item in all_items:
        summary = item.get("ai_summary", "").lower()
        if len(summary) < 60 or not any(kw in summary for kw in ["introduc", "propos", "method", "approach", "framework", "technique", "system", "model", "architecture", "algorithm", "dataset", "experiment", "result", "achieve", "outperform"]):  # noqa: E501
            poor_quality.append(item.get("url", ""))
    if poor_quality and state["iterations"] < 2:
        logger.warning(f"    ⚠️ Critic requested revision for {len(poor_quality)} items.")
        return {"revision_needed": True, "flagged_items": poor_quality}
    logger.info("    ✅ Critic approved all summaries.")
    return {"revision_needed": False, "flagged_items": []}

async def synthesis_node(state: AgentState):
    logger.info("  ✍️ Graph: Synthesizing trends using Ph.D. level model (GPT-4o)...")
    from src.summarizer import generate_executive_synthesis
    report, usage = await generate_executive_synthesis(state["summarized_data"], return_usage=True)

    # TRACK COST
    if usage:
        tracker.log_usage("gpt-4o", usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0))

    return {"synthesis": report}

def should_continue(state: AgentState):
    return "analyze" if state.get("revision_needed") else "synthesize"

def _build_graph(checkpointer=None):
    workflow = StateGraph(AgentState)
    workflow.add_node("curate", curation_node)
    workflow.add_node("rank", ranking_node)
    workflow.add_node("analyze", analyst_node)
    workflow.add_node("criticize", critic_node)
    workflow.add_node("synthesize", synthesis_node)
    workflow.set_entry_point("curate")
    workflow.add_edge("curate", "rank")
    workflow.add_edge("rank", "analyze")
    workflow.add_edge("analyze", "criticize")
    workflow.add_conditional_edges("criticize", should_continue, {"analyze": "analyze", "synthesize": "synthesize"})
    workflow.add_edge("synthesize", END)
    return workflow.compile(checkpointer=checkpointer)

# Module-level singleton — compiled once at import time with memory
graph = _build_graph(checkpointer=MemorySaver())

def create_graph(checkpointer=None):
    if checkpointer:
        return _build_graph(checkpointer=checkpointer)
    return graph
