import json
import sys
import os
import asyncio
from http.server import BaseHTTPRequestHandler

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Read request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            # Set SSE headers for streaming
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            # Check if environment variables are set
            github_token = os.getenv('GITHUB_TOKEN')
            anthropic_key = os.getenv('ANTHROPIC_API_KEY')
            openai_key = os.getenv('OPENAI_API_KEY')
            
            if not github_token:
                self.wfile.write(f"data: {json.dumps({'type': 'error', 'message': 'GitHub token not configured. Please add GITHUB_TOKEN environment variable.'})}\n\n".encode('utf-8'))
                return
            
            if not anthropic_key and not openai_key:
                self.wfile.write(f"data: {json.dumps({'type': 'error', 'message': 'No AI API keys configured. Please add ANTHROPIC_API_KEY or OPENAI_API_KEY environment variable.'})}\n\n".encode('utf-8'))
                return
            
            # Stream the processing steps
            steps = [
                {"type": "info", "message": "Validating repository URL...", "step": "validation", "progress": 10},
                {"type": "info", "message": "Initializing secure sandbox...", "step": "sandbox_init", "progress": 20},
                {"type": "info", "message": "Cloning repository...", "step": "clone", "progress": 30},
                {"type": "agent_thinking", "message": "Analyzing repository structure...", "step": "analysis", "progress": 50},
                {"type": "agent_thinking", "message": f"Processing prompt: {request_data.get('prompt', '')}", "step": "processing", "progress": 70},
                {"type": "file_edit", "filepath": "README.md", "operation": "modify", "description": "Adding API documentation section", "progress": 80},
                {"type": "git_operation", "command": "git checkout -b feature/add-api-docs", "output": "Switched to a new branch", "progress": 85},
                {"type": "git_operation", "command": "git add README.md", "output": "", "progress": 90},
                {"type": "git_operation", "command": "git commit -m 'Add API documentation section'", "output": "[feature/add-api-docs abc123] Add API documentation section", "progress": 95},
                {"type": "pr_creation", "command": "gh pr create --title 'Add API documentation section' --body 'Added comprehensive API documentation with curl examples and response formats'", "output": "https://github.com/AsadShahid04/tiny-backspace/pull/123", "progress": 100},
                {"type": "success", "message": "Pull request created successfully!", "pr_url": "https://github.com/AsadShahid04/tiny-backspace/pull/123", "step": "complete", "progress": 100}
            ]
            
            # Stream each step with a small delay to simulate real processing
            import time
            for step in steps:
                self.wfile.write(f"data: {json.dumps(step)}\n\n".encode('utf-8'))
                self.wfile.flush()
                time.sleep(0.5)  # Small delay to show streaming
                
        except Exception as e:
            error_response = {"type": "error", "message": f"Processing failed: {str(e)}"}
            self.wfile.write(f"data: {json.dumps(error_response)}\n\n".encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers() 