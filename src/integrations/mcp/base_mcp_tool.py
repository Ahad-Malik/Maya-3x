"""
Base MCP Tool class
Provides the abstract interface for all MCP-compatible tools
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class BaseMCPTool(ABC):
    """
    Abstract base class for MCP tools.
    All MCP tools should inherit from this class and implement the required methods.
    """

    def __init__(self, name: str):
        self.name = name
        logger.info(f"Initialized MCP tool: {name}")

    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """
        Returns the JSON schema for this tool's input parameters.
        
        Returns:
            Dict[str, Any]: JSON schema object
        """
        pass

    @abstractmethod
    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the tool with the given payload.
        
        Args:
            payload: Dictionary containing the tool's parameters
            
        Returns:
            Dict[str, Any]: Result dictionary with success status and data
        """
        pass

    def validate_payload(self, payload: Dict[str, Any]) -> bool:
        """
        Validate the payload against the tool's schema.
        Basic validation - can be overridden for more complex validation.
        
        Args:
            payload: The payload to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        schema = self.get_schema()
        required_fields = schema.get('required', [])
        
        # Check if all required fields are present
        for field in required_fields:
            if field not in payload:
                logger.error(f"Missing required field: {field}")
                return False
        
        return True

    def log_execution(self, action: str, success: bool, duration_ms: float, error: str = None):
        """
        Log tool execution details.
        
        Args:
            action: The action that was executed
            success: Whether the execution was successful
            duration_ms: Execution time in milliseconds
            error: Error message if execution failed
        """
        log_msg = f"MCP Tool [{self.name}] - Action: {action}, Success: {success}, Duration: {duration_ms:.2f}ms"
        if error:
            log_msg += f", Error: {error}"
        
        if success:
            logger.info(log_msg)
        else:
            logger.error(log_msg)
