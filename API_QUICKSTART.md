# XunLong API 快速开始

## 目录结构概览

```
api/                                # 新 API 根目录
├── core/                          # 核心功能
│   ├── config.py                  # 配置管理 (环境变量)
│   ├── exceptions.py              # 自定义异常
│   └── middleware.py              # 中间件 (日志/错误/性能)
│
├── models/                        # 领域模型
│   ├── enums.py                   # TaskStatus, TaskType 等枚举
│   └── task.py                    # Task 数据模型
│
├── v1/                            # API v1
│   ├── routes/                    # 路由层 (HTTP 端点)
│   │   ├── health.py              # 健康检查
│   │   └── tasks.py               # 任务管理
│   │
│   ├── schemas/                   # Pydantic 请求/响应模式
│   │   ├── common.py              # 通用模式
│   │   └── task.py                # 任务相关模式
│   │
│   ├── services/                  # 业务逻辑层
│   │   └── task_service.py        # 任务管理服务
│   │
│   └── dependencies/              # 依赖注入 (预留)
│
└── main.py                        # FastAPI 应用入口

workers/                           # 后台任务处理器
└── task_worker.py                 # 异步任务执行

run_server.py                      # 启动 API 服务器
run_worker.py                      # 启动 Worker
```

## 安装依赖

确保已安装所需的 Python 包（如果尚未安装）：

```bash
pip install fastapi uvicorn pydantic-settings loguru
```

## 启动服务

### 1. 启动 API 服务器

```bash
python run_server.py
```

输出示例：
```
2025-01-15 10:30:00 | INFO     | Starting XunLong API v2.0.0
2025-01-15 10:30:00 | INFO     | Server: 0.0.0.0:8000
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 2. 启动 Worker（新终端）

```bash
python run_worker.py
```

输出示例：
```
2025-01-15 10:31:00 | INFO     | Starting XunLong Task Worker
2025-01-15 10:31:00 | INFO     | TaskWorker started
```

## 测试 API

### 方式 1: 使用 Swagger UI (推荐)

打开浏览器访问: **http://localhost:8000/docs**

这是交互式 API 文档，可以直接测试所有端点。

### 方式 2: 使用 curl

#### 健康检查

```bash
curl http://localhost:8000/health
```

响应：
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "timestamp": "2025-01-15T10:30:00.000000"
}
```

#### 创建报告任务

```bash
curl -X POST http://localhost:8000/api/v1/tasks/report \
  -H "Content-Type: application/json" \
  -d '{
    "query": "人工智能技术发展趋势",
    "report_type": "comprehensive",
    "search_depth": "deep",
    "max_results": 20,
    "output_format": "html"
  }'
```

响应：
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Report task created successfully"
}
```

#### 查询任务状态

```bash
curl http://localhost:8000/api/v1/tasks/550e8400-e29b-41d4-a716-446655440000
```

响应：
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_type": "report",
  "status": "running",
  "progress": {
    "percentage": 45,
    "current_step": "Generating report outline",
    "total_steps": 8,
    "completed_steps": 3
  },
  "created_at": "2025-01-15T10:30:00Z",
  "started_at": "2025-01-15T10:30:05Z"
}
```

#### 列出所有任务

```bash
curl "http://localhost:8000/api/v1/tasks?page=1&page_size=10"
```

#### 创建小说任务

```bash
curl -X POST http://localhost:8000/api/v1/tasks/fiction \
  -H "Content-Type: application/json" \
  -d '{
    "query": "一个关于时间旅行的科幻故事",
    "genre": "scifi",
    "length": "medium",
    "viewpoint": "third",
    "output_format": "html"
  }'
```

#### 创建 PPT 任务

```bash
curl -X POST http://localhost:8000/api/v1/tasks/ppt \
  -H "Content-Type: application/json" \
  -d '{
    "query": "区块链技术商业应用",
    "target_slides": 15,
    "style": "business",
    "theme": "corporate-blue"
  }'
```

## 环境变量配置

创建 `.env` 文件自定义配置：

