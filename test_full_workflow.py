#!/usr/bin/env python3
"""
Complete E2B Sandbox + Claude Code Workflow Test
"""
import asyncio
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_full_workflow():
    """Test the complete E2B sandbox + Claude Code workflow"""
    
    print("🧪 Testing Complete E2B Sandbox + Claude Code Workflow")
    print("=" * 60)
    
    # Check environment variables
    github_token = os.getenv('GITHUB_PAT') or os.getenv('GITHUB_TOKEN')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    e2b_api_key = os.getenv('E2B_API_KEY')
    
    print(f"✅ E2B_API_KEY: {'Set' if e2b_api_key else 'Not set'}")
    print(f"✅ ANTHROPIC_API_KEY: {'Set' if anthropic_key else 'Not set'}")
    print(f"✅ GITHUB_PAT: {'Set' if github_token else 'Not set'}")
    
    if not all([e2b_api_key, anthropic_key, github_token]):
        print("❌ Missing required environment variables")
        return
    
    sandbox = None
    try:
        # Step 1: Create E2B Sandbox
        print("\n🚀 Step 1: Creating E2B Sandbox...")
        from e2b import Sandbox
        
        sandbox = Sandbox(
            template="base",
            metadata={
                'type': 'tiny_backspace_sandbox',
                'request_id': 'test-123'
            }
        )
        
        print(f"✅ Sandbox created with ID: {sandbox.sandbox_id}")
        
        # Step 2: Clone Repository
        print("\n📥 Step 2: Cloning Repository...")
        repo_url = "https://github.com/AsadShahid04/tiny-backspace"
        
        result = sandbox.commands.run(f'git clone {repo_url} repo')
        print(f"✅ Repository cloned: {result}")
        
        # Step 3: Setup Claude Code
        print("\n🔧 Step 3: Setting up Claude Code...")
        
        # Install required packages
        result = sandbox.commands.run('pip install anthropic')
        print(f"✅ Anthropic installed: {result}")
        
        result = sandbox.commands.run('pip install requests')
        print(f"✅ Requests installed: {result}")
        
        # Step 4: Analyze Repository
        print("\n🔍 Step 4: Analyzing Repository...")
        
        result = sandbox.commands.run('find repo -type f -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.md" -o -name "*.txt" | head -10')
        files = result.stdout.strip().split('\n') if result.stdout else []
        
        print(f"✅ Found {len(files)} files:")
        for file in files[:5]:  # Show first 5 files
            print(f"   - {file}")
        
        # Step 5: Generate Code with Claude
        print("\n🤖 Step 5: Generating Code with Claude...")
        
        prompt = "Add a simple logging feature to track API requests"
        
        claude_script = f'''
import anthropic
import json
import os

client = anthropic.Anthropic(api_key="{anthropic_key}")

message = f"""
You are an expert AI coding assistant. Analyze this repository and generate code modifications based on the user's prompt.

Repository Information:
- Files found: {files}

User Request: {prompt}

Please analyze the repository structure and generate appropriate code modifications.
Focus on the most relevant files for the user's request.

Generate file edits in this exact format:
```python:file_path
new content here
```

Be specific and provide meaningful improvements based on the user's prompt.
"""

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=4000,
    messages=[{{"role": "user", "content": message}}]
)

print(json.dumps({{
    "content": response.content[0].text,
    "model": response.model,
    "usage": {{
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens
    }}
}}))
'''
        
        # Write Claude script to sandbox
        sandbox.files.write('/home/user/claude_code.py', claude_script)
        print("✅ Claude script written to sandbox")
        
        # Execute Claude script
        result = sandbox.commands.run('python claude_code.py')
        print(f"✅ Claude script executed: {result}")
        
        if result.stdout:
            try:
                claude_response = json.loads(result.stdout)
                content = claude_response.get('content', '')
                
                print(f"✅ Claude response received ({len(content)} characters)")
                print(f"📊 Token usage: {claude_response.get('usage', {})}")
                
                # Parse the response into file edits
                import re
                pattern = r'```(\w+):([^\n]+)\n(.*?)```'
                matches = re.findall(pattern, content, re.DOTALL)
                
                edits = []
                for file_ext, file_path, file_content in matches:
                    edits.append({
                        'file_path': file_path.strip(),
                        'new_content': file_content.strip(),
                        'description': f'AI-generated modification for {file_path}'
                    })
                
                print(f"✅ Parsed {len(edits)} file edits from Claude response")
                
                # Step 6: Apply Changes
                print("\n✏️ Step 6: Applying Changes...")
                
                for i, edit in enumerate(edits):
                    file_path = edit['file_path']
                    new_content = edit['new_content']
                    
                    print(f"   Applying edit {i+1}/{len(edits)}: {file_path}")
                    
                    # Write the new content to the file
                    full_path = f'/home/user/repo/{file_path}'
                    sandbox.files.write(full_path, new_content)
                
                print("✅ All changes applied successfully")
                
                # Step 7: Test the changes
                print("\n🧪 Step 7: Testing Changes...")
                
                # List the modified files
                result = sandbox.commands.run('find repo -name "*.py" -exec ls -la {} \\;')
                print(f"✅ Files in repo: {result}")
                
                print("\n🎉 SUCCESS! Complete workflow tested successfully!")
                print(f"📝 Generated {len(edits)} file modifications")
                print(f"🤖 Used Claude model: {claude_response.get('model', 'Unknown')}")
                
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse Claude response: {e}")
                print(f"Raw output: {result.stdout}")
            except Exception as e:
                print(f"❌ Error processing Claude response: {e}")
        else:
            print(f"❌ Claude script produced no output: {result.stderr}")
        
    except Exception as e:
        print(f"❌ Error in workflow: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        if sandbox:
            print("\n🧹 Cleaning up sandbox...")
            try:
                sandbox.kill()
                print("✅ Sandbox cleaned up successfully")
            except Exception as e:
                print(f"⚠️ Cleanup warning: {e}")

if __name__ == "__main__":
    asyncio.run(test_full_workflow()) 