#!/usr/bin/env python3
"""
Real-time Monitoring Dashboard for Tiny Backspace
Provides live insights into system performance, agent behavior, and observability metrics.
"""

import os
import sys
import time
import json
import threading
from datetime import datetime, timedelta
from collections import defaultdict, deque
import argparse
from pathlib import Path

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent / "app"))

from app.utils.log_analyzer import LogAnalyzer
from app.logging_config import get_observability_summary

class RealTimeMonitor:
    """Real-time monitoring dashboard for Tiny Backspace."""
    
    def __init__(self, log_dir: str = "logs", refresh_interval: int = 5):
        self.log_dir = Path(log_dir)
        self.refresh_interval = refresh_interval
        self.analyzer = LogAnalyzer(log_dir)
        
        # Real-time metrics
        self.metrics = {
            "requests_per_minute": deque(maxlen=60),
            "errors_per_minute": deque(maxlen=60),
            "avg_response_time": deque(maxlen=60),
            "ai_provider_usage": defaultdict(int),
            "active_requests": set(),
            "recent_errors": deque(maxlen=10)
        }
        
        self.running = False
        self.last_file_sizes = {}
    
    def start_monitoring(self):
        """Start the real-time monitoring dashboard."""
        self.running = True
        print("🚀 Starting Tiny Backspace Real-Time Monitor")
        print("=" * 60)
        
        # Start background monitoring thread
        monitor_thread = threading.Thread(target=self._monitor_logs, daemon=True)
        monitor_thread.start()
        
        try:
            while self.running:
                self._clear_screen()
                self._display_dashboard()
                time.sleep(self.refresh_interval)
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
            self.running = False
    
    def _monitor_logs(self):
        """Background thread to monitor log files for changes."""
        while self.running:
            self._update_metrics()
            time.sleep(1)  # Check every second
    
    def _update_metrics(self):
        """Update real-time metrics from log files."""
        current_time = datetime.now()
        
        # Monitor app.log for new requests
        app_log = self.log_dir / "app.log"
        if app_log.exists():
            current_size = app_log.stat().st_size
            if current_size != self.last_file_sizes.get("app.log", 0):
                self._parse_new_app_logs(current_time)
                self.last_file_sizes["app.log"] = current_size
        
        # Monitor errors.log for new errors
        errors_log = self.log_dir / "errors.log"
        if errors_log.exists():
            current_size = errors_log.stat().st_size
            if current_size != self.last_file_sizes.get("errors.log", 0):
                self._parse_new_error_logs(current_time)
                self.last_file_sizes["errors.log"] = current_size
        
        # Monitor performance.log for performance metrics
        perf_log = self.log_dir / "performance.log"
        if perf_log.exists():
            current_size = perf_log.stat().st_size
            if current_size != self.last_file_sizes.get("performance.log", 0):
                self._parse_new_performance_logs(current_time)
                self.last_file_sizes["performance.log"] = current_size
    
    def _parse_new_app_logs(self, current_time: datetime):
        """Parse new entries from app.log."""
        app_log = self.log_dir / "app.log"
        try:
            with open(app_log, 'r') as f:
                lines = f.readlines()
                for line in lines[-10:]:  # Check last 10 lines
                    if "Starting code processing request" in line:
                        # Extract request ID
                        if "REQ:" in line:
                            request_id = line.split("REQ:")[1].split()[0]
                            self.metrics["active_requests"].add(request_id)
                            self.metrics["requests_per_minute"].append(current_time)
                    elif "Code processing completed" in line:
                        # Remove from active requests
                        if "REQ:" in line:
                            request_id = line.split("REQ:")[1].split()[0]
                            self.metrics["active_requests"].discard(request_id)
        except Exception as e:
            pass
    
    def _parse_new_error_logs(self, current_time: datetime):
        """Parse new entries from errors.log."""
        errors_log = self.log_dir / "errors.log"
        try:
            with open(errors_log, 'r') as f:
                lines = f.readlines()
                for line in lines[-5:]:  # Check last 5 lines
                    if "ERROR" in line:
                        self.metrics["errors_per_minute"].append(current_time)
                        self.metrics["recent_errors"].append({
                            "timestamp": current_time,
                            "error": line.strip()
                        })
        except Exception as e:
            pass
    
    def _parse_new_performance_logs(self, current_time: datetime):
        """Parse new entries from performance.log."""
        perf_log = self.log_dir / "performance.log"
        try:
            with open(perf_log, 'r') as f:
                lines = f.readlines()
                for line in lines[-5:]:  # Check last 5 lines
                    if "PERFORMANCE" in line:
                        # Extract response time
                        import re
                        match = re.search(r'(\d+\.?\d*)ms', line)
                        if match:
                            response_time = float(match.group(1))
                            self.metrics["avg_response_time"].append(response_time)
        except Exception as e:
            pass
    
    def _clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _display_dashboard(self):
        """Display the real-time dashboard."""
        current_time = datetime.now()
        
        print("🏥 TINY BACKSPACE REAL-TIME MONITOR")
        print("=" * 60)
        print(f"🕐 Last Updated: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔄 Refresh Interval: {self.refresh_interval}s")
        print()
        
        # System Status
        self._display_system_status()
        print()
        
        # Real-time Metrics
        self._display_realtime_metrics()
        print()
        
        # Active Requests
        self._display_active_requests()
        print()
        
        # Recent Errors
        self._display_recent_errors()
        print()
        
        # Health Summary
        self._display_health_summary()
        print()
        
        print("=" * 60)
        print("Press Ctrl+C to stop monitoring")
    
    def _display_system_status(self):
        """Display system status."""
        print("📊 SYSTEM STATUS")
        print("-" * 30)
        
        # Check if logs directory exists
        if self.log_dir.exists():
            print("✅ Logs directory: Active")
            
            # Check log files
            log_files = ["app.log", "errors.log", "performance.log", "agent_thinking.log"]
            for log_file in log_files:
                file_path = self.log_dir / log_file
                if file_path.exists():
                    size = file_path.stat().st_size
                    print(f"✅ {log_file}: {size:,} bytes")
                else:
                    print(f"❌ {log_file}: Not found")
        else:
            print("❌ Logs directory: Not found")
    
    def _display_realtime_metrics(self):
        """Display real-time metrics."""
        print("📈 REAL-TIME METRICS (Last 60 seconds)")
        print("-" * 40)
        
        # Requests per minute
        current_time = datetime.now()
        recent_requests = [t for t in self.metrics["requests_per_minute"] 
                          if (current_time - t).seconds <= 60]
        requests_per_min = len(recent_requests)
        print(f"🚀 Requests/min: {requests_per_min}")
        
        # Errors per minute
        recent_errors = [t for t in self.metrics["errors_per_minute"] 
                        if (current_time - t).seconds <= 60]
        errors_per_min = len(recent_errors)
        print(f"❌ Errors/min: {errors_per_min}")
        
        # Average response time
        if self.metrics["avg_response_time"]:
            recent_times = list(self.metrics["avg_response_time"])[-10:]  # Last 10
            avg_time = sum(recent_times) / len(recent_times)
            print(f"⏱️ Avg Response Time: {avg_time:.1f}ms")
        else:
            print("⏱️ Avg Response Time: N/A")
        
        # Active requests
        active_count = len(self.metrics["active_requests"])
        print(f"🔄 Active Requests: {active_count}")
    
    def _display_active_requests(self):
        """Display currently active requests."""
        print("🔄 ACTIVE REQUESTS")
        print("-" * 30)
        
        if self.metrics["active_requests"]:
            for i, request_id in enumerate(list(self.metrics["active_requests"])[:5], 1):
                print(f"{i}. Request ID: {request_id}")
            if len(self.metrics["active_requests"]) > 5:
                print(f"... and {len(self.metrics['active_requests']) - 5} more")
        else:
            print("No active requests")
    
    def _display_recent_errors(self):
        """Display recent errors."""
        print("❌ RECENT ERRORS")
        print("-" * 30)
        
        if self.metrics["recent_errors"]:
            for i, error in enumerate(list(self.metrics["recent_errors"])[-3:], 1):
                timestamp = error["timestamp"].strftime("%H:%M:%S")
                error_msg = error["error"][:50] + "..." if len(error["error"]) > 50 else error["error"]
                print(f"{i}. [{timestamp}] {error_msg}")
        else:
            print("No recent errors")
    
    def _display_health_summary(self):
        """Display health summary."""
        print("🏥 HEALTH SUMMARY")
        print("-" * 30)
        
        try:
            # Generate health report for last hour
            report = self.analyzer.generate_health_report(hours=1)
            
            print(f"📊 Health Score: {report['health_score']}/100 - {report['status']}")
            print(f"📈 Total Requests (1h): {report['performance_summary']['total_requests']}")
            print(f"❌ Error Rate: {report['error_summary']['error_rate']}%")
            
            # AI Provider distribution
            ai_dist = report['agent_summary']['ai_provider_distribution']
            if ai_dist:
                print("🤖 AI Provider Usage:")
                for provider, count in ai_dist.items():
                    print(f"  {provider.title()}: {count}")
            
        except Exception as e:
            print(f"⚠️ Unable to generate health report: {str(e)}")

def main():
    """Main entry point for the monitoring dashboard."""
    parser = argparse.ArgumentParser(description="Tiny Backspace Real-Time Monitor")
    parser.add_argument("--log-dir", default="logs", help="Directory containing log files")
    parser.add_argument("--refresh", type=int, default=5, help="Refresh interval in seconds")
    parser.add_argument("--health-report", action="store_true", help="Generate one-time health report and exit")
    
    args = parser.parse_args()
    
    if args.health_report:
        # Generate one-time health report
        analyzer = LogAnalyzer(args.log_dir)
        from app.utils.log_analyzer import print_health_report
        print_health_report()
        return
    
    # Start real-time monitoring
    monitor = RealTimeMonitor(args.log_dir, args.refresh)
    monitor.start_monitoring()

if __name__ == "__main__":
    main() 