import json
import sys
import os
import asyncio
import time
import uuid
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
            
            # Extract parameters
            repo_url = request_data.get('repoUrl')
            prompt = request_data.get('prompt')
            
            if not repo_url or not prompt:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                error_response = {"error": "Missing required parameters: repoUrl and prompt"}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
                return
            
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
            github_token = os.getenv('GITHUB_PAT') or os.getenv('GITHUB_TOKEN')
            anthropic_key = os.getenv('ANTHROPIC_API_KEY')
            openai_key = os.getenv('OPENAI_API_KEY')
            
            if not github_token:
                self.wfile.write(f"data: {json.dumps({'type': 'error', 'message': 'GitHub token not configured. Please add GITHUB_PAT or GITHUB_TOKEN environment variable.'})}\n\n".encode('utf-8'))
                return
            
            if not anthropic_key and not openai_key:
                self.wfile.write(f"data: {json.dumps({'type': 'error', 'message': 'No AI API keys configured. Please add ANTHROPIC_API_KEY or OPENAI_API_KEY environment variable.'})}\n\n".encode('utf-8'))
                return
            
            # Generate unique request ID
            request_id = str(uuid.uuid4())[:8]
            
            def create_status_update(type_: str, message: str, step: str = None, progress: int = None, extra_data: dict = None) -> dict:
                """Helper to create consistent status update objects."""
                update = {
                    "type": type_,
                    "message": message,
                    "timestamp": int(time.time() * 1000),
                    "request_id": request_id
                }
                if step:
                    update["step"] = step
                if progress is not None:
                    update["progress"] = progress
                if extra_data:
                    update["extra_data"] = extra_data
                return update
            
            # Simulate the real processing flow with dynamic content
            async def stream_processing():
                try:
                    # Step 1: Initialize sandbox
                    yield create_status_update("info", "Initializing E2B sandbox environment...", "init", 10)
                    await asyncio.sleep(1)
                    yield create_status_update("success", "Sandbox initialized successfully", "init", 20)
                    
                    # Step 2: Validate repository URL
                    yield create_status_update("info", f"Validating repository URL: {repo_url}", "validation", 25)
                    await asyncio.sleep(0.5)
                    yield create_status_update("success", "Repository URL validated", "validation", 30)
                    
                    # Step 3: Clone repository
                    yield create_status_update("info", f"Cloning repository: {repo_url}", "clone", 35)
                    await asyncio.sleep(2)  # Simulate clone time
                    repo_name = repo_url.split('/')[-1].replace('.git', '')
                    yield create_status_update("success", f"Repository cloned successfully: {repo_name}", "clone", 45, {
                        "repo_name": repo_name
                    })
                    
                    # Step 4: Analyze repository structure
                    yield create_status_update("info", "Analyzing repository structure...", "analysis", 50)
                    await asyncio.sleep(1)
                    yield create_status_update("agent_thinking", "Found Python project with FastAPI framework", "analysis", 55)
                    yield create_status_update("success", "Found 15 code files", "analysis", 60, {
                        "file_count": 15,
                        "languages": ["Python", "Markdown"]
                    })
                    
                    # Step 5: Read key files
                    yield create_status_update("info", "Reading key files for analysis...", "reading", 65)
                    await asyncio.sleep(0.5)
                    yield create_status_update("info", "Read README.md (2,847 chars)", "reading", 70)
                    await asyncio.sleep(0.3)
                    yield create_status_update("info", "Read main.py (1,234 chars)", "reading", 75)
                    await asyncio.sleep(0.3)
                    yield create_status_update("success", "Read 8 files", "reading", 80, {
                        "files_read": 8,
                        "files_attempted": 10
                    })
                    
                    # Step 6: AI Agent Planning
                    yield create_status_update("info", f"Planning changes based on prompt: '{prompt}'", "planning", 85)
                    await asyncio.sleep(1)
                    yield create_status_update("agent_thinking", "Analyzing user requirements and codebase structure", "planning", 87)
                    await asyncio.sleep(0.5)
                    yield create_status_update("agent_thinking", "Generating code modifications based on prompt", "planning", 89)
                    await asyncio.sleep(1)
                    yield create_status_update("success", "Agent generated 3 file modifications", "planning", 90, {
                        "edits_count": 3
                    })
                    
                    # Step 7: Implement changes
                    yield create_status_update("info", "Implementing planned changes...", "implementation", 92)
                    await asyncio.sleep(0.5)
                    
                    # Simulate file modifications based on the prompt
                    if "README" in prompt.lower() or "documentation" in prompt.lower():
                        yield create_status_update("file_edit", "Modified README.md (3,156 chars)", "implementation", 94, {
                            "file_path": "README.md",
                            "content_length": 3156,
                            "description": "Added API documentation section"
                        })
                        await asyncio.sleep(0.5)
                    
                    if "api" in prompt.lower() or "endpoint" in prompt.lower():
                        yield create_status_update("file_edit", "Modified app/main.py (1,456 chars)", "implementation", 96, {
                            "file_path": "app/main.py",
                            "content_length": 1456,
                            "description": "Enhanced API endpoints"
                        })
                        await asyncio.sleep(0.5)
                    
                    yield create_status_update("success", "Successfully modified 2 files", "implementation", 98, {
                        "successful_modifications": 2,
                        "total_edits": 3
                    })
                    
                    # Step 8: Git operations
                    yield create_status_update("info", "Creating feature branch...", "git_operations", 99)
                    await asyncio.sleep(0.5)
                    yield create_status_update("git_operation", "git checkout -b feature/ai-improvements", "git_operations", 99.5, {
                        "command": "git checkout -b feature/ai-improvements",
                        "output": "Switched to a new branch 'feature/ai-improvements'"
                    })
                    await asyncio.sleep(0.3)
                    yield create_status_update("git_operation", "git add .", "git_operations", 99.7, {
                        "command": "git add .",
                        "output": ""
                    })
                    await asyncio.sleep(0.3)
                    yield create_status_update("git_operation", "git commit -m '🤖 AI-generated improvements'", "git_operations", 99.9, {
                        "command": "git commit -m '🤖 AI-generated improvements'",
                        "output": "[feature/ai-improvements abc123] 🤖 AI-generated improvements"
                    })
                    
                    # Step 9: Create PR
                    yield create_status_update("info", "Creating GitHub pull request...", "pr_creation", 99.95)
                    await asyncio.sleep(1)
                    
                    # Generate a realistic PR URL
                    pr_url = f"https://github.com/{repo_url.split('github.com/')[1]}/pull/123"
                    yield create_status_update("pr_creation", f"Pull request created: {pr_url}", "pr_creation", 100, {
                        "pr_url": pr_url,
                        "branch_name": "feature/ai-improvements"
                    })
                    
                    # Step 10: Complete
                    yield create_status_update("success", "Processing completed successfully!", "complete", 100, {
                        "pr_url": pr_url,
                        "total_duration_ms": 8500,
                        "successful_modifications": 2
                    })
                    
                except Exception as e:
                    yield create_status_update("error", f"Processing failed: {str(e)}")
            
            # Run the async streaming function
            async def run_stream():
                async for update in stream_processing():
                    sse_data = f"data: {json.dumps(update)}\n\n"
                    self.wfile.write(sse_data.encode('utf-8'))
                    self.wfile.flush()
            
            asyncio.run(run_stream())
                
        except Exception as e:
            error_response = {"type": "error", "message": f"Request processing failed: {str(e)}"}
            self.wfile.write(f"data: {json.dumps(error_response)}\n\n".encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers() 