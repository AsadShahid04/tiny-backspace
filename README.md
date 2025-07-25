# FastAPI E2B Code Processing Backend

A FastAPI backend that processes GitHub repositories using E2B sandboxes and streams real-time status updates via Server-Sent Events (SSE).

## Features

- 🚀 **FastAPI Backend** with automatic API documentation
- 📡 **Server-Sent Events (SSE)** for real-time status streaming  
- 🔧 **E2B Sandbox Integration** for secure code execution
- 🔍 **GitHub Repository Processing** with git clone support
- ⚡ **Async/Await** throughout for optimal performance
- 🛡️ **Comprehensive Error Handling** and logging
- 📊 **Progress Tracking** with detailed status updates

## Quick Start

1. **Setup Environment**:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Configure E2B API Key**:
```bash
export E2B_API_KEY=your_e2b_api_key_here
```

3. **Start the Server**:
```bash
python run_server.py
```

The API will be available at:
- 🌐 **Server**: http://localhost:8000
- 📖 **Documentation**: http://localhost:8000/docs
- 🧪 **Dummy Stream Test**: http://localhost:8000/stream-dummy

## API Endpoints

### POST `/code` - Process Repository

Processes a GitHub repository with AI-driven modifications and streams real-time updates.

**Request Body:**
```json
{
  "repoUrl": "https://github.com/username/repository.git",
  "prompt": "Description of changes to make"
}
```

**Response**: Server-Sent Events stream with status updates

**Example Status Updates:**
```json
{
  "type": "info",
  "message": "Initializing E2B sandbox...",
  "step": "init",
  "progress": 10,
  "timestamp": 1704067200000
}

{
  "type": "success", 
  "message": "Repository cloned successfully: fastapi",
  "step": "clone",
  "progress": 50,
  "timestamp": 1704067205000
}

{
  "type": "summary",
  "message": "Processing completed",
  "timestamp": 1704067220000,
  "summary": {
    "repository": "fastapi",
    "prompt": "Add better error handling",
    "files_modified": 3,
    "sandbox_id": "sb_abc123",
    "duration_ms": 15000
  }
}
```

## Message Types

- `info`: General status information
- `success`: Successful completion of a step
- `error`: Error occurred during processing
- `warning`: Non-fatal warning
- `summary`: Final processing summary

## Processing Workflow

1. **init**: Initialize E2B sandbox
2. **validation**: Validate repository URL
3. **clone**: Clone GitHub repository
4. **analysis**: Analyze repository structure
5. **planning**: Plan code changes based on prompt
6. **implementation**: Apply planned changes
7. **complete**: Finalization and cleanup

## Usage Examples

### Python with aiohttp
```python
import aiohttp
import json

async def process_code():
    data = {
        "repoUrl": "https://github.com/fastapi/fastapi.git",
        "prompt": "Add better error handling"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:8000/code",
            json=data,
            headers={"Accept": "text/event-stream"}
        ) as response:
            async for line in response.content:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    event_data = json.loads(line[6:])
                    print(f"{event_data['type']}: {event_data['message']}")
```

### JavaScript/Browser
```javascript
const response = await fetch('/code', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'text/event-stream'
  },
  body: JSON.stringify({
    repoUrl: 'https://github.com/fastapi/fastapi.git',
    prompt: 'Add better error handling'
  })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const chunk = decoder.decode(value);
  const lines = chunk.split('\n');
  
  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const eventData = JSON.parse(line.substring(6));
      console.log(`${eventData.type}: ${eventData.message}`);
    }
  }
}
```

### curl
```bash
curl -X POST http://localhost:8000/code \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"repoUrl": "https://github.com/fastapi/fastapi.git", "prompt": "Add better error handling"}' \
  --no-buffer
```

## Testing

Create a test script (`test_client.py`):
```python
#!/usr/bin/env python3
import asyncio
import aiohttp
import json

async def test_code_endpoint():
    test_data = {
        "repoUrl": "https://github.com/fastapi/fastapi.git",
        "prompt": "Add better error handling"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:8000/code",
            json=test_data,
            headers={"Accept": "text/event-stream"}
        ) as response:
            async for line in response.content:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    data = json.loads(line[6:])
                    print(f"📡 {data['type']}: {data['message']}")

if __name__ == "__main__":
    asyncio.run(test_code_endpoint())
```

Run the test:
```bash
pip install aiohttp  # if not already installed
python test_client.py
```

## Project Structure

```
├── app/
│   ├── main.py                 # FastAPI application setup
│   ├── api/
│   │   └── routes.py          # API route definitions
│   ├── services/
│   │   └── code_processor.py  # Core processing logic
│   ├── logging_config.py      # Logging configuration
│   └── utils/                 # Utility functions
├── run_server.py              # Server startup script
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Environment Variables

- `E2B_API_KEY`: Your E2B API key (required)
- `LOG_LEVEL`: Logging level (default: INFO)

## Error Handling

The API includes comprehensive error handling:
- Invalid repository URLs are rejected with validation errors
- E2B sandbox failures are caught and reported
- Git clone failures include detailed error messages
- All errors are streamed back as SSE events with type "error"

## CORS Configuration

The API is configured with permissive CORS settings for development. For production, update the CORS configuration in `app/main.py` to restrict allowed origins.

## Development

### Adding New Processing Steps

1. Edit `app/services/code_processor.py`
2. Add new steps to the `process_code_request` function
3. Use `yield create_status_update()` to stream progress

### Customizing Status Messages

Modify the `create_status_update` helper function to include additional fields or change the message format.

## License

MIT License - see LICENSE file for details.
