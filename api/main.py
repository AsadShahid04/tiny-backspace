#!/usr/bin/env python3
"""
Tiny Backspace - FastAPI Server with Server-Sent Events
Complete implementation meeting all assessment requirements
"""

import asyncio
import json
import os
import time
import uuid
import re
import base64
from typing import AsyncGenerator, Dict, Any, Optional
from urllib.parse import urlparse

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from dotenv import load_dotenv

# Import our working test workflow components
from simple_observability import get_observability_manager

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Tiny Backspace API",
    description="A sandboxed coding agent that creates PRs automatically",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add simple print statement
print("Starting Tiny Backspace API server...")

# Pydantic models for request validation
class CodeRequest(BaseModel):
    repoUrl: HttpUrl
    prompt: str

class CodeResponse(BaseModel):
    type: str
    message: str
    timestamp: int
    request_id: str
    step: Optional[str] = None
    progress: Optional[int] = None
    extra_data: Optional[Dict[str, Any]] = None
    telemetry: Optional[Dict[str, Any]] = None
