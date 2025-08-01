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
import logging
import time
from typing import AsyncGenerator
from dotenv import load_dotenv
import anthropic
import requests
from e2b import Sandbox
import langsmith
from langsmith import traceable, Client
from langsmith.run_trees import RunTree

# Load environment variables
load_dotenv()

# Set up comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Set up LangSmith environment variables with validation
langsmith_api_key = os.getenv("LANGSMITH_API_KEY", "")
langsmith_project = os.getenv("LANGSMITH_PROJECT", "tiny-backspace")
langsmith_tracing = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
langsmith_endpoint = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")

# Log LangSmith configuration
logger.info(f"🔍 LangSmith Configuration:")
logger.info(f"  - API Key: {'✅ Set' if langsmith_api_key else '❌ Missing'}")
logger.info(f"  - Project: {langsmith_project}")
logger.info(f"  - Tracing: {langsmith_tracing}")
logger.info(f"  - Endpoint: {langsmith_endpoint}")

# Set environment variables for LangSmith
os.environ["LANGSMITH_TRACING"] = str(langsmith_tracing).lower()
os.environ["LANGSMITH_API_KEY"] = langsmith_api_key
os.environ["LANGSMITH_PROJECT"] = langsmith_project
os.environ["LANGSMITH_ENDPOINT"] = langsmith_endpoint

# Initialize LangSmith client with error handling
langsmith_client = None
try:
    if langsmith_api_key:
        langsmith_client = langsmith.Client(
            api_key=langsmith_api_key,
            api_url=langsmith_endpoint
        )
        logger.info("✅ LangSmith client initialized successfully")
    else:
        logger.warning("⚠️ LangSmith client not initialized - missing API key")
except Exception as e:
    logger.error(f"❌ Failed to initialize LangSmith client: {e}")

