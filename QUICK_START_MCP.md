# Quick Start - MCP Notion Integration

## Prerequisites Checklist

- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed
- [ ] Notion workspace access
- [ ] Notion integration token

## Setup Steps

### 1. Install Backend Dependencies

```powershell
pip install -r requirements.txt
```

### 2. Verify Environment Variables

Check your `.env` file contains:
```
NOTION_MCP_TOKEN=your-notion-token-here
```

### 3. Start Backend Server

```powershell
python src/config/app2.py
```

Expected output:
```
INFO - Initialized MCP tool: notion
INFO - Notion client initialized successfully
* Running on http://127.0.0.1:5000
```

### 4. Start Frontend (in new terminal)

```powershell
npm run dev
```

### 5. Test the Integration

1. Open browser at `http://localhost:5173`
2. Enter a search query like "meeting notes"
3. Click **"🔍 Search Notion"** button
4. View results in the Maya interface

## Quick API Test

Test the MCP endpoint directly:

```powershell
# Search for pages
Invoke-RestMethod -Uri "http://localhost:5000/mcp/execute" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"tool":"notion","action":"search","query":"test"}'
```

## Common Issues

### Import Error: notion_client
```powershell
pip install notion-client
```

### CORS Error
- Ensure Flask server is running on port 5000
- Check CORS is enabled in app2.py

### No Results from Search
- Verify your Notion token has workspace access
- Check that pages exist matching your query

## Files Created

Backend:
- `src/integrations/__init__.py`
- `src/integrations/mcp/__init__.py`
- `src/integrations/mcp/base_mcp_tool.py`
- `src/integrations/mcp/notion_mcp.py`
- `src/integrations/mcp/permissions.py`

Frontend:
- `src/lib/mcpClient.js`

Modified:
- `src/config/app2.py` (added /mcp/execute endpoint)
- `src/components/Main/Main.jsx` (added Notion UI)
- `requirements.txt` (added notion-client)

## Next Steps

1. ✅ Test search functionality
2. ✅ Test page reading
3. ✅ Test page updates
4. 📚 Read the full guide: `MCP_INTEGRATION_GUIDE.md`
5. 🚀 Extend with more MCP tools (Slack, Calendar, etc.)

## Support

Check logs in:
- Flask console for backend errors
- Browser console (F12) for frontend errors
- `data/data.txt` for memory logs

---

Happy building! 🎉
