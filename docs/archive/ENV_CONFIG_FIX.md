# 🔧 环境变量配置修复说明

## 问题描述

之前的版本中，`.env` 文件中配置的 `DEFAULT_LLM_PROVIDER` 和 `DEFAULT_LLM_MODEL` 等环境变量**没有被读取**，系统始终使用硬编码的默认值（qwen）。

## 已修复的问题

### ✅ 修复内容

修改了 `src/llm/manager.py` 中的配置读取逻辑：

1. **支持 `DEFAULT_LLM_PROVIDER` 环境变量**
   - 现在会优先使用 `.env` 中指定的提供商
   - 如果指定的提供商没有 API 密钥，会自动回退到其他可用提供商
   - 添加了详细的日志输出

2. **支持 `DEFAULT_LLM_MODEL` 环境变量**
   - 现在会优先使用 `.env` 中指定的模型名称
   - 如果未指定，使用提供商的默认模型

3. **支持 `DEFAULT_LLM_TEMPERATURE` 环境变量**
   - 现在会从 `.env` 读取温度参数
   - 默认值：0.7

4. **支持 `DEFAULT_LLM_MAX_TOKENS` 环境变量**
   - 现在会从 `.env` 读取最大 token 数
   - 默认值：4000

## 配置示例

### `.env` 文件配置

```env
# DeepSeek 配置示例
DEEPSEEK_API_KEY=sk-a276ed41519e403283e27b5024e136ac
DEFAULT_LLM_PROVIDER=deepseek
DEFAULT_LLM_MODEL=deepseek-chat
DEFAULT_LLM_TEMPERATURE=0.7
DEFAULT_LLM_MAX_TOKENS=4000

# 通义千问配置示例
# DASHSCOPE_API_KEY=your_api_key_here
# DEFAULT_LLM_PROVIDER=qwen
# DEFAULT_LLM_MODEL=qwen-turbo

# OpenAI 配置示例
# OPENAI_API_KEY=your_api_key_here
# DEFAULT_LLM_PROVIDER=openai
# DEFAULT_LLM_MODEL=gpt-4o-mini
```

## 验证修复

运行以下命令验证配置是否生效：

```bash
python main_agent.py search "测试" 2>&1 | grep "提供商\|模型"
```

**预期输出**（如果配置了 DeepSeek）：
```
INFO | src.llm.manager:_detect_best_provider:215 - 使用环境变量指定的提供商: deepseek
INFO | src.llm.manager:_get_default_model:253 - 使用环境变量指定的模型: deepseek-chat
INFO | src.llm.manager:_create_default_configs:194 - 使用默认配置，提供商: deepseek, 模型: deepseek-chat
```

## 配置优先级

系统按以下优先级选择 LLM 提供商：

### 1. 环境变量指定（最高优先级）
```env
DEFAULT_LLM_PROVIDER=deepseek
```

### 2. 自动检测（如果环境变量未设置）

检测顺序：
1. DeepSeek (`DEEPSEEK_API_KEY`)
2. 通义千问 (`DASHSCOPE_API_KEY` 或 `QWEN_API_KEY`)
3. 智谱AI (`ZHIPU_API_KEY`)
4. OpenAI (`OPENAI_API_KEY`)
5. Anthropic (`ANTHROPIC_API_KEY`)
6. Ollama（本地模型，无需 API 密钥）

### 3. 通用 API 密钥
```env
LLM_API_KEY=your_api_key
```
- 如果设置了 `LLM_API_KEY`，默认使用 DeepSeek

## 支持的提供商

| 提供商 | 环境变量 | DEFAULT_LLM_PROVIDER 值 | 默认模型 |
|--------|---------|------------------------|---------|
| **DeepSeek** | DEEPSEEK_API_KEY | `deepseek` | deepseek-chat |
| **通义千问** | DASHSCOPE_API_KEY | `qwen` | qwen-turbo |
| **OpenAI** | OPENAI_API_KEY | `openai` | gpt-4o-mini |
| **Anthropic** | ANTHROPIC_API_KEY | `anthropic` | claude-3-sonnet-20250229 |
| **智谱AI** | ZHIPU_API_KEY | `zhipu` | glm-4 |
| **Ollama** | 无需密钥 | `ollama` | llama3 |

## 常见问题

### Q1: 配置了 DEFAULT_LLM_PROVIDER 但没有生效？

**A**: 检查以下几点：
1. `.env` 文件是否在项目根目录
2. API 密钥是否正确配置
3. 提供商名称是否正确（小写）

### Q2: 如何查看当前使用的提供商？

**A**: 运行程序时会在日志中输出：
```bash
python main_agent.py search "测试" 2>&1 | head -50
```

查找包含 "使用默认配置，提供商:" 的行。

### Q3: 可以同时配置多个提供商吗？

**A**: 可以！在 `.env` 中配置多个 API 密钥，系统会按优先级自动选择。如果指定的提供商失败，会自动切换到其他可用提供商。

### Q4: 环境变量和 config/llm_config.yaml 哪个优先级高？

**A**:
- 如果存在 `config/llm_config.yaml`，会优先使用 YAML 配置
- 如果不存在 YAML 配置，使用环境变量（`.env`）
- 建议：简单配置用 `.env`，复杂配置（多智能体不同模型）用 YAML

## 测试所有提供商

```bash
# 测试 DeepSeek
DEFAULT_LLM_PROVIDER=deepseek python main_agent.py search "测试"

# 测试通义千问
DEFAULT_LLM_PROVIDER=qwen python main_agent.py search "测试"

# 测试 OpenAI
DEFAULT_LLM_PROVIDER=openai python main_agent.py search "测试"
```

## 日志详细程度

如果需要更详细的日志输出，可以添加：

```env
DEBUG=true
```

## 相关文件

- **配置读取逻辑**: `src/llm/manager.py`
- **环境变量文件**: `.env`
- **配置示例**: `.env.example`

---

**修复日期**: 2025-10-01
**影响版本**: v1.0.0 及以后
**向后兼容**: ✅ 是
