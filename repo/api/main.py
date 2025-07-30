from fastapi import FastAPI
from .middleware import logging_middleware
from .code import process_code
import uvicorn

app = FastAPI()

# Add logging middleware
app.middleware("http")(logging_middleware)

@app.post("/process")
async def process_endpoint(code: str):
    return {"result": process_code(code)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)