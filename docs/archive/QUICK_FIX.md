# 🔧 快速修复指南

## 问题描述

启动 `main_agent.py` 时遇到依赖导入错误：

```
ImportError: lxml.html.clean module is now a separate project lxml_html_clean.
Install lxml[html_clean] or lxml_html_clean directly.
```

## 解决方案

### 1. 安装缺失的依赖

使用国内镜像源安装（推荐，速度快）：

```bash
# 安装 lxml-html-clean
pip install lxml-html-clean -i https://pypi.tuna.tsinghua.edu.cn/simple

# 安装所有依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

或使用默认源：

```bash
pip install lxml-html-clean
pip install -r requirements.txt
```

### 2. 验证安装

运行以下命令验证程序可以正常启动：

```bash
python main_agent.py --help
```

预期输出：
```
DeepSearch智能体系统使用说明:
  python main_agent.py                    # 运行完整演示
  python main_agent.py search '查询'      # 搜索指定内容
  python -m src.cli_agent search '查询'   # CLI搜索
  python -m src.cli_agent quick '问题'    # 快速问答
  python -m src.cli_agent status          # 查看状态
  python -m src.api_agent                 # 启动API服务
```

## 已修复的问题

### ✅ 依赖问题
- **lxml-html-clean**: 已添加到 `requirements.txt`
- **beautifulsoup4**: 已正确安装
- **langfuse**: 已安装（监控功能）
- **langchain**: 已安装（智能体框架）
- **trafilatura**: 已安装（内容提取）

### ✅ 代码问题
- **正则表达式警告**: 修复了 `content_extractor.py:109` 的转义序列警告

## 环境配置

### 必需配置

1. **复制环境变量模板**
   ```bash
   cp .env.example .env
   ```

2. **编辑 `.env` 文件**，至少配置一个 LLM API 密钥：
   ```env
   # 推荐：通义千问（阿里云）
   DASHSCOPE_API_KEY=your_api_key_here

   # 或者其他提供商
   OPENAI_API_KEY=your_api_key_here
   ANTHROPIC_API_KEY=your_api_key_here
   ```

3. **（可选）配置 Langfuse 监控**
   ```env
   LANGFUSE_SECRET_KEY=sk-lf-xxx
   LANGFUSE_PUB_KEY=pk-lf-xxx
   LANGFUSE_HOST=https://cloud.langfuse.com
   ```

### 安装 Playwright 浏览器

```bash
playwright install chromium
```

## 快速开始

### 1. 基础测试

```bash
# 运行默认演示
python main_agent.py

# 指定查询内容
python main_agent.py search "人工智能最新发展"
```

### 2. 查看系统状态

```bash
python -m src.cli_agent status
```

### 3. 快速问答

```bash
python -m src.cli_agent quick "什么是深度学习？"
```

### 4. 启动 API 服务

```bash
python run_api.py
```

## 常见问题

### Q1: 提示 Langfuse 配置不完整

**A**: 这是警告信息，不影响系统运行。如需监控功能，请在 `.env` 中配置 Langfuse 密钥。

### Q2: 提示 LLM 配置文件不存在

**A**: 系统会使用默认配置（通义千问）。如需自定义，创建 `config/llm_config.yaml` 文件。

### Q3: 网络连接超时

**A**: 使用国内镜像源安装依赖：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q4: 依赖版本冲突（mem0ai）

**A**: 这是其他已安装包的版本冲突，不影响本项目运行。如需解决：
```bash
pip install openai==1.99.0
```

## 技术支持

如遇到其他问题，请查看：
- 完整文档：`README.md`
- 项目结构：`PROJECT_STRUCTURE.md`
- 部署指南：`docs/DEPLOYMENT_GUIDE.md`
- 用户手册：`docs/FINAL_USER_GUIDE.md`

---

**修复状态**: ✅ 已完成
**测试状态**: ✅ 通过
**更新时间**: 2025-10-01
