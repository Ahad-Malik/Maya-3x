/**
 * MCP (Model Context Protocol) Client
 * Frontend helper functions for executing MCP tool operations
 */

/**
 * Execute an MCP tool action
 * @param {string} tool - The tool name (e.g., "notion")
 * @param {object} payload - The action payload including action, query, page_id, data, etc.
 * @returns {Promise<object>} The result from the MCP execution
 */
export async function executeMCP(tool, payload) {
  try {
    const response = await fetch('http://localhost:5000/mcp/execute', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        tool,
        ...payload,
      }),
    });

    const result = await response.json();

    if (!response.ok) {
      const errorMsg = result.error || `MCP request failed with status ${response.status}`;
      const details = result.details ? `\n${result.details}` : '';
      const suggestion = result.suggestion ? `\n${result.suggestion}` : '';
      throw new Error(`${errorMsg}${details}${suggestion}`);
    }

    return result;
  } catch (error) {
    console.error('MCP execution error:', error);
    console.error('Payload was:', { tool, ...payload });
    throw error;
  }
}

/**
 * Search Notion pages
 * @param {string} query - Search query string
 * @returns {Promise<object>} Search results with pages
 */
export async function searchNotionPages(query) {
  return executeMCP('notion', {
    action: 'search',
    query,
  });
}

/**
 * Read a Notion page
 * @param {string} pageId - The Notion page ID
 * @returns {Promise<object>} Page data with content
 */
export async function readNotionPage(pageId) {
  return executeMCP('notion', {
    action: 'read',
    page_id: pageId,
  });
}

/**
 * Update a Notion page
 * @param {string} pageId - The Notion page ID
 * @param {object} data - Update data (title, content, properties)
 * @returns {Promise<object>} Update confirmation
 */
export async function updateNotionPage(pageId, data) {
  return executeMCP('notion', {
    action: 'update',
    page_id: pageId,
    data,
  });
}

/**
 * Format MCP error for display
 * @param {Error} error - The error object
 * @returns {string} Formatted error message
 */
export function formatMCPError(error) {
  if (error.message) {
    return error.message;
  }
  return 'An unknown error occurred during MCP execution';
}

/**
 * Check if MCP is available
 * @returns {Promise<boolean>} True if MCP is available
 */
export async function checkMCPAvailability() {
  try {
    const response = await fetch('http://localhost:5000/mcp/execute', {
      method: 'OPTIONS',
    });
    return response.ok;
  } catch (error) {
    console.warn('MCP not available:', error);
    return false;
  }
}
