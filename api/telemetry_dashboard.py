"""
Simple telemetry dashboard for viewing observability data.
This provides a basic web interface to view agent thinking and performance metrics.
"""

import json
import time
import os
from datetime import datetime
from http.server import BaseHTTPRequestHandler
import threading
import queue

# Global storage for telemetry data
telemetry_data = {
    "requests": {},
    "thinking_logs": [],
    "performance_metrics": {},
    "system_stats": {
        "total_requests": 0,
        "successful_requests": 0,
        "failed_requests": 0,
        "avg_response_time": 0
    }
}

class TelemetryDashboard(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(self._get_dashboard_html().encode('utf-8'))
        elif self.path == '/api/telemetry':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(telemetry_data, indent=2).encode('utf-8'))
        elif self.path == '/api/thinking':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(telemetry_data["thinking_logs"], indent=2).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def _get_dashboard_html(self):
        return """
<!DOCTYPE html>
<html>
<head>
    <title>Tiny Backspace - Telemetry Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stat-value { font-size: 2em; font-weight: bold; color: #3498db; }
        .thinking-log { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .thinking-step { background: #ecf0f1; padding: 10px; margin: 5px 0; border-radius: 4px; }
        .thinking-time { color: #7f8c8d; font-size: 0.9em; }
        .thinking-thought { margin-top: 5px; }
        .refresh-btn { background: #3498db; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; }
        .refresh-btn:hover { background: #2980b9; }
        .auto-refresh { margin-left: 10px; }
        .request-id { font-weight: bold; color: #e74c3c; }
        .step-type { color: #27ae60; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Tiny Backspace - Real-Time Telemetry Dashboard</h1>
            <p>Live monitoring of AI agent thinking process and performance metrics</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Requests</h3>
                <div class="stat-value" id="total-requests">0</div>
            </div>
            <div class="stat-card">
                <h3>Successful Requests</h3>
                <div class="stat-value" id="successful-requests">0</div>
            </div>
            <div class="stat-card">
                <h3>Failed Requests</h3>
                <div class="stat-value" id="failed-requests">0</div>
            </div>
            <div class="stat-card">
                <h3>Avg Response Time</h3>
                <div class="stat-value" id="avg-response-time">0ms</div>
            </div>
        </div>
        
        <div style="text-align: center; margin-bottom: 20px;">
            <button class="refresh-btn" onclick="refreshData()">🔄 Refresh Data</button>
            <label class="auto-refresh">
                <input type="checkbox" id="auto-refresh" checked> Auto-refresh every 5 seconds
            </label>
        </div>
        
        <div class="thinking-log">
            <h2>🤔 Recent Agent Thinking Process</h2>
            <div id="thinking-logs">
                <p>No thinking logs available yet. Start a request to see agent thinking in real-time!</p>
            </div>
        </div>
        
        <div class="thinking-log">
            <h2>⚡ Performance Metrics</h2>
            <div id="performance-metrics">
                <p>No performance metrics available yet.</p>
            </div>
        </div>
    </div>
    
    <script>
        let autoRefreshInterval;
        
        function refreshData() {
            fetch('/api/telemetry')
                .then(response => response.json())
                .then(data => {
                    updateStats(data.system_stats);
                    updateThinkingLogs(data.thinking_logs);
                    updatePerformanceMetrics(data.performance_metrics);
                })
                .catch(error => console.error('Error fetching telemetry data:', error));
        }
        
        function updateStats(stats) {
            document.getElementById('total-requests').textContent = stats.total_requests;
            document.getElementById('successful-requests').textContent = stats.successful_requests;
            document.getElementById('failed-requests').textContent = stats.failed_requests;
            document.getElementById('avg-response-time').textContent = stats.avg_response_time + 'ms';
        }
        
        function updateThinkingLogs(logs) {
            const container = document.getElementById('thinking-logs');
            if (logs.length === 0) {
                container.innerHTML = '<p>No thinking logs available yet. Start a request to see agent thinking in real-time!</p>';
                return;
            }
            
            let html = '';
            logs.slice(-20).reverse().forEach(log => {
                const timestamp = new Date(log.timestamp * 1000).toLocaleTimeString();
                html += `
                    <div class="thinking-step">
                        <div class="thinking-time">${timestamp} | Request: <span class="request-id">${log.request_id}</span> | Step: <span class="step-type">${log.step}</span></div>
                        <div class="thinking-thought">${log.thought}</div>
                    </div>
                `;
            });
            container.innerHTML = html;
        }
        
        function updatePerformanceMetrics(metrics) {
            const container = document.getElementById('performance-metrics');
            if (Object.keys(metrics).length === 0) {
                container.innerHTML = '<p>No performance metrics available yet.</p>';
                return;
            }
            
            let html = '';
            Object.entries(metrics).forEach(([operation, data]) => {
                html += `
                    <div class="thinking-step">
                        <strong>${operation}</strong>: ${data.duration_ms.toFixed(2)}ms
                        <br><small>${new Date(data.timestamp * 1000).toLocaleTimeString()}</small>
                    </div>
                `;
            });
            container.innerHTML = html;
        }
        
        function toggleAutoRefresh() {
            const checkbox = document.getElementById('auto-refresh');
            if (checkbox.checked) {
                autoRefreshInterval = setInterval(refreshData, 5000);
            } else {
                clearInterval(autoRefreshInterval);
            }
        }
        
        document.getElementById('auto-refresh').addEventListener('change', toggleAutoRefresh);
        
        // Initial load and start auto-refresh
        refreshData();
        toggleAutoRefresh();
    </script>
</body>
</html>
        """


def add_thinking_log(request_id: str, step: str, thought: str, data: dict = None):
    """Add a thinking log entry to the telemetry data."""
    log_entry = {
        "timestamp": time.time(),
        "request_id": request_id,
        "step": step,
        "thought": thought,
        "data": data or {}
    }
    
    telemetry_data["thinking_logs"].append(log_entry)
    
    # Keep only last 100 logs
    if len(telemetry_data["thinking_logs"]) > 100:
        telemetry_data["thinking_logs"] = telemetry_data["thinking_logs"][-100:]


def add_performance_metric(operation: str, duration_ms: float, metadata: dict = None):
    """Add a performance metric to the telemetry data."""
    telemetry_data["performance_metrics"][operation] = {
        "duration_ms": duration_ms,
        "metadata": metadata or {},
        "timestamp": time.time()
    }


def update_system_stats(total_requests: int, successful_requests: int, failed_requests: int, avg_response_time: float):
    """Update system statistics."""
    telemetry_data["system_stats"].update({
        "total_requests": total_requests,
        "successful_requests": successful_requests,
        "failed_requests": failed_requests,
        "avg_response_time": avg_response_time
    })


def start_dashboard(port: int = 8080):
    """Start the telemetry dashboard server."""
    import http.server
    import socketserver
    
    Handler = TelemetryDashboard
    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"🤖 Telemetry Dashboard running at http://localhost:{port}")
        print("📊 View real-time agent thinking and performance metrics")
        httpd.serve_forever()


if __name__ == "__main__":
    start_dashboard() 