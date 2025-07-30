# Tiny Backspace

A sandboxed coding agent that can create pull requests! 🚀

## 📋 **Project Overview**

I built Tiny Backspace as an autonomous coding agent that takes a GitHub repo URL and coding prompt, then automatically creates pull requests with AI-generated changes. The system streams real-time updates via Server-Sent Events and provides comprehensive observability through Langsmith.

**Live Demo**: [https://asad-tiny-backspace.vercel.app](https://asad-tiny-backspace.vercel.app)

### **✅ Recent Implementation Success**

The system has been successfully tested and is fully functional:

- **✅ FastAPI Server**: Running with Server-Sent Events streaming
- **✅ E2B Sandbox**: Secure sandboxed execution working
- **✅ Claude Code**: AI agent generating meaningful code modifications
- **✅ GitHub Integration**: Automatic PR creation verified
- **✅ Real-time Streaming**: Progress updates working perfectly

**Latest Test Results**: Successfully created PR #12 with logging functionality for the tiny-backspace repository!

## 🚀 **Quick Start**

### **Test the Live API**

```bash
curl -X POST "https://asad-tiny-backspace.vercel.app/api/code" \
  -H "Content-Type: application/json" \
  -d '{
    "repoUrl": "https://github.com/your-username/your-repo",
    "prompt": "Add error handling to the main function"
  }'
```

### **Run Locally (FastAPI Server)**

```bash
# Start the FastAPI server
python api/main.py

# Test the server
curl -X GET "http://localhost:8000/health"

# Test the main endpoint
curl -X POST "http://localhost:8000/code" \
  -H "Content-Type: application/json" \
  -d '{
    "repoUrl": "https://github.com/AsadShahid04/tiny-backspace",
    "prompt": "Add a simple logging feature to track API requests"
  }' --no-buffer
```

### **Run Locally (Legacy Vercel Functions)**

```bash
# Clone and setup
git clone https://github.com/AsadShahid04/tiny-backspace.git
cd tiny-backspace
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env  # Edit with your API keys

# Start server
python api/main.py

# Test locally
curl -X POST "http://localhost:8000/code" \
  -H "Content-Type: application/json" \
  -d '{
    "repoUrl": "https://github.com/AsadShahid04/tiny-backspace",
    "prompt": "Add a test section to README"
  }'
```

## 🤖 **AI Agent Approach**

I chose **Claude Code (Anthropic)** as the primary AI agent for this implementation:

### **Primary: Claude Code (Anthropic)**

- **Why**: Superior reasoning for complex code analysis and context understanding
- **Strengths**: Best code generation quality, reduced hallucinations, advanced pattern recognition
- **Model**: `claude-3-5-sonnet-20241022` (latest stable version)
- **Use Case**: Primary choice for all code modifications
- **Integration**: Runs directly in E2B sandbox environment

### **Implementation Details**

- **Sandboxed Execution**: Claude Code runs securely in E2B sandbox
- **Repository Analysis**: Automatically analyzes repository structure
- **File Parsing**: Intelligently parses AI responses into file modifications
- **Error Handling**: Graceful fallbacks and comprehensive error management

**Why This Approach?** Claude Code provides the best balance of code quality, reasoning capabilities, and reliability for autonomous coding tasks. The sandboxed execution ensures security while maintaining full functionality.

## 🔍 **How It Works**

### **Real-Time Streaming Flow**

1. **API Call** → Validates repo URL and initializes environment
2. **Repository Analysis** → Scans structure and identifies relevant files
3. **AI Processing** → Generates code modifications using selected agent
4. **GitHub Integration** → Creates branch, applies changes, generates PR
5. **Observability** → Streams progress updates and performance metrics

### **Observability & Monitoring**

- **Langsmith Dashboard**: https://smith.langchain.com/ - Real-time traces of agent thinking process
- **Streaming Telemetry**: 24+ thinking steps with performance metrics
- **Example Response**:

```json
{
  "type": "success",
  "message": "Processing completed successfully!",
  "telemetry": {
    "thinking_logs_count": 25,
    "langsmith_enabled": true,
    "recent_thoughts": [
      { "step": "ai_planning", "thought": "Planning AI processing..." },
      { "step": "github_pr", "thought": "Creating pull request..." }
    ]
  },
  "extra_data": {
    "pr_url": "https://github.com/user/repo/pull/123",
    "total_duration_ms": 5000,
    "ai_provider": "openai"
  }
}
```

## 🛠️ **Key Features**

- **🔒 E2B Sandboxed Execution**: Secure, isolated environment for code processing
- **🤖 Claude Code Integration**: Real AI coding agent running in sandbox
- **🔗 GitHub Automation**: Automatic PR creation with AI-generated descriptions
- **📡 Real-Time Streaming**: Server-Sent Events for live progress updates
- **📊 Comprehensive Observability**: Langsmith traces + performance telemetry
- **🛡️ Error Handling**: Graceful fallbacks and comprehensive error management

## 🔧 **Configuration**

### **Required Environment Variables**

```env
# Required for sandboxed execution
E2B_API_KEY=your_e2b_api_key

# AI Providers (at least one required)
ANTHROPIC_API_KEY=your_claude_key
OPENAI_API_KEY=your_openai_key

# GitHub Integration
GITHUB_PAT=your_github_token

# Observability (optional but recommended)
LANGSMITH_API_KEY=your_langsmith_key
```

**API Key Sources:**

- **E2B**: https://e2b.dev/ (sandboxed execution)
- **GitHub PAT**: https://github.com/settings/tokens (repo scope)
- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/
- **Langsmith**: https://smith.langchain.com/ (free tier)

## 🏗️ **Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client        │    │   API Backend   │    │   E2B Sandbox   │
│   (Frontend)    │◄──►│   (Vercel)      │◄──►│  (Claude Code)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   GitHub API    │    │   Repository    │
                       │  (PR Creation)  │    │   (Cloned)      │
                       └─────────────────┘    └─────────────────┘
```

## 🧪 **Testing & Development**

```bash
# Test the complete workflow
python test_full_workflow.py

# Test the FastAPI server
python api/main.py

# Test with curl
curl -X POST "http://localhost:8000/code" \
  -H "Content-Type: application/json" \
  -d '{
    "repoUrl": "https://github.com/AsadShahid04/tiny-backspace",
    "prompt": "Add a simple logging feature to track API requests"
  }' --no-buffer

# Check Langsmith traces (if configured)
# Visit: https://smith.langchain.com/
```

## 🚀 **Deployment**

### **Vercel (Recommended)**

1. Connect GitHub repo to Vercel
2. Add environment variables in Vercel dashboard
3. Deploy automatically on push

### **Other Platforms**

- Render, Heroku, AWS, GCP, Azure supported
- Add `Procfile` for Heroku deployment

## 📁 **Project Structure**

```
tiny-backspace/
├── api/                    # FastAPI server and Vercel functions
│   ├── main.py            # FastAPI server with SSE streaming
│   ├── code.py            # Legacy Vercel function
│   └── simple_observability.py  # Observability module
├── test_full_workflow.py  # Complete workflow test
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
└── README.md             # This file
```

---

**Built with ❤️ for the developer community**

_This project demonstrates modern autonomous coding agent architecture with enterprise-grade observability and reliability._