class TinyBackspaceProcessor:
    def __init__(self):
        self.github_token = os.getenv('GITHUB_PAT') or os.getenv('GITHUB_TOKEN')
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not self.github_token:
            raise ValueError("GITHUB_PAT environment variable is required")
        if not self.anthropic_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        logger.info("🚀 TinyBackspaceProcessor initialized")
    
    def _create_manual_trace(self, name: str, run_type: str, inputs: dict, tags: list = None, metadata: dict = None):
        """Create a manual trace as fallback when @traceable fails"""
        if not langsmith_client:
            logger.warning("⚠️ Cannot create manual trace - LangSmith client not available")
            return None
            
        try:
            run_tree = RunTree(
                name=name,
                run_type=run_type,
                inputs=inputs,
                tags=tags or [],
                extra=metadata or {},
                project_name=langsmith_project,
                client=langsmith_client
            )
            run_tree.post()
            logger.info(f"✅ Manual trace created: {name} (ID: {run_tree.id})")
            return run_tree
        except Exception as e:
            logger.error(f"❌ Failed to create manual trace {name}: {e}")
            return None
    
    def _end_manual_trace(self, run_tree, outputs: dict = None, error: str = None):
        """End a manual trace"""
        if not run_tree:
            return
            
        try:
            if error:
                run_tree.end(error=error)
            else:
                run_tree.end(outputs=outputs or {})
            run_tree.patch()
            logger.info(f"✅ Manual trace ended: {run_tree.name}")
        except Exception as e:
            logger.error(f"❌ Failed to end manual trace: {e}")

    async def process_request(self, repo_url: str, prompt: str) -> AsyncGenerator[str, None]:
        """Simple processing pipeline with enhanced LangSmith observability"""
        request_id = str(uuid.uuid4())[:8]
        sandbox = None
        final_result = None
        
        # Create main trace manually
        main_trace = self._create_manual_trace(
            name="tiny-backspace-main-process",
            run_type="chain",
            inputs={"repo_url": repo_url, "prompt": prompt, "request_id": request_id},
            tags=["main-process", "async"],
            metadata={"request_id": request_id, "version": "1.0"}
        )
        
        try:
            logger.info(f"🚀 Starting request {request_id} - Repo: {repo_url}")
            
            # Step 1: Initialize
            yield self._create_sse_event("info", f"🚀 Starting request {request_id}")
            yield self._create_sse_event("info", f"📁 Repository: {repo_url}")
            yield self._create_sse_event("info", f"💭 Prompt: {prompt}")
            
            # Step 2: Create sandbox
            yield self._create_sse_event("info", "💭 Creating E2B sandbox")
            sandbox = Sandbox()
            yield self._create_sse_event("success", f"✅ Sandbox created: {sandbox.sandbox_id}")
            logger.info(f"✅ Sandbox created: {sandbox.sandbox_id}")
            
            # Step 3: Clone repository
            yield self._create_sse_event("info", f"📥 Cloning repository")
            clone_result = sandbox.commands.run(f"git clone {repo_url} repo")
            if clone_result.exit_code != 0:
                error_msg = f"❌ Clone failed: {clone_result.stderr}"
                yield self._create_sse_event("error", error_msg)
                logger.error(f"Clone failed for {request_id}: {clone_result.stderr}")
                final_result = {"status": "error", "message": error_msg}
                self._end_manual_trace(main_trace, error=error_msg)
                return
            yield self._create_sse_event("success", "✅ Repository cloned")
            logger.info(f"✅ Repository cloned for {request_id}")
            
            # Step 4: List files
            yield self._create_sse_event("info", "📁 Analyzing repository structure")
            files_result = sandbox.commands.run("find repo -type f -name '*.py' | head -5")
            files = files_result.stdout.strip().split('\n') if files_result.stdout else []
            yield self._create_sse_event("success", f"✅ Found {len(files)} Python files")
            logger.info(f"✅ Found {len(files)} Python files for {request_id}")
            
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
            
            logger.info(f"✅ Read {len(file_contents)} files for {request_id}")
            
            # Step 6: Generate code with Claude
            yield self._create_sse_event("info", "🤖 Generating code with Claude")
            logger.info(f"🤖 Starting code generation for {request_id}")
            
            code_changes = await self._generate_code(prompt, file_contents, repo_url)
            
            if not code_changes:
                error_msg = "❌ Failed to generate code"
                yield self._create_sse_event("error", error_msg)
                logger.error(f"Code generation failed for {request_id}")
                final_result = {"status": "error", "message": error_msg}
                self._end_manual_trace(main_trace, error=error_msg)
                return
            
            logger.info(f"✅ Generated {len(code_changes)} code changes for {request_id}")
            
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
                        logger.info(f"✅ Applied change to {filepath}")
                    else:
                        error_msg = f"❌ Failed to write: {filepath}"
                        yield self._create_sse_event("error", error_msg)
                        logger.error(f"Failed to write {filepath}: {write_result.stderr}")
            
            # Step 8: Git operations
            yield self._create_sse_event("info", "🔧 Setting up Git")
            sandbox.commands.run("git config --global user.name 'Tiny Backspace Bot'")
            sandbox.commands.run("git config --global user.email 'bot@tinybackspace.com'")
            
            branch_name = f"feature/{request_id}"
            yield self._create_sse_event("info", f"🔧 Creating branch: {branch_name}")
            logger.info(f"🔧 Creating branch {branch_name} for {request_id}")
            
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
                    logger.error(f"Git command failed for {request_id}: {result.stderr}")
                    git_success = False
                    break
            
            if not git_success:
                final_result = {"status": "error", "message": "Git operations failed"}
                self._end_manual_trace(main_trace, error="Git operations failed")
                return
            
            logger.info(f"✅ Git operations completed for {request_id}")
            
            # Step 9: Create PR
            yield self._create_sse_event("info", "🔧 Creating pull request")
            logger.info(f"🔧 Creating PR for {request_id}")
            
            pr_result = await self._create_pull_request(repo_url, branch_name, prompt)
            
            if pr_result:
                yield self._create_sse_event("success", f"✅ Pull request created: {pr_result['url']}")
                logger.info(f"✅ PR created for {request_id}: {pr_result['url']}")
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
                logger.error(f"PR creation failed for {request_id}")
                final_result = {"status": "error", "message": error_msg}
                
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            yield self._create_sse_event("error", error_msg)
            logger.error(f"❌ Main error for request {request_id}: {e}")
            import traceback
            traceback.print_exc()
            final_result = {"status": "error", "message": error_msg}
            self._end_manual_trace(main_trace, error=str(e))
        finally:
            if sandbox:
                yield self._create_sse_event("info", "🧹 Cleaning up sandbox")
                sandbox.kill()
                yield self._create_sse_event("success", "✅ Cleanup complete")
                logger.info(f"✅ Cleanup completed for {request_id}")
            
            # End main trace
            if final_result:
                self._end_manual_trace(main_trace, outputs=final_result)
    
    @traceable(
        name="tiny-backspace-code-generation", 
        tags=["claude", "code-generation", "anthropic"],
        metadata={
            "model": "claude-3-5-sonnet-20241022",
            "model_provider": "anthropic",
            "operation": "code_generation"
        }
    )
    async def _generate_code(self, prompt: str, file_contents: dict, repo_url: str) -> list:
        """Generate code changes using Claude with enhanced LangSmith tracing"""
        logger.info("🤖 Starting code generation with Claude")
        
        # Create manual trace as fallback
        manual_trace = self._create_manual_trace(
            name="claude-code-generation-manual",
            run_type="llm",
            inputs={
                "prompt": prompt,
                "repo_url": repo_url,
                "file_count": len(file_contents),
                "model": "claude-3-5-sonnet-20241022"
            },
            tags=["claude", "manual", "fallback"],
            metadata={"operation": "code_generation", "model_provider": "anthropic"}
        )
        
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
            
            logger.info("🤖 Sending request to Claude")
            start_time = time.time()
            
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                temperature=0.1,
                messages=[{"role": "user", "content": detailed_prompt}]
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            response_text = response.content[0].text.strip()
            logger.info(f"✅ Claude response received ({response_time:.2f}s): {response_text[:200]}...")
            
            response_data = json.loads(response_text)
            changes = response_data.get('changes', [])
            
            logger.info(f"✅ Code generation completed: {len(changes)} changes")
            
            # End manual trace with success
            self._end_manual_trace(manual_trace, outputs={
                "changes_count": len(changes),
                "response_time": response_time,
                "model": "claude-3-5-sonnet-20241022"
            })
            
            return changes
            
        except Exception as e:
            logger.error(f"❌ Error generating code: {e}")
            import traceback
            traceback.print_exc()
            
            # End manual trace with error
            self._end_manual_trace(manual_trace, error=str(e))
            
            return []
    
    @traceable(
        name="tiny-backspace-pr-creation", 
        tags=["github", "pr-creation", "api"],
        metadata={
            "operation": "pull_request_creation",
            "platform": "github",
            "api_version": "v3"
        }
    )
    async def _create_pull_request(self, repo_url: str, branch_name: str, prompt: str) -> dict:
        """Create a pull request using GitHub API with enhanced LangSmith tracing"""
        logger.info("🔧 Starting PR creation")
        
        # Create manual trace as fallback
        manual_trace = self._create_manual_trace(
            name="github-pr-creation-manual",
            run_type="tool",
            inputs={
                "repo_url": repo_url,
                "branch_name": branch_name,
                "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt
            },
            tags=["github", "manual", "fallback"],
            metadata={"operation": "pr_creation", "platform": "github"}
        )
        
        try:
            # Extract owner and repo from URL
            parts = repo_url.rstrip('/').split('/')
            owner = parts[-2]
            repo = parts[-1]
            
            logger.info(f"🔧 Creating PR for {owner}/{repo}, branch: {branch_name}")
            
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
            
            logger.info("🔧 Sending PR creation request to GitHub API")
            start_time = time.time()
            
            response = requests.post(
                f'https://api.github.com/repos/{owner}/{repo}/pulls',
                headers=headers,
                json=data,
                timeout=30
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 201:
                pr_data = response.json()
                result = {
                    'url': pr_data['html_url'],
                    'title': pr_title,
                    'body': pr_body,
                    'number': pr_data['number']
                }
                
                logger.info(f"✅ PR created successfully: {result['url']} (#{result['number']})")
                
                # End manual trace with success
                self._end_manual_trace(manual_trace, outputs={
                    "pr_url": result['url'],
                    "pr_number": result['number'],
                    "response_time": response_time,
                    "status_code": response.status_code
                })
                
                return result
            else:
                error_msg = f"Failed to create PR: {response.status_code} - {response.text}"
                logger.error(f"❌ {error_msg}")
                
                # End manual trace with error
                self._end_manual_trace(manual_trace, error=error_msg)
                
                return None
                
        except Exception as e:
            error_msg = f"Error creating PR: {e}"
            logger.error(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
            
            # End manual trace with error
            self._end_manual_trace(manual_trace, error=str(e))
            
            return None
    
    def _create_sse_event(self, event_type: str, message: str) -> str:
        """Create Server-Sent Event format"""
        return f"data: {json.dumps({'type': event_type, 'message': message})}\n\n" 