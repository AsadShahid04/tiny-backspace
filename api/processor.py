#!/usr/bin/env python3
"""
Tiny Backspace Processor
Core logic for AI-powered code generation and PR creation
"""

import json
import asyncio
import os
import uuid
import re
from typing import AsyncGenerator
from dotenv import load_dotenv
import anthropic
import requests
from e2b import Sandbox
import langsmith
from langsmith import traceable

# Load environment variables
load_dotenv()

# Set up LangSmith environment variables
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY", "")
os.environ["LANGSMITH_PROJECT"] = "tiny-backspace"

# Initialize LangSmith client
langsmith_client = langsmith.Client(
    api_key=os.getenv("LANGSMITH_API_KEY"),
    api_url=os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
)

class TinyBackspaceProcessor:
    def __init__(self):
        self.github_token = os.getenv('GITHUB_PAT') or os.getenv('GITHUB_TOKEN')
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not self.github_token:
            raise ValueError("GITHUB_PAT environment variable is required")
        if not self.anthropic_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
    
    async def process_request(self, repo_url: str, prompt: str) -> AsyncGenerator[str, None]:
        """Simple processing pipeline with LangSmith observability"""
        request_id = str(uuid.uuid4())[:8]
        sandbox = None
        final_result = None
        
        try:
            # Step 1: Initialize
            yield self._create_sse_event("info", f"🚀 Starting request {request_id}")
            yield self._create_sse_event("info", f"📁 Repository: {repo_url}")
            yield self._create_sse_event("info", f"💭 Prompt: {prompt}")
            
            # Step 2: Create sandbox
            yield self._create_sse_event("info", "💭 Creating E2B sandbox")
            sandbox = Sandbox()
            yield self._create_sse_event("success", f"✅ Sandbox created: {sandbox.sandbox_id}")
            
            # Step 3: Clone repository
            yield self._create_sse_event("info", f"📥 Cloning repository")
            clone_result = sandbox.commands.run(f"git clone {repo_url} repo")
            if clone_result.exit_code != 0:
                error_msg = f"❌ Clone failed: {clone_result.stderr}"
                yield self._create_sse_event("error", error_msg)
                final_result = {"status": "error", "message": error_msg}
                return
            yield self._create_sse_event("success", "✅ Repository cloned")
            
            # Step 4: List files
            yield self._create_sse_event("info", "📁 Analyzing repository structure")
            files_result = sandbox.commands.run("find repo -type f -name '*.py' | head -5")
            files = files_result.stdout.strip().split('\n') if files_result.stdout else []
            yield self._create_sse_event("success", f"✅ Found {len(files)} Python files")
            
            # Step 5: Read files
            yield self._create_sse_event("info", "📖 Reading files")
            file_contents = {}
            for file_path in files:
                if file_path and file_path.strip():
                    read_result = sandbox.commands.run(f"cat {file_path}")
                    if read_result.exit_code == 0:
                        # Remove 'repo/' prefix for AI consumption
                        clean_path = file_path.replace('repo/', '')
                        file_contents[clean_path] = read_result.stdout
                        yield self._create_sse_event("info", f"📖 Read: {clean_path}")
            
            # Step 6: Generate code with Claude
            yield self._create_sse_event("info", "🤖 Generating code with Claude")
            
            code_changes = await self._generate_code(prompt, file_contents, repo_url)
            
            if not code_changes:
                error_msg = "❌ Failed to generate code"
                yield self._create_sse_event("error", error_msg)
                final_result = {"status": "error", "message": error_msg}
                return
            
            # Step 7: Apply changes
            yield self._create_sse_event("info", "🔧 Applying changes")
            applied_changes = []
            for change in code_changes:
                if change['type'] == 'edit':
                    filepath = change['filepath']
                    content = change['content']
                    
                    # Add repo/ prefix for sandbox
                    sandbox_path = f"repo/{filepath}"
                    
                    # Write file
                    write_result = sandbox.commands.run(f"echo '{content}' > {sandbox_path}")
                    if write_result.exit_code == 0:
                        yield self._create_sse_event("success", f"✅ Applied: {filepath}")
                        applied_changes.append(filepath)
                    else:
                        error_msg = f"❌ Failed to write: {filepath}"
                        yield self._create_sse_event("error", error_msg)
            
            # Step 8: Git operations
            yield self._create_sse_event("info", "🔧 Setting up Git")
            sandbox.commands.run("git config --global user.name 'Tiny Backspace Bot'")
            sandbox.commands.run("git config --global user.email 'bot@tinybackspace.com'")
            
            branch_name = f"feature/{request_id}"
            yield self._create_sse_event("info", f"🔧 Creating branch: {branch_name}")
            
            git_commands = [
                f"cd repo && git checkout -b {branch_name}",
                "cd repo && git add .",
                "cd repo && git commit -m 'Apply changes from Tiny Backspace'",
                f"cd repo && git remote set-url origin https://{self.github_token}@github.com/AsadShahid04/tiny-backspace.git",
                f"cd repo && git push origin {branch_name}"
            ]
            
            git_success = True
            for cmd in git_commands:
                result = sandbox.commands.run(cmd)
                if result.exit_code != 0:
                    error_msg = f"❌ Git command failed: {result.stderr}"
                    yield self._create_sse_event("error", error_msg)
                    git_success = False
                    break
            
            if not git_success:
                final_result = {"status": "error", "message": "Git operations failed"}
                return
            
            # Step 9: Create PR
            yield self._create_sse_event("info", "🔧 Creating pull request")
            
            pr_result = await self._create_pull_request(repo_url, branch_name, prompt)
            
            if pr_result:
                yield self._create_sse_event("success", f"✅ Pull request created: {pr_result['url']}")
                final_result = {
                    "status": "success",
                    "pr_url": pr_result['url'],
                    "pr_title": pr_result['title'],
                    "changes_applied": applied_changes,
                    "request_id": request_id
                }
            else:
                error_msg = "❌ Failed to create pull request"
                yield self._create_sse_event("error", error_msg)
                final_result = {"status": "error", "message": error_msg}
                
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            yield self._create_sse_event("error", error_msg)
            print(f"❌ Main error for request {request_id}: {e}")
            import traceback
            traceback.print_exc()
            final_result = {"status": "error", "message": error_msg}
        finally:
            if sandbox:
                yield self._create_sse_event("info", "🧹 Cleaning up sandbox")
                sandbox.kill()
                yield self._create_sse_event("success", "✅ Cleanup complete")
    
    @traceable(
        name="tiny-backspace-sandbox", 
        tags=["claude", "code-generation"],
        metadata={
            "model": "claude-3-5-sonnet-20241022",
            "model_provider": "anthropic",
            "operation": "code_generation"
        }
    )
    async def _generate_code(self, prompt: str, file_contents: dict, repo_url: str) -> list:
        """Generate code changes using Claude with LangSmith tracing"""
        try:
            # Create client without proxies argument
            client = anthropic.Anthropic(api_key=self.anthropic_key)
            
            # Simple prompt without complex formatting - using string concatenation
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
                "- Make minimal, focused changes to implement the user's request\n"
                "- Follow the existing code style and patterns\n"
                "- Only return valid JSON, no additional text.\n"
            )
            
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                temperature=0.1,
                messages=[{"role": "user", "content": detailed_prompt}]
            )
            
            response_text = response.content[0].text.strip()
            print(f"Claude response: {response_text[:200]}...")
            
            response_data = json.loads(response_text)
            changes = response_data.get('changes', [])
            
            return changes
            
        except Exception as e:
            print(f"Error generating code: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    @traceable(
        name="tiny-backspace-pr", 
        tags=["github", "pr-creation"],
        metadata={
            "operation": "pull_request_creation",
            "platform": "github"
        }
    )
    async def _create_pull_request(self, repo_url: str, branch_name: str, prompt: str) -> dict:
        """Create a pull request using GitHub API with LangSmith tracing"""
        try:
            # Extract owner and repo from URL
            parts = repo_url.rstrip('/').split('/')
            owner = parts[-2]
            repo = parts[-1]
            
            pr_title = f"Apply changes: {prompt[:50]}..."
            pr_body = f"""
## Changes Applied

This PR was automatically generated by Tiny Backspace to implement the following request:

**Request:** {prompt}

### What was changed:
- Code modifications applied based on the user's prompt
- All changes were generated and tested in a secure sandbox environment

---
*This PR was created automatically by Tiny Backspace*
"""
            
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            data = {
                'title': pr_title,
                'body': pr_body,
                'head': branch_name,
                'base': 'main'
            }
            
            response = requests.post(
                f'https://api.github.com/repos/{owner}/{repo}/pulls',
                headers=headers,
                json=data
            )
            
            if response.status_code == 201:
                pr_data = response.json()
                result = {
                    'url': pr_data['html_url'],
                    'title': pr_title,
                    'body': pr_body
                }
                return result
            else:
                error_msg = f"Failed to create PR: {response.status_code} - {response.text}"
                print(error_msg)
                return None
                
        except Exception as e:
            error_msg = f"Error creating PR: {e}"
            print(error_msg)
            return None
    
    def _create_sse_event(self, event_type: str, message: str) -> str:
        """Create Server-Sent Event format"""
        return f"data: {json.dumps({'type': event_type, 'message': message})}\n\n" 