# Tiny Backspace

A sandboxed coding agent that can create pull requests! 🚀

## 🌐 Public URL

**Live Demo**: [https://your-app-name-production.up.railway.app](https://your-app-name-production.up.railway.app) _(Replace with your actual URL)_

You can test the API directly by sending a POST request to the public endpoint:

```bash
curl -X POST "https://your-app-name-production.up.railway.app/code" \
  -H "Content-Type: application/json" \
  -d '{
    "repoUrl": "https://github.com/your-username/your-repo",
    "prompt": "Add error handling to the main function"
  }'
```

## 🏃‍♂️ Quick Start (Local Development)

### Prerequisites

- Python 3.8+
- Git
- Virtual environment (recommended)

### 1. Clone and Setup

```bash
git clone https://github.com/AsadShahid04/tiny-backspace.git
cd tiny-backspace

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory:

```env
# Required for sandboxed execution
E2B_API_KEY=your_e2b_api_key_here

# AI Providers (choose one or both)
ANTHROPIC_API_KEY=your_claude_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# GitHub Integration (for PR creation)
GITHUB_PAT=your_github_personal_access_token_here
```

### 4. Run Locally

```bash
# Start the server
python run_server.py

# Or using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Test Locally

```bash
# Basic API test
curl -X POST "http://localhost:8000/code" \
  -H "Content-Type: application/json" \
  -d '{
    "repoUrl": "https://github.com/AsadShahid04/tiny-backspace",
    "prompt": "Add a simple test file"
  }'

# Run comprehensive tests
python -m pytest tests/

# Start monitoring dashboard
python tools/monitor_dashboard.py
```

## 🤖 Coding Agent Approach

### **Chosen Approach: Hybrid AI with Fallback Strategy**

We implemented a **dual-AI approach** with intelligent fallback mechanisms:

#### **Primary Agent: Claude (Anthropic)**

- **Why Claude?** Superior reasoning capabilities for code analysis and generation
- **Strengths**: Better understanding of context, more reliable code generation
- **Use Case**: Primary choice for all code modification tasks

#### **Fallback Agent: OpenAI GPT**

- **Why OpenAI?** High availability and consistent performance
- **Strengths**: Fast response times, good code completion
- **Use Case**: Backup when Claude is unavailable or rate-limited

#### **Final Fallback: Dummy Agent**

- **Why Dummy Agent?** Ensures the system never fails completely
- **Strengths**: Always available, provides basic file modifications
- **Use Case**: When both AI providers are unavailable

### **Agent Selection Logic**

```python
# Priority order:
1. Claude (Anthropic) - Best quality
2. OpenAI GPT - Good quality, high availability
3. Dummy Agent - Basic functionality, always works
```

### **Why This Approach?**

1. **Reliability**: Multiple fallbacks ensure the system never fails
2. **Quality**: Claude provides the best code generation quality
3. **Cost Optimization**: Can switch between providers based on usage
4. **Scalability**: Easy to add more AI providers in the future
5. **User Experience**: Consistent service even during API outages

### **Agent Capabilities**

| Feature               | Claude       | OpenAI  | Dummy    |
| --------------------- | ------------ | ------- | -------- |
| Code Analysis         | ✅ Excellent | ✅ Good | ❌ None  |
| File Modifications    | ✅ Advanced  | ✅ Good | ✅ Basic |
| Context Understanding | ✅ Superior  | ✅ Good | ❌ None  |
| Error Handling        | ✅ Excellent | ✅ Good | ❌ None  |
| Response Time         | Medium       | Fast    | Instant  |
| Cost                  | Medium       | Low     | Free     |

## 📋 Features

- **🔒 Sandboxed Execution**: Isolated code processing using E2B
- **🤖 AI-Powered Code Generation**: Multiple AI providers with fallback
- **🔗 GitHub Integration**: Automatic PR creation
- **📡 Real-Time Updates**: Server-Sent Events (SSE) for live progress
- **🛡️ Error Handling**: Comprehensive error management
- **📊 Progress Tracking**: Step-by-step progress updates
- **🧹 Auto Cleanup**: Automatic sandbox cleanup

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client        │    │   FastAPI       │    │   E2B Sandbox   │
│   (Frontend)    │◄──►│   Backend       │◄──►│   (Isolated)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   AI Agents     │
                       │  (Claude/OpenAI)│
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   GitHub API    │
                       │  (PR Creation)  │
                       └─────────────────┘
```

## 🔧 Configuration

### Environment Variables

| Variable                       | Required | Description                  |
| ------------------------------ | -------- | ---------------------------- |
| `E2B_API_KEY`                  | ✅       | E2B API key for sandbox      |
| `ANTHROPIC_API_KEY`            | ❌       | Claude API key (primary AI)  |
| `OPENAI_API_KEY`               | ❌       | OpenAI API key (fallback AI) |
| `GITHUB_TOKEN` or `GITHUB_PAT` | ❌       | GitHub token for PR creation |

### AI Provider Priority

1. **Claude (Anthropic)** - Primary choice for best quality
2. **OpenAI GPT** - Fallback for high availability

## 🔍 Observability & Monitoring

Tiny Backspace includes comprehensive observability features to track agent behavior, performance, and system health:

### **Real-Time Agent Thinking**

- **Live Logging**: See what the agent is thinking in real-time
- **Step-by-Step Tracking**: Monitor each decision and operation
- **Context Preservation**: Maintain request correlation across all operations

### **Performance Monitoring**

- **Operation Timing**: Track performance of each step
- **Bottleneck Detection**: Identify slow operations
- **Resource Usage**: Monitor sandbox and API usage

### **Error Tracking & Analysis**

- **Structured Error Logging**: Detailed error context and stack traces
- **Error Patterns**: Identify common failure modes
- **Recovery Strategies**: Automatic fallback mechanisms

### **Health Monitoring**

```bash
# Generate health report
python monitor_dashboard.py --health-report

# Real-time monitoring dashboard
python monitor_dashboard.py

# Test observability features
python test_observability.py
```

### **Log Analysis**

- **Structured Logs**: JSON-formatted logs for easy parsing
- **Log Rotation**: Automatic log management and compression
- **Multi-level Logging**: Debug, Info, Error, and Performance logs

3. **Dummy Agent** - Final fallback for basic functionality

## 🧪 Testing

### Quick Test

```bash
python test_simple.py
```

### Comprehensive Test

```bash
python test_file_editing.py
```

### Manual API Test

```bash
curl -X POST "http://localhost:8000/code" \
  -H "Content-Type: application/json" \
  -d '{
    "repoUrl": "https://github.com/AsadShahid04/tiny-backspace",
    "prompt": "Add comprehensive error handling"
  }'
