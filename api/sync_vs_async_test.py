#!/usr/bin/env python3
"""
Sync vs Async Tracing Test
Compare @traceable behavior between sync and async functions
"""

import asyncio
import time
import logging
from typing import Dict, Any
from dotenv import load_dotenv
from langsmith import traceable

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TracingComparison:
    def __init__(self):
        logger.info("🔍 TracingComparison initialized")
    
    @traceable(name="sync_simple_function", tags=["sync", "test"])
    def sync_simple_function(self, input_data: str) -> str:
        """Simple synchronous function with @traceable"""
        logger.info(f"🔄 Sync function processing: {input_data}")
        time.sleep(0.1)  # Simulate work
        result = f"Sync processed: {input_data}"
        logger.info(f"✅ Sync function completed: {result}")
        return result
    
    @traceable(name="async_simple_function", tags=["async", "test"])
    async def async_simple_function(self, input_data: str) -> str:
        """Simple asynchronous function with @traceable"""
        logger.info(f"🔄 Async function processing: {input_data}")
        await asyncio.sleep(0.1)  # Simulate async work
        result = f"Async processed: {input_data}"
        logger.info(f"✅ Async function completed: {result}")
        return result
    
    @traceable(
        name="sync_complex_function", 
        tags=["sync", "complex", "test"],
        metadata={"operation": "complex_sync", "version": "1.0"}
    )
    def sync_complex_function(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Complex synchronous function with detailed tracing"""
        logger.info(f"🔄 Sync complex function processing: {len(data)} items")
        
        # Simulate complex processing
        results = {}
        for key, value in data.items():
            time.sleep(0.05)  # Simulate processing time
            results[key] = f"processed_{value}"
        
        # Add some metadata
        results["_metadata"] = {
            "processed_count": len(data),
            "processing_time": 0.05 * len(data),
            "function_type": "sync"
        }
        
        logger.info(f"✅ Sync complex function completed: {len(results)} results")
        return results
    
    @traceable(
        name="async_complex_function", 
        tags=["async", "complex", "test"],
        metadata={"operation": "complex_async", "version": "1.0"}
    )
    async def async_complex_function(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Complex asynchronous function with detailed tracing"""
        logger.info(f"🔄 Async complex function processing: {len(data)} items")
        
        # Simulate complex async processing
        results = {}
        for key, value in data.items():
            await asyncio.sleep(0.05)  # Simulate async processing time
            results[key] = f"async_processed_{value}"
        
        # Add some metadata
        results["_metadata"] = {
            "processed_count": len(data),
            "processing_time": 0.05 * len(data),
            "function_type": "async"
        }
        
        logger.info(f"✅ Async complex function completed: {len(results)} results")
        return results
    
    @traceable(name="sync_error_function", tags=["sync", "error", "test"])
    def sync_error_function(self, should_error: bool = True) -> str:
        """Synchronous function that can throw errors"""
        logger.info(f"🔄 Sync error function called (should_error={should_error})")
        
        if should_error:
            logger.error("❌ Sync function throwing error")
            raise ValueError("This is a test error from sync function")
        
        result = "Sync function succeeded"
        logger.info(f"✅ Sync error function completed: {result}")
        return result
    
    @traceable(name="async_error_function", tags=["async", "error", "test"])
    async def async_error_function(self, should_error: bool = True) -> str:
        """Asynchronous function that can throw errors"""
        logger.info(f"🔄 Async error function called (should_error={should_error})")
        
        await asyncio.sleep(0.1)  # Simulate async work
        
        if should_error:
            logger.error("❌ Async function throwing error")
            raise ValueError("This is a test error from async function")
        
        result = "Async function succeeded"
        logger.info(f"✅ Async error function completed: {result}")
        return result
    
    @traceable(name="sync_nested_function", tags=["sync", "nested", "test"])
    def sync_nested_function(self, data: str) -> str:
        """Synchronous function that calls other sync functions"""
        logger.info(f"🔄 Sync nested function called with: {data}")
        
        # Call simple function
        simple_result = self.sync_simple_function(f"nested_{data}")
        
        # Call complex function
        complex_data = {"item1": data, "item2": f"modified_{data}"}
        complex_result = self.sync_complex_function(complex_data)
        
        result = f"Nested result: {simple_result} + {len(complex_result)} items"
        logger.info(f"✅ Sync nested function completed: {result}")
        return result
    
    @traceable(name="async_nested_function", tags=["async", "nested", "test"])
    async def async_nested_function(self, data: str) -> str:
        """Asynchronous function that calls other async functions"""
        logger.info(f"🔄 Async nested function called with: {data}")
        
        # Call simple async function
        simple_result = await self.async_simple_function(f"nested_{data}")
        
        # Call complex async function
        complex_data = {"item1": data, "item2": f"modified_{data}"}
        complex_result = await self.async_complex_function(complex_data)
        
        result = f"Async nested result: {simple_result} + {len(complex_result)} items"
        logger.info(f"✅ Async nested function completed: {result}")
        return result
    
    def run_sync_tests(self) -> Dict[str, Any]:
        """Run all synchronous tests"""
        logger.info("🧪 Running synchronous tests...")
        results = {}
        
        try:
            # Test 1: Simple function
            results["sync_simple"] = self.sync_simple_function("test_data")
            
            # Test 2: Complex function
            test_data = {"key1": "value1", "key2": "value2", "key3": "value3"}
            results["sync_complex"] = self.sync_complex_function(test_data)
            
            # Test 3: Error handling (success case)
            results["sync_no_error"] = self.sync_error_function(should_error=False)
            
            # Test 4: Error handling (error case)
            try:
                results["sync_with_error"] = self.sync_error_function(should_error=True)
            except Exception as e:
                results["sync_with_error"] = f"Expected error: {str(e)}"
            
            # Test 5: Nested function
            results["sync_nested"] = self.sync_nested_function("nested_test")
            
            logger.info("✅ All synchronous tests completed")
            
        except Exception as e:
            logger.error(f"❌ Sync tests failed: {e}")
            results["error"] = str(e)
        
        return results
    
    async def run_async_tests(self) -> Dict[str, Any]:
        """Run all asynchronous tests"""
        logger.info("🧪 Running asynchronous tests...")
        results = {}
        
        try:
            # Test 1: Simple function
            results["async_simple"] = await self.async_simple_function("test_data")
            
            # Test 2: Complex function
            test_data = {"key1": "value1", "key2": "value2", "key3": "value3"}
            results["async_complex"] = await self.async_complex_function(test_data)
            
            # Test 3: Error handling (success case)
            results["async_no_error"] = await self.async_error_function(should_error=False)
            
            # Test 4: Error handling (error case)
            try:
                results["async_with_error"] = await self.async_error_function(should_error=True)
            except Exception as e:
                results["async_with_error"] = f"Expected error: {str(e)}"
            
            # Test 5: Nested function
            results["async_nested"] = await self.async_nested_function("nested_test")
            
            logger.info("✅ All asynchronous tests completed")
            
        except Exception as e:
            logger.error(f"❌ Async tests failed: {e}")
            results["error"] = str(e)
        
        return results
    
    async def run_comparison(self) -> Dict[str, Any]:
        """Run both sync and async tests and compare"""
        logger.info("🚀 Starting sync vs async comparison...")
        
        start_time = time.time()
        
        # Run sync tests
        sync_start = time.time()
        sync_results = self.run_sync_tests()
        sync_duration = time.time() - sync_start
        
        # Run async tests
        async_start = time.time()
        async_results = await self.run_async_tests()
        async_duration = time.time() - async_start
        
        total_duration = time.time() - start_time
        
        comparison = {
            "timestamp": time.time(),
            "sync_results": sync_results,
            "async_results": async_results,
            "performance": {
                "sync_duration": sync_duration,
                "async_duration": async_duration,
                "total_duration": total_duration
            },
            "summary": {
                "sync_tests_passed": len([k for k, v in sync_results.items() if not str(v).startswith("Expected error") and k != "error"]),
                "async_tests_passed": len([k for k, v in async_results.items() if not str(v).startswith("Expected error") and k != "error"]),
                "sync_errors": 1 if "error" in sync_results else 0,
                "async_errors": 1 if "error" in async_results else 0
            }
        }
        
        logger.info(f"🏁 Comparison completed in {total_duration:.2f}s")
        return comparison

async def main():
    """Main comparison function"""
    print("="*60)
    print("🔍 SYNC VS ASYNC TRACING COMPARISON")
    print("="*60)
    
    try:
        comparison = TracingComparison()
        results = await comparison.run_comparison()
        
        # Print summary
        print(f"\n📊 COMPARISON RESULTS")
        print("-" * 40)
        print(f"⏱️ Sync duration: {results['performance']['sync_duration']:.2f}s")
        print(f"⏱️ Async duration: {results['performance']['async_duration']:.2f}s")
        print(f"⏱️ Total duration: {results['performance']['total_duration']:.2f}s")
        
        print(f"\n✅ Sync tests passed: {results['summary']['sync_tests_passed']}")
        print(f"✅ Async tests passed: {results['summary']['async_tests_passed']}")
        print(f"❌ Sync errors: {results['summary']['sync_errors']}")
        print(f"❌ Async errors: {results['summary']['async_errors']}")
        
        # Save detailed results
        import json
        with open("sync_async_comparison.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📝 Detailed results saved to: sync_async_comparison.json")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS")
        print("-" * 40)
        print("1. Check LangSmith dashboard for traces from both sync and async functions")
        print("2. Compare trace completeness between sync and async functions")
        print("3. Look for any differences in error handling in traces")
        print("4. Verify nested function traces show proper parent-child relationships")
        print("5. If async traces are missing, consider using manual tracing as fallback")
        
        print(f"\n🔗 Next steps:")
        print("- Run: python monitor_traces.py (to check if traces appeared)")
        print("- Check: https://smith.langchain.com (LangSmith dashboard)")
        print("- Review: processor.log (for application logs)")
        
    except Exception as e:
        logger.error(f"❌ Comparison failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())