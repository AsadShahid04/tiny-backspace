#!/usr/bin/env python3
"""
Test script to demonstrate Tiny Backspace observability features.
This script simulates various scenarios to show the logging and monitoring capabilities.
"""

import asyncio
import time
import uuid
from datetime import datetime
from app.logging_config import (
    observability_logger,
    log_agent_operation,
    log_performance_metric,
    log_error_with_context,
    performance_timer,
    get_observability_summary
)

async def simulate_agent_thinking():
    """Simulate agent thinking process with detailed logging."""
    request_id = str(uuid.uuid4())[:8]
    observability_logger.set_request_id(request_id)
    
    print(f"🤖 Simulating agent thinking for request: {request_id}")
    print("=" * 60)
    
    # Step 1: Repository Analysis
    with performance_timer("repository_analysis", {"repo_size": "medium"}):
        log_agent_operation("analysis_start", "Beginning repository structure analysis", {
            "files_to_analyze": 25,
            "languages_detected": ["Python", "JavaScript"]
        })
        
        await asyncio.sleep(0.5)
        
        log_agent_operation("analysis_complete", "Repository analysis completed", {
            "files_analyzed": 25,
            "main_files_found": 8,
            "test_files_found": 5,
            "config_files_found": 3
        })
    
    # Step 2: AI Provider Selection
    log_agent_operation("ai_selection", "Selecting AI provider for code generation", {
        "available_providers": ["claude", "openai", "dummy"],
        "selected_provider": "claude",
        "reason": "best_quality"
    })
    
    # Step 3: Code Generation
    with performance_timer("ai_generation", {"provider": "claude", "model": "claude-3-sonnet"}):
        log_agent_operation("generation_start", "Starting AI-powered code generation", {
            "prompt_length": 150,
            "context_files": 3
        })
        
        await asyncio.sleep(1.2)
        
        log_agent_operation("generation_complete", "AI generation completed successfully", {
            "edits_generated": 2,
            "files_to_modify": ["main.py", "utils.py"],
            "total_tokens_used": 1250
        })
    
    # Step 4: File Implementation
    with performance_timer("file_implementation", {"files_count": 2}):
        log_agent_operation("implementation_start", "Starting file modification implementation")
        
        for i, file_name in enumerate(["main.py", "utils.py"]):
            await asyncio.sleep(0.3)
            log_agent_operation("file_modified", f"Successfully modified {file_name}", {
                "file_path": file_name,
                "bytes_written": 450 + i * 100,
                "modification_type": "enhancement"
            })
    
    # Step 5: PR Creation
    with performance_timer("github_pr_creation", {"repo": "test-repo"}):
        log_agent_operation("pr_creation", "Creating GitHub pull request")
        await asyncio.sleep(0.8)
        log_agent_operation("pr_success", "Pull request created successfully", {
            "pr_url": "https://github.com/test/repo/pull/123",
            "branch_name": "feature/ai-enhancements"
        })
    
    print("\n✅ Agent thinking simulation completed!")
    return request_id

async def simulate_error_scenarios():
    """Simulate various error scenarios to test error logging."""
    request_id = str(uuid.uuid4())[:8]
    observability_logger.set_request_id(request_id)
    
    print(f"❌ Simulating error scenarios for request: {request_id}")
    print("=" * 60)
    
    # Simulate API timeout
    try:
        with performance_timer("api_call", {"endpoint": "claude_api"}):
            await asyncio.sleep(0.1)
            raise TimeoutError("API request timed out after 30 seconds")
    except Exception as e:
        log_error_with_context(e, {
            "operation": "claude_api_call",
            "retry_count": 2,
            "timeout_seconds": 30
        })
    
    # Simulate file system error
    try:
        with performance_timer("file_operation", {"operation": "write"}):
            await asyncio.sleep(0.1)
            raise PermissionError("Permission denied: cannot write to file")
    except Exception as e:
        log_error_with_context(e, {
            "operation": "file_write",
            "file_path": "/sandbox/main.py",
            "user_permissions": "read_only"
        })
    
    # Simulate network error
    try:
        with performance_timer("network_call", {"endpoint": "github_api"}):
            await asyncio.sleep(0.1)
            raise ConnectionError("Failed to connect to GitHub API")
    except Exception as e:
        log_error_with_context(e, {
            "operation": "github_api_call",
            "endpoint": "/repos/test/repo/pulls",
            "network_status": "unreachable"
        })
    
    print("\n✅ Error scenario simulation completed!")

