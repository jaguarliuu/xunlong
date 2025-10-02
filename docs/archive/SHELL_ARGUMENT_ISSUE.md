# Shell参数解析问题说明

## 问题描述

在使用命令行运行小说创作时，查询字符串无法正确传递给程序。

### 问题表现

```bash
# 运行命令
python main_agent.py search '搜集资料写一篇密室杀人类型的本格短篇推理小说;要求小说从凶手视角展开,但是直到最后才揭晓"我是凶手"'

# 调试输出
[DEBUG] 命令行参数数量: 2
[DEBUG] 所有参数: ['main_agent.py', 'search']
[DEBUG] 使用默认查询

# 结果
查询: 人工智能在医疗领域的应用  ← 错误！应该是小说查询
```

## 根本原因

Shell（特别是zsh）在解析包含特殊字符的参数时存在问题：

1. **中文引号问题**: 查询中包含中文双引号 `"我是凶手"`
2. **分号问题**: 分号 `;` 在某些shell中是命令分隔符
3. **引号嵌套**: 单引号中包含双引号（即使是中文双引号）可能导致解析异常
4. **Shell版本差异**: 不同shell（bash/zsh/fish）对引号的处理不同

## 解决方案

### 方案1：使用专用Python脚本（推荐）

创建了 `run_fiction_test.py`，直接在Python代码中定义查询：

```bash
python run_fiction_test.py
```

**优点**:
- ✅ 完全绕过shell参数解析
- ✅ 查询内容100%准确传递
- ✅ 支持任意特殊字符
- ✅ 跨平台兼容

**使用示例**:
```python
# run_fiction_test.py 中修改查询
query = '你的小说创作需求'
```

### 方案2：修改引号使用

使用ASCII双引号代替中文双引号：

```bash
python main_agent.py search '搜集资料写一篇密室杀人类型的本格短篇推理小说;要求小说从凶手视角展开,但是直到最后才揭晓"我是凶手"'
```

注意：`"我是凶手"` 使用ASCII双引号

### 方案3：转义特殊字符

```bash
python main_agent.py search "搜集资料写一篇密室杀人类型的本格短篇推理小说\;要求小说从凶手视角展开,但是直到最后才揭晓'我是凶手'"
```

- 分号前加反斜杠 `\;`
- 外层用双引号，内层用单引号

### 方案4：使用Bash脚本

创建了 `test_fiction.sh`:

```bash
./test_fiction.sh
```

脚本内容使用单引号包裹，并将中文引号改为ASCII引号。

## 改进措施

### 1. 增强的参数解析

修改了 `main_agent.py` 的参数解析逻辑：

```python
# 更详细的调试信息
print(f"[DEBUG] 命令行参数数量: {len(sys.argv)}")
print(f"[DEBUG] 所有参数: {sys.argv}")

# 检测到search命令但缺少参数时的提示
if sys.argv[1] == "search" and len(sys.argv) <= 2:
    print(f"[DEBUG] 检测到search命令但缺少查询参数")
    print(f"[DEBUG] 提示：使用方式 python main_agent.py search '你的查询'")
    print(f"[DEBUG] 如果查询包含特殊字符，建议使用 run_fiction_test.py 脚本")
```

### 2. 自动参数合并

如果检测到多个参数（可能是引号问题导致分割），自动合并：

```python
if len(sys.argv) > 3:
    query = ' '.join(sys.argv[2:])
    print(f"[DEBUG] 检测到多个参数，已合并为: {query}")
```

## 最佳实践

### 对于小说创作

**推荐使用专用脚本**:
```bash
python run_fiction_test.py
```

在脚本中修改查询内容，避免shell解析问题。

### 对于简单查询

可以直接使用命令行：
```bash
python main_agent.py search "人工智能在医疗领域的应用"
```

### 对于包含特殊字符的查询

1. 优先使用Python脚本
2. 如果必须用命令行，避免使用：
   - 中文引号（`""`）
   - 分号（`;`）
   - 反引号（`` ` ``）
   - 美元符号（`$`）

## Shell差异对照表

| Shell | 单引号 | 双引号 | 分号 | 中文引号 |
|-------|--------|--------|------|----------|
| bash  | ✅ 字面量 | ⚠️ 解析变量 | ❌ 分隔符 | ⚠️ 可能有问题 |
| zsh   | ✅ 字面量 | ⚠️ 解析变量 | ❌ 分隔符 | ❌ 常有问题 |
| fish  | ✅ 字面量 | ⚠️ 解析变量 | ❌ 分隔符 | ❌ 常有问题 |

## 测试验证

### 测试1：使用Python脚本

```bash
python run_fiction_test.py
```

**预期**: 正确识别为fiction类型，开始小说创作流程

### 测试2：使用ASCII引号

```bash
python main_agent.py search '搜集资料写一篇密室推理小说;从凶手视角,最后揭晓"我是凶手"'
```

**预期**: 正确传递查询

### 测试3：简单查询

```bash
python main_agent.py search "写一篇科幻小说"
```

**预期**: 正确识别为fiction类型

## 调试技巧

### 查看实际接收的参数

运行后查看调试输出：
```
[DEBUG] 命令行参数数量: X
[DEBUG] 所有参数: [...]
```

### 验证查询内容

```
查询: XXX  ← 确认这里显示的是否是你期望的内容
```

### 检查输出类型检测

```
[输出类型检测器] 输出类型检测完成: fiction (置信度: 0.95)
```

如果显示 `report` 而不是 `fiction`，说明查询内容有问题。

## 总结

**问题**: Shell参数解析导致查询字符串丢失或错误

**根因**: 特殊字符（分号、中文引号）在shell解析时出现问题

**解决**: 使用专用Python脚本 `run_fiction_test.py` 绕过shell解析

**建议**:
- ✅ 复杂查询用Python脚本
- ✅ 简单查询用命令行
- ❌ 避免在命令行参数中使用特殊字符
