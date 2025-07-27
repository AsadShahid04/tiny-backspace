from dotenv import load_dotenv
load_dotenv()  # This will load variables from .env into os.environ

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.logging_config import setup_logging

setup_logging()

app = FastAPI(
    title="Code Processing API",
    description="FastAPI backend for processing code repositories with AI agents",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router) 