# Tiny Backspace

A sandboxed coding agent that can create pull requests! 🚀

## 📋 **Project Overview**

I built Tiny Backspace as an autonomous coding agent that takes a GitHub repo URL and coding prompt, then automatically creates pull requests with AI-generated changes. The system streams real-time updates via Server-Sent Events and provides comprehensive observability through Langsmith.

**Live Demo**: [https://asad-tiny-backspace.vercel.app](https://asad-tiny-backspace.vercel.app)

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

### **Run Locally**

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
python run_server.py

# Test locally
curl -X POST "http://localhost:8000/code" \
  -H "Content-Type: application/json" \
  -d '{
    "repoUrl": "https://github.com/AsadShahid04/tiny-backspace",
    "prompt": "Add a test section to README"
  }'
```

## 🤖 **AI Agent Approach**

I chose a **three-tier hybrid approach** with intelligent fallbacks to ensure reliability and quality:

### **Primary: Claude (Anthropic)**

- **Why**: Superior reasoning for complex code analysis and context understanding
- **Strengths**: Best code generation quality, reduced hallucinations, advanced pattern recognition
- **Use Case**: Primary choice for all code modifications

### **Fallback: OpenAI GPT**

- **Why**: High availability and fast response times for quick iterations
- **Strengths**: ~2-3 second response times, cost-effective scaling, proven reliability
- **Use Case**: Backup when Claude is unavailable

### **Final Fallback: Dummy Agent**

- **Why**: Ensures the system never fails completely, even during API outages
- **Strengths**: Always available, instant response, zero cost
- **Use Case**: When both AI providers are unavailable

**Why This Approach?** It provides enterprise-grade reliability through multiple fallbacks, optimizes for quality (Claude) and performance (OpenAI), and ensures consistent user experience regardless of external API status.

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
# Run comprehensive tests
python -m pytest tests/

# Start monitoring dashboard
python tools/monitor_dashboard.py

# Check Langsmith traces
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
├── api/                    # Vercel functions
├── app/                    # Main application
│   ├── services/           # AI integration & GitHub
│   └── utils/              # Helper modules
├── tests/                  # Test suite
├── tools/                  # Monitoring & utilities
└── docs/                   # Documentation
```

---

**Built with ❤️ for the developer community**

_This project demonstrates modern autonomous coding agent architecture with enterprise-grade observability and reliability._
