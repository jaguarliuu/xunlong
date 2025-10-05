# 快速开始

本指南将帮助你在几分钟内开始使用XunLong。

## 前置要求

开始之前，请确保你有：

- Python 3.10 或更高版本
- pip（Python包管理器）
- OpenAI、Anthropic或DeepSeek的API密钥

## 安装步骤

### 1. 克隆仓库

```bash
git clone https://github.com/jaguarliuu/xunlong.git
cd XunLong
```

### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Windows用户: venv\Scripts\activate
```

### 3. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 4. 安装系统依赖

::: tabs

== macOS
```bash
brew install pango gdk-pixbuf libffi
```

== Ubuntu/Debian
```bash
sudo apt-get install libpango-1.0-0 libpangoft2-1.0-0 gdk-pixbuf2.0
```

== CentOS/RHEL
```bash
sudo yum install pango gdk-pixbuf2
```

:::

### 5. 安装浏览器

```bash
playwright install chromium
```

### 6. 配置环境变量

复制`.env.example`为`.env`:

```bash
cp .env.example .env
```

编辑`.env`文件，添加你的API密钥:

```env
# 选择你的LLM提供商
OPENAI_API_KEY=your_key_here
# 或
ANTHROPIC_API_KEY=your_key_here
# 或
DEEPSEEK_API_KEY=your_key_here
```

## 第一次生成

### 生成报告

```bash
python xunlong.py report "2025年人工智能行业概览"
```

这将：
1. 分析主题
2. 搜索相关信息
3. 生成全面的报告
4. 保存到`storage/`目录

### 查看输出

```bash
# 列出生成的项目
ls -la storage/

# 查看报告
cat storage/20251005_*/reports/FINAL_REPORT.md
```

## 下一步

::: tip 接下来做什么？
- 学习[报告生成](/zh/guide/features/report)
- 探索[小说创作](/zh/guide/features/fiction)
- 尝试[PPT制作](/zh/guide/features/ppt)
- 理解[系统架构](/zh/guide/architecture)
:::

## 获取帮助

如果遇到任何问题：

- 查看[常见问题](/zh/guide/faq)
- 搜索[GitHub Issues](https://github.com/jaguarliuu/xunlong/issues)
- 加入我们的社区讨论
