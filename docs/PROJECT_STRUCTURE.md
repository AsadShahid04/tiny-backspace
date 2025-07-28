# Project Structure

```
tiny-backspace/
├── README.md                    # Main project README
├── PROJECT_STRUCTURE.md         # This file - project structure overview
├── requirements.txt             # Python dependencies
├── run_server.py               # Server startup script
├── .gitignore                  # Git ignore rules
│
├── app/                        # Main application code
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── logging_config.py       # Logging and observability setup
│   ├── api/                    # API layer
│   │   ├── __init__.py
│   │   └── routes.py           # API endpoints
│   ├── services/               # Business logic layer
│   │   ├── __init__.py
│   │   ├── agent_runner.py     # AI agent management
│   │   ├── code_processor.py   # Main workflow orchestration
│   │   └── github_pr_creator.py # GitHub integration
│   └── utils/                  # Utility modules
│       ├── __init__.py
│       ├── log_analyzer.py     # Log analysis engine
│       └── sse.py              # Server-Sent Events utilities
│
├── tests/                      # Test files
│   ├── __init__.py
│   ├── README.md               # Test documentation
│   ├── test_simple.py          # Basic API tests
│   ├── test_file_editing.py    # File editing tests
│   ├── test_observability.py   # Observability tests
│   └── test_small_repo.py      # Small repo tests
│
├── tools/                      # Monitoring and utility tools
│   ├── README.md               # Tools documentation
│   └── monitor_dashboard.py    # Real-time monitoring dashboard
│
├── scripts/                    # Development scripts
│   ├── README.md               # Scripts documentation
│   └── sandbox_playground.py   # E2B sandbox testing
│
├── docs/                       # Documentation
│   ├── README.md               # Documentation overview
│   ├── DOCUMENTATION.md        # Complete technical documentation
│   └── IMPLEMENTATION_COMPLETE.md # Implementation summary
│
├── logs/                       # Application logs (auto-generated)
│   ├── app.log                 # Application logs
│   ├── errors.log              # Error logs
│   ├── performance.log         # Performance metrics
│   └── agent_thinking.log      # AI agent thinking logs
│
└── venv/                       # Python virtual environment
```

## Directory Purposes

### `/app` - Main Application

- **API Layer**: FastAPI endpoints and request handling
- **Services Layer**: Core business logic and AI integration
- **Utils**: Helper modules and utilities

### `/tests` - Testing

- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing
- **Observability Tests**: Logging and monitoring validation

### `/tools` - Monitoring & Utilities

- **Real-time Monitoring**: Live system monitoring dashboard
- **Health Analysis**: System health and performance analysis

### `/scripts` - Development Scripts

- **Development Tools**: Scripts for development and debugging
- **Testing Utilities**: Helper scripts for testing

### `/docs` - Documentation

- **Technical Documentation**: Comprehensive system documentation
- **Implementation Guides**: Detailed implementation information
- **Architecture Documentation**: System design and decisions

### `/logs` - Application Logs

- **Structured Logging**: Organized log files for different purposes
- **Observability Data**: Performance metrics and error tracking

## Key Files

### Core Application Files

- `app/main.py` - FastAPI application setup
- `app/services/code_processor.py` - Main workflow orchestration
- `app/services/agent_runner.py` - AI agent management
- `app/logging_config.py` - Observability setup

### Configuration Files

- `requirements.txt` - Python dependencies
- `run_server.py` - Server startup script
- `.gitignore` - Git ignore rules

### Documentation Files

- `README.md` - Main project overview
- `docs/DOCUMENTATION.md` - Complete technical documentation
- `PROJECT_STRUCTURE.md` - This file

## Development Workflow

1. **Development**: Work in `/app` directory
2. **Testing**: Add tests in `/tests` directory
3. **Monitoring**: Use tools in `/tools` directory
4. **Documentation**: Update files in `/docs` directory
5. **Scripts**: Add development scripts in `/scripts` directory
