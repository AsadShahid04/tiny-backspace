import logging
import time
from fastapi import Request, FastAPI
from typing import Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def logging_middleware(request: Request, call_next: Callable):
    start_time = time.time()
    
    # Log request details
    logger.info(f"Request started: {request.method} {request.url}")
    logger.info(f"Client IP: {request.client.host}")
    logger.info(f"Headers: {dict(request.headers)}")
    
    try:
        # Process the request
        response = await call_next(request)
        
        # Log response details
        process_time = time.time() - start_time
        logger.info(f"Request completed: {request.method} {request.url}")
        logger.info(f"Status code: {response.status_code}")
        logger.info(f"Process time: {process_time:.2f}s")
        
        return response
        
    except Exception as e:
        # Log any errors
        logger.error(f"Request failed: {str(e)}")
        raise e