```

## 📁 Project Structure

```
tiny-backspace/
├── app/                      # Main application code
│   ├── api/                  # API endpoints
│   ├── services/             # Business logic & AI integration
│   ├── utils/                # Helper modules
│   ├── logging_config.py     # Observability setup
│   └── main.py               # FastAPI application
├── tests/                    # Test files
│   ├── test_simple.py        # Basic API tests
│   ├── test_file_editing.py  # File editing tests
│   ├── test_observability.py # Observability tests
│   └── test_small_repo.py    # Small repo tests
├── tools/                    # Monitoring & utilities
│   └── monitor_dashboard.py  # Real-time monitoring
├── scripts/                  # Development scripts
│   └── sandbox_playground.py # E2B sandbox testing
├── docs/                     # Documentation
│   ├── DOCUMENTATION.md      # Complete technical docs
│   └── IMPLEMENTATION_COMPLETE.md
├── logs/                     # Application logs (auto-generated)
├── requirements.txt          # Python dependencies
├── run_server.py            # Server startup script
└── README.md                # This file
```

📋 **See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed structure overview**

## 🔄 Workflow

1. **Receive Request**: Client sends repo URL and prompt
2. **Initialize Sandbox**: Create isolated E2B environment
3. **Clone Repository**: Download target repository
4. **Analyze Codebase**: Scan files and structure
5. **Generate Changes**: AI agents create modifications
6. **Apply Changes**: Modify files in sandbox
7. **Create PR**: Generate GitHub pull request
8. **Cleanup**: Remove sandbox and temporary files

## 🧪 Testing & Development

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python tests/test_simple.py          # Basic API tests
python tests/test_file_editing.py    # File editing tests
python tests/test_observability.py   # Observability tests
python tests/test_small_repo.py      # Small repo tests

# Run with verbose output
python -m pytest tests/ -v
```

### Monitoring & Observability

```bash
# Start real-time monitoring dashboard
python tools/monitor_dashboard.py

# View logs
tail -f logs/app.log
tail -f logs/errors.log
tail -f logs/performance.log
tail -f logs/agent_thinking.log
```

### Development Scripts

```bash
# Test E2B sandbox functionality
python scripts/sandbox_playground.py
```

## 🚀 Development

### Adding New AI Providers

1. Add provider to `app/services/agent_runner.py`
2. Update fallback logic
3. Add environment variable
4. Update tests in `tests/` directory

### Extending Features

- Add authentication
- Support more file types
- Implement caching
- Add rate limiting

## 🌍 Deployment

### Railway (Recommended - 100% Free, No Credit Card)

1. **Go to [railway.app](https://railway.app)**
2. **Click "Start a New Project"**
3. **Choose "Deploy from GitHub repo"**
4. **Select your repository**: `AsadShahid04/tiny-backspace`
5. **Add environment variables**:
   ```
   GITHUB_TOKEN = your_github_token
   ANTHROPIC_API_KEY = your_anthropic_key
   OPENAI_API_KEY = your_openai_key
   ```
6. **Deploy automatically**
7. **Get your public URL**: `https://your-app-name-production.up.railway.app`

### Other Platforms

- **Render**: Automatic deployment from GitHub
- **Heroku**: Add `Procfile`
- **AWS**: Use Elastic Beanstalk
- **GCP**: Use Cloud Run
- **Azure**: Use App Service

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **E2B** for sandboxed execution
- **Anthropic** for Claude AI
- **OpenAI** for GPT models
- **FastAPI** for the web framework
- **GitHub** for repository integration

---

**Built with ❤️ for the developer community**
