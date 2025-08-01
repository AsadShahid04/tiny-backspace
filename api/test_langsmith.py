#!/usr/bin/env python3
"""
Quick LangSmith Test Script
Simple test to verify LangSmith tracing is working
"""

import asyncio
import os
import logging
from dotenv import load_dotenv
from processor import TinyBackspaceProcessor
from debug_langsmith import LangSmithDebugger

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_langsmith_integration():
    """Test LangSmith integration with the processor"""
    logger.info("🚀 Starting LangSmith integration test")
    
    try:
        # Initialize processor
        processor = TinyBackspaceProcessor()
        logger.info("✅ Processor initialized")
        
        # Test code generation function directly
        logger.info("🧪 Testing code generation function...")
        
        test_prompt = "Add a simple hello world function to the main.py file"
        test_files = {
            "main.py": "# Empty file\nprint('Hello World')\n"
        }
        test_repo = "https://github.com/test/repo"
        
        # This will test both @traceable and manual tracing
        result = await processor._generate_code(test_prompt, test_files, test_repo)
        
        if result:
            logger.info(f"✅ Code generation test passed: {len(result)} changes generated")
        else:
            logger.warning("⚠️ Code generation test returned empty result")
        
        # Test PR creation function (without actually creating a PR)
        logger.info("🧪 Testing PR creation function...")
        
        # This would normally create a PR, but we'll catch the error since we're using a fake repo
        try:
            pr_result = await processor._create_pull_request(
                "https://github.com/test/fake-repo", 
                "test-branch", 
                "Test PR creation"
            )
            if pr_result:
                logger.info("✅ PR creation test passed")
            else:
                logger.info("ℹ️ PR creation test completed (expected to fail with fake repo)")
        except Exception as e:
            logger.info(f"ℹ️ PR creation test completed with expected error: {str(e)[:100]}...")
        
        logger.info("✅ Integration test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("="*60)
    print("🔍 LANGSMITH TESTING SUITE")
    print("="*60)
    
    # Step 1: Run comprehensive debugging
    print("\n📋 Step 1: Running comprehensive debugging...")
    debugger = LangSmithDebugger()
    debug_results = await debugger.run_comprehensive_debug()
    
    # Check if basic connectivity works
    connectivity_ok = debug_results.get("api_connectivity", {}).get("status") == "success"
    client_ok = debug_results.get("client_test", {}).get("status") == "success"
    
    print(f"\n📊 Debug Results Summary:")
    print(f"  - API Connectivity: {'✅' if connectivity_ok else '❌'}")
    print(f"  - Client Test: {'✅' if client_ok else '❌'}")
    
    # Step 2: Test integration if basic tests pass
    if connectivity_ok and client_ok:
        print("\n📋 Step 2: Running integration tests...")
        integration_ok = await test_langsmith_integration()
        print(f"  - Integration Test: {'✅' if integration_ok else '❌'}")
    else:
        print("\n⚠️ Skipping integration tests due to connectivity issues")
        print("Please check your LANGSMITH_API_KEY and network connection")
    
    # Step 3: Provide recommendations
    print("\n📋 Step 3: Recommendations")
    print("-" * 40)
    
    if connectivity_ok and client_ok:
        print("✅ LangSmith is properly configured and working!")
        print("   - Traces should appear in real-time")
        print("   - Check the LangSmith dashboard for your project: tiny-backspace")
        print("   - Logs are saved to: processor.log and langsmith_debug.log")
    else:
        print("❌ LangSmith configuration issues detected:")
        if not connectivity_ok:
            print("   - Check your LANGSMITH_API_KEY")
            print("   - Verify network connectivity to api.smith.langchain.com")
        if not client_ok:
            print("   - LangSmith client initialization failed")
            print("   - Check environment variables and API key permissions")
    
    print("\n📝 Next Steps:")
    print("1. Check langsmith_debug_results.json for detailed results")
    print("2. Review processor.log for application logs")
    print("3. Visit https://smith.langchain.com to view traces")
    print("4. If issues persist, check the manual tracing fallbacks are working")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    asyncio.run(main())