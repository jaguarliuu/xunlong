# API使用指南

XunLong提供RESTful API用于异步内容生成。这允许您将XunLong的功能集成到应用程序中，而无需阻塞长时间运行的操作。

## 概述

XunLong API使用**异步任务模型**：

1. **创建任务**: 提交生成请求并接收任务ID
2. **轮询状态**: 使用任务ID检查任务进度
3. **获取结果**: 任务完成后获取最终结果
4. **下载文件**: 下载生成的文件

这种方法适用于:
- Web应用程序
- 后台作业处理
- 分布式系统
- 多用户环境

## 快速开始

### 1. 启动API服务器

```bash
python run_api.py
```

API服务器将在 `http://localhost:8000` 启动。

### 2. 启动任务执行器

在另一个终端中:

```bash
python start_worker.py
```

这个后台进程执行任务。

### 3. 发送API请求

```python
import requests

# 创建报告任务
response = requests.post('http://localhost:8000/api/v1/tasks/report', json={
    "query": "人工智能在医疗领域的应用",
    "report_type": "comprehensive",
    "search_depth": "deep"
})

task_id = response.json()['task_id']
print(f"任务已创建: {task_id}")

# 检查状态
status = requests.get(f'http://localhost:8000/api/v1/tasks/{task_id}')
print(f"进度: {status.json()['progress']}%")
```

## API端点

### 基础信息

**`GET /`**

获取API信息和可用端点。

**`GET /health`**

健康检查端点。

### 任务创建

#### 创建报告任务

**`POST /api/v1/tasks/report`**

创建异步报告生成任务。

**请求体:**
```json
{
  "query": "2024年人工智能趋势",
  "report_type": "comprehensive",
  "search_depth": "deep",
  "max_results": 20,
  "output_format": "html"
}
```

**参数:**
- `query` (必需): 主题或研究问题
- `report_type` (可选): `comprehensive`/`daily`/`analysis`/`research` (默认: `comprehensive`)
- `search_depth` (可选): `surface`/`medium`/`deep` (默认: `deep`)
- `max_results` (可选): 最大搜索结果数 (默认: 20)
- `output_format` (可选): `html`/`md` (默认: `html`)

**响应:**
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "pending",
  "message": "报告生成任务已创建"
}
```

#### 创建小说任务

**`POST /api/v1/tasks/fiction`**

创建异步小说创作任务。

**请求体:**
```json
{
  "query": "一个设定在维多利亚时代伦敦的推理小说",
  "genre": "mystery",
  "length": "short",
  "viewpoint": "first"
}
```

#### 创建PPT任务

**`POST /api/v1/tasks/ppt`**

创建异步PPT生成任务。

**请求体:**
```json
{
  "query": "产品发布策略",
  "slides": 15,
  "style": "business"
}
```

### 任务管理

#### 获取任务状态

**`GET /api/v1/tasks/{task_id}`**

获取任务的当前状态和进度。

**响应:**
```json
{
  "task_id": "a1b2c3d4...",
  "task_type": "report",
  "status": "running",
  "progress": 45,
  "current_step": "深度搜索中",
  "created_at": "2025-10-05T14:30:00",
  "started_at": "2025-10-05T14:30:05"
}
```

**状态值:**
- `pending`: 等待执行
- `running`: 正在执行
- `completed`: 已完成
- `failed`: 执行失败
- `cancelled`: 已取消

#### 获取任务结果

**`GET /api/v1/tasks/{task_id}/result`**

获取已完成任务的结果。

#### 下载生成的文件

**`GET /api/v1/tasks/{task_id}/download`**

下载任务生成的文件。

**查询参数:**
- `file_type`: `html`/`md`/`pdf` (默认: `html`)

#### 取消任务

**`DELETE /api/v1/tasks/{task_id}`**

取消待执行或正在执行的任务。

#### 列出任务

**`GET /api/v1/tasks`**

列出所有任务，支持筛选。

**查询参数:**
- `status`: 按状态筛选
- `task_type`: 按类型筛选
- `limit`: 最大返回数量 (默认: 50)

## Python客户端库

XunLong提供Python客户端以便于集成。

### 基本用法

```python
from examples.async_api_client import XunLongAsyncClient

client = XunLongAsyncClient(base_url="http://localhost:8000")

# 创建报告任务
task = client.create_report(
    query="机器学习在药物发现中的应用",
    report_type="research",
    search_depth="deep"
)
task_id = task['task_id']

# 等待完成（显示进度）
result = client.wait_for_completion(task_id, verbose=True)

# 下载生成的文件
file_path = client.download_file(task_id, file_type="html")
print(f"报告已保存到: {file_path}")
```

### 高级用法

```python
# 创建小说
task = client.create_fiction(
    query="一个赛博朋克惊悚故事",
    genre="scifi",
    length="medium"
)

# 创建PPT
task = client.create_ppt(
    query="2025营销策略",
    slides=20,
    style="business"
)

# 列出所有任务
tasks = client.list_tasks(status="completed", limit=10)

# 取消任务
client.cancel_task(task_id)
```

## 错误处理

API使用标准HTTP状态码:

| 代码 | 含义 |
|-----|------|
| 200 | 成功 |
| 400 | 错误请求（参数无效） |
| 404 | 未找到（任务不存在） |
| 500 | 内部服务器错误 |

## 最佳实践

### 1. 使用适当的轮询间隔

不要过于频繁地轮询:

```python
# 好: 每5-10秒轮询一次
result = client.wait_for_completion(task_id, poll_interval=5)

# 不好: 每秒轮询（浪费资源）
# result = client.wait_for_completion(task_id, poll_interval=1)
```

### 2. 处理超时

为长时间运行的任务设置适当的超时:

```python
# 报告通常需要10-20分钟
result = client.wait_for_completion(
    task_id,
    timeout=1800,  # 30分钟
    poll_interval=10
)
```

### 3. 在获取结果前检查任务状态

```python
status = client.get_task_status(task_id)

if status['status'] == 'completed':
    result = client.get_task_result(task_id)
elif status['status'] == 'failed':
    print(f"任务失败: {status['error']}")
elif status['status'] == 'running':
    print(f"任务进行中: {status['progress']}%")
```

## 部署

### 生产环境设置

生产环境部署:

1. **使用进程管理器** (如 systemd, supervisor)
2. **运行多个worker** 以实现并行处理
3. **使用反向代理** (如 nginx)
4. **启用HTTPS**
5. **添加认证**
6. **监控任务队列**

## 故障排除

### 问题: 任务停留在pending状态

**原因**: Worker未运行

**解决方案**:
```bash
python start_worker.py
```

### 问题: API返回404

**原因**: API服务器未运行

**解决方案**:
```bash
python run_api.py
```

### 问题: 任务立即失败

**原因**: 配置或依赖问题

**解决方案**:
- 检查worker日志
- 验证环境变量
- 确保所有依赖已安装

## 下一步

- 查看[快速开始](/zh/guide/getting-started)了解CLI使用
- 探索[示例](/zh/examples/report)了解实际用例
- 检查[配置](/zh/api/configuration)了解高级设置
