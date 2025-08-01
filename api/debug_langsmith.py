#!/usr/bin/env python3
"""
LangSmith Debugging Script
Comprehensive debugging for LangSmith tracing issues
"""

import os
import asyncio
import json
import time
import logging
from typing import Dict, Any
from dotenv import load_dotenv
import langsmith
from langsmith import traceable, Client
from langsmith.run_trees import RunTree
import requests

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('langsmith_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class LangSmithDebugger:
    def __init__(self):
        self.api_key = os.getenv("LANGSMITH_API_KEY")
        self.project = os.getenv("LANGSMITH_PROJECT", "tiny-backspace")
        self.tracing_enabled = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
        self.endpoint = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
        
        logger.info("🔍 LangSmith Debugger initialized")
        
    def verify_environment_variables(self) -> Dict[str, Any]:
        """Verify all LangSmith environment variables"""
        logger.info("🔍 Verifying environment variables...")
        
        env_vars = {
            "LANGSMITH_API_KEY": self.api_key,
            "LANGSMITH_PROJECT": self.project,
            "LANGSMITH_TRACING": self.tracing_enabled,
            "LANGSMITH_ENDPOINT": self.endpoint
        }
        
        results = {}
        for key, value in env_vars.items():
            if value:
                results[key] = f"✅ Set: {str(value)[:20]}..." if key == "LANGSMITH_API_KEY" else f"✅ Set: {value}"
                logger.info(f"{key}: {results[key]}")
            else:
                results[key] = "❌ Not set"
                logger.error(f"{key}: {results[key]}")
        
        return results
    
    def test_api_connectivity(self) -> Dict[str, Any]:
        """Test direct API connectivity to LangSmith"""
        logger.info("🔍 Testing API connectivity...")
        
        if not self.api_key:
            return {"status": "error", "message": "No API key available"}
        
        try:
            # Test basic API connectivity
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Try to get session info
            response = requests.get(
                f"{self.endpoint}/sessions",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("✅ API connectivity successful")
                return {
                    "status": "success",
                    "message": "API connectivity successful",
                    "response_code": response.status_code
                }
            else:
                logger.error(f"❌ API connectivity failed: {response.status_code}")
                return {
                    "status": "error",
                    "message": f"API returned {response.status_code}",
                    "response_text": response.text[:200]
                }
                
        except Exception as e:
            logger.error(f"❌ API connectivity error: {e}")
            return {"status": "error", "message": str(e)}
    
    def test_langsmith_client(self) -> Dict[str, Any]:
        """Test LangSmith client initialization and basic operations"""
        logger.info("🔍 Testing LangSmith client...")
        
        try:
            client = Client(
                api_key=self.api_key,
                api_url=self.endpoint
            )
            
            # Try to create a simple run
            run_id = client.create_run(
                name="debug_test_run",
                run_type="llm",
                inputs={"test": "debug"},
                project_name=self.project
            )
            
            logger.info(f"✅ Client test successful, run ID: {run_id}")
            
            # Try to end the run
            client.update_run(
                run_id=run_id,
                outputs={"result": "debug_success"},
                end_time=time.time()
            )
            
            return {
                "status": "success",
                "message": "Client test successful",
                "run_id": str(run_id)
            }
            
        except Exception as e:
            logger.error(f"❌ Client test failed: {e}")
            return {"status": "error", "message": str(e)}
    
    @traceable(name="debug_sync_function", tags=["debug", "sync"])
    def test_sync_traceable(self, input_data: str) -> str:
        """Test @traceable decorator with synchronous function"""
        logger.info("🔍 Testing sync @traceable decorator...")
        
        time.sleep(0.1)  # Simulate some work
        result = f"Processed: {input_data}"
        
        logger.info(f"✅ Sync traceable completed: {result}")
        return result
    
    @traceable(name="debug_async_function", tags=["debug", "async"])
    async def test_async_traceable(self, input_data: str) -> str:
        """Test @traceable decorator with async function"""
        logger.info("🔍 Testing async @traceable decorator...")
        
        await asyncio.sleep(0.1)  # Simulate async work
        result = f"Async processed: {input_data}"
        
        logger.info(f"✅ Async traceable completed: {result}")
        return result
    
    def test_manual_tracing(self) -> Dict[str, Any]:
        """Test manual trace creation without decorators"""
        logger.info("🔍 Testing manual tracing...")
        
        try:
            client = Client(
                api_key=self.api_key,
                api_url=self.endpoint
            )
            
            # Create a run tree manually
            run_tree = RunTree(
                name="manual_debug_trace",
                run_type="chain",
                inputs={"manual_test": "debug_data"},
                project_name=self.project,
                client=client
            )
            
            # Start the trace
            run_tree.post()
            logger.info(f"✅ Manual trace started: {run_tree.id}")
            
            # Add some child operations
            child_run = run_tree.create_child(
                name="manual_child_operation",
                run_type="llm",
                inputs={"child_input": "test"}
            )
            child_run.post()
            
            # End child
            child_run.end(outputs={"child_output": "success"})
            child_run.patch()
            
            # End parent
            run_tree.end(outputs={"manual_result": "completed"})
            run_tree.patch()
            
            logger.info("✅ Manual tracing completed successfully")
            return {
                "status": "success", 
                "message": "Manual tracing successful",
                "run_id": str(run_tree.id)
            }
            
        except Exception as e:
            logger.error(f"❌ Manual tracing failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def run_comprehensive_debug(self) -> Dict[str, Any]:
        """Run all debugging tests"""
        logger.info("🚀 Starting comprehensive LangSmith debugging...")
        
        results = {
            "timestamp": time.time(),
            "environment_variables": self.verify_environment_variables(),
            "api_connectivity": self.test_api_connectivity(),
            "client_test": self.test_langsmith_client(),
            "manual_tracing": self.test_manual_tracing()
        }
        
        # Test sync traceable
        try:
            sync_result = self.test_sync_traceable("debug_sync_input")
            results["sync_traceable"] = {"status": "success", "result": sync_result}
        except Exception as e:
            results["sync_traceable"] = {"status": "error", "message": str(e)}
        
        # Test async traceable
        try:
            async_result = await self.test_async_traceable("debug_async_input")
            results["async_traceable"] = {"status": "success", "result": async_result}
        except Exception as e:
            results["async_traceable"] = {"status": "error", "message": str(e)}
        
        # Summary
        successful_tests = sum(1 for test in results.values() 
                             if isinstance(test, dict) and test.get("status") == "success")
        total_tests = len([k for k in results.keys() if k != "timestamp"])
        
        results["summary"] = {
            "successful_tests": successful_tests,
            "total_tests": total_tests,
            "success_rate": f"{(successful_tests/total_tests)*100:.1f}%"
        }
        
        logger.info(f"🏁 Debug completed: {successful_tests}/{total_tests} tests passed")
        return results

async def main():
    """Main debugging function"""
    debugger = LangSmithDebugger()
    results = await debugger.run_comprehensive_debug()
    
    # Save results to file
    with open("langsmith_debug_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print("\n" + "="*60)
    print("🔍 LANGSMITH DEBUG RESULTS")
    print("="*60)
    
    for test_name, result in results.items():
        if test_name == "timestamp":
            continue
            
        if isinstance(result, dict):
            status = result.get("status", "unknown")
            if status == "success":
                print(f"✅ {test_name}: SUCCESS")
            elif status == "error":
                print(f"❌ {test_name}: ERROR - {result.get('message', 'Unknown error')}")
            else:
                print(f"ℹ️  {test_name}: {result}")
        else:
            print(f"ℹ️  {test_name}: {result}")
    
    print("\n" + "="*60)
    print(f"📊 SUMMARY: {results['summary']}")
    print("="*60)
    
    print(f"\n📝 Detailed logs saved to: langsmith_debug.log")
    print(f"📝 Results saved to: langsmith_debug_results.json")

if __name__ == "__main__":
    asyncio.run(main())