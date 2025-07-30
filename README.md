# Tiny Backspace

A sandboxed coding agent that can create pull requests! 🚀

## 📋 **Project Requirements Checklist**

✅ **Public URL**: Live demo at https://asad-tiny-backspace.vercel.app  
✅ **Local Setup**: Complete instructions for running on your machine  
✅ **Coding Agent Approach**: Hybrid AI with intelligent fallback strategy  
✅ **Demo Flow**: Full documentation of API call to PR creation process  
✅ **Observability**: Real-time telemetry via Langsmith

## 🌐 Public URL

**Live Demo**: [https://asad-tiny-backspace.vercel.app](https://asad-tiny-backspace.vercel.app)

You can test the API directly by sending a POST request to the public endpoint:

```bash
curl -X POST "https://asad-tiny-backspace.vercel.app/api/code" \
  -H "Content-Type: application/json" \
  -d '{
    "repoUrl": "https://github.com/your-username/your-repo",
    "prompt": "Add error handling to the main function"
  }'
```

## 🎬 **Demo: Full Flow from API Call to PR Creation**

### **What You'll See in the Demo**

This section demonstrates the complete flow that would be shown in a demo video, from API call to final PR creation:

#### **1. API Call & Real-Time Streaming**

```bash
# Step 1: Make the API call
curl -X POST "https://asad-tiny-backspace.vercel.app/api/code" \
  -H "Content-Type: application/json" \
  -d '{
    "repoUrl": "https://github.com/AsadShahid04/tiny-backspace",
    "prompt": "Add a section about error handling to the README"
  }'
```

**Real-time streaming response shows:**

- ✅ Environment initialization
- ✅ Repository URL validation
- ✅ Repository structure analysis (13 files detected)
- ✅ AI processing with OpenAI (12.1 seconds)
- ✅ GitHub PR creation (1.8 seconds)
- ✅ Final PR URL: https://github.com/AsadShahid04/tiny-backspace/pull/7

#### **2. Langsmith Observability Dashboard**

- **URL**: https://smith.langchain.com/
- **Real-time traces** showing agent thinking process
- **24 thinking steps** with timestamps
- **Performance metrics** for each operation
- **Complete request timeline** from start to finish

#### **3. GitHub Pull Request Creation**

- **Automatic branch creation**: `tiny-backspace-1753856468`
- **File modifications**: README.md updated with error handling section
- **PR description**: AI-generated explanation of changes
- **Final result**: Live PR ready for review

### **Demo Timeline (2-3 minutes)**

1. **0:00-0:30**: Show API call and initial streaming response
2. **0:30-1:30**: Demonstrate Langsmith dashboard with real-time traces
3. **1:30-2:00**: Show GitHub PR creation and final result
4. **2:00-2:30**: Highlight observability features and performance metrics

## 🔍 **Real-Time Observability**

### **Langsmith Dashboard**

- **URL**: https://smith.langchain.com/
- **Features**: Real-time AI agent thinking process, performance metrics, request flows
- **What you'll see**: Complete traces of agent reasoning, step-by-step decision making

### **Streaming Telemetry**

The API streams detailed real-time updates including:

- **Agent thinking steps** (24+ per request)
- **Performance metrics** for each operation
- **Real-time progress indicators**
- **Complete request timeline** with timestamps

### **Example Response**

```json
{
  "type": "success",
  "message": "Processing completed successfully!",
  "telemetry": {
    "thinking_logs_count": 25,
    "performance_metrics_count": 5,
    "langsmith_enabled": true,
    "recent_thoughts": [
      { "step": "ai_planning", "thought": "Planning AI processing..." },
      { "step": "github_pr", "thought": "Creating pull request..." }
    ]
  },
  "extra_data": {
    "pr_url": "https://github.com/user/repo/pull/123",
    "total_duration_ms": 5000,
    "successful_modifications": 1,
    "ai_provider": "openai"
  }
}
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

# Observability (Langsmith)
LANGSMITH_API_KEY=your_langsmith_api_key_here
```

**Getting API Keys:**

- **GitHub PAT**: https://github.com/settings/tokens (repo scope required)
- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/
- **Langsmith**: https://smith.langchain.com/ (free tier available)
- **E2B**: https://e2b.dev/ (sandbox provider)

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

# Test with real-time streaming (watch the progress)
curl -X POST "http://localhost:8000/code" \
  -H "Content-Type: application/json" \
  -d '{
    "repoUrl": "https://github.com/AsadShahid04/tiny-backspace",
    "prompt": "Add a section about local development to the README"
  }' | while read line; do echo "$line"; done

