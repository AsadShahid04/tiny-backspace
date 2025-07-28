from dotenv import load_dotenv
load_dotenv()
from e2b_code_interpreter import Sandbox

sbx = Sandbox()

code = '''
import subprocess

commands = [
    "git clone https://github.com/AsadShahid04/postit.git",
    "cd postit && echo 'This is a test file' > testfile.txt",
    "cd postit && git add testfile.txt",
    "cd postit && git config user.email 'sandbox@example.com'",
    "cd postit && git config user.name 'sandbox-bot'",
    "cd postit && git commit -m 'Add test file from sandbox'",
    "cd postit && ls -l"
]

for cmd in commands:
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)
'''

execution = sbx.run_code(code)
print("LOGS:")
print(execution.logs)

files = sbx.files.list("/")
print("FILES IN ROOT:")
print(files)