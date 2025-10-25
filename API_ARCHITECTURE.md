# XunLong API 架构文档 v2.0

## 概述

这是 XunLong (DeepSearch) 项目全新设计的 RESTful API 架构。采用现代化、分层的设计模式，具有高度的可扩展性和可维护性。

## 技术栈

- **Web 框架**: FastAPI (异步、高性能)
- **验证**: Pydantic v2 (数据验证和序列化)
- **服务器**: Uvicorn (ASGI 服务器)
- **日志**: Loguru (结构化日志)
- **架构模式**: 分层架构 (Routes → Services → Models)

## 项目结构

```
XunLong/
├── api/                          # API 根目录
│   ├── __init__.py
│   ├── main.py                   # FastAPI 应用入口
│   │
│   ├── core/                     # 核心功能模块
│   │   ├── config.py             # 配置管理 (基于环境变量)
│   │   ├── exceptions.py         # 自定义异常
│   │   └── middleware.py         # 中间件 (日志、错误处理、性能监控)
│   │
│   ├── models/                   # 数据模型
│   │   ├── enums.py              # 枚举类型 (TaskStatus, TaskType, etc.)
│   │   └── task.py               # Task 领域模型
│   │
│   └── v1/                       # API v1 版本
│       ├── routes/               # 路由层 (端点定义)
│       │   ├── health.py         # 健康检查
│       │   └── tasks.py          # 任务管理端点
│       │
│       ├── schemas/              # Pydantic 模式 (请求/响应)
│       │   ├── common.py         # 通用模式
│       │   └── task.py           # 任务相关模式
│       │
│       ├── services/             # 业务逻辑层
│       │   └── task_service.py   # 任务管理服务
│       │
│       └── dependencies/         # 依赖注入
│           └── __init__.py       # (预留:认证、限流等)
│
├── workers/                      # 后台任务处理器
│   ├── __init__.py
│   └── task_worker.py            # 异步任务执行器
│
├── run_server.py                 # API 服务器启动脚本
├── run_worker.py                 # Worker 启动脚本
│
├── tasks/                        # 任务元数据存储 (运行时创建)
│   └── *.json                    # 每个任务一个 JSON 文件
│
└── storage/                      # 生成内容存储 (运行时创建)
    └── <project_id>/             # 每个项目一个目录
        ├── metadata.json
        └── exports/
```

## 架构设计

### 1. 分层架构

```
┌─────────────────────────────────────────┐
│          Client (HTTP Requests)         │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         Routes Layer (Endpoints)        │  ← FastAPI 路由，处理 HTTP
│         - 参数验证                       │
│         - 请求/响应序列化                 │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│        Services Layer (Business)        │  ← 业务逻辑
│         - TaskService                   │
│         - 任务生命周期管理                │
│         - 持久化操作                     │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         Models Layer (Domain)           │  ← 领域模型
│         - Task                          │
│         - TaskMetadata                  │
│         - Enums                         │
└─────────────────────────────────────────┘
```

### 2. 异步任务处理模型

```
API Server (FastAPI)                Worker (Background)
─────────────────────              ─────────────────────

1. POST /api/v1/tasks/report
   └─> TaskService.create_task()
       └─> Save to tasks/*.json
       └─> Return task_id (pending)

                                   2. Poll for pending tasks
                                      └─> Load task from disk
                                      └─> Update status: running
                                      └─> Execute task
                                          ├─> Report generation
                                          ├─> Fiction generation
                                          └─> PPT generation
                                      └─> Update status: completed/failed

3. GET /api/v1/tasks/{task_id}
   └─> TaskService.get_task()
       └─> Load from tasks/*.json
       └─> Return current status + progress

4. GET /api/v1/tasks/{task_id}/download
   └─> Return generated files
```

### 3. 中间件栈

请求经过以下中间件（从外到内）：

1. **ErrorHandlingMiddleware**: 捕获所有异常，返回标准 JSON 错误响应
2. **PerformanceMiddleware**: 监控请求性能，记录慢请求
3. **LoggingMiddleware**: 记录所有请求/响应
4. **RequestIDMiddleware**: 为每个请求生成唯一 ID，用于追踪
5. **CORSMiddleware**: 处理跨域请求

## API 端点

### 健康检查

```http
GET /health
GET /
```

### 任务管理

#### 创建任务

```http
POST /api/v1/tasks/report
Content-Type: application/json

{
  "query": "AI技术发展趋势",
  "report_type": "comprehensive",
  "search_depth": "deep",
  "max_results": 20,
  "output_format": "html"
}

Response: 201 Created
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Task created successfully"
}
```

```http
POST /api/v1/tasks/fiction
POST /api/v1/tasks/ppt
```

#### 查询任务状态

```http
GET /api/v1/tasks/{task_id}

Response: 200 OK
{
  "task_id": "550e8400...",
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

#### 列出任务

```http
GET /api/v1/tasks?status=running&page=1&page_size=20

Response: 200 OK
{
  "tasks": [...],
  "total": 50,
  "page": 1,
  "page_size": 20
}
```

#### 取消任务

```http
DELETE /api/v1/tasks/{task_id}