# Run comprehensive tests
python -m pytest tests/

# Start monitoring dashboard
python tools/monitor_dashboard.py

# Check Langsmith traces (if configured)
# Visit: https://smith.langchain.com/
```

## 🤖 Coding Agent Approach

### **Chosen Approach: Hybrid AI with Intelligent Fallback Strategy**

We implemented a **three-tier AI approach** with intelligent fallback mechanisms, prioritizing **reliability** and **quality** over single-provider dependency.

#### **Primary Agent: Claude (Anthropic) - Best Quality**

**Why Claude?**

- **Superior reasoning capabilities** for complex code analysis
- **Better context understanding** across multiple files
- **More reliable code generation** with fewer hallucinations
- **Advanced pattern recognition** for codebase structure

**Strengths:**

- Excellent code analysis and understanding
- Superior context preservation across files
- More reliable file modification generation
- Better handling of complex prompts

**Use Case:** Primary choice for all code modification tasks

#### **Fallback Agent: OpenAI GPT - High Availability**

**Why OpenAI?**

- **High availability** and consistent uptime
- **Fast response times** for quick iterations
- **Cost-effective** for high-volume usage
- **Proven reliability** in production environments

**Strengths:**

- Fast response times (~2-3 seconds)
- Good code completion capabilities
- High availability and uptime
- Cost-effective for scaling

**Use Case:** Backup when Claude is unavailable or rate-limited

#### **Final Fallback: Dummy Agent - Always Available**

**Why Dummy Agent?**

- **Ensures the system never fails completely**
- **Provides basic functionality** even during API outages
- **Maintains user experience** consistency
- **Demonstrates robust architecture** principles

**Strengths:**

- Always available (no external dependencies)
- Provides basic file modifications
- Instant response time
- Zero cost

**Use Case:** When both AI providers are unavailable

### **Agent Selection Logic**

```python
# Priority order:
1. Claude (Anthropic) - Best quality
2. OpenAI GPT - Good quality, high availability
3. Dummy Agent - Basic functionality, always works
```

### **Why This Approach?**

#### **1. Reliability & Fault Tolerance**

- **Multiple fallbacks** ensure the system never fails completely
- **Graceful degradation** from best quality to basic functionality
- **No single point of failure** in the AI provider layer
- **Consistent user experience** regardless of external API status

#### **2. Quality Optimization**

- **Claude provides superior code generation** for complex tasks
- **Better context understanding** across multiple files
- **Reduced hallucinations** and more reliable outputs
- **Advanced reasoning** for architectural decisions

#### **3. Cost & Performance Optimization**

- **Intelligent provider selection** based on task complexity
- **Cost-effective scaling** with multiple provider options
- **Performance optimization** through provider-specific strengths
- **Resource allocation** based on availability and cost

#### **4. Scalability & Extensibility**

- **Easy to add new AI providers** without code changes
- **Provider-agnostic architecture** for future flexibility
- **Modular design** allows independent provider management
- **Future-proof** for emerging AI technologies

#### **5. Production Readiness**

- **Enterprise-grade reliability** with multiple fallbacks
- **Comprehensive error handling** at every level
- **Observability** across all provider interactions
- **Monitoring and alerting** for provider health

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

### Vercel (Recommended - 100% Free, No Credit Card)

1. **Go to [vercel.com](https://vercel.com)**
2. **Click "New Project"**
3. **Import GitHub repository**: `AsadShahid04/tiny-backspace`
4. **Configure project** (auto-detects Python)
5. **Add environment variables**:
   ```
   GITHUB_PAT = your_github_token
   ANTHROPIC_API_KEY = your_anthropic_key
   OPENAI_API_KEY = your_openai_key
   LANGSMITH_API_KEY = your_langsmith_key
   ```
6. **Deploy automatically**
7. **Get your public URL**: `https://asad-tiny-backspace.vercel.app`

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
