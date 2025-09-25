"""启动API服务器"""

import uvicorn
from src.api import app

if __name__ == "__main__":
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        reload=True
    )