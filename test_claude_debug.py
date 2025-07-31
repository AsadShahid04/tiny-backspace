#!/usr/bin/env python3
"""
Test script to debug Claude Code response parsing
"""

import os
import json
import anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_claude_response_parsing():
    """Test the actual Claude Code response and parsing."""
    
    # Get API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment")
        return False
    
    print(f"✅ Using ANTHROPIC_API_KEY: {api_key[:20]}...")
    
    try:
        # Initialize Anthropic client
        client = anthropic.Anthropic(api_key=api_key)
        print("✅ Anthropic client initialized")
        
        # Simulate the exact message that's sent to Claude Code
        message = """
You are an expert AI coding assistant. Analyze this repository and generate code modifications based on the user's prompt.

Repository Information:
- Name: tiny-backspace
- File count: 8
- Files: ['DEBUG_SUMMARY.md', 'README.md', 'TODO.md', 'api/code.py', 'api/main.py', 'api/requirements.txt', 'api/simple_observability.py', 'requirements.txt']

User Request: Add a simple test endpoint

Please analyze the repository structure and generate appropriate code modifications.
Focus on the most relevant files for the user's request.

IMPORTANT: Generate file edits in this EXACT format:

```python:api/main.py
# Add your new code here
@app.get("/test")
async def test_endpoint():
    return {"message": "Test endpoint working!"}
```

For each file you want to modify, use the format:
```python:file_path
new content here
```

Be specific and provide meaningful improvements based on the user's prompt.
Make sure to include the file path in the code block header.
"""
        
        print("🚀 Sending message to Claude Code...")
        
        # Call Claude Code
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            messages=[{"role": "user", "content": message}]
        )
        
        print("✅ Claude Code response received")
        print(f"📝 Response content length: {len(response.content[0].text)}")
        print(f"📝 Response content:\n{response.content[0].text}")
        
        # Test the parsing logic
        from api.main import TinyBackspaceProcessor
        processor = TinyBackspaceProcessor()
        
        print("\n🔍 Testing parsing logic...")
        edits = processor._parse_ai_response(response.content[0].text)
        
        print(f"📝 Parsed {len(edits)} edits")
        for i, edit in enumerate(edits):
            print(f"📝 Edit {i+1}: {edit['file_path']} ({len(edit['new_content'])} chars)")
            print(f"📝 Content preview: {edit['new_content'][:200]}...")
        
        return len(edits) > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_claude_response_parsing()
    if success:
        print("✅ Test passed - Claude Code is working!")
    else:
        print("❌ Test failed - Claude Code needs debugging") 