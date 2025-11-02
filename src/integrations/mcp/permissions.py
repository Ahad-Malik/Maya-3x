"""
MCP Permissions and Validation Module
Enforces security policies for MCP tool execution
"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

# Define allowed actions for each MCP tool
ALLOWED_ACTIONS: Dict[str, List[str]] = {
    "notion": ["search", "read", "update"],
    # Add more tools here as they are implemented
    # "slack": ["send_message", "read_channel", "list_channels"],
    # "calendar": ["list_events", "create_event", "update_event"],
}

# Define tools that require additional permissions
RESTRICTED_TOOLS: Dict[str, List[str]] = {
    "notion": ["update"],  # Update actions need extra validation
}


def validate_mcp(tool: str, action: str) -> bool:
    """
    Validate that a tool and action combination is allowed.
    
    Args:
        tool: The name of the MCP tool (e.g., "notion")
        action: The action to be performed (e.g., "search", "read", "update")
        
    Returns:
        bool: True if the action is allowed for the tool, False otherwise
    """
    # Check if tool exists in allowed actions
    if tool not in ALLOWED_ACTIONS:
        logger.warning(f"MCP validation failed: Unknown tool '{tool}'")
        return False
    
    # Check if action is allowed for this tool
    allowed_actions = ALLOWED_ACTIONS.get(tool, [])
    if action not in allowed_actions:
        logger.warning(f"MCP validation failed: Action '{action}' not allowed for tool '{tool}'")
        return False
    
    logger.info(f"MCP validation passed: tool='{tool}', action='{action}'")
    return True


def is_restricted_action(tool: str, action: str) -> bool:
    """
    Check if an action is restricted and requires additional validation.
    
    Args:
        tool: The name of the MCP tool
        action: The action to be performed
        
    Returns:
        bool: True if the action is restricted, False otherwise
    """
    if tool not in RESTRICTED_TOOLS:
        return False
    
    return action in RESTRICTED_TOOLS.get(tool, [])


def validate_payload_schema(tool: str, payload: Dict) -> tuple[bool, str]:
    """
    Validate the payload structure for a specific tool.
    
    Args:
        tool: The name of the MCP tool
        payload: The payload to validate
        
    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    # Check if action is present
    if "action" not in payload:
        return False, "Missing required field: 'action'"
    
    action = payload["action"]
    
    # Validate based on tool and action
    if tool == "notion":
        if action == "search":
            if "query" not in payload:
                return False, "Missing required field for search: 'query'"
        elif action == "read":
            if "page_id" not in payload:
                return False, "Missing required field for read: 'page_id'"
        elif action == "update":
            if "page_id" not in payload:
                return False, "Missing required field for update: 'page_id'"
            if "data" not in payload:
                return False, "Missing required field for update: 'data'"
    
    return True, ""


def sanitize_payload(payload: Dict) -> Dict:
    """
    Sanitize the payload to prevent injection attacks.
    Basic sanitization - can be extended for more complex needs.
    
    Args:
        payload: The payload to sanitize
        
    Returns:
        Dict: Sanitized payload
    """
    # Create a copy to avoid modifying the original
    sanitized = payload.copy()
    
    # Basic string sanitization for text fields
    text_fields = ["query", "title", "content"]
    for field in text_fields:
        if field in sanitized and isinstance(sanitized[field], str):
            # Remove potentially dangerous characters
            sanitized[field] = sanitized[field].strip()
    
    return sanitized


def log_mcp_request(tool: str, action: str, user_id: str = None, success: bool = True):
    """
    Log MCP request for audit purposes.
    
    Args:
        tool: The name of the MCP tool
        action: The action performed
        user_id: Optional user identifier
        success: Whether the request was successful
    """
    log_entry = f"MCP Request - Tool: {tool}, Action: {action}"
    if user_id:
        log_entry += f", User: {user_id}"
    log_entry += f", Success: {success}"
    
    if success:
        logger.info(log_entry)
    else:
        logger.warning(log_entry)
