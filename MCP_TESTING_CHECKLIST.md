# MCP Notion Integration - Testing Checklist

## Pre-Testing Setup

- [ ] Python dependencies installed (`pip install -r requirements.txt`)
- [ ] `notion-client` package installed and verified
- [ ] `.env` file contains valid `NOTION_MCP_TOKEN`
- [ ] Backend server starts without errors
- [ ] Frontend dev server running
- [ ] No compile errors in console

## Backend API Tests

### Test 1: MCP Endpoint Availability
```powershell
# Should return OPTIONS 200
Invoke-RestMethod -Uri "http://localhost:5000/mcp/execute" -Method OPTIONS
```
- [ ] Response: 200 OK
- [ ] CORS headers present

### Test 2: Search Action
```powershell
$body = @{
    tool = "notion"
    action = "search"
    query = "meeting"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/mcp/execute" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```
- [ ] Response contains `success: true`
- [ ] Response has `data.results` array
- [ ] Response has `data.count` number
- [ ] Each result has: `id`, `title`, `url`, timestamps
- [ ] Console shows: "Searching Notion pages with query: meeting"
- [ ] Console shows: "Found X pages"
- [ ] Console shows: "MCP Tool [notion] - Action: search, Success: True"

### Test 3: Read Action
```powershell
# Replace PAGE_ID with actual ID from search results
$body = @{
    tool = "notion"
    action = "read"
    page_id = "YOUR-PAGE-ID-HERE"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/mcp/execute" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```
- [ ] Response contains `success: true`
- [ ] Response has `data.id`, `data.title`, `data.content`
- [ ] Content is text string
- [ ] Console shows: "Retrieving Notion page: {page_id}"
- [ ] Console shows: "Successfully retrieved page: {title}"

### Test 4: Update Action
```powershell
$body = @{
    tool = "notion"
    action = "update"
    page_id = "YOUR-PAGE-ID-HERE"
    data = @{
        content = "Test content from Maya MCP integration - " + (Get-Date).ToString()
    }
} | ConvertTo-Json -Depth 3

Invoke-RestMethod -Uri "http://localhost:5000/mcp/execute" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```
- [ ] Response contains `success: true`
- [ ] Response has `data.message: "Page updated successfully"`
- [ ] Console shows: "Updating Notion page: {page_id}"
- [ ] Console shows: "Successfully updated page: {title}"
- [ ] Open Notion page - verify content appended

### Test 5: Permission Validation
```powershell
# Should fail - invalid action
$body = @{
    tool = "notion"
    action = "delete"
    page_id = "test"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/mcp/execute" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```
- [ ] Response: 403 Forbidden
- [ ] Error message: "Action 'delete' not allowed for tool 'notion'"
- [ ] Console shows validation failure

### Test 6: Schema Validation
```powershell
# Should fail - missing required field
$body = @{
    tool = "notion"
    action = "search"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/mcp/execute" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```
- [ ] Response: 400 Bad Request
- [ ] Error message: "Missing required field for search: 'query'"

### Test 7: Memory Logging
```powershell
# After successful search, check memory file
Get-Content "src/config/data/data.txt" -Tail 10
```
- [ ] Contains: `[MCP Notion search] Query: {query}, Result: {...}`
- [ ] Timestamp present
- [ ] Result data included

## Frontend UI Tests

### Test 8: Search Button - Default View
1. Open `http://localhost:5173`
2. Enter "project" in search box
3. Click "🔍 Search Notion"

- [ ] Button shows "Searching..." while loading
- [ ] Button disabled during search
- [ ] Results appear (or error message)
- [ ] No console errors in browser
- [ ] Network tab shows POST to `/mcp/execute`

### Test 9: Search Button - Audio Mode
1. Click audio mode icon (top right)
2. Hover over screen
3. Click "🔍 Search Notion" button

- [ ] Button appears on hover
- [ ] Button has semi-transparent background
- [ ] Search executes with input/recent prompt
- [ ] Results displayed

### Test 10: Send to Notion Button
1. Type some text in input
2. Click "📝 Send to Notion"

- [ ] Shows error about specifying page ID (expected)
- [ ] Error displayed in red box
- [ ] No crashes or console errors

### Test 11: Error Display
1. Disconnect from internet
2. Click "🔍 Search Notion"

- [ ] Error message displayed
- [ ] Error is user-friendly
- [ ] UI recovers gracefully

