#!/usr/bin/env python3
"""
Test script to demonstrate the file editing capabilities of the FastAPI backend.
This script tests different types of prompts and shows the SSE streaming in action.
"""

import asyncio
import aiohttp
import json
import sys
from typing import Dict, Any

# Test prompts for different types of improvements
TEST_PROMPTS = {
    "error_handling": {
        "repoUrl": "https://github.com/fastapi/fastapi.git",
        "prompt": "Add comprehensive error handling and exception management"
    },
    "testing": {
        "repoUrl": "https://github.com/pallets/flask.git", 
        "prompt": "Add unit tests and improve test coverage"
    },
    "logging": {
        "repoUrl": "https://github.com/psf/requests.git",
        "prompt": "Implement better logging and monitoring capabilities"
    },
    "api_improvements": {
        "repoUrl": "https://github.com/tiangolo/fastapi.git",
        "prompt": "Enhance API endpoints with better validation and documentation"
    },
    "configuration": {
        "repoUrl": "https://github.com/python/cpython.git",
        "prompt": "Add configuration management and environment settings"
    },
    "generic": {
        "repoUrl": "https://github.com/microsoft/vscode.git",
        "prompt": "Improve code quality and maintainability"
    }
}

async def test_code_endpoint(test_name: str, test_data: Dict[str, str]):
    """Test a specific prompt type and display the streaming results."""
    
    print(f"\n{'='*60}")
    print(f"🧪 Testing: {test_name.upper()}")
    print(f"📂 Repository: {test_data['repoUrl']}")
    print(f"💭 Prompt: {test_data['prompt']}")
    print(f"{'='*60}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:8000/code",
                json=test_data,
                headers={"Accept": "text/event-stream"},
                timeout=aiohttp.ClientTimeout(total=300)  # 5 minute timeout
            ) as response:
                
                if response.status != 200:
                    print(f"❌ Error: HTTP {response.status}")
                    text = await response.text()
                    print(f"Response: {text}")
                    return False
                
                print("📡 Receiving Server-Sent Events:")
                print("-" * 50)
                
                files_modified = 0
                
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    
                    if line.startswith('data: '):
                        try:
                            data = json.loads(line[6:])  # Remove 'data: ' prefix
                            
                            msg_type = data.get('type', 'unknown')
                            message = data.get('message', '')
                            step = data.get('step', '')
                            progress = data.get('progress', '')
                            
                            # Create status indicator
                            if msg_type == 'success':
                                indicator = "✅"
                            elif msg_type == 'error':
                                indicator = "❌"
                            elif msg_type == 'warning':
                                indicator = "⚠️"
                            elif msg_type == 'summary':
                                indicator = "📋"
                            else:
                                indicator = "ℹ️"
                            
                            # Format progress and step info
                            progress_str = f" ({progress}%)" if progress else ""
                            step_str = f" [{step}]" if step else ""
                            
                            print(f"{indicator} {message}{progress_str}{step_str}")
                            
                            # Track file modifications
                            if "Modified" in message and msg_type == "success":
                                files_modified += 1
                            
                            # Print summary details
                            if msg_type == 'summary' and 'summary' in data:
                                summary = data['summary']
                                print(f"\n📊 Final Summary:")
                                print(f"   Repository: {summary.get('repository', 'N/A')}")
                                print(f"   Files Read: {summary.get('files_read', 0)}")
                                print(f"   Files Modified: {summary.get('files_modified', 0)}")
                                print(f"   Sandbox ID: {summary.get('sandbox_id', 'N/A')}")
                                print(f"   Duration: {summary.get('duration_ms', 0)}ms")
                                print(f"   Steps: {', '.join(summary.get('steps_completed', []))}")
                            
                            # Stop on error or completion
                            if msg_type in ['error', 'summary']:
                                break
                                
                        except json.JSONDecodeError as e:
                            print(f"❌ Failed to parse JSON: {e}")
                            print(f"   Raw line: {line}")
                
                print("-" * 50)
                print(f"🎉 Test '{test_name}' completed! Modified {files_modified} files.")
                return True
                
    except asyncio.TimeoutError:
        print("❌ Request timed out")
        return False
    except aiohttp.ClientError as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

async def run_all_tests():
    """Run all test cases."""
    print("🔧 FastAPI File Editing Test Suite")
    print("=" * 60)
    
    results = {}
    
    for test_name, test_data in TEST_PROMPTS.items():
        try:
            success = await test_code_endpoint(test_name, test_data)
            results[test_name] = success
            
            if not success:
                print(f"⏸️  Test '{test_name}' failed. Continue? (y/n): ", end="")
                # For automated testing, continue automatically
                print("y (auto-continue)")
                
            # Small delay between tests
            await asyncio.sleep(2)
            
        except KeyboardInterrupt:
            print(f"\n⏹️  Tests interrupted by user")
            break
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with error: {e}")
            results[test_name] = False
    
    # Print final results
    print(f"\n{'='*60}")
    print("📊 TEST RESULTS SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for success in results.values() if success)
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check the logs above.")

async def run_single_test(test_name: str):
    """Run a single test by name."""
    if test_name not in TEST_PROMPTS:
        print(f"❌ Unknown test: {test_name}")
        print(f"Available tests: {', '.join(TEST_PROMPTS.keys())}")
        return
    await test_code_endpoint(test_name, TEST_PROMPTS[test_name])

def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        if test_name == "list":
            print("Available tests:")
            for name, data in TEST_PROMPTS.items():
                print(f"  {name}: {data['prompt']}")
            return
        else:
            asyncio.run(run_single_test(test_name))
    else:
        print("Usage:")
        print("  python test_file_editing.py                 # Run all tests")
        print("  python test_file_editing.py <test_name>     # Run specific test")
        print("  python test_file_editing.py list            # List available tests")
        print()
        print("Run all tests? (y/n): ", end="")
        
        try:
            choice = input().lower().strip()
            if choice in ['y', 'yes', '']:
                asyncio.run(run_all_tests())
            else:
                print("Tests cancelled.")
        except KeyboardInterrupt:
            print("\nTests cancelled.")

if __name__ == "__main__":
    main() 