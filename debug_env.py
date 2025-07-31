#!/usr/bin/env python3
"""
Debug script to check environment variables
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Environment Variables Check:")
print("=" * 40)
print(f"GITHUB_PAT: {os.getenv('GITHUB_PAT', 'NOT SET')[:20]}...")
print(f"ANTHROPIC_API_KEY: {os.getenv('ANTHROPIC_API_KEY', 'NOT SET')[:20]}...")
print(f"E2B_API_KEY: {os.getenv('E2B_API_KEY', 'NOT SET')[:20]}...")
print(f"OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY', 'NOT SET')[:20]}...")

# Test the validation logic
github_token = os.getenv('GITHUB_PAT') or os.getenv('GITHUB_TOKEN')
anthropic_key = os.getenv('ANTHROPIC_API_KEY')
openai_key = os.getenv('OPENAI_API_KEY')

print("\nValidation Logic Test:")
print("=" * 40)
print(f"github_token: {github_token[:20] if github_token else 'NOT SET'}...")
print(f"anthropic_key: {anthropic_key[:20] if anthropic_key else 'NOT SET'}...")
print(f"openai_key: {openai_key[:20] if openai_key else 'NOT SET'}...")

if not github_token:
    print("❌ GITHUB_PAT or GITHUB_TOKEN is missing")
else:
    print("✅ GITHUB_PAT or GITHUB_TOKEN is set")

if not anthropic_key and not openai_key:
    print("❌ Both ANTHROPIC_API_KEY and OPENAI_API_KEY are missing")
else:
    print("✅ At least one AI API key is set") 