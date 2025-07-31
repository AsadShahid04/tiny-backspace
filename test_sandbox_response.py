#!/usr/bin/env python3
"""
Test script to see what the sandbox is actually returning
"""

import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_sandbox_response():
    """Test what the sandbox is actually returning from Claude Code."""
    
    try:
        from e2b import Sandbox
        
        print("🧪 Testing sandbox Claude Code response...")
        
        # Create sandbox
        sandbox = Sandbox(template="base")
        print(f"✅ Sandbox created: {sandbox.sandbox_id}")
        
        # Install required packages
        print("📦 Installing packages...")
        sandbox.commands.run('pip install --upgrade anthropic')
        sandbox.commands.run('pip install requests')
        
        # Create a simple test script that simulates what we're doing
        test_script = '''
import anthropic
import json
import os

# Initialize Anthropic client
api_key = "''' + os.getenv('ANTHROPIC_API_KEY') + '''"
client = anthropic.Anthropic(api_key=api_key)

# Test message
message = """
You are an expert AI coding assistant. Generate a simple test endpoint.

IMPORTANT: Generate file edits in this EXACT format:

```python:test.py
@app.get("/test")
async def test_endpoint():
    return {"message": "Test endpoint working!"}
```

Be specific and provide the code modification.
"""

print("🚀 Sending message to Claude Code...")

# Call Claude Code
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1000,
    messages=[{"role": "user", "content": message}]
)

print("✅ Claude Code response received")
print(f"📝 Response content length: {len(response.content[0].text)}")
print(f"📝 Response content:\\n{response.content[0].text}")

# Try to serialize as JSON
try:
    result = {
        "content": response.content[0].text,
        "model": "claude-3-5-sonnet-20241022"
    }
    json_result = json.dumps(result)
    print(f"✅ JSON serialization successful")
    print(f"📝 JSON result: {json_result}")
except Exception as e:
    print(f"❌ JSON serialization failed: {e}")
    print(f"📝 Raw content: {response.content[0].text}")
'''
        
        # Write test script to sandbox
        await sandbox.files.write('/home/user/test_claude.py', test_script)
        
        # Run test script
        print("🚀 Running Claude Code test in sandbox...")
        process = sandbox.commands.run('python test_claude.py')
        
        print(f"📝 Exit code: {process.exit_code}")
        print(f"📝 Stdout length: {len(process.stdout) if process.stdout else 0}")
        print(f"📝 Stderr length: {len(process.stderr) if process.stderr else 0}")
        
        if process.stdout:
            print(f"📝 Stdout:\\n{process.stdout}")
        
        if process.stderr:
            print(f"📝 Stderr:\\n{process.stderr}")
        
        # Cleanup
        sandbox.kill()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_sandbox_response()) 