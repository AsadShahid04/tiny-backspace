# Tools

This directory contains monitoring and utility tools for the Tiny Backspace project.

## Tools

### monitor_dashboard.py

Real-time terminal-based monitoring dashboard that provides:

- Live metrics (requests/min, errors/min, response times)
- Active request tracking
- Recent error display
- Health summary with recommendations
- Continuous log tailing and analysis

## Usage

```bash
# Start the monitoring dashboard
python tools/monitor_dashboard.py

# The dashboard will show:
# - System status (HEALTHY/WARNING/CRITICAL)
# - Real-time metrics
# - Active requests
# - Recent errors
# - Health summary
```

## Features

- **Real-time Updates**: Dashboard refreshes every 2 seconds
- **Log Monitoring**: Tails log files for live updates
- **Health Scoring**: Automated health score calculation
- **Error Tracking**: Recent error display with timestamps
- **Performance Metrics**: Response time and throughput monitoring
