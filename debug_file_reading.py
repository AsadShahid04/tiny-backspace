#!/usr/bin/env python3
"""
Debug script to test file reading in sandbox
"""

import asyncio
import os
from dotenv import load_dotenv
from e2b import Sandbox

# Load environment variables
load_dotenv()

async def debug_file_reading():
    """Debug file reading in sandbox"""
    
    print("🔍 Debugging file reading in sandbox...")
    
    try:
        # Create sandbox
        print("📦 Creating sandbox...")
        sandbox = Sandbox()
        print(f"✅ Sandbox created with ID: {sandbox.sandbox_id}")
        
        # Clone repository
        print("📥 Cloning repository...")
        clone_result = sandbox.commands.run("git clone https://github.com/AsadShahid04/tiny-backspace repo")
        print(f"Clone result: {clone_result.exit_code}")
        if clone_result.exit_code != 0:
            print(f"Clone error: {clone_result.stderr}")
            return
        
        # List files
        print("📁 Listing files...")
        list_result = sandbox.commands.run("find repo -type f -name '*.py' | head -10")
        print(f"List result: {list_result.exit_code}")
        print(f"Files found: {list_result.stdout}")
        
        # Try to read a specific file
        print("📖 Reading api/main.py...")
        read_result = sandbox.commands.run("cat repo/api/main.py")
        print(f"Read result: {read_result.exit_code}")
        if read_result.exit_code == 0:
            print(f"File content length: {len(read_result.stdout)}")
            print(f"First 200 chars: {read_result.stdout[:200]}")
        else:
            print(f"Read error: {read_result.stderr}")
        
        # Cleanup
        print("🧹 Cleaning up...")
        sandbox.kill()
        print("✅ Cleanup complete")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_file_reading()) 