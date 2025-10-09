"""API"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.api:app",  # reload
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )