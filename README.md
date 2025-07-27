# Tiny Backspace

A sandboxed coding agent that can create pull requests! 🚀

## 🌐 Public URL

**Live Demo**: [https://tiny-backspace.onrender.com](https://tiny-backspace.onrender.com)

You can test the API directly by sending a POST request to the public endpoint:

```bash
curl -X POST "https://tiny-backspace.onrender.com/code" \
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
curl -X POST "http://localhost:8000/code" \
  -H "Content-Type: application/json" \
  -d '{
    "repoUrl": "https://github.com/AsadShahid04/tiny-backspace",
    "prompt": "Add a simple test file"
  }'
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
├── app/
│   ├── api/
│   │   └── routes.py          # API endpoints
│   ├── services/
│   │   ├── code_processor.py  # Main orchestration
│   │   ├── agent_runner.py    # AI agent management
│   │   └── github_pr_creator.py # GitHub integration
│   ├── utils/
│   │   └── sse.py            # Server-Sent Events
│   ├── logging_config.py     # Logging setup
│   └── main.py               # FastAPI app
├── requirements.txt          # Dependencies
├── run_server.py            # Server startup script
├── test_simple.py           # Quick tests
├── test_file_editing.py     # Comprehensive tests
└── README.md                # This file
```

## 🔄 Workflow

1. **Receive Request**: Client sends repo URL and prompt
2. **Initialize Sandbox**: Create isolated E2B environment
3. **Clone Repository**: Download target repository
4. **Analyze Codebase**: Scan files and structure
5. **Generate Changes**: AI agents create modifications
6. **Apply Changes**: Modify files in sandbox
7. **Create PR**: Generate GitHub pull request
8. **Cleanup**: Remove sandbox and temporary files

## 🚀 Development

### Adding New AI Providers

1. Add provider to `agent_runner.py`
2. Update fallback logic
3. Add environment variable
4. Update tests

### Extending Features

- Add authentication
- Support more file types
- Implement caching
- Add rate limiting

## 🌍 Deployment

### Render (Current)

- Automatic deployment from GitHub
- Environment variables configured
- HTTPS enabled
- Auto-scaling

### Other Platforms

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
