"""
production_rag.main - Main Application Entrypoint
"""

import sys
import os

# Guarantee project root directory is in sys.path so imports work from any working directory
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import uvicorn
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from production_rag.app.api import app
from production_rag.config.settings import settings

# Path to React frontend folder
frontend_dir = os.path.join(settings.BASE_DIR, "frontend")

@app.get("/", include_in_schema=False)
def serve_react_app():
    """Serve the single-page React frontend application."""
    index_file = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "React frontend index.html not found."}

def main():
    """Entrypoint function to run Uvicorn server."""
    print("====================================================================")
    print(f"STARTING {settings.PROJECT_NAME} v{settings.VERSION}")
    print("Serving React Frontend and REST API on http://127.0.0.1:8000")
    print("====================================================================")
    uvicorn.run("production_rag.main:app", host="127.0.0.1", port=8000, reload=False)

if __name__ == "__main__":
    main()
