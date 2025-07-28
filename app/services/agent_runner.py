"""
Agent runner module for processing code changes based on prompts.
This module integrates with Claude/OpenAI to generate actual file edits.
Enhanced with comprehensive observability and real-time thinking logs.
"""

import asyncio
import os
import re
import uuid
from typing import List, Dict, Any
from loguru import logger
import anthropic
import openai
from app.logging_config import (
    observability_logger, 
    log_agent_operation, 
    log_performance_metric,
    log_error_with_context,
    performance_timer,
    get_request_id
)

# Initialize AI clients
anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def run_agent(prompt: str, repo_path: str) -> List[Dict[str, str]]:
    """
    Run the AI agent to generate file edits based on the prompt.
    Enhanced with comprehensive observability and real-time thinking logs.
    
    Args:
        prompt: The user's request for what changes to make
        repo_path: Path to the cloned repository in the sandbox
        
    Returns:
        List of file edits in format:
        [
            {
                "file_path": "path/to/file.py",
                "new_content": "updated file content",
                "description": "what was changed"
            }
        ]
    """
    request_id = get_request_id()
    
    try:
        log_agent_operation("start", f"Starting agent processing for prompt: '{prompt}'", {
            "prompt": prompt,
            "repo_path": repo_path,
            "request_id": request_id
        })
        
        with performance_timer("agent_total_processing", {"prompt_length": len(prompt)}):
            # Step 1: Analyze repository structure
            log_agent_operation("analysis", "Beginning repository structure analysis")
            repo_files = await analyze_repository_structure(repo_path)
            
            log_agent_operation("analysis_complete", f"Repository analysis complete", {
                "files_found": len(repo_files.get("all_files", [])),
                "language": repo_files.get("language", "unknown"),
                "structure_summary": {
                    "main_files": len(repo_files.get("main_files", [])),
                    "config_files": len(repo_files.get("config_files", [])),
                    "test_files": len(repo_files.get("test_files", []))
                }
            })
            
            # Step 2: Generate file edits using AI
            log_agent_operation("ai_generation", "Starting AI-powered code generation")
            file_edits = await generate_file_edits(prompt, repo_files)
            
            log_agent_operation("generation_complete", f"AI generation complete - {len(file_edits)} edits created", {
                "edits_count": len(file_edits),
                "files_to_modify": [edit.get("file_path") for edit in file_edits]
            })
        
        log_agent_operation("success", f"Agent processing completed successfully", {
            "total_edits": len(file_edits),
            "processing_time_ms": "calculated_by_timer"
        })
        
        return file_edits
        
    except Exception as e:
        log_error_with_context(e, {
            "operation": "run_agent",
            "prompt": prompt,
            "repo_path": repo_path,
            "request_id": request_id
        })
        return []

async def analyze_repository_structure(repo_path: str) -> Dict[str, Any]:
    """Analyze the repository structure to understand the codebase with detailed logging."""
    
    with performance_timer("repository_analysis", {"repo_path": repo_path}):
        log_agent_operation("structure_scan", "Scanning repository file structure")
        
        # This would scan the repo and identify key files
        # For now, return a simple structure with enhanced logging
        structure = {
            "main_files": ["main.py", "app.py", "index.py"],
            "config_files": ["requirements.txt", "package.json", "setup.py"],
            "test_files": ["test_*.py", "*_test.py"],
            "language": "python",  # or detect from files
            "all_files": ["main.py", "app.py", "index.py", "requirements.txt", "README.md"]
        }
        
        log_agent_operation("structure_analysis", "Analyzing code patterns and dependencies", {
            "detected_language": structure["language"],
            "file_categories": {
                "main_files": structure["main_files"],
                "config_files": structure["config_files"],
                "test_files": structure["test_files"]
            }
        })
        
        return structure

async def generate_file_edits(prompt: str, repo_files: Dict[str, Any]) -> List[Dict[str, str]]:
    """Generate actual file edits using AI with comprehensive fallback strategy."""
    
    log_agent_operation("ai_selection", "Selecting AI provider for code generation", {
        "available_providers": ["claude", "openai", "dummy"],
        "preference_order": ["claude", "openai", "dummy"]
    })
    
    # Try Claude first, fallback to OpenAI, then dummy
    try:
        log_agent_operation("claude_attempt", "Attempting to generate with Claude (primary AI)")
        return await generate_with_claude(prompt, repo_files)
    except Exception as e:
        log_agent_operation("claude_failed", f"Claude generation failed: {str(e)}", {
            "error_type": type(e).__name__,
            "fallback_to": "openai"
        })
        
        try:
            log_agent_operation("openai_attempt", "Attempting to generate with OpenAI (fallback)")
            return await generate_with_openai(prompt, repo_files)
        except Exception as e2:
            log_agent_operation("openai_failed", f"OpenAI generation failed: {str(e2)}", {
                "error_type": type(e2).__name__,
                "fallback_to": "dummy"
            })
            
            log_agent_operation("dummy_fallback", "Using dummy agent as final fallback")
            return generate_fallback_edits(prompt)

