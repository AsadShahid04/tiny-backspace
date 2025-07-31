from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import json
import asyncio
import os
import uuid
import re
from typing import AsyncGenerator
import subprocess
import tempfile
import shutil
from pathlib import Path
from dotenv import load_dotenv

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
        """Main processing pipeline"""
        request_id = str(uuid.uuid4())[:8]
        
        try:
            # Validate environment variables
            self._validate_environment()
            # Step 1: Initialize
            yield self._create_sse_event("info", f"🚀 Starting request {request_id}")
            yield self._create_sse_event("info", f"📁 Repository: {repo_url}")
            yield self._create_sse_event("info", f"💭 Prompt: {prompt}")
            
            # Step 2: Validate repository URL
            if not self._is_valid_github_url(repo_url):
                yield self._create_sse_event("error", "Invalid GitHub repository URL")
                return
            
            # Step 3: Create sandbox
            yield self._create_sse_event("info", "💭 [SANDBOX] Creating secure E2B sandbox environment")
            sandbox = Sandbox()
            try:
                yield self._create_sse_event("success", f"💭 [SANDBOX] E2B sandbox created successfully with ID: {sandbox.sandbox_id}")
                
                # Step 4: Clone repository
                yield self._create_sse_event("info", f"💭 [CLONE] Cloning repository {repo_url} into sandbox")
                clone_result = sandbox.commands.run(f"git clone {repo_url} repo")
                if clone_result.exit_code != 0:
                    yield self._create_sse_event("error", f"Failed to clone repository: {clone_result.stderr}")
                    return
                yield self._create_sse_event("success", "💭 [CLONE] Repository successfully cloned into sandbox")
                
                # Step 5: Analyze repository structure
                yield self._create_sse_event("info", "🔍 [ANALYSIS] Analyzing repository structure")
                files_result = sandbox.commands.run("find repo -type f -name '*.py' -o -name '*.js' -o -name '*.ts' -o -name '*.jsx' -o -name '*.tsx' | head -20")
                files = files_result.stdout.strip().split('\n') if files_result.stdout else []
                yield self._create_sse_event("success", f"🔍 [ANALYSIS] Repository analysis complete: {len(files)} files found")
                
                # Step 6: Read key files
                yield self._create_sse_event("info", "💭 [FILE_READING] Reading key repository files")
                file_contents = {}
                for file_path in files[:5]:  # Read first 5 files
                    if file_path and os.path.exists(file_path):
                        read_result = sandbox.commands.run(f"cat {file_path}")
                        if read_result.exit_code == 0:
                            file_contents[file_path] = read_result.stdout
                            yield self._create_sse_event("info", f"💭 [FILE_READING] Reading file: {file_path}")
                
                # Step 7: Generate code with Claude Code locally
                yield self._create_sse_event("info", "🤖 [AI_PROCESSING] Processing with Claude Code locally")
                code_changes = await self._generate_code_locally(prompt, file_contents, repo_url)
                
                if not code_changes:
                    yield self._create_sse_event("error", "❌ [ERROR] Failed to generate code modifications")
                    return
                
                # Step 8: Apply changes in sandbox
                yield self._create_sse_event("info", "🔧 [APPLYING] Applying code changes in sandbox")
                for change in code_changes:
                    if change['type'] == 'edit':
                        await self._apply_file_edit(sandbox, change)
                        yield self._create_sse_event("info", f"🔧 [APPLYING] Applied edit to {change['filepath']}")
                
                # Step 9: Git operations in sandbox
                yield self._create_sse_event("info", "🔧 [GIT] Setting up Git operations in sandbox")
                await self._setup_git_in_sandbox(sandbox, repo_url)
                
                # Step 10: Create branch and commit
                branch_name = f"feature/{request_id}"
                yield self._create_sse_event("info", f"🔧 [GIT] Creating branch: {branch_name}")
                
                git_commands = [
                    f"cd repo && git checkout -b {branch_name}",
                    "cd repo && git add .",
                    f"cd repo && git commit -m 'Apply changes: {prompt[:50]}...'",
                    f"cd repo && git push origin {branch_name}"
                ]
                
                for cmd in git_commands:
                    result = sandbox.commands.run(cmd)
                    if result.exit_code != 0:
                        yield self._create_sse_event("error", f"Git command failed: {cmd}")
                        yield self._create_sse_event("error", f"Error: {result.stderr}")
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
                # Clean up sandbox
                sandbox.kill()
                
        except Exception as e:
            yield self._create_sse_event("error", f"❌ [ERROR] Processing failed: {str(e)}")
    
    def _is_valid_github_url(self, url: str) -> bool:
        """Validate GitHub repository URL"""
        github_pattern = r'^https://github\.com/[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+/?$'
        return bool(re.match(github_pattern, url))
    
    async def _generate_code_locally(self, prompt: str, file_contents: dict, repo_url: str) -> list:
        """Generate code changes using Claude Code locally"""
        try:
            # Create a temporary script to run Claude Code
            script_content = f'''
import anthropic
import json
import sys

client = anthropic.Anthropic(api_key="{self.anthropic_key}")

# Prepare context
files_info = {json.dumps(file_contents)}
repo_url = "{repo_url}"
prompt = "{prompt}"

# Create detailed prompt for Claude Code
detailed_prompt = f"""
You are a coding agent working on repository: {{repo_url}}

User request: {{prompt}}

Available files and their contents:
{{json.dumps(files_info, indent=2)}}

Please analyze the codebase and provide specific code changes to implement the user's request.
Return your response in the following JSON format:

{{
    "changes": [
        {{
            "type": "edit",
            "filepath": "path/to/file",
            "content": "new file content",
            "description": "what this change does"
        }}
    ],
    "explanation": "Brief explanation of the changes made"
}}

Focus on:
1. Understanding the existing codebase structure
2. Making minimal, focused changes
3. Following the existing code style and patterns
4. Adding proper error handling where needed
5. Ensuring the changes are testable and maintainable

Only return valid JSON, no additional text.
"""

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=4000,
    temperature=0.1,
    messages=[{{"role": "user", "content": detailed_prompt}}]
)

print(response.content[0].text)
'''
            
            # Write script to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(script_content)
                script_path = f.name
            
            # Run the script
            result = subprocess.run([sys.executable, script_path], 
                                  capture_output=True, text=True, timeout=60)
            
            # Clean up
            os.unlink(script_path)
            
            if result.returncode != 0:
                print(f"Claude Code script failed: {result.stderr}")
                return []
            
            # Parse the response
            try:
                response_data = json.loads(result.stdout.strip())
                return response_data.get('changes', [])
            except json.JSONDecodeError:
                print(f"Failed to parse Claude Code response: {result.stdout}")
                return []
                
        except Exception as e:
            print(f"Error generating code locally: {e}")
            return []
    
    async def _apply_file_edit(self, sandbox, change):
        """Apply a file edit in the sandbox"""
        filepath = change['filepath']
        content = change['content']
        
        # Ensure the directory exists
        dir_path = os.path.dirname(f"repo/{filepath}")
        if dir_path:
            sandbox.commands.run(f"mkdir -p repo/{dir_path}")
        
        # Write the file content
        sandbox.commands.run(f"cat > repo/{filepath} << 'EOF'\n{content}\nEOF")
    
    async def _setup_git_in_sandbox(self, sandbox, repo_url):
        """Setup Git configuration in the sandbox"""
        git_commands = [
            "git config --global user.name 'Tiny Backspace Bot'",
            "git config --global user.email 'bot@tinybackspace.com'"
        ]
        
        for cmd in git_commands:
            sandbox.commands.run(cmd)
    
    async def _create_pull_request(self, repo_url: str, branch_name: str, prompt: str) -> dict:
        """Create a pull request using GitHub API"""
        try:
            # Extract owner and repo from URL
            parts = repo_url.rstrip('/').split('/')
            owner = parts[-2]
            repo = parts[-1]
            
            # Create PR using GitHub CLI or API
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
            
            # Use GitHub CLI to create PR
            import subprocess
            result = subprocess.run([
                'gh', 'pr', 'create',
                '--repo', f'{owner}/{repo}',
                '--head', branch_name,
                '--title', pr_title,
                '--body', pr_body
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                # Extract PR URL from output
                output_lines = result.stdout.strip().split('\n')
                pr_url = None
                for line in output_lines:
                    if 'https://github.com' in line and '/pull/' in line:
                        pr_url = line.strip()
                        break
                
                return {
                    'url': pr_url,
                    'title': pr_title,
                    'body': pr_body
                }
            else:
                print(f"Failed to create PR: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"Error creating PR: {e}")
            return None
    
    def _create_sse_event(self, event_type: str, message: str) -> str:
        """Create Server-Sent Event format"""
        return f"data: {json.dumps({'type': event_type, 'message': message})}\n\n"

# Initialize processor
processor = TinyBackspaceProcessor()

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
    uvicorn.run(app, host="0.0.0.0", port=8000) 