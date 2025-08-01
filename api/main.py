# LangSmith integration for observability and monitoring
# This allows tracking of AI requests, responses, and performance metrics
# To enable, set LANGCHAIN_TRACING_V2=true and LANGCHAIN_ENDPOINT/API_KEY

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
