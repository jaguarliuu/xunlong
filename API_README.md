# XunLong API 使用指南

XunLong提供异步API，支持通过HTTP请求生成报告、小说和PPT。

## 快速开始

### 方式一：使用启动脚本（推荐）

```bash
# 启动所有服务（API + Worker）
./scripts/start_all.sh

# 停止所有服务
./scripts/stop_all.sh
```

### 方式二：手动启动

```bash
# 终端1: 启动API服务器
python run_api.py

# 终端2: 启动任务执行器
python start_worker.py
```

### 测试API

```bash
# 运行测试脚本
python scripts/test_api.py

# 或直接访问
curl http://localhost:8000/health
```

## API端点

### 创建任务

```bash
# 创建报告任务
curl -X POST http://localhost:8000/api/v1/tasks/report \
  -H "Content-Type: application/json" \
  -d '{
    "query": "人工智能在医疗领域的应用",
    "report_type": "comprehensive",
    "search_depth": "deep"
  }'

# 创建小说任务
curl -X POST http://localhost:8000/api/v1/tasks/fiction \
  -H "Content-Type: application/json" \
  -d '{
    "query": "一个科幻推理故事",
    "genre": "scifi",
    "length": "short"
  }'

# 创建PPT任务
curl -X POST http://localhost:8000/api/v1/tasks/ppt \
  -H "Content-Type: application/json" \
  -d '{
    "query": "产品发布策略",
    "slides": 15,
    "style": "business"
  }'
```

### 查询任务状态

```bash
# 获取任务状态
curl http://localhost:8000/api/v1/tasks/{task_id}

# 获取任务结果（完成后）
curl http://localhost:8000/api/v1/tasks/{task_id}/result

# 下载生成的文件
curl -O http://localhost:8000/api/v1/tasks/{task_id}/download?file_type=html
```

### 管理任务

```bash
# 列出所有任务
curl http://localhost:8000/api/v1/tasks

# 筛选任务
curl http://localhost:8000/api/v1/tasks?status=completed&limit=10

# 取消任务
curl -X DELETE http://localhost:8000/api/v1/tasks/{task_id}
```

## Python客户端

```python
from examples.async_api_client import XunLongAsyncClient

# 创建客户端
client = XunLongAsyncClient()

# 创建报告任务
task = client.create_report(
    query="人工智能发展趋势",
    report_type="comprehensive",
    search_depth="deep"
)

# 等待完成（自动轮询）
result = client.wait_for_completion(task['task_id'], verbose=True)

# 下载文件
file_path = client.download_file(task['task_id'], file_type="html")
print(f"文件已保存: {file_path}")
```

## 完整示例

查看 `examples/async_api_client.py` 获取更多示例：

```bash
# 运行示例
python examples/async_api_client.py
```

## API文档

启动API服务器后，访问：

- **交互式文档**: http://localhost:8000/docs
- **API信息**: http://localhost:8000/
- **健康检查**: http://localhost:8000/health

## 日志

服务日志位于：

- API日志: `logs/api.log`
- Worker日志: `logs/worker.log`

查看实时日志：

```bash
# API日志
tail -f logs/api.log

# Worker日志
tail -f logs/worker.log
```

## 任务存储

任务数据存储在 `tasks/` 目录：

```
tasks/
├── {task-id-1}.json
├── {task-id-2}.json
└── ...
```

生成的内容存储在 `storage/` 目录：

```
storage/
├── {project-id}/
│   ├── reports/
│   │   └── FINAL_REPORT.html
│   └── exports/
│       └── report.pdf
```

## 故障排除

### API服务器无法访问

```bash
# 检查服务是否运行
curl http://localhost:8000/health

# 如果失败，重新启动
python run_api.py
```

### 任务一直处于pending状态

```bash
# 检查worker是否运行
ps aux | grep start_worker

# 如果没有运行，启动worker
python start_worker.py
```

### 查看错误日志

```bash
# 查看API错误
tail -100 logs/api.log

# 查看Worker错误
tail -100 logs/worker.log
```

## 生产环境部署

### 使用systemd

创建服务文件 `/etc/systemd/system/xunlong-api.service`:

```ini
[Unit]
Description=XunLong API Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/xunlong
ExecStart=/opt/xunlong/venv/bin/python run_api.py
Restart=always

[Install]
WantedBy=multi-user.target
```

创建worker服务文件 `/etc/systemd/system/xunlong-worker.service`:

```ini
[Unit]
Description=XunLong Task Worker
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/xunlong
ExecStart=/opt/xunlong/venv/bin/python start_worker.py
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl enable xunlong-api xunlong-worker
sudo systemctl start xunlong-api xunlong-worker
sudo systemctl status xunlong-api xunlong-worker
```

### 使用nginx反向代理

```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## 更多信息

- 完整文档: [docs/guide/api-usage.md](docs/guide/api-usage.md)
- 中文文档: [docs/zh/guide/api-usage.md](docs/zh/guide/api-usage.md)
- 项目主页: https://jaguarliuu.github.io/xunlong/
