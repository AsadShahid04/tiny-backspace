import os
from app.services.sandbox import run_in_sandbox

async def run_agent(repo_url: str, prompt: str):
    repo_name = repo_url.rstrip('.git').split('/')[-1]
    commands = [
        f"git clone {repo_url}",
        f"cd {repo_name} && pip install -r requirements.txt",
        f"cd {repo_name} && echo 'Pretend to edit code for: {prompt}'",
    ]
    for step, output in enumerate(run_in_sandbox(commands)):
        yield {"type": "step", "step": step, "output": output}
    yield {"type": "result", "pr_url": "https://github.com/example/repo/pull/1"} 