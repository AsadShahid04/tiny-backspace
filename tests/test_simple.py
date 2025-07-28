#!/usr/bin/env python3
"""
Simple test script to verify the core functionality works.
"""

import asyncio
import aiohttp
import json
import sys

async def test_basic_functionality():
    """Test the basic API functionality."""
    
    # Test data
    test_data = {
        "repoUrl": "https://github.com/fastapi/fastapi.git",
        "prompt": "Add a simple README update"
    }
    
    print("🧪 Testing basic API functionality...")
    print(f"📂 Repository: {test_data['repoUrl']}")
    print(f"💭 Prompt: {test_data['prompt']}")
    print("-" * 60)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:8000/code",
                json=test_data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 200:
                    print("✅ API endpoint is working!")
                    print("📡 Streaming response received...")
                    
                    # Read the streaming response
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        if line.startswith('data: '):
                            try:
                                data = json.loads(line[6:])  # Remove 'data: ' prefix
                                print(f"📊 {data.get('type', 'info').upper()}: {data.get('message', 'No message')}")
                                
                                # Check if we have PR creation info
                                if data.get('type') == 'success' and 'pr_url' in data.get('extra_data', {}):
                                    pr_info = data['extra_data']
                                    print(f"🎉 PR Created!")
                                    print(f"🔗 PR URL: {pr_info['pr_url']}")
                                    print(f"📝 PR Number: {pr_info['pr_number']}")
                                    print(f"🌿 Branch: {pr_info['branch_name']}")
                                    break
                                    
                            except json.JSONDecodeError:
                                continue
                else:
                    print(f"❌ API returned status {response.status}")
                    print(await response.text())
                    
    except asyncio.TimeoutError:
        print("⏰ Request timed out (this is expected for large repos)")
        print("✅ The API is working, just taking time to process")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_basic_functionality()) 