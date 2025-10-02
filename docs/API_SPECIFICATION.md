# XunLong API 接口规范

## 📋 目录

- [概述](#概述)
- [通用规范](#通用规范)
- [认证](#认证)
- [API端点](#api端点)
  - [报告生成](#报告生成-api)
  - [小说创作](#小说创作-api)
  - [PPT生成](#ppt生成-api)
  - [快速问答](#快速问答-api)
  - [系统状态](#系统状态-api)
- [数据模型](#数据模型)
- [错误处理](#错误处理)
- [前端集成示例](#前端集成示例)

---

## 概述

XunLong 提供 RESTful API 接口，所有CLI参数都可通过API调用。

### Base URL

```
http://localhost:8000/api/v1
```

### 技术栈

- **框架**: FastAPI
- **认证**: JWT Token
- **数据格式**: JSON
- **文档**: Swagger UI (自动生成)

---

## 通用规范

### 请求头

```http
Content-Type: application/json
Authorization: Bearer <token>
```

### 响应格式

#### 成功响应

```json
{
  "status": "success",
  "data": {
    // 具体数据
  },
  "message": "操作成功"
}
```

#### 错误响应

```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": {}
  }
}
```

### HTTP状态码

- `200` - 成功
- `201` - 创建成功
- `400` - 请求参数错误
- `401` - 未认证
- `403` - 无权限
- `404` - 资源不存在
- `500` - 服务器错误

---

## 认证

### 获取Token

```http
POST /api/v1/auth/login
```

**Request**:
```json
{
  "username": "user",
  "password": "pass"
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 3600
  }
}
```

---

## API端点

### 报告生成 API

#### 创建报告任务

```http
POST /api/v1/report/generate
```

**Request Body**:
```json
{
  "query": "人工智能在医疗领域的应用",
  "type": "comprehensive",
  "depth": "deep",
  "max_results": 20,
  "options": {
    "language": "zh",
    "save_intermediate": true
  }
}
```

**Parameters**:

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `query` | string | ✅ | - | 查询内容 |
| `type` | enum | ❌ | comprehensive | 报告类型：comprehensive, daily, analysis, research |
| `depth` | enum | ❌ | deep | 搜索深度：surface, medium, deep |
| `max_results` | integer | ❌ | 20 | 最大搜索结果数（1-100） |
| `options` | object | ❌ | {} | 额外选项 |

**Response**:
```json
{
  "status": "success",
  "data": {
    "task_id": "report_20251002_093058",
    "project_id": "20251002_093058_人工智能在医疗领域的应用",
    "status": "processing",
    "estimated_time": 60
  }
}
```

#### 查询任务状态

```http
GET /api/v1/report/{task_id}/status
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "task_id": "report_20251002_093058",
    "status": "completed",
    "progress": 100,
    "current_step": "report_generator",
    "steps_completed": [
      "output_type_detector",
      "task_decomposer",
      "deep_searcher",
      "search_analyzer",
      "content_synthesizer",
      "report_generator"
    ]
  }
}
```

**任务状态**:
- `pending` - 等待中
- `processing` - 执行中
- `completed` - 已完成
- `failed` - 失败

#### 获取报告结果

```http
GET /api/v1/report/{task_id}/result
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "task_id": "report_20251002_093058",
    "project_id": "20251002_093058_人工智能在医疗领域的应用",
    "report": {
      "title": "人工智能在医疗领域的应用研究报告",
      "content": "# 报告内容...",
      "word_count": 5000,
      "metadata": {
        "type": "comprehensive",
        "generated_at": "2025-10-02T09:30:58",
        "sources_count": 20
      }
    },
    "files": {
      "markdown": "/storage/.../FINAL_REPORT.md",
      "summary": "/storage/.../SUMMARY.md",
      "json": "/storage/.../06_final_report.json"
    }
  }
}
```

---

### 小说创作 API

#### 创建小说任务

```http
POST /api/v1/fiction/generate
```

**Request Body**:
```json
{
  "query": "写一篇密室推理小说",
  "genre": "mystery",
  "length": "short",
  "viewpoint": "first",
  "constraints": ["暴风雪山庄", "本格推理"],
  "options": {
    "language": "zh",
    "style": "classic"
  }
}
```

**Parameters**:

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `query` | string | ✅ | - | 创作需求 |
| `genre` | enum | ❌ | mystery | 类型：mystery, scifi, fantasy, horror, romance, wuxia |
| `length` | enum | ❌ | short | 篇幅：short(5章), medium(12章), long(30章) |
| `viewpoint` | enum | ❌ | first | 视角：first, third, omniscient |
| `constraints` | array | ❌ | [] | 特殊约束列表 |
| `options` | object | ❌ | {} | 额外选项 |

**Response**:
```json
{
  "status": "success",
  "data": {
    "task_id": "fiction_20251002_093058",
    "project_id": "20251002_093058_写一篇密室推理小说",
    "status": "processing",
    "estimated_time": 180,
    "outline": {
      "total_chapters": 5,
      "estimated_words": 5000
    }
  }
}
```

#### 获取小说结果

```http
GET /api/v1/fiction/{task_id}/result
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "task_id": "fiction_20251002_093058",
    "project_id": "20251002_093058_写一篇密室推理小说",
    "fiction": {
      "title": "墨色杀机",
      "synopsis": "台风夜被困画廊的六人中...",
      "content": "# 墨色杀机\n\n## 第1章...",
      "word_count": 4500,
      "metadata": {
        "type": "fiction",
        "genre": "推理",
        "total_chapters": 5,
        "successful_chapters": 5,
        "viewpoint": "第一人称",
        "elements": {
          "time": {...},
          "place": {...},
          "characters": [...],
          "plot": {...},
          "environment": {...},
          "theme": {...}
        }
      }
    },
    "files": {
      "markdown": "/storage/.../FINAL_REPORT.md",
      "outline": "/storage/.../04_fiction_outline.json",
      "elements": "/storage/.../01_fiction_elements.json"
    }
  }
}
```

---

### PPT生成 API

#### 创建PPT任务（开发中）

```http
POST /api/v1/ppt/generate
```

**Request Body**:
```json
{
  "query": "产品介绍PPT",
  "theme": "business",
  "slides": 15,
  "options": {
    "language": "zh",
    "include_images": true
  }
}
```

---

### 快速问答 API

#### 提问（开发中）

```http
POST /api/v1/ask
```

**Request Body**:
```json
{
  "question": "什么是量子计算？",
  "model": "balanced",
  "options": {
    "language": "zh",
    "max_tokens": 500
  }
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "question": "什么是量子计算？",
    "answer": "量子计算是...",
    "model": "balanced",
    "tokens_used": 150
  }
}
```

---

### 系统状态 API

#### 获取系统状态

```http
GET /api/v1/system/status
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "system": "DeepSearch智能体系统",
    "status": "running",
    "version": "1.0.0",
    "llm": {
      "total_configs": 1,
      "providers": {
        "deepseek": {
          "status": "available",
          "model": "deepseek-chat"
        },
        "openai": {
          "status": "unavailable"
        }
      }
    },
    "stats": {
      "total_tasks": 150,
      "completed_tasks": 145,
      "failed_tasks": 5,
      "active_tasks": 3
    }
  }
}
```

#### 获取任务列表

```http
GET /api/v1/tasks?type={type}&status={status}&limit={limit}&offset={offset}
```

**Query Parameters**:
- `type` - 任务类型：report, fiction, ppt
- `status` - 任务状态：pending, processing, completed, failed
- `limit` - 每页数量（默认10）
- `offset` - 偏移量（默认0）

**Response**:
```json
{
  "status": "success",
  "data": {
    "total": 150,
    "limit": 10,
    "offset": 0,
    "tasks": [
      {
        "task_id": "report_20251002_093058",
        "type": "report",
        "status": "completed",
        "query": "人工智能在医疗领域的应用",
        "created_at": "2025-10-02T09:30:58",
        "completed_at": "2025-10-02T09:32:15"
      }
    ]
  }
}
```

---

## 数据模型

### Task (任务)

```typescript
interface Task {
  task_id: string;
  type: 'report' | 'fiction' | 'ppt' | 'ask';
  status: 'pending' | 'processing' | 'completed' | 'failed';
  query: string;
  created_at: string;
  completed_at?: string;
  error?: string;
}
```

### Report (报告)

```typescript
interface Report {
  title: string;
  content: string;
  word_count: number;
  metadata: {
    type: string;
    generated_at: string;
    sources_count: number;
  };
}
```

### Fiction (小说)

```typescript
interface Fiction {
  title: string;
  synopsis: string;
  content: string;
  word_count: number;
  metadata: {
    type: 'fiction';
    genre: string;
    total_chapters: number;
    successful_chapters: number;
    viewpoint: string;
    elements: FictionElements;
  };
}

interface FictionElements {
  time: object;
  place: object;
  characters: Character[];
  plot: object;
  environment: object;
  theme: object;
}
```

---

## 错误处理

### 错误码列表

| 错误码 | HTTP状态 | 说明 |
|--------|----------|------|
| `INVALID_PARAMETERS` | 400 | 请求参数无效 |
| `TASK_NOT_FOUND` | 404 | 任务不存在 |
| `TASK_FAILED` | 500 | 任务执行失败 |
| `LLM_ERROR` | 500 | LLM调用失败 |
| `STORAGE_ERROR` | 500 | 存储错误 |
| `UNAUTHORIZED` | 401 | 未认证 |
| `RATE_LIMIT_EXCEEDED` | 429 | 请求频率超限 |

### 错误响应示例

```json
{
  "status": "error",
  "error": {
    "code": "INVALID_PARAMETERS",
    "message": "参数 'genre' 的值 'invalid_genre' 无效",
    "details": {
      "field": "genre",
      "valid_values": ["mystery", "scifi", "fantasy", "horror", "romance", "wuxia"]
    }
  }
}
```

---

## 前端集成示例

### React + TypeScript

```typescript
// api/xunlong.ts
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export interface ReportRequest {
  query: string;
  type?: 'comprehensive' | 'daily' | 'analysis' | 'research';
  depth?: 'surface' | 'medium' | 'deep';
  max_results?: number;
}

export interface FictionRequest {
  query: string;
  genre?: 'mystery' | 'scifi' | 'fantasy' | 'horror' | 'romance' | 'wuxia';
  length?: 'short' | 'medium' | 'long';
  viewpoint?: 'first' | 'third' | 'omniscient';
  constraints?: string[];
}

class XunLongAPI {
  private token: string = '';

  setToken(token: string) {
    this.token = token;
  }

  private getHeaders() {
    return {
      'Authorization': `Bearer ${this.token}`,
      'Content-Type': 'application/json'
    };
  }

  // 报告生成
  async generateReport(request: ReportRequest) {
    const response = await axios.post(
      `${API_BASE_URL}/report/generate`,
      request,
      { headers: this.getHeaders() }
    );
    return response.data;
  }

  async getReportStatus(taskId: string) {
    const response = await axios.get(
      `${API_BASE_URL}/report/${taskId}/status`,
      { headers: this.getHeaders() }
    );
    return response.data;
  }

  async getReportResult(taskId: string) {
    const response = await axios.get(
      `${API_BASE_URL}/report/${taskId}/result`,
      { headers: this.getHeaders() }
    );
    return response.data;
  }

  // 小说创作
  async generateFiction(request: FictionRequest) {
    const response = await axios.post(
      `${API_BASE_URL}/fiction/generate`,
      request,
      { headers: this.getHeaders() }
    );
    return response.data;
  }

  async getFictionStatus(taskId: string) {
    const response = await axios.get(
      `${API_BASE_URL}/fiction/${taskId}/status`,
      { headers: this.getHeaders() }
    );
    return response.data;
  }

  async getFictionResult(taskId: string) {
    const response = await axios.get(
      `${API_BASE_URL}/fiction/${taskId}/result`,
      { headers: this.getHeaders() }
    );
    return response.data;
  }

  // 系统状态
  async getSystemStatus() {
    const response = await axios.get(
      `${API_BASE_URL}/system/status`,
      { headers: this.getHeaders() }
    );
    return response.data;
  }
}

export const xunlongAPI = new XunLongAPI();
```

### Vue 3 组件示例

```vue
<template>
  <div class="fiction-creator">
    <h2>小说创作</h2>

    <form @submit.prevent="createFiction">
      <input v-model="query" placeholder="输入创作需求" required />

      <select v-model="genre">
        <option value="mystery">推理</option>
        <option value="scifi">科幻</option>
        <option value="fantasy">奇幻</option>
        <option value="horror">恐怖</option>
      </select>

      <select v-model="length">
        <option value="short">短篇(5章)</option>
        <option value="medium">中篇(12章)</option>
        <option value="long">长篇(30章)</option>
      </select>

      <select v-model="viewpoint">
        <option value="first">第一人称</option>
        <option value="third">第三人称</option>
        <option value="omniscient">全知视角</option>
      </select>

      <button type="submit" :disabled="loading">
        {{ loading ? '创作中...' : '开始创作' }}
      </button>
    </form>

    <div v-if="result" class="result">
      <h3>{{ result.title }}</h3>
      <p>{{ result.synopsis }}</p>
      <div class="metadata">
        <span>类型: {{ result.metadata.genre }}</span>
        <span>章节: {{ result.metadata.total_chapters }}</span>
        <span>字数: {{ result.word_count }}</span>
      </div>
      <div class="content" v-html="markdownToHtml(result.content)"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { xunlongAPI } from '@/api/xunlong';
import { marked } from 'marked';

const query = ref('');
const genre = ref('mystery');
const length = ref('short');
const viewpoint = ref('first');
const loading = ref(false);
const result = ref(null);

const createFiction = async () => {
  loading.value = true;

  try {
    // 1. 创建任务
    const createResponse = await xunlongAPI.generateFiction({
      query: query.value,
      genre: genre.value,
      length: length.value,
      viewpoint: viewpoint.value
    });

    const taskId = createResponse.data.task_id;

    // 2. 轮询任务状态
    const checkStatus = async () => {
      const statusResponse = await xunlongAPI.getFictionStatus(taskId);

      if (statusResponse.data.status === 'completed') {
        // 3. 获取结果
        const resultResponse = await xunlongAPI.getFictionResult(taskId);
        result.value = resultResponse.data.fiction;
        loading.value = false;
      } else if (statusResponse.data.status === 'failed') {
        alert('创作失败');
        loading.value = false;
      } else {
        // 继续轮询
        setTimeout(checkStatus, 2000);
      }
    };

    checkStatus();

  } catch (error) {
    console.error('创作失败:', error);
    loading.value = false;
  }
};

const markdownToHtml = (markdown: string) => {
  return marked(markdown);
};
</script>
```

---

## WebSocket支持（可选）

对于长时间任务，可使用WebSocket获取实时进度：

```typescript
const ws = new WebSocket('ws://localhost:8000/ws/task/{task_id}');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Progress:', data.progress);
  console.log('Current Step:', data.current_step);
};
```

---

## 版本控制

API版本通过URL路径指定：

- `/api/v1/` - 当前版本
- `/api/v2/` - 未来版本

---

## 限流

默认限流规则：

- 未认证用户：10 请求/分钟
- 认证用户：100 请求/分钟
- 企业用户：1000 请求/分钟

---

**XunLong API v1.0.0** - 为前端赋能 🚀
