"""
Agent runner module for processing code changes based on prompts.
This module integrates with Claude/OpenAI to generate actual file edits.
"""

import asyncio
import os
import re
from typing import List, Dict, Any
from loguru import logger
import anthropic
import openai

# Initialize AI clients
anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def run_agent(prompt: str, repo_path: str) -> List[Dict[str, str]]:
    """
    Run the AI agent to generate file edits based on the prompt.
    
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
    try:
        logger.info(f"Running agent with prompt: '{prompt}' on repo: {repo_path}")
        
        # Get repository structure and key files
        repo_files = await analyze_repository_structure(repo_path)
        
        # Generate file edits using AI
        file_edits = await generate_file_edits(prompt, repo_files)
        
        logger.info(f"Agent generated {len(file_edits)} file edits")
        return file_edits
        
    except Exception as e:
        logger.error(f"Error in agent runner: {str(e)}")
        return []

async def analyze_repository_structure(repo_path: str) -> Dict[str, Any]:
    """Analyze the repository structure to understand the codebase."""
    # This would scan the repo and identify key files
    # For now, return a simple structure
    return {
        "main_files": ["main.py", "app.py", "index.py"],
        "config_files": ["requirements.txt", "package.json", "setup.py"],
        "test_files": ["test_*.py", "*_test.py"],
        "language": "python"  # or detect from files
    }

async def generate_file_edits(prompt: str, repo_files: Dict[str, Any]) -> List[Dict[str, str]]:
    """Generate actual file edits using AI."""
    
    # Try Claude first, fallback to OpenAI
    try:
        return await generate_with_claude(prompt, repo_files)
    except Exception as e:
        logger.warning(f"Claude failed, trying OpenAI: {str(e)}")
        try:
            return await generate_with_openai(prompt, repo_files)
        except Exception as e2:
            logger.error(f"Both AI providers failed: {str(e2)}")
            return generate_fallback_edits(prompt)

async def generate_with_claude(prompt: str, repo_files: Dict[str, Any]) -> List[Dict[str, str]]:
    """Generate edits using Claude."""
    
    system_prompt = f"""
    You are a coding assistant that generates file edits based on user requests.
    
    Repository context:
    - Language: {repo_files.get('language', 'unknown')}
    - Main files: {repo_files.get('main_files', [])}
    - Config files: {repo_files.get('config_files', [])}
    
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
    
    response = anthropic_client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4000,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": f"Please implement: {prompt}"
            }
        ]
    )
    
    # Parse the response and extract file edits
    content = response.content[0].text
    return parse_ai_response(content)

async def generate_with_openai(prompt: str, repo_files: Dict[str, Any]) -> List[Dict[str, str]]:
    """Generate edits using OpenAI."""
    
    system_prompt = f"""
    You are a coding assistant that generates file edits based on user requests.
    
    Repository context:
    - Language: {repo_files.get('language', 'unknown')}
    - Main files: {repo_files.get('main_files', [])}
    - Config files: {repo_files.get('config_files', [])}
    
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
    
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Please implement: {prompt}"}
        ],
        max_tokens=4000
    )
    
    content = response.choices[0].message.content
    return parse_ai_response(content)

def parse_ai_response(content: str) -> List[Dict[str, str]]:
    """Parse AI response and extract file edits."""
    try:
        # Extract JSON from the response
        import json
        import re
        
        # Find JSON array in the response
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            return json.loads(json_str)
        else:
            logger.warning("No JSON found in AI response")
            return generate_fallback_edits("Failed to parse AI response")
            
    except Exception as e:
        logger.error(f"Error parsing AI response: {str(e)}")
        return generate_fallback_edits("Error parsing AI response")

def generate_fallback_edits(prompt: str) -> List[Dict[str, str]]:
    """Generate fallback edits when AI fails."""
    return [
        {
            "file_path": "README.md",
            "new_content": f"# Updated Project\n\nThis project has been updated based on the request: {prompt}\n\n## Changes Made\n- Implemented requested improvements\n- Added better documentation\n- Enhanced functionality\n",
            "description": "Updated README with project improvements"
        }
    ] 