from langgraph.graph import StateGraph
from .workflow_state import WorkflowState
from .workflow_nodes import (
    parse_user_intent,
    fetch_documents,
    summarize_notes,
    create_tasks,
)


def build_workflow_graph() -> StateGraph:
    graph = StateGraph(WorkflowState)

    graph.add_node("parse_user_intent", parse_user_intent)
    graph.add_node("fetch_documents", fetch_documents)
    graph.add_node("summarize_notes", summarize_notes)
    graph.add_node("create_tasks", create_tasks)

    graph.add_edge("parse_user_intent", "fetch_documents")
    graph.add_edge("fetch_documents", "summarize_notes")
    graph.add_edge("summarize_notes", "create_tasks")

    graph.set_entry_point("parse_user_intent")
    return graph


