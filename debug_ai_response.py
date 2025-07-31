#!/usr/bin/env python3
"""
Debug script to see the exact AI response
"""

import os
import json
import anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def debug_ai_response():
    """Debug the AI response"""
    
    # Sample file contents (matching what the server sees)
    file_contents = {
        "api/code.py": "# This is the code.py file content",
        "api/main.py": "# This is the main.py file content",
        "api/simple_observability.py": "# This is the simple_observability.py file content"
    }
    
    # Create client
    client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    # Create detailed prompt for Claude Code
    detailed_prompt = f"""
You are a coding agent working on repository: https://github.com/AsadShahid04/tiny-backspace

User request: Add a simple print statement to the main.py file

Available files and their contents:
{json.dumps(file_contents, indent=2)}

Please analyze the codebase and provide specific code changes to implement the user's request.
Return your response in the following JSON format:

{{
    "changes": [
        {{
            "type": "edit",
            "filepath": "api/main.py",
            "content": "new file content",
            "description": "what this change does"
        }}
    ],
    "explanation": "Brief explanation of the changes made"
}}

IMPORTANT: 
- Use relative file paths WITHOUT the 'repo/' prefix (e.g., 'api/main.py' not 'repo/api/main.py')
- The filepath should match exactly with the files shown in the available files list
- Make minimal, focused changes to implement the user's request
- Follow the existing code style and patterns
- Add proper error handling where needed

Focus on:
1. Understanding the existing codebase structure
2. Making minimal, focused changes
3. Following the existing code style and patterns
4. Adding proper error handling where needed
5. Ensuring the changes are testable and maintainable

Only return valid JSON, no additional text.
"""
    
    print("🤖 Debugging AI response...")
    print("=" * 50)
    print("File contents passed to AI:")
    for file_path, content in file_contents.items():
        print(f"  {file_path}: {len(content)} chars")
    print("=" * 50)
    
    try:
        # Send request to Claude
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            temperature=0.1,
            messages=[{"role": "user", "content": detailed_prompt}]
        )
        
        print("🤖 Raw AI Response:")
        print(response.content[0].text)
        print("=" * 50)
        
        # Try to parse the response
        try:
            response_data = json.loads(response.content[0].text.strip())
            changes = response_data.get('changes', [])
            print(f"✅ Parsed {len(changes)} changes:")
            for i, change in enumerate(changes):
                print(f"  {i+1}. File: '{change.get('filepath', 'N/A')}'")
                print(f"     Type: {change.get('type', 'N/A')}")
                print(f"     Description: {change.get('description', 'N/A')}")
                print(f"     Content preview: {change.get('content', '')[:100]}...")
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON: {e}")
            print(f"Response was: {response.content[0].text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_ai_response() 