#!/usr/bin/env python3
"""
Test script for the complete Tiny Backspace workflow
"""

import requests
import json
import time
import sys

def test_complete_workflow():
    """Test the complete end-to-end workflow"""
    
    # Test data
    test_data = {
        "repoUrl": "https://github.com/AsadShahid04/tiny-backspace",
        "prompt": "Add a simple test endpoint that returns 'Hello from Tiny Backspace!'"
    }
    
    print("🚀 Testing Tiny Backspace Complete Workflow")
    print("=" * 50)
    print(f"📁 Repository: {test_data['repoUrl']}")
    print(f"💭 Prompt: {test_data['prompt']}")
    print("=" * 50)
    
    try:
        # Make the request to the API
        print("📡 Making request to Tiny Backspace API...")
        response = requests.post(
            "http://localhost:8000/code",
            json=test_data,
            stream=True,
            timeout=300  # 5 minute timeout
        )
        
        if response.status_code != 200:
            print(f"❌ API request failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        print("✅ API request successful, streaming response...")
        print("-" * 50)
        
        # Process the streaming response
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    try:
                        data = json.loads(line_str[6:])  # Remove 'data: ' prefix
                        event_type = data.get('type', 'info')
                        message = data.get('message', '')
                        
                        # Color coding for different event types
                        if event_type == 'error':
                            print(f"❌ {message}")
                        elif event_type == 'success':
                            print(f"✅ {message}")
                        elif event_type == 'info':
                            print(f"ℹ️  {message}")
                        else:
                            print(f"📝 {message}")
                            
                        # Check for completion
                        if "Pull request created:" in message:
                            print("\n🎉 SUCCESS! Pull request created successfully!")
                            return True
                        elif "Processing failed:" in message:
                            print(f"\n❌ FAILED: {message}")
                            return False
                            
                    except json.JSONDecodeError:
                        print(f"⚠️  Could not parse SSE data: {line_str}")
        
        print("\n✅ Stream completed successfully!")
        return True
        
    except requests.exceptions.Timeout:
        print("❌ Request timed out after 5 minutes")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API. Make sure the server is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def check_server_health():
    """Check if the server is running and healthy"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is healthy and running")
            return True
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error checking server health: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Checking server health...")
    if not check_server_health():
        print("\n💡 To start the server, run:")
        print("   source venv/bin/activate && export $(cat .env | xargs) && python api/main.py")
        sys.exit(1)
    
    print("\n" + "="*60)
    success = test_complete_workflow()
    
    if success:
        print("\n🎉 Complete workflow test PASSED!")
        print("✅ The Tiny Backspace system is working correctly!")
    else:
        print("\n❌ Complete workflow test FAILED!")
        print("🔧 Check the logs above for issues to fix.")
    
    sys.exit(0 if success else 1) 