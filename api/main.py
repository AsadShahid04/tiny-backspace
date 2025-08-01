from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import json
import asyncio
import os
import sys
import uuid
import re
from typing import AsyncGenerator, Optional
import subprocess
import tempfile
import shutil
from pathlib import Path
from dotenv import load_dotenv
import anthropic
import requests
import socket
import signal
import psutil
import time
import traceback

# Load environment variables from .env file
load_dotenv()

# Debug: Print environment variables
print("🔍 Environment variables loaded:")
print(f"GITHUB_PAT: {os.getenv(GITHUB_PAT, NOT SET)[:20]}...")
print(f"ANTHROPIC_API_KEY: {os.getenv(ANTHROPIC_API_KEY, NOT SET)[:20]}...")
print(f"E2B_API_KEY: {os.getenv(E2B_API_KEY, NOT SET)[:20]}...")

# E2B imports
from e2b import Sandbox

# Initialize FastAPI app
app = FastAPI(title="Tiny Backspace", description="AI-powered code generation and PR creation")

# Add test endpoint
@app.get("/test")
async def test_endpoint():
    """Simple test endpoint to verify API functionality"""
    return {
        "status": "success",
        "message": "Test endpoint working",
        "timestamp": time.time()
    }

class TinyBackspaceProcessor:
    def __init__(self):
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        pass

    # ... rest of the file content remains the same ...
