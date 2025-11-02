from typing import TypedDict, List, Dict, Any


class WorkflowState(TypedDict, total=False):
    current_step: str
    input_text: str
    documents: List[str]
    summary: str
    tasks: List[str]
    status: str
    history: List[Dict[str, Any]]  # step-wise outputs for persistence


