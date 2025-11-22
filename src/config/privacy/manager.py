"""
Maya Private - Privacy Manager
Routes inference between local (WebLLM/ONNX) and cloud (OpenAI) based on context size.
Logs all offload events for transparency.
"""

from flask import Blueprint, request, jsonify
import os
import time
from datetime import datetime

bp = Blueprint("privacy", __name__)

# Local/offload thresholds
LOCAL_CONTEXT_LIMIT = 2000
OFFLOAD_LOG_PATH = "logs/offload_events.log"

# Ensure log directory exists
os.makedirs(os.path.dirname(OFFLOAD_LOG_PATH), exist_ok=True)


@bp.route("/privacy/execute", methods=["POST"])
def execute_private():
    """
    Execute private inference with automatic routing:
    - Short prompts (<2000 chars) -> Local inference
    - Long prompts (>=2000 chars) -> Cloud inference (with logging)
    """
    try:
        data = request.json
        prompt = data.get("prompt", "")
        context_len = len(prompt)
        
        if not prompt:
            return jsonify({
                "success": False,
                "error": "Missing required field: 'prompt'"
            }), 400
        
        # Decide execution mode based on context length
        if context_len < LOCAL_CONTEXT_LIMIT:
            # Route to local inference (WebLLM / ONNX / TinyLLM)
            try:
                from privacy.local_inference import run_local
                result = run_local(prompt)
                mode = "local"
            except Exception as e:
                # Fallback to cloud if local inference fails
                from privacy.remote_inference import run_cloud
                result = run_cloud(prompt)
                mode = "offloaded (local failed)"
                log_offload_event(mode, context_len, str(e))
        else:
            # Route to cloud inference (OpenAI fallback)
            from privacy.remote_inference import run_cloud
            result = run_cloud(prompt)
            mode = "offloaded"
            log_offload_event(mode, context_len, "Context too large")
        
        return jsonify({
            "success": True,
            "mode": mode,
            "output": result,
            "context_length": context_len,
            "threshold": LOCAL_CONTEXT_LIMIT
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route("/privacy/status", methods=["GET"])
def get_privacy_status():
    """
    Get privacy mode status and configuration.
    """
    try:
        # Check if log file exists
        log_exists = os.path.exists(OFFLOAD_LOG_PATH)
        
        # Count offload events if log exists
        offload_count = 0
        if log_exists:
            with open(OFFLOAD_LOG_PATH, "r") as f:
                offload_count = len(f.readlines())
        
        return jsonify({
            "success": True,
            "status": "active",
            "context_limit": LOCAL_CONTEXT_LIMIT,
            "offload_logging": True,
            "total_offloads": offload_count,
            "log_path": OFFLOAD_LOG_PATH
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route("/privacy/logs", methods=["GET"])
def get_offload_logs():
    """
    Retrieve recent offload events log.
    """
    try:
        if not os.path.exists(OFFLOAD_LOG_PATH):
            return jsonify({
                "success": True,
                "logs": [],
                "message": "No offload events logged yet"
            })
        
        # Read last N lines (default 50)
        limit = request.args.get("limit", 50, type=int)
        
        with open(OFFLOAD_LOG_PATH, "r") as f:
            lines = f.readlines()
        
        # Return most recent entries
        recent_logs = lines[-limit:]
        
        return jsonify({
            "success": True,
            "logs": [line.strip() for line in recent_logs],
            "total": len(lines)
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


def log_offload_event(mode: str, context_len: int, reason: str = ""):
    """
    Log every offload event to file with timestamp.
    """
    try:
        timestamp = datetime.now().strftime("%a %b %d %H:%M:%S %Y")
        log_entry = f"[{timestamp}] Mode={mode} | Len={context_len}"
        
        if reason:
            log_entry += f" | Reason={reason}"
        
        log_entry += "\n"
        
        with open(OFFLOAD_LOG_PATH, "a") as f:
            f.write(log_entry)
    
    except Exception as e:
        print(f"Warning: Failed to log offload event: {e}")
