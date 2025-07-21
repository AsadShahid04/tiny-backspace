from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from app.services.agent import run_agent

router = APIRouter()

@router.post("/code")
async def code_endpoint(request: Request):
    data = await request.json()
    repo_url = data.get("repoUrl")
    prompt = data.get("prompt")
    async def event_stream():
        async for msg in run_agent(repo_url, prompt):
            yield f"data: {msg}\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream")

@router.get("/stream-dummy")
async def stream_dummy():
    async def dummy_stream():
        import asyncio
        for i in range(5):
            yield f"data: {{'step': {i}}}\n\n"
            await asyncio.sleep(1)
    return StreamingResponse(dummy_stream(), media_type="text/event-stream") 