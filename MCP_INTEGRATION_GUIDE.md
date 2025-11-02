# MCP (Model Context Protocol) Integration - Setup Guide

## Overview

Maya Live now supports MCP (Model Context Protocol) integration with Notion, allowing you to seamlessly search, read, and update Notion pages directly from the Maya interface.

## Features

✅ **Search Notion Pages** - Find pages by query  
✅ **Read Page Content** - Retrieve full page content  
✅ **Update Pages** - Modify page properties and content  
✅ **Memory Integration** - All MCP actions logged to GraphRAG memory  
✅ **Permission System** - Secure validation for all actions  
✅ **Real-time UI** - Notion buttons in both default and audio views  

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install the `notion-client` package along with other dependencies.

### 2. Configure Environment Variables

The `.env` file already contains the necessary Notion credentials:

```env
NOTION_MCP_URL=https://mcp.notion.com/mcp
NOTION_MCP_TOKEN=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
```

**Important:** Keep your Notion token secure and never commit it to version control.

### 3. Verify Backend Setup

The MCP integration is automatically loaded when you start the Flask server:

```bash
python src/config/app2.py
```

Check the console for:
```
INFO - Initialized MCP tool: notion
INFO - Notion client initialized successfully
```

## Usage

### Frontend (React)

#### Search Notion Pages

Click the **"🔍 Search Notion"** button in the default view or audio mode. The search will use your current input or recent prompt as the query.

```javascript
// Programmatic usage:
import { searchNotionPages } from '../../lib/mcpClient';

const results = await searchNotionPages("project notes");
console.log(results.data.results); // Array of pages
```

#### Send/Update Notion Page

Click the **"📝 Send to Notion"** button. Currently requires a page ID to be specified.

```javascript
import { updateNotionPage } from '../../lib/mcpClient';

await updateNotionPage("page-id-here", {
  title: "Updated Title",
  content: "New content to append"
});
```

#### Read a Notion Page

```javascript
import { readNotionPage } from '../../lib/mcpClient';

const pageData = await readNotionPage("page-id-here");
console.log(pageData.data.title);
console.log(pageData.data.content);
```

### Backend (Flask API)

#### Endpoint: `/mcp/execute`

**Method:** `POST`

**Payload:**
```json
{
  "tool": "notion",
  "action": "search|read|update",
  "query": "search term",      // required for search
  "page_id": "page-id",         // required for read/update
  "data": {                     // required for update
    "title": "New Title",
    "content": "Content to append"
  }
}
```

**Response (Success):**
```json
{
  "success": true,
  "action": "search",
  "data": {
    "results": [
      {
        "id": "page-id",
        "title": "Page Title",
        "url": "https://notion.so/...",
        "last_edited_time": "2025-11-02T...",
        "created_time": "2025-11-01T..."
      }
    ],
    "count": 1
  }
}
```

**Response (Error):**
```json
{
  "success": false,
  "action": "search",
  "error": "Error message"
}
```

## Architecture

### Backend Structure

```
src/
├── integrations/
│   ├── __init__.py
│   └── mcp/
│       ├── __init__.py
│       ├── base_mcp_tool.py      # Abstract base class
│       ├── notion_mcp.py         # Notion integration
│       └── permissions.py        # Security & validation
└── config/
    └── app2.py                   # Flask app with /mcp/execute route
```

### Frontend Structure

```
src/
├── lib/
│   └── mcpClient.js              # MCP API client
└── components/
    └── Main/
        └── Main.jsx              # UI with Notion buttons
```

### Key Components

1. **BaseMCPTool** - Abstract class for all MCP tools
   - `get_schema()` - Returns JSON schema
   - `execute()` - Executes tool action
   - `validate_payload()` - Validates input
   - `log_execution()` - Logs performance metrics

2. **NotionTool** - Notion-specific implementation
   - `fetch_notion_pages()` - Search API
   - `get_notion_page()` - Retrieve page
   - `update_notion_page()` - Update page
   - `_extract_title()` - Parse page title
   - `_extract_content_from_blocks()` - Parse content

3. **Permissions System**
   - `validate_mcp()` - Check if action is allowed
   - `validate_payload_schema()` - Validate request structure
   - `sanitize_payload()` - Prevent injection attacks
   - `log_mcp_request()` - Audit logging

## Security

### Allowed Actions

```python
ALLOWED_ACTIONS = {
    "notion": ["search", "read", "update"]
}
```

