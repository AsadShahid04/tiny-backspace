#!/usr/bin/env python3
"""
Test script to debug just the parsing logic
"""

import re

def parse_ai_response(content: str) -> list:
    """Parse AI response into file edits - standalone version."""
    edits = []
    
    print(f"🔍 DEBUG: Starting to parse AI response")
    print(f"🔍 DEBUG: Content length: {len(content)}")
    print(f"🔍 DEBUG: Content preview (first 500 chars): {content[:500]}")
    print(f"🔍 DEBUG: Content preview (last 500 chars): {content[-500:]}")
    print(f"🔍 DEBUG: Full content:\n{content}")
    print(f"🔍 DEBUG: Content repr: {repr(content)}")
    
    # Try multiple patterns to extract file edits
    patterns = [
        (r'```(\w+):([^\n]+)\n(.*?)```', "language:filepath format"),  # ```python:file.py\ncontent```
        (r'```([^\n]+)\n(.*?)```', "filepath format"),       # ```file.py\ncontent```
        (r'File:\s*([^\n]+)\n(.*?)(?=\n\s*File:|$)', "File: format"),  # File: file.py\ncontent
        (r'([^\n]+\.py)\n```\n(.*?)```', "filepath with code blocks"),  # file.py\n```\ncontent```
        (r'```python\n([^`]+)```', "python code blocks"),  # ```python\ncode```
        (r'```([^`]+)```', "generic code blocks"),  # ```code```
    ]
    
    for pattern, description in patterns:
        print(f"🔍 DEBUG: Trying pattern '{description}': {pattern}")
        matches = re.findall(pattern, content, re.DOTALL | re.MULTILINE)
        print(f"🔍 DEBUG: Pattern '{description}' found {len(matches)} matches")
        
        if matches:
            print(f"✅ Found {len(matches)} file edits with pattern: {description}")
            print(f"🔍 DEBUG: Raw matches: {matches}")
            
            for i, match in enumerate(matches):
                print(f"🔍 DEBUG: Processing match {i+1}: {match}")
                print(f"🔍 DEBUG: Match type: {type(match)}, length: {len(match) if isinstance(match, (tuple, list)) else 'N/A'}")
                
                if isinstance(match, tuple) and len(match) == 3:  # pattern with language:filepath
                    file_ext, file_path, file_content = match
                    print(f"🔍 DEBUG: 3-tuple match - ext: '{file_ext}', path: '{file_path}', content preview: '{file_content[:100]}...'")
                elif isinstance(match, tuple) and len(match) == 2:  # patterns with filepath and content
                    file_path, file_content = match
                    print(f"🔍 DEBUG: 2-tuple match - path: '{file_path}', content preview: '{file_content[:100]}...'")
                elif isinstance(match, str):  # single string match
                    file_content = match
                    # For single matches, try to extract a reasonable filename
                    if description == "python code blocks":
                        file_path = "generated_code.py"
                    else:
                        # Try to find a filename in the content
                        lines = file_content.split('\n')
                        first_line = lines[0].strip()
                        if first_line in ['python', 'javascript', 'typescript']:
                            file_path = f"generated_code.{first_line[:2]}"
                            file_content = '\n'.join(lines[1:])  # Remove language identifier
                        else:
                            file_path = "generated_code.py"
                    print(f"🔍 DEBUG: String match - using path: '{file_path}', content preview: '{file_content[:100]}...'")
                else:
                    print(f"🔍 DEBUG: Unexpected match format, skipping: {match}")
                    continue
                
                file_path = file_path.strip()
                file_content = file_content.strip()
                
                print(f"🔍 DEBUG: Cleaned - path: '{file_path}', content length: {len(file_content)}")
                
                # Skip if file_path is empty or looks like a language identifier
                if not file_path or file_path in ['python', 'javascript', 'typescript', 'json']:
                    print(f"🔍 DEBUG: Skipping invalid file path: '{file_path}'")
                    continue
                
                # Skip if content is too short to be meaningful
                if len(file_content) < 10:
                    print(f"🔍 DEBUG: Skipping too short content: {len(file_content)} chars")
                    continue
                
                edit = {
                    'file_path': file_path,
                    'new_content': file_content,
                    'description': f'AI-generated modification for {file_path}'
                }
                edits.append(edit)
                print(f"✅ DEBUG: Added edit for {file_path} ({len(file_content)} chars)")
            
            if edits:  # If we found edits with this pattern, use them
                break
        else:
            print(f"❌ DEBUG: No matches found for pattern '{description}'")
    
    print(f"📝 DEBUG: Final result - parsed {len(edits)} file edits")
    for i, edit in enumerate(edits):
        print(f"📝 DEBUG: Edit {i+1}: {edit['file_path']} ({len(edit['new_content'])} chars)")
    
    print(f"📝 Parsed {len(edits)} file edits")
    return edits

def test_parsing():
    """Test the parsing logic with the actual Claude Code response."""
    
    # This is the actual response from Claude Code from our test
    content = """I'll help add a simple test endpoint to the API. Based on the repository structure, we should add this to `api/main.py` since that's the main API file.

Here's the code modification:

```python:api/main.py
from fastapi import FastAPI, HTTPException
from .code import process_request
from .simple_observability import log_request

app = FastAPI()

@app.get("/test")
async def test_endpoint():
    # Simple test endpoint to verify API is running
    try:
        return {
            "status": "success",
            "message": "API is running correctly",
            "service": "tiny-backspace"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Keep existing endpoints below
```

This modification:
1. Adds a simple GET endpoint at `/test`
2. Returns a JSON response with basic service information
3. Includes error handling with proper HTTP status codes
4. Follows the existing project structure
5. Provides a way to quickly verify the API is running

You can test this endpoint by making a GET request to:
```
GET http://localhost:8000/test
```

The endpoint will return a 200 OK response with the JSON payload if everything is working correctly.

Would you like me to suggest any additional improvements or modifications to this test endpoint?"""
    
    print("🔍 Testing parsing logic with actual Claude Code response...")
    edits = parse_ai_response(content)
    
    print(f"\n📝 Final result: {len(edits)} edits parsed")
    for i, edit in enumerate(edits):
        print(f"📝 Edit {i+1}: {edit['file_path']}")
        print(f"📝 Content preview: {edit['new_content'][:200]}...")
    
    return len(edits) > 0

if __name__ == "__main__":
    success = test_parsing()
    if success:
        print("✅ Parsing test passed!")
    else:
        print("❌ Parsing test failed!") 