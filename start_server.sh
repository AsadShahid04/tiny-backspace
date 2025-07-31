#!/bin/bash

# Load environment variables
export $(cat .env | xargs)

# Verify environment variables are loaded
echo "Environment variables loaded:"
echo "GITHUB_PAT: ${GITHUB_PAT:+SET}"
echo "ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:+SET}"
echo "E2B_API_KEY: ${E2B_API_KEY:+SET}"

# Activate virtual environment and start server
source venv/bin/activate
python api/main.py 