async def simulate_performance_variations():
    """Simulate various performance scenarios."""
    request_id = str(uuid.uuid4())[:8]
    observability_logger.set_request_id(request_id)
    
    print(f"⏱️ Simulating performance variations for request: {request_id}")
    print("=" * 60)
    
    # Fast operation
    with performance_timer("fast_operation", {"type": "validation"}):
        await asyncio.sleep(0.05)
        log_agent_operation("validation", "URL validation completed quickly")
    
    # Medium operation
    with performance_timer("medium_operation", {"type": "file_reading"}):
        await asyncio.sleep(0.5)
        log_agent_operation("file_reading", "Read 3 configuration files")
    
    # Slow operation
    with performance_timer("slow_operation", {"type": "ai_generation"}):
        await asyncio.sleep(2.0)
        log_agent_operation("ai_generation", "Generated complex code changes")
    
    # Very slow operation
    with performance_timer("very_slow_operation", {"type": "large_repo_clone"}):
        await asyncio.sleep(3.5)
        log_agent_operation("repo_clone", "Cloned large repository with many files")
    
    print("\n✅ Performance variation simulation completed!")

async def demonstrate_observability_summary():
    """Demonstrate the observability summary feature."""
    print("📊 Demonstrating Observability Summary")
    print("=" * 60)
    
    # Generate summary
    summary = get_observability_summary()
    
    print("🤖 Agent Thinking Summary:")
    print(f"  - Thinking Steps: {summary.get('thinking_steps', 0)}")
    print(f"  - Request ID: {summary.get('request_id', 'N/A')}")
    
    performance = summary.get('performance_summary', {})
    if performance:
        print("\n⏱️ Performance Summary:")
        print(f"  - Total Operations: {performance.get('total_operations', 0)}")
        print(f"  - Total Duration: {performance.get('total_duration_ms', 0):.2f}ms")
        print(f"  - Average Duration: {performance.get('average_duration_ms', 0):.2f}ms")
        
        operations = performance.get('operations', [])
        if operations:
            print("\n  Operation Breakdown:")
            for op in operations[-5:]:  # Show last 5 operations
                print(f"    - {op['operation']}: {op['duration_ms']:.2f}ms")
    
    thinking_log = summary.get('thinking_log', [])
    if thinking_log:
        print(f"\n🧠 Thinking Log ({len(thinking_log)} entries):")
        for entry in thinking_log[-3:]:  # Show last 3 thinking steps
            print(f"  - [{entry['step']}] {entry['thought']}")

async def main():
    """Main function to run all observability demonstrations."""
    print("🚀 TINY BACKSPACE OBSERVABILITY DEMONSTRATION")
    print("=" * 60)
    print("This script demonstrates the comprehensive observability features")
    print("including real-time agent thinking, performance tracking, and error monitoring.")
    print()
    
    # Run simulations
    await simulate_agent_thinking()
    print()
    
    await simulate_error_scenarios()
    print()
    
    await simulate_performance_variations()
    print()
    
    await demonstrate_observability_summary()
    print()
    
    print("🎉 Observability demonstration completed!")
    print("\n📝 Next steps:")
    print("1. Check the 'logs' directory for generated log files")
    print("2. Run 'python monitor_dashboard.py' for real-time monitoring")
    print("3. Run 'python app/utils/log_analyzer.py' for health report")
    print("4. Run 'python monitor_dashboard.py --health-report' for one-time report")

if __name__ == "__main__":
    asyncio.run(main()) 