Response: 204 No Content
```

## 数据模型

### TaskStatus (枚举)

- `pending`: 等待处理
- `queued`: 已加入队列
- `running`: 正在执行
- `completed`: 已完成
- `failed`: 失败
- `cancelled`: 已取消

### TaskType (枚举)

- `report`: 报告生成
- `fiction`: 小说生成
- `ppt`: PPT 生成

### Task (领域模型)

```python
class Task:
    task_id: str                    # UUID
    status: TaskStatus
    metadata: TaskMetadata

class TaskMetadata:
    query: str
    task_type: TaskType
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    progress_percentage: int        # 0-100
    current_step: Optional[str]
    output_files: List[str]
    error_message: Optional[str]
    extra: Dict[str, Any]           # 扩展字段
```

## 配置管理

所有配置通过环境变量或 `.env` 文件加载（使用 Pydantic Settings）。

### 环境变量

```bash
# 应用配置
APP_NAME=XunLong API
APP_VERSION=2.0.0
DEBUG=false

# 服务器配置
HOST=0.0.0.0
PORT=8000
RELOAD=false

# 任务管理
TASK_STORAGE_DIR=tasks
MAX_CONCURRENT_TASKS=10
TASK_TIMEOUT_SECONDS=3600

# Worker 配置
WORKER_POLL_INTERVAL=2.0
WORKER_MAX_RETRIES=3

# 存储配置
STORAGE_DIR=storage

# 日志配置
LOG_LEVEL=INFO
```

## 启动方式

### 1. 启动 API 服务器

```bash
python run_server.py
```

或使用环境变量：

```bash
HOST=0.0.0.0 PORT=8000 DEBUG=true python run_server.py
```

### 2. 启动 Worker

在另一个终端：

```bash
python run_worker.py
```

### 3. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## 扩展性设计

### 1. 添加新的任务类型

1. 在 `api/models/enums.py` 添加新的 `TaskType`
2. 在 `api/v1/schemas/task.py` 添加请求模式
3. 在 `api/v1/routes/tasks.py` 添加端点
4. 在 `workers/task_worker.py` 添加执行逻辑

### 2. 添加认证

1. 在 `api/core/security.py` 实现认证逻辑
2. 在 `api/v1/dependencies/` 添加认证依赖
3. 在路由中使用 `Depends(get_current_user)`

### 3. 添加数据库

目前使用文件系统存储任务元数据。如需添加数据库：

1. 在 `api/core/database.py` 配置 SQLAlchemy
2. 在 `api/models/` 添加 ORM 模型
3. 修改 `TaskService` 使用数据库而非文件系统

### 4. 添加消息队列

如需更强大的任务队列（如 Celery、RQ）：

1. 在 `workers/` 配置队列客户端
2. 修改 `TaskService.create_task()` 推送到队列
3. 修改 Worker 从队列消费任务

## 错误处理

所有异常都会被 `ErrorHandlingMiddleware` 捕获并转换为标准 JSON 响应：

```json
{
  "error": "Task not found: 550e8400...",
  "status_code": 404,
  "details": {
    "task_id": "550e8400..."
  }
}
```

### 自定义异常

- `TaskNotFoundException` (404)
- `InvalidTaskStateException` (400)
- `ValidationException` (422)
- `ServiceUnavailableException` (503)
- `RateLimitException` (429)

## 日志记录

使用 Loguru 进行结构化日志记录：

```python
logger.info(f"Task created: {task_id} | Type: {task_type}")
logger.warning(f"Slow request detected | Duration: {duration}s")
logger.error(f"Task failed: {task_id} | Error: {error}")
```

每个请求都有唯一的 Request-ID，可用于追踪完整的请求链路。

## 性能优化

1. **异步处理**: 使用 FastAPI 的异步特性
2. **分离架构**: API Server 和 Worker 分离，可独立扩展
3. **文件缓存**: 任务元数据持久化到磁盘，重启后可恢复
4. **中间件优化**: 性能监控中间件检测慢请求

## 安全考虑

1. **CORS 配置**: 默认允许所有来源（生产环境需限制）
2. **输入验证**: 使用 Pydantic 严格验证所有输入
3. **错误隐藏**: 生产环境不暴露内部错误细节
4. **认证预留**: dependencies/ 目录预留认证模块

## 下一步集成

当前 Worker 中的任务执行是占位符实现。下一步需要：

1. 将 `workers/task_worker.py` 中的 `_execute_*_task()` 方法与现有 Agent 集成：
   - `_execute_report_task()` → `src/agents/report/`
   - `_execute_fiction_task()` → `src/agents/fiction/`
   - `_execute_ppt_task()` → `src/agents/ppt/`

2. 集成现有的 LLM 管理器 (`src/llm/`)
3. 集成现有的导出管理器 (`src/export/`)
4. 集成现有的存储管理器 (`src/storage/`)

## 总结

这个新的 API 架构具有以下优势：

✅ **清晰的分层**: Routes → Services → Models
✅ **高度解耦**: API Server 和 Worker 可独立部署
✅ **类型安全**: Pydantic 提供完整的类型验证
✅ **可观测性**: 完整的日志、追踪、性能监控
✅ **易于扩展**: 添加新功能只需扩展对应层
✅ **生产就绪**: 错误处理、中间件、配置管理完备

可以在此基础上进行功能开发和业务集成。
