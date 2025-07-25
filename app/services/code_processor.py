import asyncio
import time
from typing import AsyncGenerator, Dict, Any
from e2b import Sandbox
from loguru import logger
import re


async def process_code_request(repo_url: str, prompt: str) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Process a code request by:
    1. Initializing E2B sandbox
    2. Cloning the GitHub repo
    3. Streaming back status updates
    4. Planning and implementing changes (dummy for now)
    """
    
    def create_status_update(type_: str, message: str, step: str = None, progress: int = None) -> Dict[str, Any]:
        """Helper to create consistent status update objects."""
        update = {
            "type": type_,
            "message": message,
            "timestamp": int(time.time() * 1000)
        }
        if step:
            update["step"] = step
        if progress is not None:
            update["progress"] = progress
        return update
    
    sandbox = None
    
    try:
        # Step 1: Initialize sandbox
        yield create_status_update("info", "Initializing E2B sandbox...", "init", 10)
        await asyncio.sleep(0.5)  # Simulate some processing time
        
        sandbox = Sandbox()
        logger.info(f"E2B sandbox initialized with ID: {sandbox.id}")
        
        yield create_status_update("success", f"Sandbox initialized (ID: {sandbox.id})", "init", 20)
        await asyncio.sleep(0.3)
        
        # Step 2: Validate repo URL
        yield create_status_update("info", "Validating repository URL...", "validation", 25)
        await asyncio.sleep(0.2)
        
        if not _is_valid_github_url(repo_url):
            raise ValueError(f"Invalid GitHub repository URL: {repo_url}")
        
        repo_name = _extract_repo_name(repo_url)
        yield create_status_update("success", f"Repository URL validated: {repo_name}", "validation", 30)
        
        # Step 3: Clone repository
        yield create_status_update("info", f"Cloning repository: {repo_url}", "clone", 35)
        await asyncio.sleep(0.5)
        
        # Execute git clone in sandbox
        clone_result = sandbox.process.start_and_wait(f"git clone {repo_url}")
        
        if clone_result.exit_code != 0:
            error_msg = f"Failed to clone repository. Exit code: {clone_result.exit_code}"
            if clone_result.stderr:
                error_msg += f". Error: {clone_result.stderr}"
            raise RuntimeError(error_msg)
        
        yield create_status_update("success", f"Repository cloned successfully: {repo_name}", "clone", 50)
        await asyncio.sleep(0.3)
        
        # Step 4: Analyze repository structure
        yield create_status_update("info", "Analyzing repository structure...", "analysis", 55)
        await asyncio.sleep(0.7)
        
        # List files in the cloned repo
        ls_result = sandbox.process.start_and_wait(f"find {repo_name} -type f -name '*.py' -o -name '*.js' -o -name '*.ts' -o -name '*.jsx' -o -name '*.tsx' | head -20")
        
        file_count = len(ls_result.stdout.split('\n')) if ls_result.stdout else 0
        yield create_status_update("success", f"Repository analyzed. Found {file_count} code files", "analysis", 65)
        
        # Step 5: Planning changes
        yield create_status_update("info", f"Planning changes based on prompt: '{prompt}'", "planning", 70)
        await asyncio.sleep(1.0)
        
        # Dummy planning logic
        planning_steps = [
            "Analyzing code patterns and structure",
            "Identifying files that need modification",
            "Generating implementation strategy",
            "Validating proposed changes"
        ]
        
        for i, step in enumerate(planning_steps):
            yield create_status_update("info", step, "planning", 70 + (i + 1) * 5)
            await asyncio.sleep(0.4)
        
        yield create_status_update("success", "Change plan generated successfully", "planning", 90)
        
        # Step 6: Implementing changes (dummy)
        yield create_status_update("info", "Implementing planned changes...", "implementation", 92)
        await asyncio.sleep(0.8)
        
        # Simulate file modifications
        modification_steps = [
            f"Modified 3 files in {repo_name}/src/",
            f"Updated configuration in {repo_name}/config/",
            f"Added new utility functions",
            "Running code validation checks"
        ]
        
        for i, step in enumerate(modification_steps):
            yield create_status_update("info", step, "implementation", 92 + i * 2)
            await asyncio.sleep(0.3)
        
        # Step 7: Completion
        yield create_status_update("success", "Code processing completed successfully!", "complete", 100)
        
        # Final summary
        summary = {
            "type": "summary",
            "message": "Processing completed",
            "timestamp": int(time.time() * 1000),
            "summary": {
                "repository": repo_name,
                "prompt": prompt,
                "files_modified": 3,
                "sandbox_id": sandbox.id,
                "duration_ms": int(time.time() * 1000) - int(time.time() * 1000) + 5000  # Rough estimate
            }
        }
        yield summary
        
    except Exception as e:
        logger.error(f"Error processing code request: {str(e)}")
        yield create_status_update("error", f"Processing failed: {str(e)}", "error")
        raise
    
    finally:
        # Clean up sandbox
        if sandbox:
            try:
                yield create_status_update("info", "Cleaning up sandbox...", "cleanup")
                sandbox.close()
                yield create_status_update("success", "Sandbox cleaned up", "cleanup")
                logger.info(f"Sandbox {sandbox.id} closed successfully")
            except Exception as e:
                logger.error(f"Error closing sandbox: {str(e)}")
                yield create_status_update("warning", f"Sandbox cleanup warning: {str(e)}", "cleanup")


def _is_valid_github_url(url: str) -> bool:
    """Validate if the URL is a valid GitHub repository URL."""
    github_patterns = [
        r'^https://github\.com/[\w\-\.]+/[\w\-\.]+(?:\.git)?/?$',
        r'^git@github\.com:[\w\-\.]+/[\w\-\.]+\.git$'
    ]
    
    return any(re.match(pattern, url.strip()) for pattern in github_patterns)


def _extract_repo_name(url: str) -> str:
    """Extract repository name from GitHub URL."""
    # Remove .git suffix and trailing slashes
    clean_url = url.rstrip('/').rstrip('.git')
    
    # Extract repo name (last part of the path)
    if 'github.com/' in clean_url:
        return clean_url.split('/')[-1]
    elif ':' in clean_url:  # SSH format
        return clean_url.split(':')[-1].split('/')[-1]
    
    return clean_url.split('/')[-1]