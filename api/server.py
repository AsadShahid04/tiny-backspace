#!/usr/bin/env python3
"""
Tiny Backspace Server
A FastAPI server for AI-powered code generation and PR creation
"""

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import json
import asyncio
import os
from dotenv import load_dotenv
from processor import TinyBackspaceProcessor

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Tiny Backspace", description="Simple AI-powered code generation and PR creation")

# Initialize processor
processor = TinyBackspaceProcessor()

@app.post("/code")
async def code_endpoint(request: Request):
    """Main endpoint for code generation"""
    try:
        print("🔍 Received POST request to /code")
        body = await request.json()
        print(f"🔍 Request body: {body}")
        repo_url = body.get('repoUrl')
        prompt = body.get('prompt')
        
        print(f"🔍 Repo URL: {repo_url}")
        print(f"🔍 Prompt: {prompt}")
        
        if not repo_url or not prompt:
            print("❌ Missing repoUrl or prompt")
            return StreamingResponse(
                iter([processor._create_sse_event("error", "Missing repoUrl or prompt")]),
                media_type="text/plain"
            )
        
        print("🔍 Starting processing")
        # Stream the events
        return StreamingResponse(
            processor.process_request(repo_url, prompt),
            media_type="text/plain"
        )
    except Exception as e:
        print(f"❌ Error in endpoint: {e}")
        import traceback
        traceback.print_exc()
        return StreamingResponse(
            iter([processor._create_sse_event("error", f"Request failed: {str(e)}")]),
            media_type="text/plain"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Tiny Backspace is running"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Tiny Backspace server on port 8000")
    uvicorn.run(app, host="0.0.0.0", port=8000) 