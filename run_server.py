#!/usr/bin/env python3
"""
Simple script to run the FastAPI server.
"""

import os
import sys

def main():
    """Run the FastAPI server."""
    try:
        # Import uvicorn
        import uvicorn
        
        # Set environment variables if not set
        if not os.getenv("E2B_API_KEY"):
            print("⚠️  Warning: E2B_API_KEY not set. The /code endpoint may fail.")
        
        print("🚀 Starting FastAPI server...")
        print("📖 API Documentation will be available at: http://localhost:8000/docs")
        print("🔄 Test the /code endpoint at: http://localhost:8000/code")
        print("🧪 Test the dummy streaming at: http://localhost:8000/stream-dummy")
        print("-" * 60)
        
        # Run the server
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you've activated the virtual environment and installed dependencies:")
        print("   source venv/bin/activate")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()