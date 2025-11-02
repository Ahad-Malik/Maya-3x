from typing import Dict, Any
from .workflow_state import WorkflowState


def _append_history(state: WorkflowState, step: str, output: Dict[str, Any]) -> None:
    history = state.get("history", [])
    history.append({"step": step, "output": output})
    state["history"] = history


def parse_user_intent(state: WorkflowState) -> WorkflowState:
    input_text = state.get("input_text", "")
    intent = "summarize_and_schedule" if "summar" in input_text.lower() else "generic"
    state["current_step"] = "fetch_documents"
    _append_history(state, "parse_user_intent", {"intent": intent})
    return state


def fetch_documents(state: WorkflowState) -> WorkflowState:
    # Placeholder: integrate RAG/doc fetch
    docs = ["meeting_notes_1.txt", "meeting_notes_2.txt"]
    state["documents"] = docs
    state["current_step"] = "summarize_notes"
    _append_history(state, "fetch_documents", {"documents": docs})
    return state


def summarize_notes(state: WorkflowState) -> WorkflowState:
    # Placeholder: call LLM summarizer
    summary = "Key decisions and action items extracted."
    state["summary"] = summary
    state["current_step"] = "create_tasks"
    _append_history(state, "summarize_notes", {"summary": summary})
    return state


def create_tasks(state: WorkflowState) -> WorkflowState:
    # Placeholder: integrate Google Calendar/Notion
    tasks = ["Follow up with team", "Schedule sync next Tuesday"]
    state["tasks"] = tasks
    state["current_step"] = "complete"
    state["status"] = "completed"
    _append_history(state, "create_tasks", {"tasks": tasks})
    return state


