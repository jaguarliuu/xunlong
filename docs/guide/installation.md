# Installation

This guide provides detailed installation instructions for XunLong on different operating systems.

## System Requirements

### Minimum Requirements

- **Operating System**: macOS, Linux, or Windows 10/11
- **Python**: 3.10 or higher
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Disk Space**: 2GB free space
- **Internet Connection**: Required for LLM API calls and web search

### Recommended Setup

- **Python**: 3.11 or 3.12
- **Memory**: 16GB RAM for better performance
- **Disk Space**: 5GB for storing generated projects
- **Network**: Stable high-speed internet connection

## Step-by-Step Installation

### 1. Install Python

::: tabs

== macOS

**Using Homebrew (Recommended):**
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.11

# Verify installation
python3 --version
```

**Using Official Installer:**
Download from [python.org](https://www.python.org/downloads/macos/)

== Linux (Ubuntu/Debian)

```bash
# Update package list
sudo apt update

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip

# Verify installation
python3.11 --version
```

== Linux (CentOS/RHEL)

```bash
# Install Python 3.11
sudo dnf install python3.11 python3.11-pip

# Verify installation
python3.11 --version
```

== Windows

**Using Python Installer:**
1. Download from [python.org](https://www.python.org/downloads/windows/)
2. Run installer
3. ✅ Check "Add Python to PATH"
4. Click "Install Now"

**Verify installation:**
```powershell
python --version
```

:::

### 2. Clone the Repository

```bash
# Using HTTPS
git clone https://github.com/yourusername/XunLong.git
cd XunLong

# Or using SSH
git clone git@github.com:yourusername/XunLong.git
cd XunLong
```

::: tip No Git?
If you don't have Git installed:
- macOS: `brew install git`
- Linux: `sudo apt install git`
- Windows: Download from [git-scm.com](https://git-scm.com/)
:::

### 3. Create Virtual Environment

::: tabs

== macOS/Linux

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Your prompt should now show (venv)
```

== Windows (PowerShell)

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

== Windows (Command Prompt)

```cmd
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate.bat
```

:::

::: warning Keep Virtual Environment Activated
Always activate the virtual environment before running XunLong. You'll see `(venv)` in your terminal prompt when activated.
:::

### 4. Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

This will install all required packages including:
- LangChain & LangGraph
- OpenAI/Anthropic clients
- Playwright
- Export libraries (WeasyPrint, python-pptx, python-docx)

### 5. Install System Dependencies

#### For PDF Export (WeasyPrint)

::: tabs

== macOS

```bash
# Install system libraries
brew install pango gdk-pixbuf libffi
```

== Ubuntu/Debian

```bash
# Install required libraries
sudo apt-get update
sudo apt-get install -y \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info
```

== CentOS/RHEL

```bash
# Install required libraries
sudo yum install -y \
    pango \
    gdk-pixbuf2 \
    libffi-devel
```

== Windows

WeasyPrint on Windows requires GTK+:

1. Download GTK+ installer from [gtk.org](https://www.gtk.org/docs/installations/windows/)
2. Install to default location
3. Add GTK+ to PATH

**Alternative:** Use WSL (Windows Subsystem for Linux) for easier setup.

:::

#### For Web Search (Playwright)

```bash
# Install Playwright browsers
playwright install chromium

# Or install all browsers
playwright install
```

::: details Troubleshooting Playwright
If you encounter issues:

```bash
# Install system dependencies for Playwright
playwright install-deps chromium

# On Ubuntu/Debian
sudo apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2
```
:::

### 6. Configure Environment Variables

#### Create .env File

```bash
# Copy example configuration
cp .env.example .env

# Edit the file
nano .env  # or vim .env, or use your favorite editor
```

#### Configure LLM Provider

Choose **one** of the following providers and add your API key:

::: code-group

```env [OpenAI]
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o

# Optional: Set as default provider
DEFAULT_LLM_PROVIDER=openai
```

```env [Anthropic]
# Anthropic Configuration
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
ANTHROPIC_MODEL=claude-3-5-sonnet-20251022

# Optional: Set as default provider
DEFAULT_LLM_PROVIDER=anthropic
```

```env [DeepSeek]
# DeepSeek Configuration
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat

# Optional: Set as default provider
DEFAULT_LLM_PROVIDER=deepseek
```

:::

#### Optional: Add Search API

```env
# Perplexity Search (Recommended)
PERPLEXITY_API_KEY=pplx-xxxxxxxxxxxxx
PERPLEXITY_MODEL=sonar
```

#### Optional: Add Observability

```env
# LangFuse Configuration
LANGFUSE_PUBLIC_KEY=pk-xxxxxxxxxxxxx
LANGFUSE_SECRET_KEY=sk-xxxxxxxxxxxxx
LANGFUSE_HOST=https://cloud.langfuse.com
```

::: tip Getting API Keys
- **OpenAI**: [platform.openai.com](https://platform.openai.com/api-keys)
- **Anthropic**: [console.anthropic.com](https://console.anthropic.com/)
- **DeepSeek**: [platform.deepseek.com](https://platform.deepseek.com/)
- **Perplexity**: [perplexity.ai/settings/api](https://www.perplexity.ai/settings/api)
- **LangFuse**: [cloud.langfuse.com](https://cloud.langfuse.com/)
:::

### 7. Verify Installation

Run the verification script:

```bash
python -c "
import sys
print(f'Python version: {sys.version}')

try:
    import langchain
    print('✅ LangChain installed')
except ImportError:
    print('❌ LangChain not installed')

try:
    import playwright
    print('✅ Playwright installed')
except ImportError:
    print('❌ Playwright not installed')

try:
    import weasyprint
    print('✅ WeasyPrint installed')
except ImportError:
    print('❌ WeasyPrint not installed')

print('Installation check complete!')
"
```

### 8. Test Your Installation

Generate your first report:

```bash
python xunlong.py report "Test Report" --verbose
```

If successful, you should see:
- Search progress indicators
- Content generation steps
- Final report saved to `storage/` directory

## Post-Installation

### Update XunLong

```bash
# Pull latest changes
git pull origin master

# Update dependencies
pip install -r requirements.txt --upgrade

# Update Playwright browsers
playwright install chromium
```

### Uninstallation

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
rm -rf venv

# Remove generated projects (optional)
rm -rf storage/

# Remove configuration
rm .env
```

## Troubleshooting

### Common Issues

#### Issue: `ModuleNotFoundError`

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # macOS/Linux
# or
.\venv\Scripts\Activate.ps1  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

#### Issue: WeasyPrint fails on macOS

**Solution:**
```bash
# Reinstall with proper library paths
brew reinstall pango gdk-pixbuf libffi

# Set library path
export DYLD_LIBRARY_PATH=/opt/homebrew/lib:$DYLD_LIBRARY_PATH

# Try again
python xunlong.py export <project_id> pdf
```

#### Issue: Playwright browser not found

**Solution:**
```bash
# Reinstall browsers
playwright install chromium --force

# Or install with dependencies
playwright install chromium --with-deps
```

#### Issue: Permission denied on Linux

**Solution:**
```bash
# Make script executable
chmod +x xunlong.py

# Or run with python
python xunlong.py report "Test"
```

#### Issue: API key not found

**Solution:**
- Check `.env` file exists in project root
- Verify API key format (no quotes, no spaces)
- Ensure environment variables are loaded
- Try restarting your terminal

### Getting Help

If you're still having issues:

1. Check the [FAQ](/guide/faq)
2. Search [GitHub Issues](https://github.com/yourusername/XunLong/issues)
3. Create a new issue with:
   - Your OS and Python version
   - Full error message
   - Steps to reproduce

## Next Steps

Now that XunLong is installed:

- 📖 Read the [Getting Started Guide](/guide/getting-started)
- 🏗️ Understand the [Architecture](/guide/architecture)
- 📊 Try [Report Generation](/guide/features/report)
- 📖 Explore [Fiction Writing](/guide/features/fiction)
- 🎨 Create [PPT Presentations](/guide/features/ppt)