### Restricted Actions

Update actions are flagged as restricted and may require additional validation:

```python
RESTRICTED_TOOLS = {
    "notion": ["update"]
}
```

### Validation Flow

1. Check if tool exists
2. Check if action is allowed for tool
3. Validate payload schema
4. Sanitize input data
5. Execute tool
6. Log result

## Memory Integration

All successful MCP actions are automatically logged to the GraphRAG memory system:

```python
memory_entry = f"\n[MCP Notion {action}] Query: {query}, Result: {result}"
append_to_data_file(memory_entry)
```

This allows Maya to reference Notion interactions in future conversations.

## Error Handling

The system includes comprehensive error handling:

- **Network errors** - Caught and formatted for display
- **API errors** - Notion API errors logged and returned
- **Validation errors** - Schema validation failures with helpful messages
- **Permission errors** - 403 responses for unauthorized actions

## Logging

All MCP operations are logged with:
- Tool name
- Action performed
- Success/failure status
- Execution time in milliseconds
- Error messages (if any)

Example log output:
```
INFO - MCP validation passed: tool='notion', action='search'
INFO - Searching Notion pages with query: project notes
INFO - Found 3 pages
INFO - MCP Tool [notion] - Action: search, Success: True, Duration: 245.32ms
INFO - MCP Request - Tool: notion, Action: search, Success: True
```

## Testing

### Manual Testing

1. Start the Flask backend:
   ```bash
   python src/config/app2.py
   ```

2. Start the React frontend:
   ```bash
   npm run dev
   ```

3. Test search:
   - Enter a query in the input field
   - Click "🔍 Search Notion"
   - Verify results appear

4. Test update:
   - Get a page ID from search results
   - Modify the update handler to use that ID
   - Click "📝 Send to Notion"

### API Testing with curl

```bash
# Search
curl -X POST http://localhost:5000/mcp/execute \
  -H "Content-Type: application/json" \
  -d '{"tool":"notion","action":"search","query":"test"}'

# Read
curl -X POST http://localhost:5000/mcp/execute \
  -H "Content-Type: application/json" \
  -d '{"tool":"notion","action":"read","page_id":"YOUR-PAGE-ID"}'

# Update
curl -X POST http://localhost:5000/mcp/execute \
  -H "Content-Type: application/json" \
  -d '{"tool":"notion","action":"update","page_id":"YOUR-PAGE-ID","data":{"title":"Updated"}}'
```

## Extending the System

### Adding a New MCP Tool

1. Create a new file in `src/integrations/mcp/`:
   ```python
   from .base_mcp_tool import BaseMCPTool
   
   class SlackTool(BaseMCPTool):
       def __init__(self):
           super().__init__("slack")
           # Initialize Slack client
       
       def get_schema(self):
           return {...}
       
       def execute(self, payload):
           # Implementation
   ```

2. Update `permissions.py`:
   ```python
   ALLOWED_ACTIONS = {
       "notion": ["search", "read", "update"],
       "slack": ["send_message", "list_channels"]
   }
   ```

3. Add to `/mcp/execute` route in `app2.py`:
   ```python
   elif tool == "slack":
       slack_tool = get_slack_tool()
       result = slack_tool.execute(sanitized_payload)
   ```

## Troubleshooting

### "MCP integrations not available" Error

- Check that `notion-client` is installed: `pip list | grep notion`
- Verify the import statement in `app2.py` works
- Check Flask console for import errors

### "NOTION_MCP_TOKEN not found" Error

- Verify `.env` file exists in project root
- Check that `NOTION_MCP_TOKEN` is set
- Restart the Flask server after modifying `.env`

### Search Returns No Results

- Verify your Notion token has access to the workspace
- Check that the search query matches page titles
- Try a broader search term

### Update Fails

- Ensure the page ID is valid
- Verify your token has write permissions
- Check that the page hasn't been deleted or archived

## Future Enhancements

- [ ] Add page creation functionality
- [ ] Support for databases (not just pages)
- [ ] Batch operations
- [ ] Rich text formatting support
- [ ] File attachments
- [ ] Comments and mentions
- [ ] Webhook support for real-time updates

## Support

For issues or questions:
1. Check the Flask logs for detailed error messages
2. Verify your Notion token and permissions
3. Test the endpoint directly with curl
4. Review the browser console for frontend errors

---

**Author:** Maya Development Team  
**Version:** 1.0.0  
**Last Updated:** November 2, 2025
