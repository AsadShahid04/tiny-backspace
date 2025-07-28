"""
Enhanced logging configuration for Tiny Backspace with comprehensive observability.
Includes structured logging, performance metrics, and real-time agent thinking.
"""

import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import contextmanager
from loguru import logger
import threading
from collections import defaultdict
import traceback

# Global performance tracking
performance_metrics = defaultdict(list)
current_request_id = threading.local()

class ObservabilityLogger:
    """Enhanced logger with observability features."""
    
    def __init__(self):
        self.request_id = None
        self.agent_thinking_log = []
        self.performance_start = None
        
    def set_request_id(self, request_id: str):
        """Set request ID for correlation across logs."""
        self.request_id = request_id
        current_request_id.value = request_id
        
    def log_agent_thinking(self, step: str, thought: str, data: Optional[Dict[str, Any]] = None):
        """Log agent thinking process in real-time."""
        thinking_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": self.request_id,
            "step": step,
            "thought": thought,
            "data": data or {},
            "type": "agent_thinking"
        }
        
        self.agent_thinking_log.append(thinking_entry)
        
        # Log to console with special formatting - bind request_id properly
        logger.bind(request_id=self.request_id or "N/A").info(f"🤖 AGENT THINKING [{step}]: {thought}")
        if data:
            logger.bind(request_id=self.request_id or "N/A").debug(f"📊 Agent Data: {json.dumps(data, indent=2)}")
    
    def log_performance(self, operation: str, duration_ms: float, metadata: Optional[Dict[str, Any]] = None):
        """Log performance metrics."""
        metric = {
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": self.request_id,
            "operation": operation,
            "duration_ms": duration_ms,
            "metadata": metadata or {}
        }
        
        performance_metrics[operation].append(metric)
        logger.bind(request_id=self.request_id or "N/A").info(f"⏱️ PERFORMANCE [{operation}]: {duration_ms:.2f}ms")
    
    @contextmanager
    def performance_timer(self, operation: str, metadata: Optional[Dict[str, Any]] = None):
        """Context manager for timing operations."""
        start_time = time.time()
        try:
            yield
        finally:
            duration_ms = (time.time() - start_time) * 1000
            self.log_performance(operation, duration_ms, metadata)
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Log errors with full context and stack trace."""
        error_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": self.request_id,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "stack_trace": traceback.format_exc(),
            "context": context or {},
            "type": "error"
        }
        
        logger.bind(request_id=self.request_id or "N/A").error(f"❌ ERROR [{error_entry['error_type']}]: {error_entry['error_message']}")
        logger.bind(request_id=self.request_id or "N/A").debug(f"🔍 Error Context: {json.dumps(error_entry, indent=2)}")
    
    def get_agent_thinking_summary(self) -> Dict[str, Any]:
        """Get summary of agent thinking for this request."""
        return {
            "request_id": self.request_id,
            "thinking_steps": len(self.agent_thinking_log),
            "thinking_log": self.agent_thinking_log,
            "performance_summary": self.get_performance_summary()
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for this request."""
        if not self.request_id:
            return {}
            
        request_metrics = []
        for operation, metrics in performance_metrics.items():
            request_metrics.extend([m for m in metrics if m.get("request_id") == self.request_id])
        
        if not request_metrics:
            return {}
            
        total_duration = sum(m["duration_ms"] for m in request_metrics)
        avg_duration = total_duration / len(request_metrics)
        
        return {
            "total_operations": len(request_metrics),
            "total_duration_ms": total_duration,
            "average_duration_ms": avg_duration,
            "operations": request_metrics
        }

# Global observability logger instance
observability_logger = ObservabilityLogger()

def setup_logging():
    """Setup enhanced logging with observability features."""
    
    # Remove default handler
    logger.remove()
    
    # Add structured console logging
    logger.add(
        sys.stdout,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <yellow>REQ:{extra[request_id]:<8}</yellow> | <level>{message}</level>",
        filter=lambda record: record["extra"].get("request_id", "N/A") != "N/A"
    )
    
    # Add detailed debug logging to file
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    logger.add(
        f"{log_dir}/app.log",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | REQ:{extra[request_id]:<8} | {message}",
        rotation="10 MB",
        retention="30 days",
        compression="zip"
    )
    
    # Add error logging to separate file
    logger.add(
        f"{log_dir}/errors.log",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | REQ:{extra[request_id]:<8} | {message}",
        rotation="5 MB",
        retention="90 days",
        compression="zip"
    )
    
    # Add performance metrics logging
    logger.add(
        f"{log_dir}/performance.log",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | PERFORMANCE | REQ:{extra[request_id]:<8} | {message}",
        filter=lambda record: "PERFORMANCE" in record["message"],
        rotation="10 MB",
        retention="30 days",
        compression="zip"
    )
    
    # Add agent thinking logs
    logger.add(
        f"{log_dir}/agent_thinking.log",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | AGENT_THINKING | REQ:{extra[request_id]:<8} | {message}",
        filter=lambda record: "AGENT THINKING" in record["message"],
        rotation="10 MB",
        retention="30 days",
        compression="zip"
    )
    
    logger.info("🚀 Enhanced logging system initialized with observability features")

def get_request_id() -> str:
    """Get current request ID for correlation."""
    return getattr(current_request_id, 'value', 'N/A')

def log_with_request_id(level: str, message: str, extra_data: Optional[Dict[str, Any]] = None, **kwargs):
    """Log message with request ID correlation."""
    request_id = get_request_id()
    logger.bind(request_id=request_id).log(level, message, **kwargs)

def log_agent_operation(operation: str, details: str, data: Optional[Dict[str, Any]] = None):
    """Log agent operations with observability."""
    observability_logger.log_agent_thinking(operation, details, data)
    log_with_request_id("INFO", f"Agent {operation}: {details}")

def log_performance_metric(operation: str, duration_ms: float, metadata: Optional[Dict[str, Any]] = None):
    """Log performance metrics."""
    observability_logger.log_performance(operation, duration_ms, metadata)

def log_error_with_context(error: Exception, context: Optional[Dict[str, Any]] = None):
    """Log errors with full context."""
    observability_logger.log_error(error, context)

@contextmanager
def performance_timer(operation: str, metadata: Optional[Dict[str, Any]] = None):
    """Context manager for timing operations."""
    with observability_logger.performance_timer(operation, metadata):
        yield

def get_observability_summary() -> Dict[str, Any]:
    """Get comprehensive observability summary."""
    return observability_logger.get_agent_thinking_summary()

# Initialize logging
setup_logging() 