# 📁 存储系统说明

## 概述

每次搜索都会创建一个独立的项目目录，保存所有中间产物和最终报告，方便后续查阅和扩展。

---

## 🗂️ 目录结构

```
storage/
├── 20251001_213000_人工智能最新发展/
│   ├── metadata.json                    # 项目元数据
│   ├── execution_log.json               # 执行日志(JSON)
│   ├── execution_log.txt                # 执行日志(文本)
│   ├── intermediate/                    # 中间产物
│   │   ├── 01_task_decomposition.json   # 任务分解结果
│   │   ├── 02_search_results.json       # 搜索结果
│   │   ├── 03_content_evaluation.json   # 内容评估
│   │   ├── 04_search_analysis.json      # 搜索分析
│   │   ├── 05_content_synthesis.json    # 内容综合
│   │   └── 06_final_report.json         # 最终报告(JSON)
│   ├── search_results/                  # 搜索结果(可读)
│   │   └── search_results.txt           # 搜索结果文本
│   └── reports/                         # 报告文件
│       ├── FINAL_REPORT.md              # 完整报告(主文件)
│       ├── SUMMARY.md                   # 报告摘要
│       └── synthesis_report.md          # 内容综合报告
│
└── 20251001_214500_深度学习技术/
    └── ... (相同结构)
```

---

## 📄 文件说明

### 1. metadata.json
项目元数据，包含：
- `project_id`: 项目唯一标识
- `query`: 搜索查询
- `created_at`: 创建时间
- `completed_at`: 完成时间
- `status`: 状态 (running/completed/failed)
- `report_path`: 最终报告路径

```json
{
  "project_id": "20251001_213000_人工智能最新发展",
  "query": "人工智能最新发展",
  "created_at": "2025-10-01T21:30:00",
  "completed_at": "2025-10-01T21:35:00",
  "status": "completed",
  "report_path": "storage/20251001_213000_人工智能最新发展/reports/FINAL_REPORT.md"
}
```

### 2. intermediate/ 目录
保存所有中间处理步骤的结果（JSON格式），方便调试和分析：

- **01_task_decomposition.json**: 任务分解智能体的输出
- **02_search_results.json**: 深度搜索智能体的输出
- **03_content_evaluation.json**: 内容评估智能体的输出
- **04_search_analysis.json**: 搜索分析智能体的输出
- **05_content_synthesis.json**: 内容综合智能体的输出
- **06_final_report.json**: 报告生成智能体的输出

### 3. search_results/ 目录
保存可读的搜索结果：

- **search_results.txt**: 所有搜索结果的文本格式，包括标题、URL、内容摘要

### 4. reports/ 目录
保存最终报告（Markdown格式）：

- **FINAL_REPORT.md**: 完整的最终报告（主要文件）
- **SUMMARY.md**: 报告摘要（快速预览）
- **synthesis_report.md**: 内容综合阶段的报告

### 5. 执行日志
- **execution_log.json**: JSON格式的执行日志
- **execution_log.txt**: 可读的文本格式执行日志

---

## 🚀 使用方式

### 基本用法

```python
from src.deep_search_agent import DeepSearchAgent

agent = DeepSearchAgent()
result = await agent.search("人工智能最新发展")

# 获取项目路径
project_dir = result['project_dir']
print(f"结果已保存到: {project_dir}")
```

### 查看报告

搜索完成后，系统会自动打印：

```
============================================================
📁 项目已保存到: storage/20251001_213000_人工智能最新发展
📄 最终报告: storage/.../reports/FINAL_REPORT.md
📋 报告摘要: storage/.../reports/SUMMARY.md
🔍 搜索结果: storage/.../search_results/search_results.txt
============================================================
```

直接打开对应的文件即可查看。

### 列出所有项目

```python
from src.storage import SearchStorage

storage = SearchStorage()
projects = storage.list_projects()

for project in projects:
    print(f"项目: {project['query']}")
    print(f"  ID: {project['project_id']}")
    print(f"  状态: {project['status']}")
    print(f"  创建时间: {project['created_at']}")
    print(f"  路径: {project['path']}")
```

