"""
MCP (Model Context Protocol) Integration Module
Provides structured interfaces for external tool sources
"""

from .base_mcp_tool import BaseMCPTool
from .notion_mcp import NotionTool

__all__ = ['BaseMCPTool', 'NotionTool']
