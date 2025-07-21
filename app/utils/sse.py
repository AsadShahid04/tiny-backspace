from sse_starlette.sse import EventSourceResponse

async def sse_event_generator(messages):
    for msg in messages:
        yield {"data": msg} 