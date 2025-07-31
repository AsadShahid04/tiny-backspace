#!/usr/bin/env python3
"""
Complete Tiny Backspace Workflow Test
This script will run the full end-to-end workflow and create a PR
"""

import requests
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_complete_workflow():
    """Run the complete Tiny Backspace workflow"""
    
    print("🚀 Starting Complete Tiny Backspace Workflow")
    print("=" * 60)
    
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
    
    # Test the main code endpoint with your repository
    print("\n🔍 Starting complete workflow...")
    print("Repository: https://github.com/AsadShahid04/tiny-backspace")
    print("Prompt: Add a simple test endpoint")
    print("-" * 60)
    
    try:
        response = requests.post(
            "http://localhost:8000/code",
            headers={"Content-Type": "application/json"},
            json={
                "repoUrl": "https://github.com/AsadShahid04/tiny-backspace",
                "prompt": "Add a simple test endpoint"
            },
            stream=True,
            timeout=300  # 5 minutes timeout
        )
        
        if response.status_code == 200:
            print("✅ Code endpoint is working")
            print("📡 Streaming response:")
            print("-" * 60)
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            data = json.loads(line_str[6:])  # Remove 'data: ' prefix
                            event_type = data['type'].upper()
                            message = data['message']
                            
                            # Color coding for different event types
                            if event_type == 'INFO':
                                print(f"📝 {message}")
                            elif event_type == 'SUCCESS':
                                print(f"✅ {message}")
                            elif event_type == 'ERROR':
                                print(f"❌ {message}")
                            else:
                                print(f"📝 {event_type}: {message}")
                            
                            # Check if we got an error
                            if data['type'] == 'error':
                                print(f"\n❌ Workflow failed with error: {data['message']}")
                                break
                                
                            # Check if we got success
                            if data['type'] == 'success' and 'Pull request created' in data['message']:
                                print("\n🎉 SUCCESS! Pull request was created!")
                                print(f"📝 PR URL: {data['message']}")
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

def check_environment():
    """Check if all required environment variables are set"""
    print("🔍 Checking environment variables...")
    
    required_vars = ['GITHUB_PAT', 'ANTHROPIC_API_KEY', 'E2B_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value[:20]}...")
        else:
            print(f"❌ {var}: NOT SET")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file")
        return False
    
    print("✅ All environment variables are set")
    return True

if __name__ == "__main__":
    print("🔍 Environment Check")
    print("=" * 30)
    
    if not check_environment():
        exit(1)
    
    print("\n🚀 Starting Complete Workflow")
    print("=" * 30)
    
    run_complete_workflow() 