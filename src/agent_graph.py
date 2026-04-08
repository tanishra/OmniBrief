"""
src/agent_graph.py
The LangGraph Intelligence Engine.
V7.2: LLM-based Ranking, Routing, and Cost Tracking.
"""

import json
from typing import List, Dict, Any, TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from config import OPENAI_API_KEY
from src.cost_tracker import tracker

class AgentState(TypedDict):
    raw_data: Dict[str, List[Dict[str, Any]]]
    ranked_data: Dict[str, List[Dict[str, Any]]]
    summarized_data: Dict[str, List[Dict[str, Any]]]
    synthesis: str
    health_stats: Dict[str, str]
    revision_needed: bool
    iterations: int

# Intelligence Routing
cheap_llm = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-4o-mini", temperature=0)
smart_llm = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-4o", temperature=0.3)

# ─── NODES ──────────────────────────────────────────────────────────────────

def curation_node(state: AgentState):
    print("  🧠 Graph: Initial curation and deduplication...")
    from src.processor import deduplicate_and_correlate
    processed = deduplicate_and_correlate(state["raw_data"])
    counts = {k: len(v) for k, v in processed.items()}
    print(f"    ✅ Curation complete. Counts: {counts}")
    return {"raw_data": processed, "iterations": 0}

async def ranking_node(state: AgentState):
    """Personalized technical novelty ranking using PROFILE.md."""
    print("  ⭐ Graph: AI performing personalized novelty ranking...")
    
    # Load Profile for Nuance
    try:
        with open("PROFILE.md", "r") as f:
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
        print(f"    ⚠️ Ranking LLM failed: {e}")

    ranked_final = {k: [] for k in state["raw_data"].keys()}
    for section, items in state["raw_data"].items():
        sorted_items = sorted(items, key=lambda x: score_map.get(x.get("url"), 0), reverse=True)
        limit = 12 if section in ["arxiv", "github"] else 8
        ranked_final[section] = sorted_items[:limit]

    print(f"    ✅ Ranking complete. Picks: {{k: len(v) for k, v in ranked_final.items()}}")
    return {"ranked_data": ranked_final}

async def analyst_node(state: AgentState):
    print(f"  🤖 Graph: Generating technical summaries (Attempt {state.get('iterations', 0) + 1})...")
    from src.summarizer import summarize_all
    from src.scraper import enrich_items
    
    ranked = state["ranked_data"]
    if state.get("iterations", 0) == 0:
        print("    🔍 Scraping full text for top items...")
        ranked["news"]   = await enrich_items(ranked.get("news", []), max_scrape=8)
        ranked["github"] = await enrich_items(ranked.get("github", []), max_scrape=8)
    
    summarized = await summarize_all(ranked)
    return {"summarized_data": summarized, "iterations": state.get("iterations", 0) + 1}

async def critic_node(state: AgentState):
    print("  ⚖️  Graph: Critic reviewing summaries...")
    all_items = []
    for items in state["summarized_data"].values(): all_items.extend(items)
    if not all_items: return {"revision_needed": False}
    poor_quality = 0
    for item in all_items:
        summary = item.get("ai_summary", "").lower()
        if len(summary) < 60 or not any(kw in summary for kw in ["python", "library", "architecture", "model", "code"]):
            poor_quality += 1
    if poor_quality > (len(all_items) * 0.2) and state["iterations"] < 2:
        print(f"    ⚠️ Critic requested revision for {poor_quality} items.")
        return {"revision_needed": True}
    print("    ✅ Critic approved all summaries.")
    return {"revision_needed": False}

async def synthesis_node(state: AgentState):
    print("  ✍️ Graph: Synthesizing trends using Ph.D. level model (GPT-4o)...")
    from src.summarizer import generate_executive_synthesis
    report, usage = await generate_executive_synthesis(state["summarized_data"], return_usage=True)
    
    # TRACK COST
    if usage:
        tracker.log_usage("gpt-4o", usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0))
        
    return {"synthesis": report}

def should_continue(state: AgentState):
    return "analyze" if state.get("revision_needed") else "synthesize"

def create_graph(checkpointer=None):
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
