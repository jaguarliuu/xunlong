# DeepSearch Dockerfile

FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装Playwright浏览器
RUN python -m playwright install chromium
RUN python -m playwright install-deps chromium

# 复制源代码
COPY src/ ./src/
COPY main.py run_api.py ./

# 创建截图目录
RUN mkdir -p /app/shots

# 设置环境变量
ENV BROWSER_HEADLESS=true
ENV DEEPSEARCH_SHOTS_DIR=/app/shots

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# 启动API服务
CMD ["python", "run_api.py"]