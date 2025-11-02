import uuid
from flask import Blueprint, request, jsonify
from .executor import run_workflow_sync
from .db_ops import save_workflow_metadata, get_workflow_metadata


maya_studio_bp = Blueprint("maya_studio", __name__, url_prefix="/maya_studio")


@maya_studio_bp.route("/start_workflow", methods=["POST"])
def start_workflow():
    body = request.get_json(silent=True) or {}
    input_text = body.get("input_text", "")

    workflow_id = body.get("workflow_id") or str(uuid.uuid4())
    save_workflow_metadata(workflow_id, status="in_progress")

    # For now, execute synchronously (non-blocking in prod with Temporal)
    final_state = run_workflow_sync({"input_text": input_text, "status": "running", "history": []})
    save_workflow_metadata(
        workflow_id,
        status=final_state.get("status", "completed"),
        output=final_state.get("summary"),
        history=final_state.get("history", []),
    )

    return jsonify({"workflow_id": workflow_id, "status": "started"})


@maya_studio_bp.route("/get_workflow_status/<workflow_id>", methods=["GET"])
def get_status(workflow_id: str):
    record = get_workflow_metadata(workflow_id)
    if not record:
        return jsonify({"error": "not_found"}), 404
    return jsonify(
        {
            "workflow_id": record.id,
            "status": record.status,
            "start_time": record.start_time.isoformat() if record.start_time else None,
            "output": record.output,
            "history": record.history or [],
        }
    )


