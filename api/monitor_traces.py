#!/usr/bin/env python3
"""
LangSmith Trace Monitor
Real-time monitoring and debugging of LangSmith traces
"""

import asyncio
import time
import json
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dotenv import load_dotenv
import langsmith
from langsmith import Client
import requests

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TraceMonitor:
    def __init__(self):
        self.api_key = os.getenv("LANGSMITH_API_KEY")
        self.project = os.getenv("LANGSMITH_PROJECT", "tiny-backspace")
        self.endpoint = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
        
        if not self.api_key:
            raise ValueError("LANGSMITH_API_KEY is required")
        
        self.client = Client(
            api_key=self.api_key,
            api_url=self.endpoint
        )
        
        self.last_check_time = datetime.now() - timedelta(hours=1)
        logger.info(f"🔍 TraceMonitor initialized for project: {self.project}")
    
    def get_recent_runs(self, minutes: int = 60) -> List[Dict[str, Any]]:
        """Get recent runs from LangSmith"""
        try:
            # Calculate time range
            end_time = datetime.now()
            start_time = end_time - timedelta(minutes=minutes)
            
            logger.info(f"🔍 Fetching runs from {start_time} to {end_time}")
            
            # Use the client to list runs
            runs = list(self.client.list_runs(
                project_name=self.project,
                start_time=start_time,
                end_time=end_time,
                limit=50
            ))
            
            logger.info(f"✅ Found {len(runs)} runs in the last {minutes} minutes")
            return runs
            
        except Exception as e:
            logger.error(f"❌ Error fetching runs: {e}")
            return []
    
    def analyze_run(self, run) -> Dict[str, Any]:
        """Analyze a single run for debugging info"""
        try:
            analysis = {
                "id": str(run.id),
                "name": run.name,
                "run_type": run.run_type,
                "status": "completed" if run.end_time else "running",
                "start_time": run.start_time.isoformat() if run.start_time else None,
                "end_time": run.end_time.isoformat() if run.end_time else None,
                "duration": None,
                "inputs": run.inputs or {},
                "outputs": run.outputs or {},
                "error": run.error,
                "tags": run.tags or [],
                "parent_run_id": str(run.parent_run_id) if run.parent_run_id else None,
                "child_runs": 0
            }
            
            # Calculate duration
            if run.start_time and run.end_time:
                duration = run.end_time - run.start_time
                analysis["duration"] = duration.total_seconds()
            
            # Get child runs count
            try:
                child_runs = list(self.client.list_runs(
                    project_name=self.project,
                    parent_run_id=run.id,
                    limit=100
                ))
                analysis["child_runs"] = len(child_runs)
            except Exception as e:
                logger.warning(f"Could not get child runs for {run.id}: {e}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing run {run.id}: {e}")
            return {"id": str(run.id), "error": str(e)}
    
    def print_run_summary(self, analysis: Dict[str, Any]):
        """Print a formatted summary of a run"""
        status_emoji = "✅" if analysis["status"] == "completed" else "🔄"
        error_emoji = "❌" if analysis.get("error") else ""
        
        print(f"\n{status_emoji} {error_emoji} Run: {analysis['name']}")
        print(f"   ID: {analysis['id']}")
        print(f"   Type: {analysis['run_type']}")
        print(f"   Status: {analysis['status']}")
        
        if analysis.get("duration"):
            print(f"   Duration: {analysis['duration']:.2f}s")
        
        if analysis.get("child_runs", 0) > 0:
            print(f"   Child runs: {analysis['child_runs']}")
        
        if analysis.get("tags"):
            print(f"   Tags: {', '.join(analysis['tags'])}")
        
        if analysis.get("error"):
            print(f"   ❌ Error: {analysis['error']}")
        
        # Show input/output info
        if analysis.get("inputs"):
            input_keys = list(analysis["inputs"].keys())
            print(f"   📥 Inputs: {', '.join(input_keys)}")
        
        if analysis.get("outputs"):
            output_keys = list(analysis["outputs"].keys())
            print(f"   📤 Outputs: {', '.join(output_keys)}")
    
    def get_project_stats(self) -> Dict[str, Any]:
        """Get overall project statistics"""
        try:
            # Get runs from last 24 hours
            runs = self.get_recent_runs(minutes=24*60)
            
            stats = {
                "total_runs": len(runs),
                "completed_runs": 0,
                "failed_runs": 0,
                "running_runs": 0,
                "avg_duration": 0,
                "recent_activity": False,
                "last_run_time": None
            }
            
            durations = []
            recent_threshold = datetime.now() - timedelta(minutes=10)
            
            for run in runs:
                # Count by status
                if run.end_time:
                    if run.error:
                        stats["failed_runs"] += 1
                    else:
                        stats["completed_runs"] += 1
                else:
                    stats["running_runs"] += 1
                
                # Check for recent activity
                if run.start_time and run.start_time > recent_threshold:
                    stats["recent_activity"] = True
                
                # Track last run time
                if run.start_time:
                    if not stats["last_run_time"] or run.start_time > stats["last_run_time"]:
                        stats["last_run_time"] = run.start_time
                
                # Calculate duration
                if run.start_time and run.end_time:
                    duration = (run.end_time - run.start_time).total_seconds()
                    durations.append(duration)
            
            if durations:
                stats["avg_duration"] = sum(durations) / len(durations)
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error getting project stats: {e}")
            return {"error": str(e)}
    
    def print_project_summary(self, stats: Dict[str, Any]):
        """Print project summary"""
        print("\n" + "="*50)
        print(f"📊 PROJECT SUMMARY: {self.project}")
        print("="*50)
        
        if stats.get("error"):
            print(f"❌ Error: {stats['error']}")
            return
        
        print(f"📈 Total runs (24h): {stats['total_runs']}")
        print(f"✅ Completed: {stats['completed_runs']}")
        print(f"❌ Failed: {stats['failed_runs']}")
        print(f"🔄 Running: {stats['running_runs']}")
        
        if stats["avg_duration"] > 0:
            print(f"⏱️ Avg duration: {stats['avg_duration']:.2f}s")
        
        if stats["recent_activity"]:
            print("🟢 Recent activity: YES")
        else:
            print("🔴 Recent activity: NO")
        
        if stats["last_run_time"]:
            time_ago = datetime.now() - stats["last_run_time"]
            if time_ago.total_seconds() < 60:
                print(f"🕐 Last run: {int(time_ago.total_seconds())}s ago")
            elif time_ago.total_seconds() < 3600:
                print(f"🕐 Last run: {int(time_ago.total_seconds()/60)}m ago")
            else:
                print(f"🕐 Last run: {int(time_ago.total_seconds()/3600)}h ago")
        else:
            print("🕐 Last run: Never")
    
    async def monitor_continuously(self, check_interval: int = 30):
        """Monitor traces continuously"""
        logger.info(f"🔄 Starting continuous monitoring (checking every {check_interval}s)")
        
        while True:
            try:
                # Get recent runs
                runs = self.get_recent_runs(minutes=5)  # Check last 5 minutes
                
                # Filter for new runs since last check
                new_runs = []
                for run in runs:
                    if run.start_time and run.start_time > self.last_check_time:
                        new_runs.append(run)
                
                if new_runs:
                    print(f"\n🔔 {len(new_runs)} new runs detected!")
                    for run in new_runs:
                        analysis = self.analyze_run(run)
                        self.print_run_summary(analysis)
                else:
                    print(f"⏳ No new runs (checked at {datetime.now().strftime('%H:%M:%S')})")
                
                self.last_check_time = datetime.now()
                
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
            
            await asyncio.sleep(check_interval)
    
    def run_single_check(self, minutes: int = 60):
        """Run a single check and analysis"""
        print(f"🔍 Checking for runs in the last {minutes} minutes...")
        
        # Get project stats
        stats = self.get_project_stats()
        self.print_project_summary(stats)
        
        # Get recent runs
        runs = self.get_recent_runs(minutes=minutes)
        
        if not runs:
            print(f"\n❌ No runs found in the last {minutes} minutes")
            print("   This might indicate:")
            print("   - Tracing is not working")
            print("   - No applications have been run")
            print("   - Wrong project name")
            return
        
        print(f"\n📋 RECENT RUNS ({len(runs)} found)")
        print("-" * 50)
        
        # Analyze each run
        for run in runs:
            analysis = self.analyze_run(run)
            self.print_run_summary(analysis)
        
        # Save detailed results
        detailed_results = {
            "timestamp": datetime.now().isoformat(),
            "project": self.project,
            "stats": stats,
            "runs": [self.analyze_run(run) for run in runs]
        }
        
        with open("trace_monitor_results.json", "w") as f:
            json.dump(detailed_results, f, indent=2, default=str)
        
        print(f"\n📝 Detailed results saved to: trace_monitor_results.json")

async def main():
    """Main monitoring function"""
    print("="*60)
    print("🔍 LANGSMITH TRACE MONITOR")
    print("="*60)
    
    try:
        monitor = TraceMonitor()
        
        # Ask user for monitoring mode
        print("\nSelect monitoring mode:")
        print("1. Single check (default)")
        print("2. Continuous monitoring")
        
        choice = input("\nEnter choice (1 or 2): ").strip()
        
        if choice == "2":
            print("\n🔄 Starting continuous monitoring...")
            print("Press Ctrl+C to stop")
            await monitor.monitor_continuously()
        else:
            print("\n🔍 Running single check...")
            monitor.run_single_check()
        
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped by user")
    except Exception as e:
        logger.error(f"❌ Monitor failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())