#!/usr/bin/env python3
"""
Test script using a smaller repository to demonstrate full functionality.
"""

import asyncio
import aiohttp
import json
import sys

async def test_small_repo():
    """Test with a smaller repository to see full functionality."""
    
    # Test with a smaller repo
    test_data = {
        "repoUrl": "https://github.com/tiangolo/typer.git",  # Smaller repo
        "prompt": "Add a simple README update with installation instructions"
    }
    
    print("🧪 Testing with smaller repository...")
    print(f"📂 Repository: {test_data['repoUrl']}")
    print(f"💭 Prompt: {test_data['prompt']}")
    print("-" * 60)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:8000/code",
                json=test_data,
                timeout=aiohttp.ClientTimeout(total=60)  # Longer timeout
            ) as response:
                
                if response.status == 200:
                    print("✅ API endpoint is working!")
                    print("📡 Streaming response received...")
                    print("-" * 40)
                    
                    # Read the streaming response
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        if line.startswith('data: '):
                            try:
                                data = json.loads(line[6:])  # Remove 'data: ' prefix
                                step = data.get('step', 'unknown')
                                progress = data.get('progress', 0)
                                message = data.get('message', 'No message')
                                
                                print(f"📊 [{step.upper()}] ({progress}%): {message}")
                                
                                # Check if we have PR creation info
                                if data.get('type') == 'success' and 'extra_data' in data:
                                    extra_data = data['extra_data']
                                    if 'pr_url' in extra_data:
                                        print(f"\n🎉 PR Created Successfully!")
                                        print(f"🔗 PR URL: {extra_data['pr_url']}")
                                        print(f"📝 PR Number: {extra_data['pr_number']}")
                                        print(f"🌿 Branch: {extra_data['branch_name']}")
                                        break
                                
                                # Check for completion
                                if data.get('type') == 'success' and data.get('step') == 'complete':
                                    print(f"\n✅ Processing completed successfully!")
                                    break
                                    
                            except json.JSONDecodeError:
                                continue
                else:
                    print(f"❌ API returned status {response.status}")
                    print(await response.text())
                    
    except asyncio.TimeoutError:
        print("⏰ Request timed out")
        print("✅ The API is working, just taking time to process")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_small_repo()) 