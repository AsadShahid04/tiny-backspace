# Tiny Backspace

A sandboxed coding agent that automatically creates pull requests based on your prompts.

## Overview

Tiny Backspace is an AI-powered code generation service that:

1. Takes a GitHub repository URL and a coding prompt
2. Clones the repository into a secure E2B sandbox
3. Uses Claude Code (running locally) to generate code changes
4. Applies the changes in the sandbox
5. Creates a pull request with the modifications

<<<<<<< Updated upstream
### **✅ Recent Implementation Success**

The system has been successfully tested and is fully functional:

- **✅ FastAPI Server**: Running with Server-Sent Events streaming
- **✅ E2B Sandbox**: Secure sandboxed execution working
- **✅ Claude Code**: AI agent generating meaningful code modifications
- **✅ GitHub Integration**: Automatic PR creation verified
- **✅ Real-time Streaming**: Progress updates working perfectly

**Latest Test Results**: Successfully created PR #12 with logging functionality for the tiny-backspace repository!

## 🚀 **Quick Start**
=======
## Architecture
>>>>>>> Stashed changes

- **Local AI Agent**: Claude Code runs locally for code generation
- **Secure Sandbox**: E2B provides isolated execution environment
- **Git Operations**: All Git operations happen within the sandbox
- **Real-time Streaming**: Server-Sent Events provide live updates

## Quick Start

### Prerequisites

1. **GitHub Personal Access Token** with repo permissions
2. **Anthropic API Key** for Claude Code
3. **E2B API Key** for sandboxing
4. **Python 3.8+**

### Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/tiny-backspace.git
cd tiny-backspace
```

<<<<<<< Updated upstream
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
=======
2. Create a virtual environment:
>>>>>>> Stashed changes

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
<<<<<<< Updated upstream

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
=======
>>>>>>> Stashed changes
```

3. Install dependencies:

<<<<<<< Updated upstream
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
=======
```bash
pip install -r api/requirements.txt
```

4. Set up environment variables:

```bash
cp env.example .env
# Edit .env with your API keys
```

5. Run the server:

```bash
python api/main.py
```

The server will start on `http://localhost:8000`

### Usage

Send a POST request to `/code` with:
>>>>>>> Stashed changes

```json
{
  "repoUrl": "https://github.com/username/repo-name",
  "prompt": "Add a simple test endpoint"
}
```

The response will be a Server-Sent Events stream showing:

<<<<<<< Updated upstream
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
=======
- Repository cloning progress
- Code analysis and generation
- File modifications
- Git operations
- Pull request creation

### Example Response Stream

```
data: {"type": "info", "message": "🚀 Starting request abc12345"}
data: {"type": "info", "message": "📁 Repository: https://github.com/example/repo"}
data: {"type": "info", "message": "💭 Prompt: Add a simple test endpoint"}
data: {"type": "info", "message": "💭 [SANDBOX] Creating secure E2B sandbox environment"}
data: {"type": "success", "message": "💭 [SANDBOX] E2B sandbox created successfully with ID: xyz789"}
data: {"type": "info", "message": "💭 [CLONE] Cloning repository https://github.com/example/repo into sandbox"}
data: {"type": "success", "message": "💭 [CLONE] Repository successfully cloned into sandbox"}
data: {"type": "info", "message": "🔍 [ANALYSIS] Analyzing repository structure"}
data: {"type": "success", "message": "🔍 [ANALYSIS] Repository analysis complete: 15 files found"}
data: {"type": "info", "message": "🤖 [AI_PROCESSING] Processing with Claude Code locally"}
data: {"type": "info", "message": "🔧 [APPLYING] Applying code changes in sandbox"}
data: {"type": "info", "message": "🔧 [GIT] Setting up Git operations in sandbox"}
data: {"type": "info", "message": "🔧 [GIT] Creating branch: feature/abc12345"}
data: {"type": "info", "message": "🔧 [PR] Creating pull request"}
data: {"type": "success", "message": "✅ [SUCCESS] Pull request created: https://github.com/example/repo/pull/123"}
>>>>>>> Stashed changes
```

## API Endpoints

<<<<<<< Updated upstream
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
=======
### POST /code

Main endpoint for code generation.

**Request Body:**

```json
{
  "repoUrl": "string (required)",
  "prompt": "string (required)"
}
>>>>>>> Stashed changes
```

**Response:** Server-Sent Events stream

### GET /health

Health check endpoint.

**Response:**

```json
{
  "status": "healthy",
  "message": "Tiny Backspace is running"
}
```

## Environment Variables

| Variable            | Description                       | Required |
| ------------------- | --------------------------------- | -------- |
| `GITHUB_PAT`        | GitHub Personal Access Token      | Yes      |
| `ANTHROPIC_API_KEY` | Anthropic API Key for Claude Code | Yes      |
| `E2B_API_KEY`       | E2B API Key for sandboxing        | Yes      |
| `OPENAI_API_KEY`    | OpenAI API Key (alternative)      | No       |

## Security Features

- **Sandboxed Execution**: All code runs in isolated E2B environments
- **Local AI Processing**: Claude Code runs locally, not in the sandbox
- **Secure File Operations**: File modifications happen in controlled sandbox
- **Git Authentication**: Uses GitHub Personal Access Token for secure operations

## Development

### Project Structure

```
tiny-backspace/
<<<<<<< Updated upstream
├── api/                    # FastAPI server and Vercel functions
│   ├── main.py            # FastAPI server with SSE streaming
│   ├── code.py            # Legacy Vercel function
│   └── simple_observability.py  # Observability module
├── test_full_workflow.py  # Complete workflow test
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
└── README.md             # This file
=======
├── api/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── simple_observability.py  # Observability utilities
├── venv/                    # Python virtual environment
├── .env                     # Environment variables (create from env.example)
├── env.example             # Environment variables template
└── README.md               # This file
>>>>>>> Stashed changes
```

### Running Tests

```bash
# Start the server
python api/main.py

# In another terminal, test the endpoint
curl -X POST http://localhost:8000/code \
  -H "Content-Type: application/json" \
  -d '{
    "repoUrl": "https://github.com/your-username/test-repo",
    "prompt": "Add a simple test endpoint"
  }'
```

## Deployment

### Local Development

```bash
python api/main.py
```

### Production

The application can be deployed to any platform that supports FastAPI:

- Railway
- Heroku
- DigitalOcean App Platform
- AWS Lambda (with modifications)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions, please open a GitHub issue.
