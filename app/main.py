from dotenv import load_dotenv
load_dotenv()  # This will load variables from .env into os.environ

from fastapi import FastAPI
from app.api.routes import router
from app.logging_config import setup_logging

setup_logging()
app = FastAPI()
app.include_router(router) 