import os
from e2b.sandbox import Sandbox

def run_in_sandbox(commands, api_key=None):
    sandbox = Sandbox(api_key=api_key or os.getenv("E2B_API_KEY"))
    try:
        process = sandbox.process.start("bash")
        for cmd in commands:
            output = process.run(cmd)
            yield output.output
    finally:
        sandbox.close() 