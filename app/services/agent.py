import os
from app.services.sandbox import run_in_sandbox

async def run_agent(repo_url: str, prompt: str):
    repo_name = repo_url.rstrip('.git').split('/')[-1]
    github_pat = os.getenv("GITHUB_PAT")
    github_username = os.getenv("GITHUB_USERNAME")
    github_email = os.getenv("GITHUB_EMAIL")

    commands = [
        f"git clone {repo_url}",
        f"cd {repo_name} && pip install -r requirements.txt",
        f"cd {repo_name} && echo 'Pretend to edit code for: {prompt}'",
        f"cd {repo_name} && git checkout -b feature/auto-change",
        f"cd {repo_name} && git config user.email '{github_email}'",
        f"cd {repo_name} && git config user.name '{github_username}'",
        f"cd {repo_name} && git add .",
        f"cd {repo_name} && git commit -m 'Automated code change: {prompt}'",
        f"cd {repo_name} && git push https://{github_pat}@github.com/{github_username}/{repo_name}.git feature/auto-change",
        f"cd {repo_name} && gh pr create --title 'Automated PR' --body 'This PR was created by an agent' --head feature/auto-change"
    ]

    # Use a queue to bridge the callback to async generator
    import asyncio
    queue = asyncio.Queue()

    def stream_callback(type_, data):
        asyncio.get_event_loop().call_soon_threadsafe(queue.put_nowait, {"type": type_, "output": data})

    # Run the sandbox in a thread to avoid blocking
    import threading
    thread = threading.Thread(target=run_in_sandbox, args=(commands, stream_callback))
    thread.start()

    while True:
        event = await queue.get()
        yield event
        if event["type"] == "error":
            break
    thread.join() 