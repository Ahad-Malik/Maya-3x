from typing import Dict, Any
from .workflow_graph import build_workflow_graph


def run_workflow_sync(initial_state: Dict[str, Any]) -> Dict[str, Any]:
    graph = build_workflow_graph()
    # Simple synchronous execution path through the linear graph for now
    state = initial_state.copy()
    state = graph.nodes["parse_user_intent"](state)
    state = graph.nodes["fetch_documents"](state)
    state = graph.nodes["summarize_notes"](state)
    state = graph.nodes["create_tasks"](state)
    return state


