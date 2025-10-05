# API Usage Guide

XunLong provides a RESTful API for asynchronous content generation. This allows you to integrate XunLong's capabilities into your applications without blocking on long-running operations.

## Overview

The XunLong API uses an **asynchronous task-based model**:

1. **Create Task**: Submit a generation request and receive a task ID
2. **Poll Status**: Check task progress using the task ID
3. **Retrieve Result**: Get the final result when the task completes
4. **Download Files**: Download generated files

This approach is ideal for:
- Web applications
- Background job processing
- Distributed systems
- Multi-user environments

## Quick Start

### 1. Start the API Server

```bash
python run_api.py
```

The API server will start on `http://localhost:8000`.

### 2. Start the Task Worker

In a separate terminal:

```bash
python start_worker.py
```

This background process executes the tasks.

### 3. Make API Requests

```python
import requests

# Create a report task
response = requests.post('http://localhost:8000/api/v1/tasks/report', json={
    "query": "AI in Healthcare",
    "report_type": "comprehensive",
    "search_depth": "deep"
})

task_id = response.json()['task_id']
print(f"Task created: {task_id}")

# Check status
status = requests.get(f'http://localhost:8000/api/v1/tasks/{task_id}')
print(f"Progress: {status.json()['progress']}%")
```

## API Endpoints

### Base Information

**`GET /`**

Get API information and available endpoints.

```bash
curl http://localhost:8000/
```

**Response:**
```json
{
  "name": "XunLong API",
  "version": "1.0.0",
  "description": "AI驱动的多模态内容生成API",
  "features": ["报告生成", "小说创作", "PPT制作"],
  "endpoints": { ... }
}
```

**`GET /health`**

Health check endpoint.

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "task_manager": "ok",
  "version": "1.0.0"
}
```

### Task Creation

#### Create Report Task

**`POST /api/v1/tasks/report`**

Create an asynchronous report generation task.

**Request Body:**
```json
{
  "query": "Artificial Intelligence Trends 2024",
  "report_type": "comprehensive",
  "search_depth": "deep",
  "max_results": 20,
  "output_format": "html",
  "html_template": "academic",
  "html_theme": "light"
}
```

**Parameters:**
- `query` (required): Topic or research question
- `report_type` (optional): `comprehensive`, `daily`, `analysis`, `research` (default: `comprehensive`)
- `search_depth` (optional): `surface`, `medium`, `deep` (default: `deep`)
- `max_results` (optional): Maximum search results (default: 20)
- `output_format` (optional): `html`, `md` (default: `html`)
- `html_template` (optional): `academic`, `technical` (default: `academic`)
- `html_theme` (optional): `light`, `dark` (default: `light`)

**Response:**
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "pending",
  "message": "报告生成任务已创建，任务ID: a1b2c3d4..."
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/tasks/report \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Blockchain Technology in Finance",
    "report_type": "analysis",
    "search_depth": "deep"
  }'
```

#### Create Fiction Task

**`POST /api/v1/tasks/fiction`**

Create an asynchronous fiction writing task.

**Request Body:**
```json
{
  "query": "A mystery novel set in Victorian London",
  "genre": "mystery",
  "length": "short",
  "viewpoint": "first",
  "constraints": ["locked room", "snowstorm"],
  "output_format": "html"
}
```

**Parameters:**
- `query` (required): Story premise or description
- `genre` (optional): `mystery`, `scifi`, `fantasy`, `horror`, `romance`, `wuxia` (default: `mystery`)
- `length` (optional): `short`, `medium`, `long` (default: `short`)
- `viewpoint` (optional): `first`, `third`, `omniscient` (default: `first`)
- `constraints` (optional): List of special constraints
- `output_format` (optional): `html`, `md` (default: `html`)

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/tasks/fiction \
  -H "Content-Type: application/json" \
  -d '{
    "query": "A time-traveling detective story",
    "genre": "scifi",
    "length": "medium"
  }'
