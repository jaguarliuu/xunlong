# DeepSearch 部署指南

## 🚀 快速部署

### 1. 环境要求
- Python 3.10+
- Windows/Linux/macOS
- 至少 2GB 内存
- 稳定的网络连接

### 2. 一键安装
```bash
# 克隆项目
git clone <repository-url>
cd deepsearch-codebuddy

# 快速安装
python quick_start.py
```

### 3. 手动安装
```bash
# 安装依赖
pip install -r requirements.txt

# 安装浏览器
python -m playwright install chromium

# 测试安装
python basic_test.py
```

## 🔧 配置选项

### 环境变量配置
```bash
# 浏览器模式
export BROWSER_HEADLESS=true          # true=无头模式, false=显示浏览器

# 搜索配置
export DEEPSEARCH_TOPK=5              # 默认抓取数量
export DEEPSEARCH_SEARCH_ENGINE=duckduckgo  # 搜索引擎
export DEEPSEARCH_SHOTS_DIR=./shots   # 截图保存目录

# 浏览器配置
export DEEPSEARCH_BROWSER_TIMEOUT=30000      # 浏览器超时(毫秒)
export DEEPSEARCH_PAGE_WAIT_TIME=3000        # 页面等待时间(毫秒)
```

### 配置文件
修改 `src/config.py` 中的 `DeepSearchConfig` 类来自定义默认配置。

## 📱 使用方式

### CLI 命令行
```bash
# 基本搜索
python main.py search "Python教程"

# 高级选项
python main.py search "机器学习" \
  --topk 10 \
  --no-headless \
  --output results.json \
  --shots-dir ./screenshots \
  --verbose

# 安装浏览器
python main.py install-browser
```

### REST API 服务
```bash
# 启动API服务
python run_api.py

# 服务将在 http://localhost:8000 启动
# API文档: http://localhost:8000/docs
```

#### API 端点
- `GET /` - 服务信息
- `GET /health` - 健康检查
- `GET /config` - 获取配置
- `GET /search?q=查询词&k=5&engine=duckduckgo&headless=true` - 搜索

#### API 使用示例
```bash
# 搜索请求
curl "http://localhost:8000/search?q=Python&k=3"

# 健康检查
curl "http://localhost:8000/health"
```

## 🐳 Docker 部署

### 构建镜像
```bash
docker build -t deepsearch:latest .
```

### 运行容器
```bash
# 基本运行
docker run -p 8000:8000 deepsearch:latest

# 挂载数据卷
docker run -p 8000:8000 -v $(pwd)/shots:/app/shots deepsearch:latest

# 环境变量配置
docker run -p 8000:8000 \
  -e BROWSER_HEADLESS=true \
  -e DEEPSEARCH_TOPK=10 \
  deepsearch:latest
```

### Docker Compose
```yaml
version: '3.8'
services:
  deepsearch:
    build: .
    ports:
      - "8000:8000"
    environment:
      - BROWSER_HEADLESS=true
      - DEEPSEARCH_TOPK=5
    volumes:
      - ./shots:/app/shots
    restart: unless-stopped
```

## 🔧 开发部署

### 开发环境设置
```bash
# 安装开发依赖
make install-dev

# 或手动安装
pip install black isort flake8 pytest
```

### 开发工具
```bash
make help          # 查看所有命令
make test          # 运行测试
make lint          # 代码检查
make format        # 格式化代码
make run-api       # 启动API服务
make clean         # 清理临时文件
```

### 代码结构
```
src/
├── config.py      # 配置管理
├── models.py      # 数据模型
├── browser.py     # 浏览器控制
├── extractor.py   # 内容抽取
├── pipeline.py    # 主流程
├── cli.py         # CLI接口
├── api.py         # REST API
└── searcher/      # 搜索器模块
    ├── base.py    # 基类
    └── duckduckgo.py  # DuckDuckGo实现
```

## 🚀 生产部署

### 系统服务 (Linux)
```bash
# 创建服务文件
sudo tee /etc/systemd/system/deepsearch.service > /dev/null <<EOF
[Unit]
Description=DeepSearch API Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/deepsearch
Environment=BROWSER_HEADLESS=true
Environment=DEEPSEARCH_TOPK=5
ExecStart=/opt/deepsearch/venv/bin/python run_api.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
sudo systemctl daemon-reload
sudo systemctl enable deepsearch
sudo systemctl start deepsearch
```

### Nginx 反向代理
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
```

### 性能优化
1. **并发设置**: 调整 uvicorn 的 workers 数量
2. **缓存**: 实现搜索结果缓存
3. **限流**: 添加 API 请求限制
4. **监控**: 集成日志和监控系统

### 安全配置
1. **HTTPS**: 使用 SSL/TLS 证书
2. **认证**: 添加 API 密钥验证
3. **防火墙**: 限制访问端口
4. **更新**: 定期更新依赖包

## 🔍 故障排除

### 常见问题

#### 1. 浏览器安装失败
```bash
# 手动安装
python -m playwright install chromium --with-deps

# 或使用系统包管理器
sudo apt-get install chromium-browser  # Ubuntu
brew install chromium                  # macOS
```

#### 2. 搜索结果为空
- 检查网络连接
- 尝试使用有头模式调试: `--no-headless`
- 检查DuckDuckGo是否可访问

#### 3. 内存不足
- 减少并发数量
- 增加系统内存
- 使用无头模式

#### 4. 权限问题
```bash
# Linux/macOS
chmod +x main.py run_api.py
sudo chown -R $USER:$USER ./shots
```

### 日志调试
```bash
# 启用详细日志
python main.py search "查询词" --verbose

# 查看API日志
python run_api.py --log-level debug
```

### 性能监控
- 监控内存使用: `htop` 或 `top`
- 监控网络: `netstat -an | grep 8000`
- 监控磁盘: `df -h`

## 📞 支持

如果遇到问题，请：
1. 查看日志文件
2. 运行 `python basic_test.py` 检查环境
3. 检查网络连接和防火墙设置
4. 提交 Issue 并附上错误日志

## 🔄 更新升级

```bash
# 备份配置
cp src/config.py src/config.py.bak

# 更新代码
git pull origin main

# 更新依赖
pip install -r requirements.txt --upgrade

# 重新安装浏览器
python -m playwright install chromium

# 测试更新
python basic_test.py