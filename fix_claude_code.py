#!/usr/bin/env python3
"""
Test Claude Code generation directly
"""

import anthropic
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_claude_code():
    """Test Claude Code generation directly"""
    
    # Get API key
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    if not anthropic_key:
        print("❌ ANTHROPIC_API_KEY not set")
        return
    
    print("✅ ANTHROPIC_API_KEY loaded")
    
    # Create client
    client = anthropic.Anthropic(api_key=anthropic_key)
    
    # Test data
    files_info = {
        "api/main.py": "# Test file content",
        "README.md": "# Test README"
    }
    repo_url = "https://github.com/AsadShahid04/tiny-backspace"
    prompt = "Add a simple test endpoint"
    
    # Create prompt without nested f-strings
    detailed_prompt = f"""
You are a coding agent working on repository: {repo_url}

User request: {prompt}

Available files and their contents:
{json.dumps(files_info, indent=2)}

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
    
    print("🤖 Sending request to Claude...")
    
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            temperature=0.1,
            messages=[{"role": "user", "content": detailed_prompt}]
        )
        
        print("✅ Claude response received:")
        print(response.content[0].text)
        
        # Try to parse as JSON
        try:
            response_data = json.loads(response.content[0].text)
            print("✅ JSON parsed successfully")
            print(f"Changes: {len(response_data.get('changes', []))}")
            return response_data.get('changes', [])
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            print(f"Raw response: {response.content[0].text}")
            return []
            
    except Exception as e:
        print(f"❌ Claude API error: {e}")
        return []

if __name__ == "__main__":
    test_claude_code() 