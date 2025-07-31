#!/usr/bin/env python3
"""
Test the full Tiny Backspace flow with environment variables
"""

import requests
import json
import time
import os

def test_full_flow():
    """Test the complete flow with environment variables"""
    
    print("🚀 Testing Tiny Backspace Full Flow")
    print("=" * 50)
    
    # Test health endpoint first
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return
    
    # Test the main code endpoint
    print("\n🔍 Testing code endpoint with full flow...")
    print("Expected: Should show the complete pipeline")
    
    try:
        response = requests.post(
            "http://localhost:8000/code",
            headers={"Content-Type": "application/json"},
            json={
                "repoUrl": "https://github.com/AsadShahid04/tiny-backspace",
                "prompt": "Add a simple test endpoint"
            },
            stream=True,
            timeout=180  # 3 minutes timeout
        )
        
        if response.status_code == 200:
            print("✅ Code endpoint is working")
            print("📡 Streaming response:")
            print("-" * 50)
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            data = json.loads(line_str[6:])  # Remove 'data: ' prefix
                            print(f"📝 {data['type'].upper()}: {data['message']}")
                            
                            # Check if we got an error
                            if data['type'] == 'error':
                                print(f"❌ Error detected: {data['message']}")
                                break
                                
                            # Check if we got success
                            if data['type'] == 'success' and 'Pull request created' in data['message']:
                                print("🎉 SUCCESS! Pull request was created!")
                                break
                                
                        except json.JSONDecodeError:
                            print(f"📝 RAW: {line_str}")
        else:
            print(f"❌ Code endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out (this might be normal for a long-running process)")
    except Exception as e:
        print(f"❌ Code endpoint error: {e}")

if __name__ == "__main__":
    test_full_flow() 