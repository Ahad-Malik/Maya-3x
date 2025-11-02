from typing import Optional, Dict, Any
from .models import db, WorkflowMetadata


def save_workflow_metadata(
    workflow_id: str,
    status: str,
    output: Optional[str] = None,
    history: Optional[list] = None,
) -> None:
    record = WorkflowMetadata.query.get(workflow_id)
    if record is None:
        record = WorkflowMetadata(id=workflow_id, status=status)
        db.session.add(record)
    record.status = status
    if output is not None:
        record.output = output
    if history is not None:
        record.history = history
    db.session.commit()


def get_workflow_metadata(workflow_id: str) -> Optional[WorkflowMetadata]:
    return WorkflowMetadata.query.get(workflow_id)


