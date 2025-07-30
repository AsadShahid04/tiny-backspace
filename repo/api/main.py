from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import code
import simple_observability

app = FastAPI()
logger = simple_observability.get_logger()

# Add health check endpoint
@app.get("/health")
async def health_check():
    """
    Simple health check endpoint to verify API is running
    Returns:
        dict: Status message indicating API health
    """
    return {"status": "healthy", "message": "API is running"}

# Keep existing endpoints below
@app.post("/process")
async def process_code(request: code.CodeRequest):
    try:
        logger.info(f"Processing request: {request}")
        result = code.process_code(request)
        return result
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))