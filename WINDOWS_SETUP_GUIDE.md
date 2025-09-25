# Windows 环境变量设置指南

## 🪟 Windows 下设置环境变量的方法

### 方法1: PowerShell 临时设置（推荐用于测试）

```powershell
# 设置通义千问API密钥
$env:DASHSCOPE_API_KEY="your-qwen-api-key"

# 设置DeepSeek API密钥
$env:DEEPSEEK_API_KEY="your-deepseek-api-key"

# 设置智谱AI API密钥
$env:ZHIPU_API_KEY="your-zhipu-api-key"

# 设置OpenAI API密钥
$env:OPENAI_API_KEY="your-openai-api-key"

# 通用LLM配置
$env:LLM_API_KEY="your-api-key"
$env:LLM_BASE_URL="your-base-url"
```

### 方法2: CMD 临时设置

```cmd
set DASHSCOPE_API_KEY=your-qwen-api-key
set DEEPSEEK_API_KEY=your-deepseek-api-key
set ZHIPU_API_KEY=your-zhipu-api-key
set OPENAI_API_KEY=your-openai-api-key
```

### 方法3: 系统环境变量永久设置（推荐）

1. **打开系统属性**
   - 按 `Win + R` 键
   - 输入 `sysdm.cpl`
   - 按回车

2. **进入环境变量设置**
   - 点击 "环境变量" 按钮

3. **添加用户环境变量**
   - 在 "用户变量" 区域点击 "新建"
   - 变量名: `DASHSCOPE_API_KEY`
   - 变量值: `your-qwen-api-key`
   - 点击 "确定"

4. **重启终端**
   - 关闭所有PowerShell/CMD窗口
   - 重新打开终端
   - 环境变量生效

### 方法4: 通过注册表设置

```powershell
# 设置用户环境变量
[Environment]::SetEnvironmentVariable("DASHSCOPE_API_KEY", "your-qwen-api-key", "User")

# 设置系统环境变量（需要管理员权限）
[Environment]::SetEnvironmentVariable("DASHSCOPE_API_KEY", "your-qwen-api-key", "Machine")
```

## 🎯 推荐的API密钥获取

### 通义千问 (推荐)
- 网站: https://dashscope.aliyuncs.com/
- 优势: 中文支持好，价格便宜
- 环境变量: `DASHSCOPE_API_KEY`

### DeepSeek (推荐)
- 网站: https://platform.deepseek.com/
- 优势: 编程能力强，价格极低
- 环境变量: `DEEPSEEK_API_KEY`

### 智谱AI
- 网站: https://open.bigmodel.cn/
- 优势: 国产大模型，功能全面
- 环境变量: `ZHIPU_API_KEY`

### OpenAI
- 网站: https://platform.openai.com/
- 优势: 功能强大，生态完善
- 环境变量: `OPENAI_API_KEY`

## 🔍 验证环境变量设置

```powershell
# 检查环境变量是否设置成功
echo $env:DASHSCOPE_API_KEY
echo $env:DEEPSEEK_API_KEY
echo $env:ZHIPU_API_KEY
```

## 🚀 快速测试

设置好环境变量后，运行：

```powershell
# 运行安装脚本
python setup_agent.py

# 测试系统
python main_agent.py
```

## 🛠️ 故障排除

### 问题1: 环境变量不生效
**解决方案**: 重启终端或重启电脑

### 问题2: API密钥格式错误
**解决方案**: 确保API密钥没有多余的空格或引号

### 问题3: 网络连接问题
**解决方案**: 检查防火墙设置，或使用代理

### 问题4: 权限问题
**解决方案**: 以管理员身份运行PowerShell

## 📝 示例配置

```powershell
# 完整的环境变量设置示例
$env:DASHSCOPE_API_KEY="sk-xxxxxxxxxxxxxxxxxxxx"
$env:LLM_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"

# 验证设置
python -c "import os; print('API Key:', os.getenv('DASHSCOPE_API_KEY')[:10] + '...' if os.getenv('DASHSCOPE_API_KEY') else 'Not set')"
```

## 🎉 设置完成后

环境变量设置完成后，你就可以：

1. 运行 `python setup_agent.py` 进行系统检测
2. 使用 `python main_agent.py` 开始体验
3. 通过 `python -m src.cli_agent search "查询内容"` 进行搜索
4. 启动 `python -m src.api_agent` 使用API服务

享受你的DeepSearch智能体系统吧！🎊