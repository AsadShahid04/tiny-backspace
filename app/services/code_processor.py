import asyncio
import time
import uuid
from typing import AsyncGenerator, Dict, Any
from e2b import Sandbox
from loguru import logger
import re
from app.services.agent_runner import run_agent
from app.services.github_pr_creator import github_pr_creator
from app.logging_config import (
    observability_logger,
    log_agent_operation,
    log_performance_metric,
    log_error_with_context,
    performance_timer,
    get_request_id,
    log_with_request_id
)


async def process_code_request(repo_url: str, prompt: str) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Process a code request by:
    1. Initializing E2B sandbox
    2. Cloning the GitHub repo
    3. Streaming back status updates
    4. Planning and implementing changes with comprehensive observability
    """
    
    # Generate unique request ID for correlation
    request_id = str(uuid.uuid4())[:8]
    observability_logger.set_request_id(request_id)
    
    log_with_request_id("INFO", f"🚀 Starting code processing request", {
        "repo_url": repo_url,
        "prompt": prompt,
        "request_id": request_id
    })
    
    def create_status_update(type_: str, message: str, step: str = None, progress: int = None, extra_data: Dict[str, Any] = None) -> Dict[str, Any]:
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

    sandbox = None
    start_time = time.time()
    
    try:
        # Step 1: Initialize sandbox
        log_agent_operation("sandbox_init", "Initializing E2B sandbox environment")
        yield create_status_update("info", "Initializing E2B sandbox...", "init", 10)
        await asyncio.sleep(0.5)
        
        with performance_timer("sandbox_initialization", {"request_id": request_id}):
            sandbox = Sandbox()
            log_agent_operation("sandbox_ready", f"E2B sandbox initialized successfully", {
                "sandbox_id": sandbox.sandbox_id,
                "initialization_time_ms": "calculated_by_timer"
            })
        
        yield create_status_update("success", f"Sandbox initialized (ID: {sandbox.sandbox_id})", "init", 20, {
            "sandbox_id": sandbox.sandbox_id
        })
        
        # Step 2: Validate repository URL
        log_agent_operation("url_validation", "Validating GitHub repository URL")
        yield create_status_update("info", "Validating repository URL...", "validation", 25)
        await asyncio.sleep(0.3)
        
        with performance_timer("url_validation", {"repo_url": repo_url}):
            if not _is_valid_github_url(repo_url):
                raise ValueError(f"Invalid GitHub URL: {repo_url}")
        
        log_agent_operation("url_valid", "Repository URL validation successful")
        yield create_status_update("success", "Repository URL validated", "validation", 30)
        
        # Step 3: Clone repository
        log_agent_operation("repo_clone", f"Starting repository clone operation", {
            "repo_url": repo_url,
            "target_sandbox": sandbox.sandbox_id
        })
        yield create_status_update("info", f"Cloning repository: {repo_url}", "clone", 35)
        await asyncio.sleep(0.5)
        
        with performance_timer("repository_clone", {"repo_url": repo_url}):
            # Execute git clone in sandbox
            clone_result = sandbox.commands.run(f"git clone {repo_url}")
            
            if clone_result.exit_code != 0:
                error_msg = f"Failed to clone repository. Exit code: {clone_result.exit_code}"
                if clone_result.stderr:
                    error_msg += f". Error: {clone_result.stderr}"
                
                log_error_with_context(RuntimeError(error_msg), {
                    "operation": "git_clone",
                    "exit_code": clone_result.exit_code,
                    "stderr": clone_result.stderr,
                    "repo_url": repo_url
                })
                raise RuntimeError(error_msg)
        
        repo_name = _extract_repo_name(repo_url)
        log_agent_operation("repo_cloned", f"Repository cloned successfully", {
            "repo_name": repo_name,
            "clone_time_ms": "calculated_by_timer"
        })
        yield create_status_update("success", f"Repository cloned successfully: {repo_name}", "clone", 45, {
            "repo_name": repo_name
        })
        
        # Step 4: Analyze repository structure
        log_agent_operation("structure_analysis", "Analyzing repository structure and file patterns")
        yield create_status_update("info", "Analyzing repository structure...", "analysis", 50)
        await asyncio.sleep(0.3)
        
        with performance_timer("structure_analysis", {"repo_name": repo_name}):
            # List files in the cloned repo
            ls_result = sandbox.commands.run(f"find {repo_name} -type f -name '*.py' -o -name '*.js' -o -name '*.ts' -o -name '*.jsx' -o -name '*.tsx' | head -20")
            
            file_count = len(ls_result.stdout.split('\n')) if ls_result.stdout else 0
            log_agent_operation("files_discovered", f"Discovered {file_count} code files in repository", {
                "file_count": file_count,
                "file_list": ls_result.stdout.split('\n')[:5] if ls_result.stdout else []
            })
        
        yield create_status_update("success", f"Found {file_count} code files", "analysis", 55, {
            "file_count": file_count
        })
        
        # Step 5: Read key files
        log_agent_operation("file_reading", "Reading key files for codebase analysis")
        yield create_status_update("info", "Reading key files for analysis...", "reading", 60)
        await asyncio.sleep(0.3)
        
        with performance_timer("file_reading", {"repo_name": repo_name}):
            # Read some key files to understand the codebase
            files_to_read = [
                "README.md", "main.py", "app.py", "index.py", 
                "requirements.txt", "package.json", "setup.py"
            ]
            
            existing_files = {}
            files_read_count = 0
            
            for filename in files_to_read:
                try:
                    file_path = f"{repo_name}/{filename}"
                    if sandbox.files.exists(file_path):
                        content = sandbox.files.read(file_path)
                        existing_files[filename] = content
                        files_read_count += 1
                        
                        log_agent_operation("file_read", f"Successfully read {filename}", {
                            "filename": filename,
                            "content_length": len(content),
                            "file_path": file_path
                        })
                        
                        yield create_status_update("info", f"Read {filename} ({len(content)} chars)", "reading", 55, {
                            "filename": filename,
                            "content_length": len(content)
                        })
                        await asyncio.sleep(0.2)
                except Exception as e:
                    log_agent_operation("file_read_error", f"Failed to read {filename}", {
                        "filename": filename,
                        "error": str(e)
                    })
        
        log_agent_operation("reading_complete", f"File reading phase completed", {
            "files_attempted": len(files_to_read),
            "files_successful": files_read_count,
            "files_failed": len(files_to_read) - files_read_count
        })
        yield create_status_update("success", f"Read {files_read_count} files", "reading", 65, {
            "files_read": files_read_count,
            "files_attempted": len(files_to_read)
        })
        
        # Step 6: Run AI agent
        log_agent_operation("agent_start", "Starting AI agent for code generation", {
            "prompt": prompt,
            "repo_name": repo_name
        })
        yield create_status_update("info", f"Planning changes based on prompt: '{prompt}'", "planning", 70)
        
        with performance_timer("ai_agent_processing", {"prompt": prompt, "repo_name": repo_name}):
            file_edits = await run_agent(prompt, repo_name)
        
        log_agent_operation("agent_complete", f"AI agent processing completed", {
            "edits_generated": len(file_edits),
            "processing_time_ms": "calculated_by_timer"
        })
        yield create_status_update("success", f"Agent generated {len(file_edits)} file modifications", "planning", 85, {
            "edits_count": len(file_edits)
        })
        
        # Step 7: Implement changes
        log_agent_operation("implementation_start", "Starting file modification implementation")
        yield create_status_update("info", "Implementing planned changes...", "implementation", 90)
        
        with performance_timer("file_implementation", {"edits_count": len(file_edits)}):
            successful_modifications = 0
            
            for i, edit in enumerate(file_edits):
                try:
                    file_path = edit["file_path"]
                    new_content = edit["new_content"]
                    description = edit.get("description", "No description")
                    
                    log_agent_operation("file_modify", f"Modifying file: {file_path}", {
                        "file_path": file_path,
                        "content_length": len(new_content),
                        "description": description,
                        "edit_index": i + 1,
                        "total_edits": len(file_edits)
                    })
                    
                    # Write the modified content
                    full_path = f"{repo_name}/{file_path}"
                    sandbox.files.write(full_path, new_content)
                    
                    successful_modifications += 1
                    
                    log_agent_operation("file_modified", f"Successfully modified {file_path}", {
                        "file_path": file_path,
                        "bytes_written": len(new_content)
                    })
                    
                    yield create_status_update("success", f"Modified {file_path} ({len(new_content)} chars)", "implementation", 95 + (i * 2), {
                        "file_path": file_path,
                        "content_length": len(new_content),
                        "description": description
                    })
                    
                except Exception as e:
                    log_error_with_context(e, {
                        "operation": "file_modification",
                        "file_path": edit.get("file_path", "unknown"),
                        "edit_index": i
                    })
                    yield create_status_update("error", f"Failed to modify {edit.get('file_path', 'unknown')}: {str(e)}", "implementation", 95 + (i * 2))
        
        log_agent_operation("implementation_complete", f"File implementation completed", {
            "successful_modifications": successful_modifications,
            "total_edits": len(file_edits),
            "success_rate": f"{(successful_modifications/len(file_edits)*100):.1f}%" if file_edits else 0
        })
        yield create_status_update("success", f"Successfully modified {successful_modifications} files", "implementation", 95, {
            "successful_modifications": successful_modifications,
            "total_edits": len(file_edits)
        })
        
        # Step 8: Create GitHub PR
        log_agent_operation("pr_creation", "Starting GitHub pull request creation")
        yield create_status_update("info", "Creating GitHub pull request...", "pr_creation", 96)
        
        with performance_timer("github_pr_creation", {"repo_url": repo_url, "edits_count": len(file_edits)}):
            try:
                pr_result = github_pr_creator.create_pr_with_changes(repo_url, prompt, file_edits)
                
                if pr_result.get("success"):
                    log_agent_operation("pr_success", f"Pull request created successfully", {
                        "pr_url": pr_result.get("pr_url"),
                        "branch_name": pr_result.get("branch_name")
                    })
                    yield create_status_update("success", f"Pull request created: {pr_result.get('pr_url', 'N/A')}", "pr_creation", 98, {
                        "pr_url": pr_result.get("pr_url"),
                        "branch_name": pr_result.get("branch_name")
                    })
                else:
                    log_agent_operation("pr_failed", f"Pull request creation failed", {
                        "error": pr_result.get("error", "Unknown error")
                    })
                    yield create_status_update("error", f"Failed to create PR: {pr_result.get('error', 'Unknown error')}", "pr_creation", 98)
                    
            except Exception as e:
                log_error_with_context(e, {
                    "operation": "github_pr_creation",
                    "repo_url": repo_url
                })
                yield create_status_update("error", f"Failed to create PR: {str(e)}", "pr_creation", 98)
        
        # Step 9: Complete
        total_duration = (time.time() - start_time) * 1000
        log_agent_operation("processing_complete", f"Code processing completed successfully", {
            "total_duration_ms": total_duration,
            "successful_modifications": successful_modifications,
            "request_id": request_id
        })
        
        yield create_status_update("success", "Code processing completed successfully!", "complete", 100, {
            "total_duration_ms": total_duration,
            "successful_modifications": successful_modifications
        })
        
        # Generate comprehensive summary
        summary = {
            "repository": repo_name,
            "prompt": prompt,
            "files_read": files_read_count,
            "files_modified": successful_modifications,
            "sandbox_id": sandbox.sandbox_id,
            "duration_ms": total_duration,
            "steps_completed": ["sandbox_init", "validation", "clone", "analysis", "reading", "planning", "implementation", "pr_creation", "complete"],
            "request_id": request_id
        }
        
        # Add observability summary
        observability_summary = observability_logger.get_agent_thinking_summary()
        summary["observability"] = observability_summary
        
        yield create_status_update("summary", "Processing completed successfully", "complete", 100, summary)
        
    except Exception as e:
        total_duration = (time.time() - start_time) * 1000
        log_error_with_context(e, {
            "operation": "process_code_request",
            "repo_url": repo_url,
            "prompt": prompt,
            "total_duration_ms": total_duration,
            "request_id": request_id
        })
        
        yield create_status_update("error", f"Processing failed: {str(e)}", "complete", 100, {
            "error": str(e),
            "total_duration_ms": total_duration,
            "request_id": request_id
        })
        
    finally:
        # Step 10: Cleanup
        if sandbox:
            log_agent_operation("cleanup", "Cleaning up sandbox resources")
            yield create_status_update("info", "Cleaning up sandbox...", "cleanup")
            
            try:
                with performance_timer("sandbox_cleanup", {"sandbox_id": sandbox.sandbox_id}):
                    sandbox.kill()
                log_agent_operation("cleanup_complete", "Sandbox cleanup completed successfully")
                yield create_status_update("success", "Sandbox cleaned up", "cleanup")
            except Exception as e:
                log_error_with_context(e, {
                    "operation": "sandbox_cleanup",
                    "sandbox_id": sandbox.sandbox_id
                })
                yield create_status_update("error", f"Cleanup failed: {str(e)}", "cleanup")


def _is_valid_github_url(url: str) -> bool:
    """Validate if the URL is a valid GitHub repository URL."""
    github_pattern = r'^https://github\.com/[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+/?$'
    return bool(re.match(github_pattern, url))


def _extract_repo_name(url: str) -> str:
    """Extract repository name from GitHub URL."""
    # Remove trailing slash and get the last part
    repo_name = url.rstrip('/').split('/')[-1]
    # Remove .git extension if present
    if repo_name.endswith('.git'):
        repo_name = repo_name[:-4]
    return repo_name 