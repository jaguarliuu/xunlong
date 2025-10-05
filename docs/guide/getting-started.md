# Getting Started

This guide will help you get started with XunLong in minutes.

## Prerequisites

Before you begin, ensure you have:

- Python 3.10 or higher
- pip (Python package manager)
- An API key from OpenAI, Anthropic, or DeepSeek

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/XunLong.git
cd XunLong
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install System Dependencies

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

### 5. Install Browser

```bash
playwright install chromium
```

### 6. Configure Environment

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# Choose your LLM provider
OPENAI_API_KEY=your_key_here
# OR
ANTHROPIC_API_KEY=your_key_here
# OR
DEEPSEEK_API_KEY=your_key_here
```

## Your First Generation

### Generate a Report

```bash
python xunlong.py report "AI Industry Overview 2025"
```

This will:
1. Analyze the topic
2. Search for relevant information
3. Generate a comprehensive report
4. Save it to `storage/` directory

### Check the Output

```bash
# List generated projects
ls -la storage/

# View the report
cat storage/20251005_*/reports/FINAL_REPORT.md
```

## Next Steps

::: tip What's Next?
- Learn about [Report Generation](/guide/features/report)
- Explore [Fiction Writing](/guide/features/fiction)
- Try [PPT Creation](/guide/features/ppt)
- Understand the [Architecture](/guide/architecture)
:::

## Getting Help

If you encounter any issues:

- Check the [FAQ](/guide/faq)
- Search [GitHub Issues](https://github.com/yourusername/XunLong/issues)
- Join our community discussions
