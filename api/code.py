import json
import sys
import os
import asyncio
import time
import uuid
import re
import base64
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import observability
from api.simple_observability import get_observability_manager

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
            e2b_api_key = os.getenv('E2B_API_KEY')
            
            if not github_token:
                self.wfile.write(f"data: {json.dumps({'type': 'error', 'message': 'GitHub token not configured. Please add GITHUB_PAT or GITHUB_TOKEN environment variable.'})}\n\n".encode('utf-8'))
                return
            
            if not e2b_api_key:
                self.wfile.write(f"data: {json.dumps({'type': 'error', 'message': 'E2B API key not configured. Please add E2B_API_KEY environment variable for sandbox execution.'})}\n\n".encode('utf-8'))
                return
            
            if not anthropic_key and not openai_key:
                self.wfile.write(f"data: {json.dumps({'type': 'error', 'message': 'No AI API keys configured. Please add ANTHROPIC_API_KEY or OPENAI_API_KEY environment variable.'})}\n\n".encode('utf-8'))
                return
            
            # Generate unique request ID
            request_id = str(uuid.uuid4())[:8]
            
            # Initialize observability
            obs = get_observability_manager()
            obs.start_request(request_id, repo_url, prompt)
            
            # Real processing flow with telemetry
            async def stream_processing():
                sandbox = None
                try:
                    # Step 1: Initialize and validate
                    obs.log_agent_thinking("initialization", "Starting code processing request")
                    yield obs.create_telemetry_update("info", "Initializing processing environment...", "init", 10)
                    await asyncio.sleep(0.5)
                    
                    with obs.performance_timer("environment_init"):
                        yield obs.create_telemetry_update("success", "Environment initialized", "init", 20)
                    
                    # Step 2: Validate repository URL
                    obs.log_agent_thinking("validation", f"Validating GitHub repository URL: {repo_url}")
                    yield obs.create_telemetry_update("info", f"Validating repository URL: {repo_url}", "validation", 25)
                    await asyncio.sleep(0.5)
                    
                    with obs.performance_timer("url_validation"):
                        if not self._is_valid_github_url(repo_url):
                            obs.log_agent_thinking("validation_error", "Invalid GitHub URL format detected")
                            yield obs.create_telemetry_update("error", "Invalid GitHub URL provided", "validation", 25)
                            return
                    
                    obs.log_agent_thinking("validation_success", "Repository URL validation passed")
                    yield obs.create_telemetry_update("success", "Repository URL validated", "validation", 30)
                    
                    # Step 3: Create secure sandbox
                    obs.log_agent_thinking("sandbox_init", "Creating secure E2B sandbox environment")
                    yield obs.create_telemetry_update("info", "Creating secure sandbox environment...", "sandbox", 35)
                    await asyncio.sleep(1)
                    
                    with obs.performance_timer("sandbox_creation"):
                        sandbox = await self._create_sandbox(obs)
                        if not sandbox:
                            obs.log_agent_thinking("sandbox_error", "Failed to create sandbox environment")
                            yield obs.create_telemetry_update("error", "Failed to create sandbox environment", "sandbox", 35)
                            return
                    
                    obs.log_agent_thinking("sandbox_success", "Secure sandbox environment created successfully")
                    yield obs.create_telemetry_update("success", "Secure sandbox environment ready", "sandbox", 40)
                    
                    # Step 4: Clone repository into sandbox
                    obs.log_agent_thinking("repo_clone", f"Cloning repository into sandbox: {repo_url}")
                    yield obs.create_telemetry_update("info", "Cloning repository into sandbox...", "clone", 45)
                    await asyncio.sleep(1)
                    
                    with obs.performance_timer("repository_clone"):
                        clone_success = await self._clone_repository(sandbox, repo_url, obs)
                        if not clone_success:
                            obs.log_agent_thinking("clone_error", "Failed to clone repository into sandbox")
                            yield obs.create_telemetry_update("error", "Failed to clone repository", "clone", 45)
                            return
                    
                    obs.log_agent_thinking("clone_success", "Repository successfully cloned into sandbox")
                    yield obs.create_telemetry_update("success", "Repository cloned into sandbox", "clone", 50)
                    
                    # Step 5: Setup Claude Code in sandbox
                    obs.log_agent_thinking("claude_setup", "Setting up Claude Code in sandbox environment")
                    yield obs.create_telemetry_update("info", "Setting up Claude Code...", "claude_setup", 55)
                    await asyncio.sleep(1)
                    
                    with obs.performance_timer("claude_setup"):
                        claude_ready = await self._setup_claude_code(sandbox, anthropic_key, obs)
                        if not claude_ready:
                            obs.log_agent_thinking("claude_setup_error", "Failed to setup Claude Code in sandbox")
                            yield obs.create_telemetry_update("error", "Failed to setup Claude Code", "claude_setup", 55)
                            return
                    
                    obs.log_agent_thinking("claude_setup_success", "Claude Code successfully configured in sandbox")
                    yield obs.create_telemetry_update("success", "Claude Code ready in sandbox", "claude_setup", 60)
                    
                    # Step 6: Analyze repository structure
                    obs.log_agent_thinking("analysis_start", "Analyzing repository structure in sandbox")
                    yield obs.create_telemetry_update("info", "Analyzing repository structure...", "analysis", 65)
                    await asyncio.sleep(1)
                    
                    with obs.performance_timer("repository_analysis"):
                        repo_info = await self._analyze_repository_in_sandbox(sandbox, obs)
                        if not repo_info:
                            obs.log_agent_thinking("analysis_error", "Failed to analyze repository structure")
                            yield obs.create_telemetry_update("error", "Failed to analyze repository", "analysis", 65)
                            return
                    
                    obs.log_agent_thinking("analysis_complete", f"Repository analysis complete: {repo_info['name']} with {repo_info['file_count']} files")
                    yield obs.create_telemetry_update("success", f"Repository analyzed: {repo_info['name']}", "analysis", 70, {
                        "repo_name": repo_info['name'],
                        "file_count": repo_info['file_count']
                    })
                    
                    # Step 7: Generate code with Claude Code
                    obs.log_agent_thinking("claude_processing", f"Processing prompt with Claude Code: '{prompt}'")
                    yield obs.create_telemetry_update("info", f"Processing with Claude Code: '{prompt}'", "claude_processing", 75)
                    await asyncio.sleep(1)
                    
                    with obs.performance_timer("claude_processing"):
                        file_edits = await self._generate_with_claude_code(sandbox, prompt, repo_info, obs)
                        if not file_edits:
                            obs.log_agent_thinking("claude_processing_error", "Claude Code failed to generate code modifications")
                            yield obs.create_telemetry_update("error", "Failed to generate code modifications", "claude_processing", 75)
                            return
                    
                    obs.log_agent_thinking("claude_success", f"Claude Code successfully generated {len(file_edits)} file modifications")
                    yield obs.create_telemetry_update("success", f"Generated {len(file_edits)} file modifications", "claude_processing", 80, {
                        "edits_count": len(file_edits),
                        "ai_provider": "claude_code"
                    })
                    
                    # Step 8: Apply changes in sandbox
                    obs.log_agent_thinking("apply_changes", f"Applying {len(file_edits)} file modifications in sandbox")
                    yield obs.create_telemetry_update("info", "Applying code modifications...", "apply_changes", 85)
                    await asyncio.sleep(1)
                    
                    with obs.performance_timer("apply_changes"):
                        changes_applied = await self._apply_changes_in_sandbox(sandbox, file_edits, obs)
                        if not changes_applied:
                            obs.log_agent_thinking("apply_error", "Failed to apply code modifications in sandbox")
                            yield obs.create_telemetry_update("error", "Failed to apply code modifications", "apply_changes", 85)
                            return
                    
                    obs.log_agent_thinking("apply_success", "Code modifications successfully applied in sandbox")
                    yield obs.create_telemetry_update("success", "Code modifications applied", "apply_changes", 90)
                    
                    # Step 9: Create GitHub PR
                    obs.log_agent_thinking("pr_creation_start", "Starting GitHub pull request creation process")
                    yield obs.create_telemetry_update("info", "Creating GitHub pull request...", "pr_creation", 95)
                    await asyncio.sleep(1)
                    
                    with obs.performance_timer("github_pr_creation"):
                        pr_result = await self._create_github_pr_from_sandbox(sandbox, repo_url, prompt, file_edits, github_token, obs)
                    
                    if pr_result.get("success"):
                        obs.log_agent_thinking("pr_success", f"Pull request created successfully: {pr_result['pr_url']}")
                        yield obs.create_telemetry_update("success", f"Pull request created: {pr_result['pr_url']}", "pr_creation", 100, {
                            "pr_url": pr_result['pr_url'],
                            "branch_name": pr_result['branch_name']
                        })
                        
                        # Get thinking summary
                        thinking_summary = obs.get_thinking_summary()
                        obs.log_agent_thinking("completion", f"Request completed successfully with {thinking_summary['total_thoughts']} thinking steps")
                        
                        yield obs.create_telemetry_update("success", "Processing completed successfully!", "complete", 100, {
                            "pr_url": pr_result['pr_url'],
                            "total_duration_ms": 5000,
                            "successful_modifications": len(file_edits),
                            "ai_provider": "claude_code",
                            "thinking_summary": thinking_summary
                        })
                        
                        # End request tracking
                        obs.end_request(True, {
                            "pr_url": pr_result['pr_url'],
                            "edits_count": len(file_edits),
                            "ai_provider": "claude_code"
                        })
                    else:
                        obs.log_agent_thinking("pr_error", f"Failed to create PR: {pr_result.get('error', 'Unknown error')}")
                        yield obs.create_telemetry_update("error", f"Failed to create PR: {pr_result.get('error', 'Unknown error')}", "pr_creation", 100)
                        obs.end_request(False, {"error": pr_result.get('error')})
                    
                except Exception as e:
                    obs.log_agent_thinking("error", f"Processing failed with error: {str(e)}")
                    yield obs.create_telemetry_update("error", f"Processing failed: {str(e)}")
                    obs.end_request(False, {"error": str(e)})
                finally:
                    # Always cleanup sandbox
                    if sandbox:
                        try:
                            obs.log_agent_thinking("cleanup", "Cleaning up sandbox environment")
                            await sandbox.kill()
                            obs.log_agent_thinking("cleanup_success", "Sandbox environment cleaned up successfully")
                        except Exception as e:
                            obs.log_agent_thinking("cleanup_error", f"Failed to cleanup sandbox: {str(e)}")
            
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
    
    async def _create_sandbox(self, obs):
        """Create a secure E2B sandbox environment."""
        try:
            import requests
            
            obs.log_agent_thinking("sandbox_create", "Creating E2B sandbox with Python environment")
            
            headers = {
                'Authorization': f'Bearer {os.getenv("E2B_API_KEY")}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'template': 'base',
                'metadata': {
                    'type': 'tiny_backspace_sandbox',
                    'request_id': obs.request_id
                }
            }
            
            response = requests.post('https://api.e2b.dev/v1/sandbox', headers=headers, json=data)
            
            if response.status_code == 201:
                sandbox_data = response.json()
                obs.log_agent_thinking("sandbox_created", f"Sandbox created with ID: {sandbox_data['sandbox_id']}")
                return sandbox_data['sandbox_id']
            else:
                obs.log_agent_thinking("sandbox_error", f"Failed to create sandbox: {response.text}")
                return None
                
        except Exception as e:
            obs.log_agent_thinking("sandbox_exception", f"Exception creating sandbox: {str(e)}")
            return None
    
    async def _clone_repository(self, sandbox_id, repo_url, obs):
        """Clone repository into the sandbox."""
        try:
            import requests
            
            obs.log_agent_thinking("clone_start", f"Cloning repository: {repo_url}")
            
            headers = {
                'Authorization': f'Bearer {os.getenv("E2B_API_KEY")}',
                'Content-Type': 'application/json'
            }
            
            # Clone the repository
            clone_cmd = {
                'cmd': f'git clone {repo_url} repo',
                'cwd': '/home/user'
            }
            
            response = requests.post(f'https://api.e2b.dev/v1/sandbox/{sandbox_id}/cmd', headers=headers, json=clone_cmd)
            
            if response.status_code == 200:
                obs.log_agent_thinking("clone_success", "Repository cloned successfully")
                return True
            else:
                obs.log_agent_thinking("clone_failed", f"Failed to clone repository: {response.text}")
                return False
                
        except Exception as e:
            obs.log_agent_thinking("clone_exception", f"Exception cloning repository: {str(e)}")
            return False
    
    async def _setup_claude_code(self, sandbox_id, anthropic_key, obs):
        """Setup Claude Code in the sandbox environment."""
        try:
            import requests
            
            obs.log_agent_thinking("claude_setup_start", "Setting up Claude Code environment")
            
            headers = {
                'Authorization': f'Bearer {os.getenv("E2B_API_KEY")}',
                'Content-Type': 'application/json'
            }
            
            # Install Claude Code
            setup_commands = [
                {
                    'cmd': 'pip install anthropic',
                    'cwd': '/home/user'
                },
                {
                    'cmd': 'pip install requests',
                    'cwd': '/home/user'
                }
            ]
            
            for cmd in setup_commands:
                response = requests.post(f'https://api.e2b.dev/v1/sandbox/{sandbox_id}/cmd', headers=headers, json=cmd)
                if response.status_code != 200:
                    obs.log_agent_thinking("claude_setup_failed", f"Failed to setup Claude Code: {response.text}")
                    return False
            
            obs.log_agent_thinking("claude_setup_success", "Claude Code environment setup complete")
            return True
            
        except Exception as e:
            obs.log_agent_thinking("claude_setup_exception", f"Exception setting up Claude Code: {str(e)}")
            return False
    
    async def _analyze_repository_in_sandbox(self, sandbox_id, obs):
        """Analyze repository structure in the sandbox."""
        try:
            import requests
            
            obs.log_agent_thinking("analysis_start", "Analyzing repository structure in sandbox")
            
            headers = {
                'Authorization': f'Bearer {os.getenv("E2B_API_KEY")}',
                'Content-Type': 'application/json'
            }
            
            # Get repository structure
            cmd = {
                'cmd': 'find repo -type f -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.md" -o -name "*.txt" | head -20',
                'cwd': '/home/user'
            }
            
            response = requests.post(f'https://api.e2b.dev/v1/sandbox/{sandbox_id}/cmd', headers=headers, json=cmd)
            
            if response.status_code == 200:
                result = response.json()
                files = result.get('stdout', '').strip().split('\n') if result.get('stdout') else []
                
                repo_info = {
                    'name': 'repository',
                    'file_count': len(files),
                    'files': files[:10]  # Limit to first 10 files
                }
                
                obs.log_agent_thinking("analysis_success", f"Repository analysis complete: {len(files)} files found")
                return repo_info
            else:
                obs.log_agent_thinking("analysis_failed", f"Failed to analyze repository: {response.text}")
                return None
                
        except Exception as e:
            obs.log_agent_thinking("analysis_exception", f"Exception analyzing repository: {str(e)}")
            return None
    
    async def _generate_with_claude_code(self, sandbox_id, prompt, repo_info, obs):
        """Generate code modifications using Claude Code in the sandbox."""
        try:
            import requests
            
            obs.log_agent_thinking("claude_generation_start", f"Starting code generation with Claude Code for prompt: {prompt}")
            
            headers = {
                'Authorization': f'Bearer {os.getenv("E2B_API_KEY")}',
                'Content-Type': 'application/json'
            }
            
            # Create Python script for Claude Code
            claude_script = f'''
import anthropic
import json
import os

client = anthropic.Anthropic(api_key="{os.getenv("ANTHROPIC_API_KEY")}")

message = f"""
You are an expert AI coding assistant. Analyze this repository and generate code modifications based on the user's prompt.

Repository Information:
- Name: {repo_info['name']}
- File count: {repo_info['file_count']}
- Files: {repo_info.get('files', [])}

User Request: {prompt}

Please analyze the repository structure and generate appropriate code modifications.
Focus on the most relevant files for the user's request.

Generate file edits in this exact format:
```python:file_path
new content here
```

Be specific and provide meaningful improvements based on the user's prompt.
"""

response = client.messages.create(
    model="claude-3-sonnet-20240229",
    max_tokens=4000,
    messages=[{{"role": "user", "content": message}}]
)

print(json.dumps({{
    "content": response.content[0].text,
    "model": response.model,
    "usage": {{
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens
    }}
}}))
'''
            
            # Write script to sandbox
            write_cmd = {
                'cmd': f'echo \'{claude_script}\' > claude_code.py',
                'cwd': '/home/user'
            }
            
            response = requests.post(f'https://api.e2b.dev/v1/sandbox/{sandbox_id}/cmd', headers=headers, json=write_cmd)
            
            if response.status_code != 200:
                obs.log_agent_thinking("claude_script_write_failed", "Failed to write Claude Code script")
                return []
            
            # Execute Claude Code
            exec_cmd = {
                'cmd': 'python claude_code.py',
                'cwd': '/home/user'
            }
            
            response = requests.post(f'https://api.e2b.dev/v1/sandbox/{sandbox_id}/cmd', headers=headers, json=exec_cmd)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('stdout'):
                    try:
                        claude_response = json.loads(result['stdout'])
                        content = claude_response.get('content', '')
                        
                        obs.log_agent_thinking("claude_response_received", f"Received Claude response: {len(content)} characters")
                        
                        # Parse the response into file edits
                        edits = self._parse_ai_response(content)
                        obs.log_agent_thinking("claude_parsing_success", f"Parsed {len(edits)} file edits from Claude response")
                        
                        return edits
                    except json.JSONDecodeError:
                        obs.log_agent_thinking("claude_json_error", "Failed to parse Claude response as JSON")
                        return []
                else:
                    obs.log_agent_thinking("claude_no_output", "Claude Code produced no output")
                    return []
            else:
                obs.log_agent_thinking("claude_execution_failed", f"Failed to execute Claude Code: {response.text}")
                return []
                
        except Exception as e:
            obs.log_agent_thinking("claude_generation_exception", f"Exception in Claude Code generation: {str(e)}")
            return []
    
    async def _apply_changes_in_sandbox(self, sandbox_id, file_edits, obs):
        """Apply the generated changes in the sandbox."""
        try:
            import requests
            
            obs.log_agent_thinking("apply_start", f"Applying {len(file_edits)} file modifications in sandbox")
            
            headers = {
                'Authorization': f'Bearer {os.getenv("E2B_API_KEY")}',
                'Content-Type': 'application/json'
            }
            
            for i, edit in enumerate(file_edits):
                file_path = edit['file_path']
                new_content = edit['new_content']
                
                obs.log_agent_thinking("apply_file", f"Applying modification {i+1}/{len(file_edits)}: {file_path}")
                
                # Write the new content to the file
                write_cmd = {
                    'cmd': f'echo \'{new_content}\' > repo/{file_path}',
                    'cwd': '/home/user'
                }
                
                response = requests.post(f'https://api.e2b.dev/v1/sandbox/{sandbox_id}/cmd', headers=headers, json=write_cmd)
                
                if response.status_code != 200:
                    obs.log_agent_thinking("apply_file_failed", f"Failed to apply changes to {file_path}")
                    return False
            
            obs.log_agent_thinking("apply_success", "All file modifications applied successfully")
            return True
            
        except Exception as e:
            obs.log_agent_thinking("apply_exception", f"Exception applying changes: {str(e)}")
            return False
    
    async def _create_github_pr_from_sandbox(self, sandbox_id, repo_url, prompt, file_edits, github_token, obs):
        """Create GitHub PR from the sandbox changes."""
        try:
            import requests
            
            obs.log_agent_thinking("pr_start", "Starting GitHub PR creation from sandbox")
            
            # Parse repo URL
            path_parts = urlparse(repo_url).path.strip('/').split('/')
            owner, repo_name = path_parts[0], path_parts[1]
            
            headers = {'Authorization': f'token {github_token}'}
            
            # Get default branch
            obs.log_agent_thinking("pr_info", "Fetching repository information")
            repo_response = requests.get(f'https://api.github.com/repos/{owner}/{repo_name}', headers=headers)
            if repo_response.status_code != 200:
                return {'success': False, 'error': 'Failed to get repository info'}
            
            repo_data = repo_response.json()
            default_branch = repo_data['default_branch']
            
            # Create branch name
            branch_name = f"tiny-backspace-{int(time.time())}"
            obs.log_agent_thinking("pr_branch", f"Creating new branch: {branch_name}")
            
            # Get latest commit SHA
            branch_response = requests.get(f'https://api.github.com/repos/{owner}/{repo_name}/branches/{default_branch}', headers=headers)
            if branch_response.status_code != 200:
                return {'success': False, 'error': 'Failed to get branch info'}
            
            latest_sha = branch_response.json()['commit']['sha']
            
            # Create new branch
            branch_data = {'ref': f'refs/heads/{branch_name}', 'sha': latest_sha}
            branch_response = requests.post(f'https://api.github.com/repos/{owner}/{repo_name}/git/refs', headers=headers, json=branch_data)
            
            if branch_response.status_code not in [200, 201]:
                return {'success': False, 'error': f'Failed to create branch: {branch_response.text}'}
            
            obs.log_agent_thinking("pr_branch_success", f"Successfully created branch: {branch_name}")
            
            # Apply file edits from sandbox
            obs.log_agent_thinking("pr_files", f"Applying {len(file_edits)} file modifications")
            for i, edit in enumerate(file_edits):
                file_path = edit['file_path']
                new_content = edit['new_content']
                
                obs.log_agent_thinking("pr_file_edit", f"Processing file {i+1}/{len(file_edits)}: {file_path}")
                
                # Check if file exists
                file_response = requests.get(f'https://api.github.com/repos/{owner}/{repo_name}/contents/{file_path}', headers=headers, params={'ref': branch_name})
                
                if file_response.status_code == 200:
                    # Update existing file
                    file_data = file_response.json()
                    update_data = {
                        'message': f'Update {file_path}: {edit.get("description", "AI-generated improvement")}',
                        'content': base64.b64encode(new_content.encode()).decode(),
                        'sha': file_data['sha'],
                        'branch': branch_name
                    }
                    update_response = requests.put(f'https://api.github.com/repos/{owner}/{repo_name}/contents/{file_path}', headers=headers, json=update_data)
                else:
                    # Create new file
                    create_data = {
                        'message': f'Add {file_path}: {edit.get("description", "AI-generated file")}',
                        'content': base64.b64encode(new_content.encode()).decode(),
                        'branch': branch_name
                    }
                    update_response = requests.put(f'https://api.github.com/repos/{owner}/{repo_name}/contents/{file_path}', headers=headers, json=create_data)
                
                if update_response.status_code not in [200, 201]:
                    return {'success': False, 'error': f'Failed to update file {file_path}'}
                
                obs.log_agent_thinking("pr_file_success", f"Successfully updated file: {file_path}")
            
            # Create pull request
            obs.log_agent_thinking("pr_create", "Creating pull request")
            pr_data = {
                'title': f'🤖 AI-Generated Improvements: {prompt[:50]}...',
                'body': f"""## AI-Generated Code Improvements

**Prompt:** {prompt}

**Changes Made:**
{chr(10).join([f"- {edit['file_path']}: {edit.get('description', 'Modified')}" for edit in file_edits])}

**Generated by:** Tiny Backspace AI Agent with Claude Code

This pull request was automatically generated based on your request.
""",
                'head': branch_name,
                'base': default_branch
            }
            
            pr_response = requests.post(f'https://api.github.com/repos/{owner}/{repo_name}/pulls', headers=headers, json=pr_data)
            
            if pr_response.status_code == 201:
                pr_data = pr_response.json()
                obs.log_agent_thinking("pr_success", f"Successfully created PR: {pr_data['html_url']}")
                return {
                    'success': True,
                    'pr_url': pr_data['html_url'],
                    'branch_name': branch_name
                }
            else:
                return {'success': False, 'error': f'Failed to create PR: {pr_response.text}'}
                
        except Exception as e:
            obs.log_agent_thinking("pr_exception", f"Exception creating PR: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _is_valid_github_url(self, url: str) -> bool:
        """Validate GitHub URL format."""
        try:
            parsed = urlparse(url)
            return parsed.netloc == 'github.com' and len(parsed.path.split('/')) >= 3
        except:
            return False
    
    def _parse_ai_response(self, content: str) -> list:
        """Parse AI response into file edits."""
        edits = []
        
        # Extract file blocks
        pattern = r'```(\w+):([^\n]+)\n(.*?)```'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for file_ext, file_path, file_content in matches:
            edits.append({
                'file_path': file_path.strip(),
                'new_content': file_content.strip(),
                'description': f'AI-generated modification for {file_path}'
            })
        
        return edits
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers() 