async def generate_with_claude(prompt: str, repo_files: Dict[str, Any]) -> List[Dict[str, str]]:
    """Generate edits using Claude with detailed thinking logs."""
    
    with performance_timer("claude_generation", {"model": "claude-3-sonnet", "prompt_length": len(prompt)}):
        log_agent_operation("claude_thinking", "Claude analyzing repository context and user request", {
            "repository_context": {
                "language": repo_files.get('language', 'unknown'),
                "file_count": len(repo_files.get('all_files', [])),
                "main_files": repo_files.get('main_files', [])
            }
        })
        
        system_prompt = f"""
        You are a coding assistant that generates file edits based on user requests.
        
        Repository context:
        - Language: {repo_files.get('language', 'unknown')}
        - Main files: {repo_files.get('main_files', [])}
        - Config files: {repo_files.get('config_files', [])}
        - Test files: {repo_files.get('test_files', [])}
        
        User request: {prompt}
        
        Think through this step by step:
        1. Analyze what the user wants to achieve
        2. Identify which files need to be modified
        3. Plan the specific changes needed
        4. Generate the updated file content
        
        Generate 1-3 realistic file edits that implement the user's request.
        Return only valid JSON in this exact format:
        [
            {{
                "file_path": "path/to/file.py",
                "new_content": "complete file content with changes",
                "description": "brief description of changes"
            }}
        ]
        
        Make the changes practical and focused on the user's request.
        """
        
        log_agent_operation("claude_prompt", "Sending structured prompt to Claude", {
            "system_prompt_length": len(system_prompt),
            "user_prompt": prompt
        })
        
        try:
            response = await anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=4000,
                messages=[
                    {"role": "user", "content": system_prompt}
                ]
            )
            
            content = response.content[0].text
            log_agent_operation("claude_response", "Received response from Claude", {
                "response_length": len(content),
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens
            })
            
            file_edits = parse_ai_response(content)
            log_agent_operation("claude_parsing", f"Successfully parsed {len(file_edits)} edits from Claude response")
            
            return file_edits
            
        except Exception as e:
            log_error_with_context(e, {
                "operation": "claude_generation",
                "prompt_length": len(system_prompt)
            })
            raise

async def generate_with_openai(prompt: str, repo_files: Dict[str, Any]) -> List[Dict[str, str]]:
    """Generate edits using OpenAI with detailed thinking logs."""
    
    with performance_timer("openai_generation", {"model": "gpt-4", "prompt_length": len(prompt)}):
        log_agent_operation("openai_thinking", "OpenAI analyzing repository context and user request", {
            "repository_context": {
                "language": repo_files.get('language', 'unknown'),
                "file_count": len(repo_files.get('all_files', [])),
                "main_files": repo_files.get('main_files', [])
            }
        })
        
        system_prompt = f"""
        You are a coding assistant that generates file edits based on user requests.
        
        Repository context:
        - Language: {repo_files.get('language', 'unknown')}
        - Main files: {repo_files.get('main_files', [])}
        - Config files: {repo_files.get('config_files', [])}
        
        User request: {prompt}
        
        Generate 1-3 realistic file edits that implement the user's request.
        Return only valid JSON in this exact format:
        [
            {{
                "file_path": "path/to/file.py",
                "new_content": "complete file content with changes",
                "description": "brief description of changes"
            }}
        ]
        
        Make the changes practical and focused on the user's request.
        """
        
        log_agent_operation("openai_prompt", "Sending structured prompt to OpenAI", {
            "system_prompt_length": len(system_prompt),
            "user_prompt": prompt
        })
        
        try:
            response = await openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt}
                ],
                max_tokens=4000,
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            log_agent_operation("openai_response", "Received response from OpenAI", {
                "response_length": len(content),
                "tokens_used": response.usage.total_tokens
            })
            
            file_edits = parse_ai_response(content)
            log_agent_operation("openai_parsing", f"Successfully parsed {len(file_edits)} edits from OpenAI response")
            
            return file_edits
            
        except Exception as e:
            log_error_with_context(e, {
                "operation": "openai_generation",
                "prompt_length": len(system_prompt)
            })
            raise

def parse_ai_response(content: str) -> List[Dict[str, str]]:
    """Parse AI response and extract file edits with error handling."""
    
    with performance_timer("ai_response_parsing", {"content_length": len(content)}):
        log_agent_operation("parsing_start", "Starting to parse AI response for file edits")
        
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                import json
                edits = json.loads(json_match.group())
                
                log_agent_operation("parsing_success", f"Successfully parsed {len(edits)} file edits", {
                    "edits_found": len(edits),
                    "files_to_modify": [edit.get("file_path", "unknown") for edit in edits]
                })
                
                return edits
            else:
                log_agent_operation("parsing_failed", "No valid JSON array found in AI response", {
                    "content_preview": content[:200] + "..." if len(content) > 200 else content
                })
                return []
                
        except Exception as e:
            log_error_with_context(e, {
                "operation": "parse_ai_response",
                "content_preview": content[:200] + "..." if len(content) > 200 else content
            })
            return []

def generate_fallback_edits(prompt: str) -> List[Dict[str, str]]:
    """Generate fallback edits when AI providers fail."""
    
    with performance_timer("dummy_generation", {"fallback_reason": "ai_providers_failed"}):
        log_agent_operation("dummy_thinking", "Generating fallback edits using dummy agent", {
            "reason": "All AI providers failed",
            "fallback_strategy": "basic_file_modification"
        })
        
        # Generate a simple test file as fallback
        test_content = f'''"""
Test file generated by Tiny Backspace agent.
User request: {prompt}

This is a fallback implementation when AI providers are unavailable.
"""

def test_function():
    """Test function generated based on user request."""
    print("Hello from Tiny Backspace!")
    return True

if __name__ == "__main__":
    test_function()
'''
        
        edit = {
            "file_path": "test_app.py",
            "new_content": test_content,
            "description": f"Generated fallback test file for request: {prompt}"
        }
        
        log_agent_operation("dummy_success", "Successfully generated fallback edit", {
            "file_created": "test_app.py",
            "content_length": len(test_content)
        })
        
        return [edit] 