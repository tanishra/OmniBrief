from src.agent_graph import AgentState, create_graph, _build_graph


def test_agent_state_has_required_keys():
    state: AgentState = {
        "raw_data": {},
        "ranked_data": {},
        "summarized_data": {},
        "synthesis": "",
        "health_stats": {},
        "revision_needed": False,
        "iterations": 0,
        "flagged_items": [],
    }
    assert state["raw_data"] == {}
    assert state["iterations"] == 0
    assert state["flagged_items"] == []


def test_build_graph_returns_compiled_graph():
    graph = _build_graph()
    assert graph is not None
    assert hasattr(graph, "invoke")


def test_create_graph_returns_singleton():
    g1 = create_graph()
    g2 = create_graph()
    assert g1 is g2


def test_create_graph_with_custom_checkpointer():
    from langgraph.checkpoint.memory import MemorySaver
    custom = MemorySaver()
    graph = create_graph(checkpointer=custom)
    assert graph is not None
    assert hasattr(graph, "invoke")
