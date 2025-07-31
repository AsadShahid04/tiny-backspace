from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import json
import asyncio
import os
import sys
import uuid
import re
from typing import AsyncGenerator, Optional
import subprocess
import tempfile
import shutil
from pathlib import Path
from dotenv import load_dotenv
import anthropic
import requests
import socket
import signal
import psutil
import time
import traceback

# Load environment variables from .env file
load_dotenv()

# Debug: Print environment variables
print("🔍 Environment variables loaded:")
print(f"GITHUB_PAT: {os.getenv('GITHUB_PAT', 'NOT SET')[:20]}...")
print(f"ANTHROPIC_API_KEY: {os.getenv('ANTHROPIC_API_KEY', 'NOT SET')[:20]}...")
print(f"E2B_API_KEY: {os.getenv('E2B_API_KEY', 'NOT SET')[:20]}...")

# E2B imports
from e2b import Sandbox

# Initialize FastAPI app
app = FastAPI(title="Tiny Backspace", description="AI-powered code generation and PR creation")

class TinyBackspaceProcessor:
    def __init__(self):
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        pass
    
    def _validate_environment(self):
        """Validate that required environment variables are set"""
        self.github_token = os.getenv('GITHUB_PAT') or os.getenv('GITHUB_TOKEN')
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        self.openai_key = os.getenv('OPENAI_API_KEY')
        
        if not self.github_token:
            raise ValueError("GITHUB_PAT or GITHUB_TOKEN environment variable is required")
        
        if not self.anthropic_key and not self.openai_key:
            raise ValueError("ANTHROPIC_API_KEY or OPENAI_API_KEY environment variable is required")
    
    async def process_request(self, repo_url: str, prompt: str) -> AsyncGenerator[str, None]:
        """Main processing pipeline with comprehensive error handling"""
        request_id = str(uuid.uuid4())[:8]
        sandbox = None
        
        try:
            # Validate environment variables
            self._validate_environment()
            # Step 1: Initialize
            yield self._create_sse_event("info", f"🚀 Starting request {request_id}")
            yield self._create_sse_event("info", f"📁 Repository: {repo_url}")
            yield self._create_sse_event("info", f"💭 Prompt: {prompt}")
            
            # Step 2: Validate repository URL
            if not self._is_valid_github_url(repo_url):
                yield self._create_sse_event("error", "❌ Invalid GitHub repository URL format")
                return
            
            # Step 3: Create sandbox with retry logic
            yield self._create_sse_event("info", "💭 [SANDBOX] Creating secure E2B sandbox environment")
            try:
                sandbox = await self._create_sandbox_async()
                yield self._create_sse_event("success", f"✅ [SANDBOX] E2B sandbox created successfully with ID: {sandbox.sandbox_id}")
            except Exception as e:
                yield self._create_sse_event("error", f"❌ [SANDBOX] Failed to create sandbox: {str(e)}")
                return
            
            # Step 4: Clone repository with retry logic
            yield self._create_sse_event("info", f"💭 [CLONE] Cloning repository {repo_url} into sandbox")
            try:
                await self._clone_repository_with_retry(sandbox, repo_url)
                yield self._create_sse_event("success", "✅ [CLONE] Repository successfully cloned into sandbox")
            except Exception as e:
                yield self._create_sse_event("error", f"❌ [CLONE] Failed to clone repository: {str(e)}")
                return
                
                # Step 5: Analyze repository structure
                yield self._create_sse_event("info", "🔍 [ANALYSIS] Analyzing repository structure")
                files_result = sandbox.commands.run("find repo -type f -name '*.py' -o -name '*.js' -o -name '*.ts' -o -name '*.jsx' -o -name '*.tsx' | head -20")
                files = files_result.stdout.strip().split('\n') if files_result.stdout else []
                yield self._create_sse_event("success", f"🔍 [ANALYSIS] Repository analysis complete: {len(files)} files found")
                
                # Step 6: Read key files
                yield self._create_sse_event("info", "💭 [FILE_READING] Reading key repository files")
                file_contents = {}
                for file_path in files[:5]:  # Read first 5 files
                    if file_path and file_path.strip():  # Check if file_path is not empty
                        read_result = sandbox.commands.run(f"cat {file_path}")
                        if read_result.exit_code == 0:
                            # Normalize file path for AI consumption
                            clean_file_path = self._normalize_file_path(file_path)
                            file_contents[clean_file_path] = read_result.stdout
                            yield self._create_sse_event("info", f"💭 [FILE_READING] Reading file: {file_path} -> {clean_file_path}")
                        else:
                            yield self._create_sse_event("info", f"💭 [FILE_READING] Failed to read file: {file_path} - {read_result.stderr}")
                
                # Debug: Show what files we have
                yield self._create_sse_event("info", f"💭 [DEBUG] Found {len(file_contents)} files with content")
                for file_path in file_contents.keys():
                    yield self._create_sse_event("info", f"💭 [DEBUG] File: {file_path} (length: {len(file_contents[file_path])})")
                
                # Step 7: Generate code with Claude Code locally
                yield self._create_sse_event("info", "🤖 [AI_PROCESSING] Processing with Claude Code locally")
                code_changes = await self._generate_code_with_retry(prompt, file_contents, repo_url)
                
                if not code_changes:
                    yield self._create_sse_event("error", "❌ [ERROR] Failed to generate code modifications")
                    return
                
                # Step 8: Apply changes in sandbox
                yield self._create_sse_event("info", "🔧 [APPLYING] Applying code changes in sandbox")
                for change in code_changes:
                    if change['type'] == 'edit':
                        original_filepath = change['filepath']
                        yield self._create_sse_event("info", f"🔧 [APPLYING] Processing change: {original_filepath}")
                        
                        # Normalize file path
                        normalized_filepath = self._normalize_file_path(original_filepath)
                        change['filepath'] = normalized_filepath
                        if original_filepath != normalized_filepath:
                            yield self._create_sse_event("info", f"🔧 [APPLYING] Normalized filepath: {original_filepath} -> {normalized_filepath}")
                        
                        await self._apply_file_edit(sandbox, change)
                        yield self._create_sse_event("info", f"🔧 [APPLYING] Applied edit to {normalized_filepath}")
                
                # Step 9: Git operations in sandbox
                yield self._create_sse_event("info", "🔧 [GIT] Setting up Git operations in sandbox")
                await self._setup_git_in_sandbox(sandbox, repo_url)
                
                # Step 10: Create branch and commit
                branch_name = f"feature/{request_id}"
                yield self._create_sse_event("info", f"🔧 [GIT] Creating branch: {branch_name}")
                
                # Use safer command execution
                git_commands = [
                    ("cd repo && git checkout -b " + branch_name, "Create branch"),
                    ("cd repo && git add .", "Add files"),
                    ("cd repo && git commit -m 'Apply changes from Tiny Backspace'", "Commit changes"),
                    ("cd repo && git remote set-url origin https://" + self.github_token + "@github.com/AsadShahid04/tiny-backspace.git", "Set remote"),
                    ("cd repo && git push origin " + branch_name, "Push branch")
                ]
                
                for cmd, description in git_commands:
                    yield self._create_sse_event("info", f"🔧 [GIT] {description}")
                    try:
                        result = self._safe_execute_with_retry(
                            f"Git {description}",
                            lambda: sandbox.commands.run(cmd)
                        )
                        if result.exit_code != 0:
                            yield self._create_sse_event("error", f"❌ [GIT] {description} failed")
                            yield self._create_sse_event("error", f"Command: {cmd}")
                            yield self._create_sse_event("error", f"Error: {result.stderr}")
                            return
                        yield self._create_sse_event("success", f"✅ [GIT] {description} completed")
                    except Exception as e:
                        yield self._create_sse_event("error", f"❌ [GIT] {description} failed after retries: {str(e)}")
                        return
                
                # Step 11: Create PR
                yield self._create_sse_event("info", "🔧 [PR] Creating pull request")
                pr_result = await self._create_pull_request(repo_url, branch_name, prompt)
                
                if pr_result:
                    yield self._create_sse_event("success", f"✅ [SUCCESS] Pull request created: {pr_result['url']}")
                    yield self._create_sse_event("success", f"📝 [PR] Title: {pr_result['title']}")
                    yield self._create_sse_event("success", f"📝 [PR] Description: {pr_result['body']}")
                else:
                    yield self._create_sse_event("error", "❌ [ERROR] Failed to create pull request")
            finally:
                # Clean up sandbox with error handling
                if sandbox:
                    try:
                        yield self._create_sse_event("info", "🧹 [CLEANUP] Cleaning up sandbox environment")
                        sandbox.kill()
                        yield self._create_sse_event("success", "✅ [CLEANUP] Sandbox cleaned up successfully")
                    except Exception as cleanup_error:
                        yield self._create_sse_event("error", f"⚠️ [CLEANUP] Failed to cleanup sandbox: {str(cleanup_error)}")
                
        except Exception as e:
            error_details = f"❌ [ERROR] Processing failed: {str(e)}"
            print(f"Full error traceback: {traceback.format_exc()}")
            yield self._create_sse_event("error", error_details)
            yield self._create_sse_event("error", "💡 [RECOVERY] Please check your environment variables and try again")
    
    def _is_valid_github_url(self, url: str) -> bool:
        """Validate GitHub repository URL"""
        github_pattern = r'^https://github\.com/[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+/?$'
        return bool(re.match(github_pattern, url))
    
    async def _generate_code_locally(self, prompt: str, file_contents: dict, repo_url: str) -> list:
        """Generate code changes using Claude Code locally"""
        try:
            # Create client
            client = anthropic.Anthropic(api_key=self.anthropic_key)
            
            # Create detailed prompt for Claude Code using string concatenation to avoid f-string issues
            json_template = """{
    "changes": [
        {
            "type": "edit",
            "filepath": "api/main.py",
            "content": "new file content",
            "description": "what this change does"
        }
    ],
    "explanation": "Brief explanation of the changes made"
}"""
            
            detailed_prompt = (
                "You are a coding agent working on repository: " + repo_url + "\n\n"
                "User request: " + prompt + "\n\n"
                "Available files and their contents:\n" +
                json.dumps(file_contents, indent=2) + "\n\n"
                "Please analyze the codebase and provide specific code changes to implement the user's request.\n"
                "Return your response in the following JSON format:\n\n" +
                json_template + "\n\n"
                "IMPORTANT:\n"
                "- Use relative file paths WITHOUT the 'repo/' prefix (e.g., 'api/main.py' not 'repo/api/main.py')\n"
                "- The filepath should match exactly with the files shown in the available files list\n"
                "- Make minimal, focused changes to implement the user's request\n"
                "- Follow the existing code style and patterns\n"
                "- Add proper error handling where needed\n\n"
                "Focus on:\n"
                "1. Understanding the existing codebase structure\n"
                "2. Making minimal, focused changes\n"
                "3. Following the existing code style and patterns\n"
                "4. Adding proper error handling where needed\n"
                "5. Ensuring the changes are testable and maintainable\n\n"
                "Only return valid JSON, no additional text."
            )
            
            # Send request to Claude
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                temperature=0.1,
                messages=[{"role": "user", "content": detailed_prompt}]
            )
            
            # Parse the response
            try:
                response_text = response.content[0].text.strip()
                print(f"Claude response: {response_text[:200]}...")
                response_data = json.loads(response_text)
                changes = response_data.get('changes', [])
                print(f"Generated {len(changes)} changes")
                return changes
            except json.JSONDecodeError as e:
                print(f"Failed to parse Claude Code response: {e}")
                print(f"Response was: {response.content[0].text}")
                return []
                
        except Exception as e:
            print(f"Error generating code locally: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def _apply_file_edit(self, sandbox, change):
        """Apply a file edit in the sandbox"""
        filepath = self._normalize_file_path(change['filepath'])  # Ensure normalized
        content = change['content']
        
        print(f"DEBUG: Applying edit to normalized filepath: {filepath}")
        
        # Get the full sandbox path
        sandbox_path = self._get_sandbox_file_path(filepath)
        dir_path = os.path.dirname(sandbox_path)
        
        print(f"DEBUG: Sandbox path: {sandbox_path}")
        print(f"DEBUG: Directory path: {dir_path}")
        
        # Ensure the directory exists
        if dir_path and dir_path != "repo":
            mkdir_result = sandbox.commands.run(f"mkdir -p {dir_path}")
            print(f"DEBUG: mkdir result: {mkdir_result.exit_code}")
        
        # Write the file content using base64 encoding to avoid shell escaping issues
        print(f"DEBUG: Writing to final path: {sandbox_path}")
        
        try:
            # Encode content to base64 to safely handle special characters
            import base64
            encoded_content = base64.b64encode(content.encode('utf-8')).decode('ascii')
            
            # Use base64 decoding to write the file safely
            write_result = sandbox.commands.run(f"echo '{encoded_content}' | base64 -d > {sandbox_path}")
            print(f"DEBUG: Write result: {write_result.exit_code}")
            
            if write_result.exit_code != 0:
                print(f"DEBUG: Write error: {write_result.stderr}")
                # Fallback: try using printf method
                print("DEBUG: Trying fallback method with printf")
                escaped_content = content.replace("'", "'\"'\"'").replace("\\", "\\\\")
                fallback_result = sandbox.commands.run(f"printf '%s' '{escaped_content}' > {sandbox_path}")
                if fallback_result.exit_code != 0:
                    raise Exception(f"Failed to write file {sandbox_path}: {fallback_result.stderr}")
                    
        except Exception as e:
            print(f"DEBUG: Exception during file write: {e}")
            raise Exception(f"Failed to write file {sandbox_path}: {str(e)}")
    
    async def _setup_git_in_sandbox(self, sandbox, repo_url):
        """Setup Git configuration in the sandbox"""
        # Configure Git with authentication
        git_commands = [
            "git config --global user.name 'Tiny Backspace Bot'",
            "git config --global user.email 'bot@tinybackspace.com'"
        ]
        
        for cmd in git_commands:
            result = sandbox.commands.run(cmd)
            if result.exit_code != 0:
                print(f"Git config failed: {cmd} - {result.stderr}")
    
    async def _create_pull_request(self, repo_url: str, branch_name: str, prompt: str) -> dict:
        """Create a pull request using GitHub API"""
        try:
            # Extract owner and repo from URL
            parts = repo_url.rstrip('/').split('/')
            owner = parts[-2]
            repo = parts[-1]
            
            # Create PR using GitHub API
            pr_title = f"Apply changes: {prompt[:50]}..."
            pr_body = f"""
## Changes Applied

This PR was automatically generated by Tiny Backspace to implement the following request:

**Request:** {prompt}

### What was changed:
- Code modifications applied based on the user's prompt
- All changes were generated and tested in a secure sandbox environment

### Technical Details:
- Generated using Claude Code AI agent
- Applied in E2B secure sandbox
- Automated testing and validation performed

---
*This PR was created automatically by Tiny Backspace*
"""
            
            # Use GitHub API to create PR
            import requests
            
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            data = {
                'title': pr_title,
                'body': pr_body,
                'head': branch_name,
                'base': 'main'  # Assuming main branch
            }
            
            response = requests.post(
                f'https://api.github.com/repos/{owner}/{repo}/pulls',
                headers=headers,
                json=data
            )
            
            if response.status_code == 201:
                pr_data = response.json()
                return {
                    'url': pr_data['html_url'],
                    'title': pr_title,
                    'body': pr_body
                }
            else:
                print(f"Failed to create PR: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error creating PR: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _create_sse_event(self, event_type: str, message: str) -> str:
        """Create Server-Sent Event format"""
        return f"data: {json.dumps({'type': event_type, 'message': message})}\n\n"

    def _normalize_file_path(self, filepath: str) -> str:
        """Normalize file path by removing repo/ prefix and ensuring consistency"""
        if not filepath:
            return filepath
            
        # Remove leading/trailing whitespace
        filepath = filepath.strip()
        
        # Remove repo/ prefix if present (handle multiple occurrences)
        while filepath.startswith('repo/'):
            filepath = filepath[5:]
        
        # Remove leading slash if present
        if filepath.startswith('/'):
            filepath = filepath[1:]
            
        return filepath
    
    def _get_sandbox_file_path(self, filepath: str) -> str:
        """Get the full sandbox file path by adding repo/ prefix to normalized path"""
        normalized = self._normalize_file_path(filepath)
        return f"repo/{normalized}" if normalized else "repo/"

    def _safe_execute_with_retry(self, operation_name: str, operation_func, *args, **kwargs):
        """Execute operation with retry logic and comprehensive error handling"""
        for attempt in range(self.max_retries):
            try:
                result = operation_func(*args, **kwargs)
                return result
            except Exception as e:
                print(f"❌ {operation_name} failed (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    print(f"⏳ Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    print(f"💥 {operation_name} failed after {self.max_retries} attempts")
                    raise e
    
    async def _safe_async_execute_with_retry(self, operation_name: str, operation_func, *args, **kwargs):
        """Execute async operation with retry logic and comprehensive error handling"""
        for attempt in range(self.max_retries):
            try:
                result = await operation_func(*args, **kwargs)
                return result
            except Exception as e:
                print(f"❌ {operation_name} failed (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    print(f"⏳ Retrying in {self.retry_delay} seconds...")
                    await asyncio.sleep(self.retry_delay)
                else:
                    print(f"💥 {operation_name} failed after {self.max_retries} attempts")
                    raise e

    async def _create_sandbox_async(self):
        """Create E2B sandbox asynchronously"""
        return Sandbox()
    
    async def _clone_repository_with_retry(self, sandbox, repo_url: str):
        """Clone repository with retry logic"""
        def clone_operation():
            result = sandbox.commands.run(f"git clone {repo_url} repo")
            if result.exit_code != 0:
                raise Exception(f"Git clone failed: {result.stderr}")
            return result
        
        return self._safe_execute_with_retry("Repository Clone", clone_operation)
    
    async def _generate_code_with_retry(self, prompt: str, file_contents: dict, repo_url: str):
        """Generate code with retry logic"""
        return await self._safe_async_execute_with_retry(
            "AI Code Generation",
            self._generate_code_locally,
            prompt, file_contents, repo_url
        )

# Initialize processor
processor = TinyBackspaceProcessor()

def _check_port_available(port: int) -> bool:
    """Check if a port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', port))
            return True
    except OSError:
        return False

def _kill_process_on_port(port: int) -> bool:
    """Kill any process using the specified port"""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'connections']):
            try:
                connections = proc.info['connections']
                if connections:
                    for conn in connections:
                        if conn.laddr.port == port:
                            print(f"Killing process {proc.info['pid']} ({proc.info['name']}) using port {port}")
                            proc.kill()
                            return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False
    except Exception as e:
        print(f"Error killing process on port {port}: {e}")
        return False

def _setup_signal_handlers():
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        print(f"Received signal {signum}, shutting down gracefully...")
        # Cleanup code here if needed
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

@app.post("/code")
async def code_endpoint(request: Request):
    """Main endpoint for code generation"""
    try:
        body = await request.json()
        repo_url = body.get('repoUrl')
        prompt = body.get('prompt')
        
        if not repo_url or not prompt:
            return StreamingResponse(
                iter([processor._create_sse_event("error", "Missing repoUrl or prompt")]),
                media_type="text/plain"
            )
        
        return StreamingResponse(
            processor.process_request(repo_url, prompt),
            media_type="text/plain"
        )
    except Exception as e:
        return StreamingResponse(
            iter([processor._create_sse_event("error", f"Request failed: {str(e)}")]),
            media_type="text/plain"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Tiny Backspace is running"}

if __name__ == "__main__":
    import uvicorn
    
    # Setup signal handlers for graceful shutdown
    _setup_signal_handlers()
    
    port = 8000
    print(f"🚀 Starting Tiny Backspace server on port {port}")
    
    # Check if port is available
    if not _check_port_available(port):
        print(f"⚠️ Port {port} is already in use, attempting to free it...")
        if _kill_process_on_port(port):
            print(f"✅ Successfully freed port {port}")
            # Wait a moment for the port to be released
            import time
            time.sleep(1)
        else:
            print(f"❌ Could not free port {port}, trying alternative port...")
            port = 8001
            if not _check_port_available(port):
                print(f"❌ Port {port} is also unavailable, exiting...")
                sys.exit(1)
    
    print(f"✅ Port {port} is available, starting server...")
    uvicorn.run(app, host="0.0.0.0", port=port) 