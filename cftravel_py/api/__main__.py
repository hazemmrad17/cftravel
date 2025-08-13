"""
Entry point for running the Semantic API as a module.
Usage:
  python -m cftravel_py.api
"""
import os
from .semantic_api import app

if __name__ == "__main__":
    import uvicorn
    
    # Environment-based configuration
    host = os.getenv("API_HOST", "0.0.0.0")
    
    # Use different ports for local vs production
    if os.getenv("ENVIRONMENT", "local") == "production":
        port = int(os.getenv("API_PORT", "8000"))
    else:
        port = int(os.getenv("API_PORT", "8002"))
    
    print(f"🚀 Starting CFTravel Semantic Search API on {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")