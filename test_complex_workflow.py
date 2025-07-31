#!/usr/bin/env python3
"""
Test script for complex Tiny Backspace workflow
"""

import requests
import json
import time
import sys

def test_complex_workflow():
    """Test a more complex workflow that should trigger full pipeline"""
    
    # Test data - more complex request
    test_data = {
        "repoUrl": "https://github.com/AsadShahid04/tiny-backspace",
        "prompt": "Add a new API endpoint /health-check that returns system status and version information"
    }
    
    print("🚀 Testing Complex Tiny Backspace Workflow")
    print("=" * 60)
    print(f"📁 Repository: {test_data['repoUrl']}")
    print(f"💭 Prompt: {test_data['prompt']}")
    print("=" * 60)
    
    try:
        # Make the request to the API
        print("📡 Making request to Tiny Backspace API...")
        response = requests.post(
            "http://localhost:8000/code",
            json=test_data,
            stream=True,
            timeout=300
        )
        
        if response.status_code == 200:
            print("✅ API request successful, streaming response...")
            print("-" * 50)
            
            # Process the streaming response
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            data = json.loads(line_str[6:])
                            event_type = data.get('type', 'info')
                            message = data.get('message', '')
                            
                            if event_type == 'error':
                                print(f"❌ {message}")
                            elif event_type == 'success':
                                print(f"✅ {message}")
                            elif event_type == 'info':
                                print(f"ℹ️  {message}")
                            else:
                                print(f"📝 {message}")
                                
                        except json.JSONDecodeError:
                            print(f"📝 Raw: {line_str[6:]}")
            
            print("-" * 50)
            print("✅ Stream completed!")
            print("\n🎉 Complex workflow test completed!")
            
        else:
            print(f"❌ API request failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure the server is running")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_complex_workflow() 