### Test 12: No Breaking Changes
Test all existing features still work:

- [ ] Text chat sends messages normally
- [ ] Vision mode works (camera access)
- [ ] Screenshare mode works
- [ ] Super Search mode works
- [ ] Audio mode records and transcribes
- [ ] Schedule modal opens and functions
- [ ] Face recognition toggle works
- [ ] All mode buttons toggle correctly

## Integration Tests

### Test 13: Search → Read Flow
1. Search for "test"
2. Copy page ID from results
3. Use API to read that page
4. Verify content matches Notion

- [ ] Search returns valid page IDs
- [ ] Read retrieves correct content
- [ ] Title matches Notion
- [ ] Content matches Notion

### Test 14: Search → Update → Verify Flow
1. Search for a page
2. Update that page with test content
3. Read the page again
4. Check Notion directly

- [ ] Update succeeds
- [ ] Content appears in subsequent read
- [ ] Content visible in Notion web app
- [ ] Timestamp updated in Notion

### Test 15: Memory Persistence
1. Perform several MCP actions
2. Restart backend server
3. Chat with Maya about Notion interactions

- [ ] Memory file persists across restarts
- [ ] Maya can reference past Notion searches
- [ ] GraphRAG integrates MCP logs

## Performance Tests

### Test 16: Response Time
Execute 10 searches and measure:

- [ ] Average < 500ms
- [ ] No timeouts
- [ ] Consistent performance
- [ ] Log shows timing for each request

### Test 17: Concurrent Requests
Send 3 search requests simultaneously:

- [ ] All complete successfully
- [ ] No race conditions
- [ ] Correct responses for each query

## Error Handling Tests

### Test 18: Invalid Notion Token
1. Change `NOTION_MCP_TOKEN` to invalid value
2. Restart backend
3. Try search

- [ ] Error: "Notion API error"
- [ ] Graceful error message
- [ ] No server crash

### Test 19: Invalid Page ID
```powershell
$body = @{
    tool = "notion"
    action = "read"
    page_id = "invalid-id-123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/mcp/execute" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```
- [ ] Error response returned
- [ ] Error logged
- [ ] No server crash

### Test 20: Network Timeout
1. Block network after request starts
2. Verify timeout handling

- [ ] Timeout caught
- [ ] Error message returned
- [ ] Server remains responsive

## Logging Tests

### Test 21: Success Logging
Check Flask console after successful search:

- [ ] "MCP validation passed: tool='notion', action='search'"
- [ ] "Searching Notion pages with query: ..."
- [ ] "Found X pages"
- [ ] "MCP Tool [notion] - Action: search, Success: True, Duration: Xms"
- [ ] "MCP Request - Tool: notion, Action: search, Success: True"

### Test 22: Error Logging
Check Flask console after failed action:

- [ ] "MCP validation failed: ..."
- [ ] "Error in MCP execute: ..."
- [ ] Error details logged
- [ ] Stack trace (if debug=True)

## Security Tests

### Test 23: SQL Injection Attempt
```powershell
$body = @{
    tool = "notion"
    action = "search"
    query = "'; DROP TABLE users; --"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/mcp/execute" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```
- [ ] Query sanitized
- [ ] No database errors
- [ ] Safe search performed

### Test 24: XSS Attempt
```powershell
$body = @{
    tool = "notion"
    action = "search"
    query = "<script>alert('xss')</script>"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/mcp/execute" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```
- [ ] Script tags not executed
- [ ] Content sanitized
- [ ] Safe display in UI

## Final Verification

### Test 25: Complete User Flow
Simulate real usage:

1. Start Maya
2. Ask "Search my Notion for project notes"
3. Click Search Notion button
4. Review results
5. Ask about a specific page
6. Update a page with new info

- [ ] All steps complete without errors
- [ ] User experience smooth
- [ ] Data accurate
- [ ] Memory retained

### Test 26: Documentation Accuracy
- [ ] README commands work as written
- [ ] Code examples in docs are correct
- [ ] API schema matches implementation
- [ ] Setup instructions complete

## Test Results Summary

Total Tests: 26
- Passed: ___
- Failed: ___
- Skipped: ___

Critical Issues: ___
Minor Issues: ___
Enhancements Needed: ___

## Sign-off

Tested By: _________________
Date: _________________
Version: 1.0.0
Status: [ ] PASS  [ ] FAIL  [ ] NEEDS WORK

---

**Notes:**
