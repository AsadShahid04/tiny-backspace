"""
Simplified observability for Tiny Backspace API.
Focuses on LangSmith for AI observability and basic telemetry.
"""

import os
import time
import json
from typing import Dict, Any, Optional
from contextlib import contextmanager

# LangSmith imports
try:
    from langsmith import Client
    from langsmith.run_trees import RunTree
    LANGSMITH_AVAILABLE = True
    print("✅ LangSmith available")
except ImportError:
    LANGSMITH_AVAILABLE = False
    print("⚠️ LangSmith not available - install with: pip install langsmith")


class SimpleObservability:
    """Simplified observability focused on AI agent tracking."""
    
    def __init__(self):
        self.request_id = None
        self.langsmith_client = None
        self.run_tree = None
        self.thinking_logs = []
        self.performance_metrics = {}
        self.request_start_time = None
        
        self._setup_langsmith()
    
    def _setup_langsmith(self):
        """Initialize LangSmith for AI observability."""
        if not LANGSMITH_AVAILABLE:
            return
        
        try:
            langsmith_api_key = os.getenv('LANGSMITH_API_KEY')
            if langsmith_api_key:
                self.langsmith_client = Client(api_key=langsmith_api_key)
                print("✅ LangSmith initialized successfully")
                print("🔗 View traces at: https://smith.langchain.com/")
            else:
                print("⚠️ LANGSMITH_API_KEY not set - LangSmith disabled")
                print("💡 Get free API key at: https://smith.langchain.com/")
                
        except Exception as e:
            print(f"⚠️ LangSmith setup failed: {e}")
    
    def start_request(self, request_id: str, repo_url: str, prompt: str):
        """Start tracking a new request."""
        self.request_id = request_id
        self.thinking_logs = []
        self.performance_metrics = {}
        self.request_start_time = time.time()
        
        print(f"🚀 Starting request {request_id}")
        print(f"📁 Repository: {repo_url}")
        print(f"💭 Prompt: {prompt}")
        
        # Create LangSmith run tree
        if self.langsmith_client:
            try:
                self.run_tree = RunTree(
                    name="tiny-backspace-request",
                    run_type="chain",
                    inputs={
                        "repo_url": repo_url,
                        "prompt": prompt,
                        "request_id": request_id
                    },
                    client=self.langsmith_client
                )
                self.run_tree.post()
                print("✅ LangSmith trace started")
            except Exception as e:
                print(f"⚠️ Failed to start LangSmith trace: {e}")
    
    def end_request(self, success: bool, result: Optional[Dict[str, Any]] = None):
        """End request tracking."""
        duration_ms = (time.time() - self.request_start_time) * 1000 if self.request_start_time else 0
        
        print(f"🏁 Request {self.request_id} completed: {'✅ SUCCESS' if success else '❌ FAILED'}")
        print(f"⏱️  Duration: {duration_ms:.2f}ms")
        print(f"🤔 Thinking steps: {len(self.thinking_logs)}")
        
        # End LangSmith run
        if self.run_tree:
            try:
                self.run_tree.end(
                    outputs=result or {},
                    error=None if success else "Request failed"
                )
                print("✅ LangSmith trace completed")
                if success and result:
                    print(f"🔗 View trace: https://smith.langchain.com/")
            except Exception as e:
                print(f"⚠️ Failed to end LangSmith trace: {e}")
    
    def log_agent_thinking(self, step: str, thought: str, data: Optional[Dict[str, Any]] = None):
        """Log AI agent thinking process."""
        thinking_entry = {
            "timestamp": time.time(),
            "step": step,
            "thought": thought,
            "data": data or {},
            "request_id": self.request_id
        }
        
        self.thinking_logs.append(thinking_entry)
        
        # Log to LangSmith
        if self.run_tree:
            try:
                # Use the correct method for logging to RunTree
                self.run_tree.add_child(
                    name=f"thinking-{step}",
                    run_type="tool",
                    inputs={
                        "step": step,
                        "thought": thought,
                        "data": data
                    }
                )
            except Exception as e:
                print(f"⚠️ Failed to log to LangSmith: {e}")
        
        # Console output with emojis
        emoji_map = {
            "initialization": "🚀",
            "validation": "✅",
            "analysis": "🔍",
            "ai_processing": "🤖",
            "ai_provider_selection": "🎯",
            "claude": "🧠",
            "openai": "⚡",
            "fallback": "🔄",
            "github": "📝",
            "pr_creation": "🔗",
            "error": "❌",
            "success": "🎉"
        }
        
        emoji = emoji_map.get(step, "💭")
        print(f"{emoji} [{step.upper()}] {thought}")
    
    def log_performance(self, operation: str, duration_ms: float, metadata: Optional[Dict[str, Any]] = None):
        """Log performance metrics."""
        self.performance_metrics[operation] = {
            "duration_ms": duration_ms,
            "metadata": metadata or {},
            "timestamp": time.time()
        }
        
        print(f"⚡ {operation}: {duration_ms:.2f}ms")
    
    @contextmanager
    def performance_timer(self, operation: str, metadata: Optional[Dict[str, Any]] = None):
        """Context manager for timing operations."""
        start_time = time.time()
        try:
            yield
        finally:
            duration_ms = (time.time() - start_time) * 1000
            self.log_performance(operation, duration_ms, metadata)
    
    def get_thinking_summary(self) -> Dict[str, Any]:
        """Get a summary of the agent's thinking process."""
        return {
            "request_id": self.request_id,
            "total_thoughts": len(self.thinking_logs),
            "thinking_steps": [log["step"] for log in self.thinking_logs],
            "performance_metrics": self.performance_metrics,
            "thinking_timeline": [
                {
                    "timestamp": log["timestamp"],
                    "step": log["step"],
                    "thought": log["thought"]
                }
                for log in self.thinking_logs
            ]
        }
    
    def create_telemetry_update(self, type_: str, message: str, step: str = None, progress: int = None, extra_data: dict = None) -> dict:
        """Create a telemetry-rich status update."""
        update = {
            "type": type_,
            "message": message,
            "timestamp": int(time.time() * 1000),
            "request_id": self.request_id,
            "telemetry": {
                "thinking_logs_count": len(self.thinking_logs),
                "performance_metrics_count": len(self.performance_metrics),
                "current_step": step,
                "langsmith_enabled": True  # LangSmith is now enabled in sandbox
            }
        }
        
        if step:
            update["step"] = step
        if progress is not None:
            update["progress"] = progress
        if extra_data:
            update["extra_data"] = extra_data
        
        # Add recent thinking logs if available
        if self.thinking_logs:
            update["telemetry"]["recent_thoughts"] = [
                {
                    "step": log["step"],
                    "thought": log["thought"][:100] + "..." if len(log["thought"]) > 100 else log["thought"]
                }
                for log in self.thinking_logs[-3:]  # Last 3 thoughts
            ]
        
        return update


# Global observability manager
observability = SimpleObservability()


def get_observability_manager() -> SimpleObservability:
    """Get the global observability manager."""
    return observability 