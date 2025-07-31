#!/usr/bin/env python3
"""
Simple test to isolate the file path issue
"""

import requests
import json

def test_simple_workflow():
    """Test with a simpler prompt"""
    
    # Test data
    test_data = {
        "repoUrl": "https://github.com/AsadShahid04/tiny-backspace",
        "prompt": "Add a simple print statement to the main.py file"
    }
    
    print("🚀 Testing Simple Workflow")
    print("=" * 30)
    print(f"📁 Repository: {test_data['repoUrl']}")
    print(f"💭 Prompt: {test_data['prompt']}")
    print("=" * 30)
    
    try:
        # Make the request to the API
        print("📡 Making request to Tiny Backspace API...")
        response = requests.post(
            "http://localhost:8000/code",
            json=test_data,
            stream=True,
            timeout=300
        )
        
        if response.status_code != 200:
            print(f"❌ API request failed with status code: {response.status_code}")
            return False
        
        print("✅ API request successful, streaming response...")
        print("-" * 30)
        
        # Process the streaming response
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    try:
                        data = json.loads(line_str[6:])
                        event_type = data.get('type', 'info')
                        message = data.get('message', '')
                        
                        print(f"{event_type.upper()}: {message}")
                        
                        # Check for completion or error
                        if "Pull request created:" in message:
                            print("\n🎉 SUCCESS! Pull request created!")
                            return True
                        elif "Processing failed:" in message:
                            print(f"\n❌ FAILED: {message}")
                            return False
                            
                    except json.JSONDecodeError:
                        print(f"⚠️  Could not parse: {line_str}")
        
        print("\n✅ Stream completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_simple_workflow()
    print(f"\n{'🎉 SUCCESS' if success else '❌ FAILED'}") 