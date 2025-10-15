"""启动API服务器"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.api:app",  # 使用导入字符串以支持reload
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config="log_config.json"
    )