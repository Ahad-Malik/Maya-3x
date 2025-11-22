import React, { useState, useEffect } from "react";
import "./PrivatePanel.css";

export default function PrivatePanel() {
  const [prompt, setPrompt] = useState("");
  const [response, setResponse] = useState("");
  const [mode, setMode] = useState("");
  const [loading, setLoading] = useState(false);
  const [contextLength, setContextLength] = useState(0);
  const [threshold, setThreshold] = useState(2000);
  const [privacyStatus, setPrivacyStatus] = useState(null);
  const [offloadLogs, setOffloadLogs] = useState([]);
  const [showLogs, setShowLogs] = useState(false);

  // Fetch privacy status on mount
  useEffect(() => {
    fetchPrivacyStatus();
  }, []);

  const fetchPrivacyStatus = async () => {
    try {
      const res = await fetch("http://localhost:5000/privacy/status");
      const data = await res.json();
      if (data.success) {
        setPrivacyStatus(data);
        setThreshold(data.context_limit);
      }
    } catch (error) {
      console.error("Failed to fetch privacy status:", error);
    }
  };

  const fetchOffloadLogs = async () => {
    try {
      const res = await fetch("http://localhost:5000/privacy/logs?limit=20");
      const data = await res.json();
      if (data.success) {
        setOffloadLogs(data.logs);
      }
    } catch (error) {
      console.error("Failed to fetch offload logs:", error);
    }
  };

  const handleRun = async () => {
    if (!prompt.trim()) {
      alert("Please enter a prompt");
      return;
    }

    setLoading(true);
    setResponse("");
    setMode("");

    try {
      const res = await fetch("http://localhost:5000/privacy/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });

      const data = await res.json();

      if (data.success) {
        setResponse(data.output);
        setMode(data.mode);
        setContextLength(data.context_length);
        setThreshold(data.threshold);
        
        // Refresh status and logs
        fetchPrivacyStatus();
        if (data.mode.includes("offload")) {
          fetchOffloadLogs();
        }
      } else {
        setResponse(`Error: ${data.error}`);
        setMode("error");
      }
    } catch (error) {
      setResponse(`Network error: ${error.message}`);
      setMode("error");
    } finally {
      setLoading(false);
    }
  };

  const getModeBadge = () => {
    if (!mode) return null;

    if (mode === "local") {
      return (
        <div className="badge badge-success">
          <span className="badge-icon">🟢</span>
          <span>Local Secure Mode Active</span>
        </div>
      );
    } else if (mode.includes("offload")) {
      return (
        <div className="badge badge-warning">
          <span className="badge-icon">⚠️</span>
          <span>Offloaded to Cloud — Large Context</span>
        </div>
      );
    } else if (mode === "error") {
      return (
        <div className="badge badge-error">
          <span className="badge-icon">❌</span>
          <span>Error Occurred</span>
        </div>
      );
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && e.ctrlKey) {
      handleRun();
    }
  };

  return (
    <div className="private-panel">
      <div className="private-header">
        <h2>🔒 Maya Private — Local Inference Mode</h2>
        <p className="privacy-description">
          Your queries are processed locally whenever possible. Large contexts
          are securely offloaded with full transparency.
        </p>
      </div>

      {privacyStatus && (
        <div className="privacy-stats">
          <div className="stat-card">
            <div className="stat-label">Status</div>
            <div className="stat-value status-active">Active</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Context Limit</div>
            <div className="stat-value">{privacyStatus.context_limit} chars</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Total Offloads</div>
            <div className="stat-value">{privacyStatus.total_offloads}</div>
          </div>
        </div>
      )}

      <div className="input-section">
        <textarea
          className="private-textarea"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder="Type your private query... (Ctrl+Enter to submit)"
          rows={6}
        />
        
        <div className="input-footer">
          <div className="char-count">
            {prompt.length} characters
            {prompt.length >= threshold && (
              <span className="warning-text"> (will offload to cloud)</span>
            )}
          </div>
          
          <button
            className="run-button"
            onClick={handleRun}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                Processing...
              </>
            ) : (
              <>
                <span>🔐</span>
                Run Securely
              </>
            )}
          </button>
        </div>
      </div>

      {response && (
        <div className="response-section">
          {getModeBadge()}
          
          <div className="response-details">
            <div className="detail-row">
              <span className="detail-label">Execution Mode:</span>
              <span className="detail-value">{mode}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Context Length:</span>
              <span className="detail-value">{contextLength} chars</span>
            </div>
          </div>

          <div className="response-content">
            <div className="response-header">Response:</div>
            <div className="response-text">{response}</div>
          </div>
        </div>
      )}

      {privacyStatus && privacyStatus.total_offloads > 0 && (
        <div className="logs-section">
          <button
            className="logs-toggle"
            onClick={() => {
              setShowLogs(!showLogs);
              if (!showLogs && offloadLogs.length === 0) {
                fetchOffloadLogs();
              }
            }}
          >
            {showLogs ? "Hide" : "Show"} Offload Transparency Log
          </button>

          {showLogs && (
            <div className="logs-content">
              {offloadLogs.length > 0 ? (
                <ul className="log-list">
                  {offloadLogs.map((log, idx) => (
                    <li key={idx} className="log-entry">
                      {log}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="no-logs">Loading logs...</p>
              )}
            </div>
          )}
        </div>
      )}

      <div className="privacy-info">
        <h3>Privacy Features</h3>
        <ul>
          <li>✅ Short queries (&lt;{threshold} chars) run locally on your device</li>
          <li>✅ Long queries are offloaded to cloud with full transparency</li>
          <li>✅ All offload events are logged with timestamps</li>
          <li>✅ No data retention on cloud servers after response</li>
        </ul>
      </div>
    </div>
  );
}