```

#### Create PPT Task

**`POST /api/v1/tasks/ppt`**

Create an asynchronous PPT generation task.

**Request Body:**
```json
{
  "query": "Product Launch Strategy",
  "slides": 15,
  "style": "business",
  "theme": "corporate-blue"
}
```

**Parameters:**
- `query` (required): Presentation topic
- `slides` (optional): Number of slides (default: 15)
- `style` (optional): `business`, `creative`, `minimal`, `educational` (default: `business`)
- `theme` (optional): Theme name (default: `corporate-blue`)

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/tasks/ppt \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Q4 Sales Performance",
    "slides": 20,
    "style": "business"
  }'
```

### Task Management

#### Get Task Status

**`GET /api/v1/tasks/{task_id}`**

Get the current status and progress of a task.

**Response:**
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "task_type": "report",
  "status": "running",
  "progress": 45,
  "current_step": "深度搜索中",
  "created_at": "2025-10-05T14:30:00",
  "started_at": "2025-10-05T14:30:05",
  "completed_at": null,
  "result": null,
  "error": null
}
```

**Status Values:**
- `pending`: Waiting to execute
- `running`: Currently executing
- `completed`: Successfully completed
- `failed`: Execution failed
- `cancelled`: Cancelled by user

**Example:**
```bash
curl http://localhost:8000/api/v1/tasks/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

#### Get Task Result

**`GET /api/v1/tasks/{task_id}/result`**

Get the result of a completed task.

**Response:**
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "completed",
  "result": {
    "success": true,
    "project_id": "20251005_143000_topic",
    "output_dir": "storage/20251005_143000_topic",
    "output_format": "html",
    "files": [
      "storage/20251005_143000_topic/reports/FINAL_REPORT.html"
    ],
    "stats": {
      "duration": 456.7,
      "words": 5432
    }
  },
  "project_id": "20251005_143000_topic",
  "output_dir": "storage/20251005_143000_topic"
}
```

**Example:**
```bash
curl http://localhost:8000/api/v1/tasks/a1b2c3d4-e5f6-7890-abcd-ef1234567890/result
```

#### Download Generated File

**`GET /api/v1/tasks/{task_id}/download`**

Download a file generated by the task.

**Query Parameters:**
- `file_type`: `html`, `md`, `pdf` (default: `html`)

**Example:**
```bash
curl -O http://localhost:8000/api/v1/tasks/a1b2c3d4.../download?file_type=html
```

#### Cancel Task

**`DELETE /api/v1/tasks/{task_id}`**

Cancel a pending or running task.

**Response:**
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "cancelled",
  "message": "任务已取消"
}
```

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/v1/tasks/a1b2c3d4...
```

#### List Tasks

**`GET /api/v1/tasks`**

List all tasks with optional filtering.

**Query Parameters:**
- `status`: Filter by status (`pending`, `running`, `completed`, `failed`, `cancelled`)
- `task_type`: Filter by type (`report`, `fiction`, `ppt`)
- `limit`: Maximum number of tasks to return (default: 50, max: 200)

**Response:**
```json
{
  "total": 10,
  "tasks": [
    {
      "task_id": "...",
      "task_type": "report",
      "status": "completed",
      "query": "AI Trends",
      "progress": 100,
      "created_at": "2025-10-05T14:30:00",
      "completed_at": "2025-10-05T14:45:00"
    },
    ...
  ]
}
```

**Examples:**
```bash
# List all tasks
curl http://localhost:8000/api/v1/tasks

# List completed tasks
curl http://localhost:8000/api/v1/tasks?status=completed

# List report tasks
curl http://localhost:8000/api/v1/tasks?task_type=report

# List recent 10 tasks
curl http://localhost:8000/api/v1/tasks?limit=10
```

## Python Client Library

XunLong provides a Python client for easier integration.

### Installation

The client is included in the `examples/` directory:

```python
from examples.async_api_client import XunLongAsyncClient

client = XunLongAsyncClient(base_url="http://localhost:8000")
```

### Basic Usage

```python
# Create a report task
task = client.create_report(
    query="Machine Learning in Drug Discovery",
    report_type="research",
    search_depth="deep"
)
task_id = task['task_id']

# Wait for completion (with progress updates)
result = client.wait_for_completion(task_id, verbose=True)

