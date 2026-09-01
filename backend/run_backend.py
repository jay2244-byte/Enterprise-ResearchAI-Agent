import sys
import os
import uvicorn

# Add workspace directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.config import settings

if __name__ == "__main__":
    print(f"Starting {settings.PROJECT_NAME} Backend on http://{settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "backend.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
