from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.services.code_processor import process_code_request
import json
from loguru import logger

router = APIRouter()

class CodeRequest(BaseModel):
    repoUrl: str
    prompt: str

@router.post("/code")
async def code_endpoint(request: CodeRequest):
    """
    Process a code request by cloning a repo and streaming status updates via SSE.
    """
    try:
        logger.info(f"Received code request for repo: {request.repoUrl}")
        
        async def event_stream():
            try:
                async for status_update in process_code_request(request.repoUrl, request.prompt):
                    yield f"data: {json.dumps(status_update)}\n\n"
            except Exception as e:
                logger.error(f"Error in event stream: {str(e)}")
                error_msg = {
                    "type": "error",
                    "message": f"Processing failed: {str(e)}",
                    "timestamp": str(int(__import__('time').time() * 1000))
                }
                yield f"data: {json.dumps(error_msg)}\n\n"
        
        return StreamingResponse(
            event_stream(), 
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # Disable nginx buffering
            }
        )
    except Exception as e:
        logger.error(f"Failed to process code request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stream-dummy")
async def stream_dummy():
    async def dummy_stream():
        import asyncio
        for i in range(5):
            yield f"data: {{'step': {i}}}\n\n"
            await asyncio.sleep(1)
    return StreamingResponse(dummy_stream(), media_type="text/event-stream") 