---

## 🎯 存储优势

### 1. **完整性**
- 保存所有中间步骤和最终结果
- 方便调试和追溯处理流程

### 2. **可读性**
- JSON格式保存原始数据（程序可读）
- Markdown/TXT格式保存报告（人类可读）

### 3. **可扩展性**
- 支持添加更多中间产物
- 支持导出为其他格式（PDF、DOCX等）

### 4. **版本管理**
- 每次搜索独立存储
- 基于时间戳的项目ID，不会覆盖

### 5. **用户友好**
- 清晰的目录结构
- 多种格式支持下载

---

## 🔧 配置

### 自定义存储路径

```python
from src.storage import SearchStorage
from src.deep_search_agent import DeepSearchAgent
from src.agents.coordinator import DeepSearchCoordinator

# 自定义存储目录
storage = SearchStorage(base_dir="my_custom_storage")

# 传入协调器
coordinator = DeepSearchCoordinator(storage=storage)
agent = DeepSearchAgent()
agent.coordinator = coordinator

# 执行搜索
result = await agent.search("查询内容")
```

---

## 📊 存储流程

```
搜索开始
  ↓
创建项目目录 (project_id = timestamp_query)
  ↓
任务分解 → 保存 01_task_decomposition.json
  ↓
深度搜索 → 保存 02_search_results.json + search_results.txt
  ↓
内容评估 → 保存 03_content_evaluation.json
  ↓
搜索分析 → 保存 04_search_analysis.json
  ↓
内容综合 → 保存 05_content_synthesis.json + synthesis_report.md
  ↓
报告生成 → 保存 06_final_report.json + FINAL_REPORT.md + SUMMARY.md
  ↓
保存执行日志 → execution_log.json + execution_log.txt
  ↓
更新元数据 (status = completed)
  ↓
搜索完成，打印项目路径
```

---

## 🛠️ API参考

### SearchStorage 类

#### 初始化
```python
storage = SearchStorage(base_dir="storage")
```

#### 创建项目
```python
project_id = storage.create_project(query="搜索查询")
```

#### 保存方法
```python
storage.save_task_decomposition(decomposition_data)
storage.save_search_results(search_data)
storage.save_content_evaluation(evaluation_data)
storage.save_search_analysis(analysis_data)
storage.save_content_synthesis(synthesis_data)
storage.save_final_report(report_data, query)
storage.save_execution_log(messages)
```

#### 查询方法
```python
# 获取当前项目目录
project_dir = storage.get_project_dir()

# 列出所有项目
projects = storage.list_projects()

# 加载元数据
metadata = storage.load_metadata()
```

---

## 📝 后续扩展

### 1. Web界面
可以基于存储的JSON文件创建Web界面：
- 列出所有搜索历史
- 在线查看报告
- 下载报告（PDF/DOCX/MD）

### 2. 搜索历史管理
- 搜索项目列表
- 按时间/关键词筛选
- 删除/归档项目

### 3. 报告对比
- 比较不同时间的搜索结果
- 分析话题演变趋势

### 4. 导出功能
- 导出为PDF
- 导出为Word文档
- 打包下载所有文件

### 5. 协作功能
- 多用户项目共享
- 评论和标注
- 报告版本管理

---

## ⚠️ 注意事项

1. **存储空间**: 每个项目可能占用 1-10 MB，注意定期清理
2. **隐私保护**: 报告可能包含敏感信息，注意访问权限
3. **备份**: 重要项目建议定期备份
4. **命名冲突**: 如果在同一秒内启动多个搜索，可能导致项目ID冲突（概率极低）

---

## ✅ 总结

存储系统提供了完整的项目管理功能：
- ✅ 自动创建项目目录
- ✅ 保存所有中间产物和最终报告
- ✅ 多种格式支持（JSON、Markdown、TXT）
- ✅ 清晰的目录结构
- ✅ 方便扩展和集成

**现在每次搜索都会自动保存，不用担心结果丢失！** 📁✨
