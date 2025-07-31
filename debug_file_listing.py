#!/usr/bin/env python3
"""
Debug script to test file listing command
"""

import asyncio
import os
from dotenv import load_dotenv
from e2b import Sandbox

# Load environment variables
load_dotenv()

async def debug_file_listing():
    """Debug file listing in sandbox"""
    
    print("🔍 Debugging file listing in sandbox...")
    
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
        
        # Test the exact file listing command from the main code
        print("📁 Testing file listing command...")
        files_result = sandbox.commands.run("find repo -type f -name '*.py' -o -name '*.js' -o -name '*.ts' -o -name '*.jsx' -o -name '*.tsx' | head -20")
        print(f"Files result: {files_result.exit_code}")
        print(f"Files found: {files_result.stdout}")
        
        if files_result.stdout:
            files = files_result.stdout.strip().split('\n')
            print(f"Number of files: {len(files)}")
            for i, file_path in enumerate(files[:5]):
                print(f"  {i+1}. {file_path}")
        else:
            print("No files found!")
        
        # Cleanup
        print("🧹 Cleaning up...")
        sandbox.kill()
        print("✅ Cleanup complete")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_file_listing()) 