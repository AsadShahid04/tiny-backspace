"""
Real-time telemetry and observability for Tiny Backspace API.
Integrates OpenTelemetry and LangSmith for comprehensive agent thinking tracking.
"""

import os
import time
import json
import uuid
from typing import Dict, Any, Optional, List
from contextlib import contextmanager
import asyncio

# OpenTelemetry imports
try:
    from opentelemetry import trace, metrics
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False
    print("OpenTelemetry not available - telemetry will be limited")

# LangSmith imports
try:
    from langsmith import Client
    from langsmith.run_trees import RunTree
    LANGSMITH_AVAILABLE = True
except ImportError:
    LANGSMITH_AVAILABLE = False
    print("LangSmith not available - AI observability will be limited")

# Add dashboard integration
from api.telemetry_dashboard import add_thinking_log, add_performance_metric, update_system_stats

class ObservabilityManager:
    """Manages real-time telemetry and observability for the API."""
    
    def __init__(self):
        self.request_id = None
        self.tracer = None
        self.meter = None
        self.langsmith_client = None
        self.run_tree = None
        self.thinking_logs = []
        self.performance_metrics = {}
        self.request_start_time = None
        
        self._setup_opentelemetry()
        self._setup_langsmith()
    
    def _setup_opentelemetry(self):
        """Initialize OpenTelemetry tracing and metrics."""
        if not OPENTELEMETRY_AVAILABLE:
            return
        
        try:
            # Initialize trace provider
            trace_provider = TracerProvider()
            
            # Add OTLP exporter if endpoint is configured
            otlp_endpoint = os.getenv('OTLP_ENDPOINT')
            if otlp_endpoint:
                otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
                trace_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
            
            # Set the global trace provider
            trace.set_tracer_provider(trace_provider)
            self.tracer = trace.get_tracer("tiny-backspace-api")
            
            # Initialize metrics
            meter_provider = MeterProvider()
            if otlp_endpoint:
                metric_reader = PeriodicExportingMetricReader(
                    OTLPMetricExporter(endpoint=otlp_endpoint)
                )
                meter_provider.add_metric_reader(metric_reader)
            
            metrics.set_meter_provider(meter_provider)
            self.meter = metrics.get_meter("tiny-backspace-api")
            
            # Instrument requests
            RequestsInstrumentor().instrument()
            
            print("✅ OpenTelemetry initialized successfully")
            
        except Exception as e:
            print(f"⚠️ OpenTelemetry setup failed: {e}")
    
    def _setup_langsmith(self):
        """Initialize LangSmith for AI observability."""
        if not LANGSMITH_AVAILABLE:
            return
        
        try:
            langsmith_api_key = os.getenv('LANGSMITH_API_KEY')
            if langsmith_api_key:
                self.langsmith_client = Client(api_key=langsmith_api_key)
                print("✅ LangSmith initialized successfully")
            else:
                print("⚠️ LANGSMITH_API_KEY not set - LangSmith disabled")
                
        except Exception as e:
            print(f"⚠️ LangSmith setup failed: {e}")
    
    def start_request(self, request_id: str, repo_url: str, prompt: str):
        """Start tracking a new request."""
        self.request_id = request_id
        self.thinking_logs = []
        self.performance_metrics = {}
        self.request_start_time = time.time()
        
        # Create LangSmith run tree
        if self.langsmith_client:
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
        
        # Create OpenTelemetry span
        if self.tracer:
            self.current_span = self.tracer.start_span(
                "process_code_request",
                attributes={
                    "request_id": request_id,
                    "repo_url": repo_url,
                    "prompt_length": len(prompt)
                }
            )
    
    def end_request(self, success: bool, result: Optional[Dict[str, Any]] = None):
        """End request tracking."""
        # Calculate request duration
        duration_ms = (time.time() - self.request_start_time) * 1000 if self.request_start_time else 0
        
        # End LangSmith run
        if self.run_tree:
            self.run_tree.end(
                outputs=result or {},
                error=None if success else "Request failed"
            )
        
        # End OpenTelemetry span
        if hasattr(self, 'current_span'):
            self.current_span.set_attribute("success", success)
            self.current_span.set_attribute("duration_ms", duration_ms)
            if result:
                self.current_span.set_attribute("pr_url", result.get('pr_url', ''))
                self.current_span.set_attribute("edits_count", result.get('edits_count', 0))
            self.current_span.end()
        
        # Update dashboard stats
        try:
            # This would need to be implemented with proper stats tracking
            # For now, we'll just log the completion
            print(f"📊 Request {self.request_id} completed: {'SUCCESS' if success else 'FAILED'} in {duration_ms:.2f}ms")
        except Exception as e:
            print(f"⚠️ Failed to update dashboard stats: {e}")
    
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
        
        # Log to dashboard
        try:
            add_thinking_log(self.request_id, step, thought, data)
        except Exception as e:
            print(f"⚠️ Failed to add thinking log to dashboard: {e}")
        
        # Log to OpenTelemetry
        if self.tracer:
            with self.tracer.start_span(
                f"agent_thinking_{step}",
                attributes={
                    "request_id": self.request_id,
                    "thinking_step": step,
                    "thought": thought
                }
            ):
                pass
        
        # Log to LangSmith
        if self.run_tree:
            self.run_tree.log({
                "step": step,
                "thought": thought,
                "data": data
            })
        
        print(f"🤖 AGENT THINKING [{step}]: {thought}")
    
    def log_performance(self, operation: str, duration_ms: float, metadata: Optional[Dict[str, Any]] = None):
        """Log performance metrics."""
        self.performance_metrics[operation] = {
            "duration_ms": duration_ms,
            "metadata": metadata or {},
            "timestamp": time.time()
        }
        
        # Log to dashboard
        try:
            add_performance_metric(operation, duration_ms, metadata)
        except Exception as e:
            print(f"⚠️ Failed to add performance metric to dashboard: {e}")
        
        # Record OpenTelemetry metric
        if self.meter:
            duration_counter = self.meter.create_histogram(
                f"{operation}_duration_ms",
                description=f"Duration of {operation} operation"
            )
            duration_counter.record(duration_ms, metadata or {})
        
        print(f"⚡ PERFORMANCE [{operation}]: {duration_ms:.2f}ms")
    
    def log_file_edit(self, file_path: str, content_length: int, description: str):
        """Log file modification."""
        if self.tracer:
            with self.tracer.start_span(
                "file_edit",
                attributes={
                    "request_id": self.request_id,
                    "file_path": file_path,
                    "content_length": content_length,
                    "description": description
                }
            ):
                pass
        
        self.log_agent_thinking(
            "file_modification",
            f"Modified {file_path} ({content_length} chars): {description}",
            {
                "file_path": file_path,
                "content_length": content_length,
                "description": description
            }
        )
    
    def log_github_operation(self, operation: str, command: str, output: str):
        """Log GitHub operation."""
        if self.tracer:
            with self.tracer.start_span(
                f"github_{operation}",
                attributes={
                    "request_id": self.request_id,
                    "command": command,
                    "output": output
                }
            ):
                pass
        
        self.log_agent_thinking(
            "github_operation",
            f"GitHub {operation}: {command}",
            {
                "operation": operation,
                "command": command,
                "output": output
            }
        )
    
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
                "current_step": step
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
observability = ObservabilityManager()


def get_observability_manager() -> ObservabilityManager:
    """Get the global observability manager."""
    return observability 