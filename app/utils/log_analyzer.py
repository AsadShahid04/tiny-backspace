"""
Log Analysis and Monitoring Tool for Tiny Backspace.
Provides comprehensive analysis of structured logs for observability insights.
"""

import json
import re
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter
import statistics
from pathlib import Path

class LogAnalyzer:
    """Comprehensive log analysis tool for observability insights."""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_files = {
            "app": self.log_dir / "app.log",
            "errors": self.log_dir / "errors.log",
            "performance": self.log_dir / "performance.log",
            "agent_thinking": self.log_dir / "agent_thinking.log"
        }
    
    def analyze_performance_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """Analyze performance metrics from logs."""
        since_time = datetime.now() - timedelta(hours=hours)
        
        performance_data = {
            "total_requests": 0,
            "average_response_time": 0,
            "operation_breakdown": defaultdict(list),
            "slowest_operations": [],
            "error_rate": 0,
            "ai_provider_usage": Counter(),
            "sandbox_metrics": defaultdict(list)
        }
        
        # Parse performance logs
        if self.log_files["performance"].exists():
            with open(self.log_files["performance"], 'r') as f:
                for line in f:
                    if self._is_recent_line(line, since_time):
                        self._parse_performance_line(line, performance_data)
        
        # Calculate statistics
        if performance_data["operation_breakdown"]:
            for operation, times in performance_data["operation_breakdown"].items():
                if times:
                    performance_data["operation_breakdown"][operation] = {
                        "count": len(times),
                        "avg_time": statistics.mean(times),
                        "min_time": min(times),
                        "max_time": max(times),
                        "p95_time": statistics.quantiles(times, n=20)[18] if len(times) >= 20 else max(times)
                    }
        
        return performance_data
    
    def analyze_agent_thinking(self, hours: int = 24) -> Dict[str, Any]:
        """Analyze agent thinking patterns and decision making."""
        since_time = datetime.now() - timedelta(hours=hours)
        
        thinking_data = {
            "total_requests": 0,
            "thinking_steps_per_request": [],
            "ai_provider_selections": Counter(),
            "common_operations": Counter(),
            "error_patterns": Counter(),
            "thinking_flow": defaultdict(int)
        }
        
        if self.log_files["agent_thinking"].exists():
            with open(self.log_files["agent_thinking"], 'r') as f:
                current_request = None
                request_steps = []
                
                for line in f:
                    if self._is_recent_line(line, since_time):
                        parsed = self._parse_thinking_line(line)
                        if parsed:
                            request_id = parsed.get("request_id")
                            
                            if request_id != current_request:
                                if current_request and request_steps:
                                    thinking_data["thinking_steps_per_request"].append(len(request_steps))
                                    thinking_data["thinking_flow"][tuple(request_steps)] += 1
                                
                                current_request = request_id
                                request_steps = []
                                thinking_data["total_requests"] += 1
                            
                            if request_steps:
                                request_steps.append(parsed.get("step", "unknown"))
                            
                            thinking_data["common_operations"][parsed.get("step", "unknown")] += 1
                            
                            # Track AI provider selections
                            if "claude" in parsed.get("thought", "").lower():
                                thinking_data["ai_provider_selections"]["claude"] += 1
                            elif "openai" in parsed.get("thought", "").lower():
                                thinking_data["ai_provider_selections"]["openai"] += 1
                            elif "dummy" in parsed.get("thought", "").lower():
                                thinking_data["ai_provider_selections"]["dummy"] += 1
                
                # Don't forget the last request
                if current_request and request_steps:
                    thinking_data["thinking_steps_per_request"].append(len(request_steps))
                    thinking_data["thinking_flow"][tuple(request_steps)] += 1
        
        # Calculate statistics
        if thinking_data["thinking_steps_per_request"]:
            thinking_data["avg_thinking_steps"] = statistics.mean(thinking_data["thinking_steps_per_request"])
            thinking_data["max_thinking_steps"] = max(thinking_data["thinking_steps_per_request"])
            thinking_data["min_thinking_steps"] = min(thinking_data["thinking_steps_per_request"])
        
        return thinking_data
    
    def analyze_errors(self, hours: int = 24) -> Dict[str, Any]:
        """Analyze error patterns and frequency."""
        since_time = datetime.now() - timedelta(hours=hours)
        
        error_data = {
            "total_errors": 0,
            "error_types": Counter(),
            "error_frequency": Counter(),
            "request_error_rate": 0,
            "common_error_contexts": Counter(),
            "error_timeline": []
        }
        
        if self.log_files["errors"].exists():
            with open(self.log_files["errors"], 'r') as f:
                for line in f:
                    if self._is_recent_line(line, since_time):
                        parsed = self._parse_error_line(line)
                        if parsed:
                            error_data["total_errors"] += 1
                            error_data["error_types"][parsed.get("error_type", "unknown")] += 1
                            error_data["error_frequency"][parsed.get("operation", "unknown")] += 1
                            
                            # Extract context information
                            context = parsed.get("context", {})
                            if context:
                                error_data["common_error_contexts"][str(context.get("operation", "unknown"))] += 1
                            
                            error_data["error_timeline"].append({
                                "timestamp": parsed.get("timestamp"),
                                "error_type": parsed.get("error_type"),
                                "operation": parsed.get("operation")
                            })
        
        return error_data
    
    def generate_health_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive health report."""
        performance = self.analyze_performance_metrics(hours)
        thinking = self.analyze_agent_thinking(hours)
        errors = self.analyze_errors(hours)
        
        # Calculate health score
        health_score = 100
        
        # Deduct points for errors
        if performance["total_requests"] > 0:
            error_rate = errors["total_errors"] / performance["total_requests"]
            health_score -= min(error_rate * 100, 50)  # Max 50 points deduction for errors
        
        # Deduct points for slow performance
        if performance["operation_breakdown"]:
            avg_response_time = performance.get("average_response_time", 0)
            if avg_response_time > 30000:  # 30 seconds
                health_score -= min((avg_response_time - 30000) / 1000, 30)  # Max 30 points deduction
        
        # Deduct points for high dummy agent usage
        total_ai_usage = sum(thinking["ai_provider_selections"].values())
        if total_ai_usage > 0:
            dummy_usage_rate = thinking["ai_provider_selections"]["dummy"] / total_ai_usage
            health_score -= dummy_usage_rate * 20  # Max 20 points deduction
        
        health_score = max(health_score, 0)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "analysis_period_hours": hours,
            "health_score": round(health_score, 2),
            "status": self._get_health_status(health_score),
            "performance_summary": {
                "total_requests": performance["total_requests"],
                "avg_response_time_ms": round(performance.get("average_response_time", 0), 2),
                "slowest_operation": max(performance["operation_breakdown"].items(), 
                                       key=lambda x: x[1].get("avg_time", 0))[0] if performance["operation_breakdown"] else "N/A"
            },
            "agent_summary": {
                "total_requests": thinking["total_requests"],
                "avg_thinking_steps": round(thinking.get("avg_thinking_steps", 0), 2),
                "ai_provider_distribution": dict(thinking["ai_provider_selections"])
            },
            "error_summary": {
                "total_errors": errors["total_errors"],
                "error_rate": round(errors["total_errors"] / max(performance["total_requests"], 1) * 100, 2),
                "most_common_error": errors["error_types"].most_common(1)[0] if errors["error_types"] else ("N/A", 0)
            },
            "recommendations": self._generate_recommendations(performance, thinking, errors)
        }
    
    def _is_recent_line(self, line: str, since_time: datetime) -> bool:
        """Check if log line is from recent time period."""
        try:
            timestamp_str = line.split(" | ")[0]
            timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            return timestamp >= since_time
        except:
            return False
    
    def _parse_performance_line(self, line: str, data: Dict[str, Any]):
        """Parse performance log line."""
        try:
            # Extract duration from performance line
            match = re.search(r'PERFORMANCE \[([^\]]+)\]: ([\d.]+)ms', line)
            if match:
                operation = match.group(1)
                duration = float(match.group(2))
                data["operation_breakdown"][operation].append(duration)
        except:
            pass
    
    def _parse_thinking_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse agent thinking log line."""
        try:
            parts = line.split(" | ")
            if len(parts) >= 4:
                timestamp = parts[0]
                request_id = parts[2].split("REQ:")[1] if "REQ:" in parts[2] else "unknown"
                thought = parts[3].replace("🤖 AGENT THINKING [", "").replace("]: ", " | ")
                
                step_match = re.search(r'\[([^\]]+)\]', thought)
                step = step_match.group(1) if step_match else "unknown"
                
                return {
                    "timestamp": timestamp,
                    "request_id": request_id,
                    "step": step,
                    "thought": thought
                }
        except:
            pass
        return None
    
    def _parse_error_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse error log line."""
        try:
            parts = line.split(" | ")
            if len(parts) >= 4:
                timestamp = parts[0]
                error_info = parts[3]
                
                error_match = re.search(r'ERROR \[([^\]]+)\]: (.+)', error_info)
                if error_match:
                    error_type = error_match.group(1)
                    error_message = error_match.group(2)
                    
                    # Try to extract operation from context
                    operation = "unknown"
                    if "operation" in error_message.lower():
                        op_match = re.search(r'operation["\']?\s*:\s*["\']([^"\']+)["\']', error_message)
                        if op_match:
                            operation = op_match.group(1)
                    
                    return {
                        "timestamp": timestamp,
                        "error_type": error_type,
                        "error_message": error_message,
                        "operation": operation
                    }
        except:
            pass
        return None
    
    def _get_health_status(self, score: float) -> str:
        """Get health status based on score."""
        if score >= 90:
            return "🟢 Excellent"
        elif score >= 75:
            return "🟡 Good"
        elif score >= 60:
            return "🟠 Fair"
        else:
            return "🔴 Poor"
    
    def _generate_recommendations(self, performance: Dict, thinking: Dict, errors: Dict) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        # Performance recommendations
        if performance["operation_breakdown"]:
            slowest_op = max(performance["operation_breakdown"].items(), 
                           key=lambda x: x[1].get("avg_time", 0))
            if slowest_op[1].get("avg_time", 0) > 10000:  # 10 seconds
                recommendations.append(f"Optimize {slowest_op[0]} operation (avg: {slowest_op[1]['avg_time']:.0f}ms)")
        
        # Error recommendations
        if errors["total_errors"] > 0:
            most_common_error = errors["error_types"].most_common(1)[0]
            recommendations.append(f"Address {most_common_error[0]} errors (occurred {most_common_error[1]} times)")
        
        # AI provider recommendations
        total_ai_usage = sum(thinking["ai_provider_selections"].values())
        if total_ai_usage > 0:
            dummy_usage_rate = thinking["ai_provider_selections"]["dummy"] / total_ai_usage
            if dummy_usage_rate > 0.1:  # More than 10% dummy usage
                recommendations.append(f"Investigate AI provider failures (dummy usage: {dummy_usage_rate:.1%})")
        
        if not recommendations:
            recommendations.append("System is performing well - no immediate actions needed")
        
        return recommendations

def print_health_report(hours: int = 24):
    """Print a formatted health report."""
    analyzer = LogAnalyzer()
    report = analyzer.generate_health_report(hours)
    
    print("=" * 60)
    print("🏥 TINY BACKSPACE HEALTH REPORT")
    print("=" * 60)
    print(f"📊 Health Score: {report['health_score']}/100 - {report['status']}")
    print(f"⏰ Analysis Period: Last {hours} hours")
    print(f"🕐 Generated: {report['timestamp']}")
    print()
    
    print("📈 PERFORMANCE SUMMARY")
    print("-" * 30)
    print(f"Total Requests: {report['performance_summary']['total_requests']}")
    print(f"Avg Response Time: {report['performance_summary']['avg_response_time_ms']}ms")
    print(f"Slowest Operation: {report['performance_summary']['slowest_operation']}")
    print()
    
    print("🤖 AGENT SUMMARY")
    print("-" * 30)
    print(f"Total Requests: {report['agent_summary']['total_requests']}")
    print(f"Avg Thinking Steps: {report['agent_summary']['avg_thinking_steps']}")
    print("AI Provider Distribution:")
    for provider, count in report['agent_summary']['ai_provider_distribution'].items():
        print(f"  {provider.title()}: {count}")
    print()
    
    print("❌ ERROR SUMMARY")
    print("-" * 30)
    print(f"Total Errors: {report['error_summary']['total_errors']}")
    print(f"Error Rate: {report['error_summary']['error_rate']}%")
    print(f"Most Common Error: {report['error_summary']['most_common_error'][0]} ({report['error_summary']['most_common_error'][1]} times)")
    print()
    
    print("💡 RECOMMENDATIONS")
    print("-" * 30)
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"{i}. {rec}")
    print()
    print("=" * 60)

if __name__ == "__main__":
    print_health_report() 