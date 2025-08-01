# Tiny Backspace

A sandboxed coding agent that can create pull requests automatically! This project implements the core technology behind autonomous coding agents with modern tooling for safety and observability.

## 🚀 Features

- **Secure Sandboxing**: Uses E2B for isolated code execution
- **AI-Powered Code Generation**: Leverages Claude 3.5 Sonnet for intelligent code changes
- **Real-time Streaming**: Server-Sent Events for live progress updates
- **Automatic PR Creation**: GitHub API integration for seamless pull request generation
- **Modern Architecture**: FastAPI with async/await for high performance

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client        │    │   FastAPI       │    │   E2B Sandbox   │
│   (Browser/     │───▶│   Server        │───▶│   (Secure       │
│   API Client)   │    │   (Port 8000)   │    │   Environment)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   GitHub API    │
                       │   (PR Creation) │
                       └─────────────────┘
```

## 📋 Prerequisites

- Python 3.8+
- GitHub Personal Access Token (PAT)
- Anthropic API Key
- E2B API Key (for sandboxing)

## 🛠️ Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/tiny-backspace.git
cd tiny-backspace
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
cd api
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the root directory:

```bash
# GitHub Configuration
GITHUB_PAT=your_github_personal_access_token_here

# AI Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Sandbox Configuration (optional - E2B provides free tier)
E2B_API_KEY=your_e2b_api_key_here
```

### 5. Get API Keys

#### GitHub Personal Access Token

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate a new token with `repo` scope
3. Copy the token to your `.env` file

#### Anthropic API Key

1. Sign up at [Anthropic Console](https://console.anthropic.com/)
2. Create an API key
3. Copy the key to your `.env` file

#### E2B API Key (Optional)

1. Sign up at [E2B](https://e2b.dev/)
2. Get your API key from the dashboard
3. Copy the key to your `.env` file

#### LangSmith API Key (Optional - for observability)

1. Sign up at [LangSmith](https://smith.langchain.com/)
2. Create an API key in your settings
3. Copy the key to your `.env` file

## 🚀 Running Locally

### Start the Server

```bash
cd api
python main.py
```

The server will start on `http://localhost:8000`

### Test the API

Use the provided test script:

```bash
python test_simple.py
```

Or make a direct API call:

```bash
curl -X POST http://localhost:8000/code \
  -H "Content-Type: application/json" \
  -d '{
    "repoUrl": "https://github.com/yourusername/test-repo",
    "prompt": "Add a simple print statement to main.py"
  }'
```

## 📡 API Endpoints

### POST /code

Main endpoint for code generation and PR creation.

**Request Body:**

```json
{
  "repoUrl": "https://github.com/owner/repo",
  "prompt": "Add input validation to all POST endpoints"
}
```

**Response:** Server-Sent Events stream with real-time updates

**Example Stream:**

```
data: {"type": "info", "message": "🚀 Starting request abc12345"}
data: {"type": "info", "message": "📁 Repository: https://github.com/owner/repo"}
data: {"type": "info", "message": "💭 Creating E2B sandbox"}
data: {"type": "success", "message": "✅ Sandbox created: sandbox_123"}
data: {"type": "info", "message": "📥 Cloning repository"}
data: {"type": "success", "message": "✅ Repository cloned"}
data: {"type": "info", "message": "🤖 Generating code with Claude"}
data: {"type": "success", "message": "✅ Pull request created: https://github.com/owner/repo/pull/123"}
```

### GET /health

Health check endpoint.

**Response:**

```json
{
  "status": "healthy",
  "message": "Tiny Backspace is running"
}
```

## 🌐 Deployment

### Vercel Deployment

The project includes Vercel configuration for easy deployment:

1. Install Vercel CLI: `npm i -g vercel`
2. Deploy: `vercel --prod`

### Docker Deployment

```bash
# Build the image
docker build -t tiny-backspace .

# Run the container
docker run -p 8000:8000 --env-file .env tiny-backspace
```

## 🔧 Configuration

### Environment Variables

| Variable            | Description                  | Required            |
| ------------------- | ---------------------------- | ------------------- |
| `GITHUB_PAT`        | GitHub Personal Access Token | Yes                 |
| `ANTHROPIC_API_KEY` | Anthropic API Key            | Yes                 |
| `E2B_API_KEY`       | E2B API Key                  | No (uses free tier) |
| `LANGSMITH_API_KEY` | LangSmith API Key for observability | No (optional) |

### Customization

You can customize the AI model, sandbox settings, and other parameters by modifying the configuration in `api/main.py`.

## 🧪 Testing

### Run Tests

```bash
# Test the basic API functionality
python test_simple.py

# Test with LangSmith observability
python test_langsmith.py

# Debug Claude API
python debug_claude.py
```

### Test with Different Repositories

Modify the `repoUrl` and `prompt` in `test_simple.py` to test with different scenarios.

## 🔒 Security

- **Sandboxed Execution**: All code runs in isolated E2B environments
- **Token Security**: API keys are stored in environment variables
- **Input Validation**: Repository URLs and prompts are validated
- **Error Handling**: Comprehensive error handling prevents information leakage

## 📊 Observability

The application provides comprehensive observability through:

- **Server-Sent Events**: Live progress updates
- **LangSmith Integration**: Real-time AI agent telemetry and tracing
- **Structured Logging**: JSON-formatted logs with detailed metadata
- **Error Tracking**: Detailed error messages and stack traces
- **Request Tracking**: Unique request IDs for tracing
- **Performance Metrics**: Token usage, response times, and success rates

### LangSmith Dashboard

When configured with a LangSmith API key, you can view:
- **AI Agent Thinking Process**: See exactly how Claude analyzes and generates code
- **Request Traces**: Complete end-to-end request flows
- **Performance Analytics**: Token usage, response times, and success rates
- **Error Analysis**: Detailed error tracking and debugging information
- **Custom Metrics**: File analysis, code changes, and PR creation success rates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details

## 🆘 Troubleshooting

### Common Issues

1. **"GITHUB_PAT environment variable is required"**

   - Make sure your `.env` file exists and contains the GitHub token

2. **"ANTHROPIC_API_KEY environment variable is required"**

   - Ensure your Anthropic API key is set in the `.env` file

3. **"Clone failed"**

   - Check that the repository URL is correct and publicly accessible
   - Verify your GitHub token has the necessary permissions

4. **"Failed to create PR"**
   - Ensure the repository exists and you have write access
   - Check that the base branch (usually 'main') exists

### Debug Mode

Run with debug logging:

```bash
python -u api/main.py
```

## 🎯 Example Use Cases

1. **Add Input Validation**: "Add Pydantic validation to all POST endpoints"
2. **Fix Security Issues**: "Add CORS headers and input sanitization"
3. **Improve Error Handling**: "Add proper error handling and logging"
4. **Add Features**: "Add a new endpoint for user authentication"
5. **Refactor Code**: "Refactor the main function to use dependency injection"

## 🔮 Future Enhancements

- [ ] Support for multiple AI models
- [ ] Advanced sandbox configurations
- [ ] Webhook support for automated triggers
- [ ] Integration with CI/CD pipelines
- [ ] Support for private repositories
- [ ] Advanced code analysis and suggestions