# Download the generated file
file_path = client.download_file(task_id, file_type="html")
print(f"Report saved to: {file_path}")
```

### Advanced Usage

```python
# Create fiction
task = client.create_fiction(
    query="A cyberpunk thriller",
    genre="scifi",
    length="medium"
)

# Create PPT
task = client.create_ppt(
    query="Marketing Strategy 2025",
    slides=20,
    style="business"
)

# List all tasks
tasks = client.list_tasks(status="completed", limit=10)
for task in tasks['tasks']:
    print(f"{task['query']}: {task['status']}")

# Cancel a task
client.cancel_task(task_id)
```

### Client Methods

| Method | Description |
|--------|-------------|
| `create_report()` | Create report generation task |
| `create_fiction()` | Create fiction writing task |
| `create_ppt()` | Create PPT generation task |
| `get_task_status()` | Get task status |
| `get_task_result()` | Get task result |
| `download_file()` | Download generated file |
| `cancel_task()` | Cancel a task |
| `list_tasks()` | List tasks |
| `wait_for_completion()` | Wait for task to complete |

## Error Handling

The API uses standard HTTP status codes:

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request (invalid parameters) |
| 404 | Not Found (task doesn't exist) |
| 500 | Internal Server Error |

**Error Response Format:**
```json
{
  "detail": "Error message here"
}
```

**Example Error Handling:**
```python
try:
    result = client.get_task_result(task_id)
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 404:
        print("Task not found")
    elif e.response.status_code == 400:
        print(f"Task not ready: {e.response.json()['detail']}")
    else:
        print(f"Error: {e}")
```

## Best Practices

### 1. Use Appropriate Polling Intervals

Don't poll too frequently:

```python
# Good: Poll every 5-10 seconds
result = client.wait_for_completion(task_id, poll_interval=5)

# Bad: Poll every second (wastes resources)
# result = client.wait_for_completion(task_id, poll_interval=1)
```

### 2. Handle Timeouts

Set appropriate timeouts for long-running tasks:

```python
# Reports typically take 10-20 minutes
result = client.wait_for_completion(
    task_id,
    timeout=1800,  # 30 minutes
    poll_interval=10
)
```

### 3. Check Task Status Before Retrieving Results

```python
status = client.get_task_status(task_id)

if status['status'] == 'completed':
    result = client.get_task_result(task_id)
elif status['status'] == 'failed':
    print(f"Task failed: {status['error']}")
elif status['status'] == 'running':
    print(f"Task in progress: {status['progress']}%")
```

### 4. Clean Up Old Tasks

Periodically clean up old tasks:

```python
# List old completed tasks
tasks = client.list_tasks(status="completed", limit=100)

# Process or archive results
for task in tasks['tasks']:
    # Download results if needed
    # Then delete the task data
    pass
```

## Deployment

### Production Setup

For production deployment:

1. **Use a process manager** (e.g., systemd, supervisor)
2. **Run multiple workers** for parallel processing
3. **Use a reverse proxy** (e.g., nginx)
4. **Enable HTTPS**
5. **Add authentication**
6. **Monitor task queue**

### Example systemd Service

API Server (`/etc/systemd/system/xunlong-api.service`):
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

Worker (`/etc/systemd/system/xunlong-worker.service`):
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

### nginx Configuration

```nginx
server {
    listen 80;
    server_name api.xunlong.example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## Troubleshooting

### Issue: Tasks Stuck in Pending

**Cause**: Worker not running

**Solution**:
```bash
# Start the worker
python start_worker.py
```

### Issue: API Returns 404 for All Endpoints

**Cause**: API server not running

**Solution**:
```bash
# Start the API server
python run_api.py
```

### Issue: Tasks Fail Immediately

**Cause**: Configuration or dependency issues

**Solution**:
- Check worker logs
- Verify environment variables
- Ensure all dependencies are installed

### Issue: Slow Task Processing

**Cause**: Only one worker running

**Solution**:
- Run multiple worker instances
- Consider using Celery for distributed processing

## Next Steps

- Review [CLI Usage](/guide/getting-started) for command-line interface
- Explore [Examples](/examples/report) for practical use cases
- Check [Configuration](/api/configuration) for advanced settings
