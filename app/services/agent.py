import asyncio

async def run_agent(repo_url: str, prompt: str):
    # Dummy implementation: yield fake progress updates
    yield {"type": "info", "message": f"Cloning repo {repo_url}"}
    await asyncio.sleep(1)
    yield {"type": "info", "message": f"Analyzing prompt: {prompt}"}
    await asyncio.sleep(1)
    yield {"type": "info", "message": "Making code changes..."}
    await asyncio.sleep(1)
    yield {"type": "info", "message": "Committing changes and creating PR..."}
    await asyncio.sleep(1)
    yield {"type": "result", "pr_url": "https://github.com/example/repo/pull/1"} 