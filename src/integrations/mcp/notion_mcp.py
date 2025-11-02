"""
Notion MCP Tool Implementation
Provides integration with Notion API for searching, reading, and updating pages
"""

import os
import time
import logging
from typing import Dict, Any, List, Optional
from notion_client import Client
from notion_client.errors import APIResponseError

from .base_mcp_tool import BaseMCPTool

logger = logging.getLogger(__name__)


class NotionTool(BaseMCPTool):
    """
    MCP Tool for Notion integration.
    Supports searching, reading, and updating Notion pages.
    """

    def __init__(self):
        super().__init__("notion")
        self.token = os.getenv('NOTION_MCP_TOKEN')
        if not self.token:
            logger.error("NOTION_MCP_TOKEN not found in environment variables")
            raise ValueError("NOTION_MCP_TOKEN is required for Notion integration")
        
        self.client = Client(auth=self.token)
        logger.info("Notion client initialized successfully")

    def get_schema(self) -> Dict[str, Any]:
        """
        Returns the JSON schema for Notion tool operations.
        """
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["search", "read", "update"],
                    "description": "The action to perform: search pages, read page content, or update page"
                },
                "query": {
                    "type": "string",
                    "description": "Search query string (required for 'search' action)"
                },
                "page_id": {
                    "type": "string",
                    "description": "Notion page ID (required for 'read' and 'update' actions)"
                },
                "data": {
                    "type": "object",
                    "description": "Update data (required for 'update' action)"
                }
            },
            "required": ["action"]
        }

    def fetch_notion_pages(self, query: str) -> List[Dict[str, Any]]:
        """
        Search Notion pages using the Notion API.
        
        Args:
            query: Search query string (empty string returns all pages)
            
        Returns:
            List of page results with id, title, and url
        # """
        try:
            logger.info(f"🔍 Searching Notion pages with query: '{query}'")
            
            # If query is empty or just whitespace, search all pages
            search_params = {
                "filter": {"property": "object", "value": "page"},
                "sort": {"direction": "descending", "timestamp": "last_edited_time"},
                "page_size": 20  # Limit results
            }
            
            # Only add query if it's not empty
            if query and query.strip():
                search_params["query"] = query
            
            logger.info(f"📤 Sending Notion API request with params: {search_params}")
            response = self.client.search(**search_params)
            
            logger.info(f"📥 Raw Notion API response: has_more={response.get('has_more')}, object={response.get('object')}, results_count={len(response.get('results', []))}")
            
            # Debug: Log first result if any
            if response.get("results"):
                first_result = response["results"][0]
                logger.info(f"📄 First result sample: id={first_result.get('id')}, object={first_result.get('object')}, archived={first_result.get('archived')}")
            else:
                logger.warning(f"⚠️ No results returned from Notion API for query: '{query}'")
            
            results = []
            for page in response.get("results", []):
                page_data = {
                    "id": page["id"],
                    "url": page.get("url", ""),
                    "title": self._extract_title(page),
                    "last_edited_time": page.get("last_edited_time", ""),
                    "created_time": page.get("created_time", "")
                }
                results.append(page_data)
            
            logger.info(f"✅ Found {len(results)} pages for query '{query}'")
            return results
            
        except APIResponseError as e:
            logger.error(f"Notion API error during search: {e}")
            raise
        except Exception as e:
            logger.error(f"Error searching Notion pages: {e}")
            raise

    def get_notion_page(self, page_id: str) -> Dict[str, Any]:
        """
        Retrieve a Notion page's content by ID.
        
        Args:
            page_id: The Notion page ID
            
        Returns:
            Dictionary containing page metadata and content
        """
        try:
            logger.info(f"Retrieving Notion page: {page_id}")
            
            # Get page metadata
            page = self.client.pages.retrieve(page_id=page_id)
            
            # Get page content (blocks)
            blocks_response = self.client.blocks.children.list(block_id=page_id)
            blocks = blocks_response.get("results", [])
            
            # Extract text content from blocks
            content = self._extract_content_from_blocks(blocks)
            
            page_data = {
                "id": page["id"],
                "url": page.get("url", ""),
                "title": self._extract_title(page),
                "content": content,
                "blocks": blocks,  # Include raw blocks for frontend processing
                "last_edited_time": page.get("last_edited_time", ""),
                "created_time": page.get("created_time", "")
            }
            
            logger.info(f"✅ Successfully retrieved page: {page_data['title']} with {len(blocks)} blocks")
            return page_data
            
        except APIResponseError as e:
            logger.error(f"Notion API error retrieving page: {e}")
            raise
        except Exception as e:
            logger.error(f"Error retrieving Notion page: {e}")
            raise

    def update_notion_page(self, page_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a Notion page's properties or content.
        
        Args:
            page_id: The Notion page ID
            data: Dictionary containing update data (properties to update)
            
        Returns:
            Updated page information
        """
        try:
            logger.info(f"Updating Notion page: {page_id}")
            
            # Prepare properties for update
            properties = {}
            if "title" in data:
                properties["title"] = {
                    "title": [{"text": {"content": data["title"]}}]
                }
            
            # Add any other properties from data
            for key, value in data.items():
                if key != "title" and key != "content":
                    # Handle different property types
                    if isinstance(value, str):
                        properties[key] = {"rich_text": [{"text": {"content": value}}]}
            
            # Update page properties
            if properties:
                page = self.client.pages.update(page_id=page_id, properties=properties)
            else:
                page = self.client.pages.retrieve(page_id=page_id)
            
            # Append content if provided
            if "content" in data and data["content"]:
                self._append_content_to_page(page_id, data["content"])
            
            result = {
                "id": page["id"],
                "url": page.get("url", ""),
                "title": self._extract_title(page),
                "success": True,
                "message": "Page updated successfully"
            }
            
            logger.info(f"Successfully updated page: {result['title']}")
            return result
            
        except APIResponseError as e:
            logger.error(f"Notion API error updating page: {e}")
            raise
        except Exception as e:
            logger.error(f"Error updating Notion page: {e}")
            raise

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the Notion tool with the given payload.
        
        Args:
            payload: Dictionary with action, query, page_id, data
            
        Returns:
            Result dictionary with success status and data
        """
        start_time = time.time()
        action = payload.get("action")
        
        try:
            # Validate payload
            if not self.validate_payload(payload):
                raise ValueError("Invalid payload structure")
            
            # Execute based on action
            if action == "search":
                query = payload.get("query")
                if not query:
                    raise ValueError("query is required for search action")
                
                results = self.fetch_notion_pages(query)
                response = {
                    "success": True,
                    "action": action,
                    "data": {
                        "results": results,
                        "count": len(results)
                    }
                }
                
            elif action == "read":
                page_id = payload.get("page_id")
                if not page_id:
                    raise ValueError("page_id is required for read action")
                
                page_data = self.get_notion_page(page_id)
                response = {
                    "success": True,
                    "action": action,
                    "data": page_data
                }
                
            elif action == "update":
                page_id = payload.get("page_id")
                data = payload.get("data")
                if not page_id:
                    raise ValueError("page_id is required for update action")
                if not data:
                    raise ValueError("data is required for update action")
                
                update_result = self.update_notion_page(page_id, data)
                response = {
                    "success": True,
                    "action": action,
                    "data": update_result
                }
                
            else:
                raise ValueError(f"Unknown action: {action}")
            
            duration_ms = (time.time() - start_time) * 1000
            self.log_execution(action, True, duration_ms)
            
            return response
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            error_msg = str(e)
            self.log_execution(action, False, duration_ms, error_msg)
            
            return {
                "success": False,
                "action": action,
                "error": error_msg
            }

    def _extract_title(self, page: Dict[str, Any]) -> str:
        """
        Extract title from a Notion page object.
        
        Args:
            page: Notion page object
            
        Returns:
            Page title as string
        """
        try:
            properties = page.get("properties", {})
            
            # Try to find title property
            for prop_name, prop_value in properties.items():
                if prop_value.get("type") == "title":
                    title_array = prop_value.get("title", [])
                    if title_array:
                        return title_array[0].get("plain_text", "Untitled")
            
            return "Untitled"
        except Exception:
            return "Untitled"

    def _extract_content_from_blocks(self, blocks: List[Dict[str, Any]]) -> str:
        """
        Extract text content from Notion blocks.
        
        Args:
            blocks: List of Notion block objects
            
        Returns:
            Combined text content as string
        """
        content_parts = []
        
        for block in blocks:
            block_type = block.get("type")
            if not block_type:
                continue
            
            block_content = block.get(block_type, {})
            rich_text = block_content.get("rich_text", [])
            
            for text_item in rich_text:
                plain_text = text_item.get("plain_text", "")
                if plain_text:
                    content_parts.append(plain_text)
        
        return "\n".join(content_parts)

    def _append_content_to_page(self, page_id: str, content: str):
        """
        Append text content to a Notion page.
        
        Args:
            page_id: The Notion page ID
            content: Text content to append
        """
        try:
            # Create a paragraph block with the content
            new_block = {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": content}}]
                }
            }
            
            self.client.blocks.children.append(block_id=page_id, children=[new_block])
            logger.info(f"Appended content to page {page_id}")
            
        except Exception as e:
            logger.error(f"Error appending content to page: {e}")
            raise


# Create a singleton instance
_notion_tool_instance = None


def get_notion_tool() -> NotionTool:
    """
    Get or create the Notion tool singleton instance.
    
    Returns:
        NotionTool instance
    """
    global _notion_tool_instance
    if _notion_tool_instance is None:
        _notion_tool_instance = NotionTool()
    return _notion_tool_instance