```bash
# .env
APP_NAME=XunLong API
DEBUG=false
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# 任务配置
TASK_STORAGE_DIR=tasks
MAX_CONCURRENT_TASKS=10

# Worker 配置
WORKER_POLL_INTERVAL=2.0
WORKER_MAX_RETRIES=3
```

## 开发模式

启用自动重载（代码修改后自动重启）：

```bash
# 方式 1: 环境变量
RELOAD=true python run_server.py

# 方式 2: 直接使用 uvicorn
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

## API 文档

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 目录说明

### 已删除的旧文件

以下旧 API 文件已被删除：

- `src/api.py` → 替换为 `api/main.py` + `api/v1/routes/tasks.py`
- `src/api_agent.py` → 功能合并到新架构
- `src/task_manager.py` → 替换为 `api/v1/services/task_service.py`
- `src/task_worker.py` → 替换为 `workers/task_worker.py`
- `run_api.py` → 替换为 `run_server.py`
- `start_worker.py` → 替换为 `run_worker.py`
- `start.py` → 待实现（可选）
- `examples/api_client.py` → 待重新实现
- `examples/async_api_client.py` → 待重新实现

### 新增的文件

**核心 API 模块 (api/)**

- `api/main.py` - FastAPI 应用入口
- `api/core/config.py` - 配置管理
- `api/core/exceptions.py` - 自定义异常
- `api/core/middleware.py` - 中间件
- `api/models/enums.py` - 枚举类型
- `api/models/task.py` - Task 数据模型

**API v1 (api/v1/)**

- `api/v1/routes/health.py` - 健康检查端点
- `api/v1/routes/tasks.py` - 任务管理端点
- `api/v1/schemas/common.py` - 通用请求/响应模式
- `api/v1/schemas/task.py` - 任务相关模式
- `api/v1/services/task_service.py` - 任务管理业务逻辑

**后台 Worker (workers/)**

- `workers/task_worker.py` - 异步任务处理器

**启动脚本**

- `run_server.py` - API 服务器启动器
- `run_worker.py` - Worker 启动器

**文档**

- `API_ARCHITECTURE.md` - 详细架构文档
- `API_QUICKSTART.md` - 快速开始指南（本文档）

## 架构特点

### 1. 分层架构

```
Routes (HTTP) → Services (Business) → Models (Domain)
```

### 2. 异步处理

- API 立即返回 task_id
- Worker 在后台异步执行任务
- 客户端轮询任务状态

### 3. 文件存储

- 任务元数据: `tasks/{task_id}.json`
- 生成内容: `storage/{project_id}/`

### 4. 中间件栈

- 错误处理
- 性能监控（检测慢请求）
- 请求日志
- Request-ID 追踪
- CORS

### 5. 类型安全

- Pydantic 模型提供完整的类型验证
- 自动生成 OpenAPI 文档

## 下一步工作

当前 API 框架已完成，但 Worker 中的任务执行是占位符实现。

**需要集成的现有模块:**

1. **Agent 集成** - 连接到 `src/agents/`
   - Report: `src/agents/report/`
   - Fiction: `src/agents/fiction/`
   - PPT: `src/agents/ppt/`

2. **LLM 管理器** - `src/llm/`
3. **导出管理器** - `src/export/`
4. **存储管理器** - `src/storage/`

集成点在 `workers/task_worker.py` 的 `_execute_*_task()` 方法中。

## 故障排除

### 端口被占用

```bash
# 查找占用 8000 端口的进程
lsof -ti:8000

# 杀死进程
kill -9 $(lsof -ti:8000)

# 或使用其他端口
PORT=8001 python run_server.py
```

### Worker 没有处理任务

1. 检查 Worker 是否正在运行
2. 检查 `tasks/` 目录是否存在并包含待处理任务
3. 查看 Worker 日志输出

### 无法导入模块

确保从项目根目录运行：

```bash
cd /path/to/XunLong
python run_server.py
```

## 总结

新的 API 架构具有：

✅ 清晰的分层结构
✅ 类型安全的请求/响应
✅ 完整的中间件支持
✅ 异步任务处理
✅ 自动生成的 API 文档
✅ 易于扩展和维护

可以在此基础上继续开发业务功能！
