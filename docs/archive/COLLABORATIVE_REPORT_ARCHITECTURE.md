# 📝 Collaborative Report Generation Architecture

## 概述

将报告生成从单一智能体升级为多智能体协作系统，实现高质量、结构化的报告生成。

---

## 🏗️ 系统架构

```
报告生成协作流程
├── 1️⃣ OutlineGenerator (大纲生成器)
│   └── 生成报告大纲和分段结构
│
├── 2️⃣ SectionWriter (段落写作者) × N
│   ├── Writer-1: 编写第1段
│   ├── Writer-2: 编写第2段  } 并行执行
│   └── Writer-N: 编写第N段
│
├── 3️⃣ SectionEvaluator (段落评估者)
│   ├── 评估每段内容质量
│   ├── 检查信息完整性
│   └── 提供改进建议
│
├── 4️⃣ ContentSearcher (内容搜索者)
│   └── 为不足的段落补充内容
│
└── 5️⃣ ReportAssembler (报告组装者)
    └── 合并所有段落，生成最终报告
```

---

## 🔄 工作流程

### Phase 1: 大纲生成

```
输入: {query, search_results, synthesis_results}
  ↓
OutlineGenerator 分析内容
  ↓
生成结构化大纲
{
  "sections": [
    {"id": 1, "title": "引言", "requirements": "..."},
    {"id": 2, "title": "核心发现", "requirements": "..."},
    {"id": 3, "title": "详细分析", "requirements": "..."},
    ...
  ],
  "total_sections": N
}
```

### Phase 2: 并行写作

```
sections → 分配给 N 个 SectionWriter (并行)

Writer-1 ─┐
Writer-2 ─┼─→ 同时写作各自段落
Writer-N ─┘

每个 Writer 输出:
{
  "section_id": 1,
  "content": "段落内容...",
  "confidence": 0.85,
  "sources_used": [...]
}
```

### Phase 3: 质量评估 (迭代)

```
for each section:
  SectionEvaluator 评估
    ↓
  confidence < threshold?
    ├─ Yes → 判断问题类型
    │   ├─ "need_more_content" → ContentSearcher 补充
    │   └─ "need_rewrite" → SectionWriter 重写
    └─ No → 标记为完成

重复直到所有段落 confidence ≥ threshold
```

### Phase 4: 报告组装

```
所有段落通过评估
  ↓
ReportAssembler 组装
  ↓
添加引言、总结、引用
  ↓
生成最终报告
{
  "title": "...",
  "content": "完整报告内容",
  "metadata": {...}
}
```

---

## 🤖 智能体详细设计

### 1. OutlineGenerator (大纲生成器)

**职责**:
- 分析查询意图和搜索结果
- 生成结构化的报告大纲
- 为每个段落定义写作要求

**输入**:
```python
{
  "query": str,
  "search_results": List[Dict],
  "synthesis_results": Dict,
  "report_type": str  # "daily", "analysis", "research"
}
```

**输出**:
```python
{
  "outline": {
    "title": str,
    "sections": [
      {
        "id": int,
        "title": str,
        "requirements": str,  # 本段应包含什么内容
        "suggested_sources": List[str],  # 推荐的信息源
        "word_count": int  # 建议字数
      }
    ]
  },
  "total_sections": int
}
```

---

### 2. SectionWriter (段落写作者)

**职责**:
- 根据大纲要求撰写特定段落
- 使用搜索结果作为信息源
- 生成高质量、连贯的内容

**输入**:
```python
{
  "section": {
    "id": int,
    "title": str,
    "requirements": str,
    "word_count": int
  },
  "available_content": List[Dict],  # 可用的搜索结果
  "context": {
    "query": str,
    "report_type": str,
    "previous_section": str  # 上一段内容（保持连贯性）
  }
}
```

**输出**:
```python
{
  "section_id": int,
  "content": str,
  "confidence": float,  # 0-1，写作置信度
  "sources_used": List[str],  # 使用的信息源
  "word_count": int,
  "issues": List[str]  # 自我识别的问题
}
```

---

### 3. SectionEvaluator (段落评估者)

**职责**:
- 评估段落质量（完整性、准确性、相关性）
- 判断是否需要补充内容或重写
- 提供具体改进建议

**输入**:
```python
{
  "section": {
    "id": int,
    "title": str,
    "requirements": str,
    "content": str
  },
  "available_sources": List[Dict],
  "evaluation_criteria": {
    "completeness": bool,  # 是否完整
    "accuracy": bool,      # 是否准确
    "relevance": bool,     # 是否相关
    "coherence": bool      # 是否连贯
  }
}
```

**输出**:
```python
{
  "section_id": int,
  "passed": bool,
  "confidence": float,  # 0-1
  "scores": {
    "completeness": float,
    "accuracy": float,
    "relevance": float,
    "coherence": float
  },
  "issues": List[str],
  "recommendation": {
    "action": str,  # "approve", "need_more_content", "need_rewrite"
    "reason": str,
    "suggestions": List[str]
  }
}
```

---

### 4. ContentSearcher (内容搜索者)

**职责**:
- 为信息不足的段落补充内容
- 执行针对性搜索
- 提取相关信息

**输入**:
```python
{
  "section_id": int,
  "missing_info": List[str],  # 缺少的信息
  "search_query": str,
  "existing_sources": List[str]  # 已有的信息源
}
```

**输出**:
```python
{
  "section_id": int,
  "additional_content": List[Dict],
  "success": bool
}
```

---

### 5. ReportAssembler (报告组装者)

**职责**:
- 组装所有完成的段落
- 添加引言、总结、引用
- 生成最终格式化报告

**输入**:
```python
{
  "outline": Dict,
  "sections": List[Dict],  # 所有完成的段落
  "metadata": Dict
}
```

**输出**:
```python
{
  "title": str,
  "content": str,  # 完整报告（Markdown）
  "sections": List[Dict],
  "metadata": {
    "total_words": int,
    "sources_count": int,
    "generation_time": str
  }
}
```

---

## 🔄 迭代与优化机制

### 质量保证循环

```python
MAX_ITERATIONS = 3

for section in sections:
    iteration = 0
    while iteration < MAX_ITERATIONS:
        # 评估
        evaluation = SectionEvaluator.evaluate(section)

        if evaluation.passed:
            break  # 通过，进入下一段

        # 未通过，根据建议采取行动
        if evaluation.recommendation.action == "need_more_content":
            # 补充内容
            additional = ContentSearcher.search(section, evaluation.issues)
            section.content += additional

        elif evaluation.recommendation.action == "need_rewrite":
            # 重写
            section = SectionWriter.rewrite(section, evaluation.suggestions)

        iteration += 1

    if not evaluation.passed:
        # 达到最大迭代次数仍未通过，标记警告
        section.warnings.append("Quality threshold not met")
```

---

## 📊 置信度计算

### 段落置信度

```python
def calculate_section_confidence(section, evaluation):
    weights = {
        "completeness": 0.3,
        "accuracy": 0.3,
        "relevance": 0.25,
        "coherence": 0.15
    }

    confidence = sum(
        evaluation.scores[criterion] * weight
        for criterion, weight in weights.items()
    )

    return confidence
```

### 报告整体置信度

```python
def calculate_report_confidence(sections):
    section_confidences = [s.confidence for s in sections]

    # 加权平均（按段落重要性）
    weights = [s.importance for s in sections]

    overall = sum(c * w for c, w in zip(section_confidences, weights)) / sum(weights)

    return overall
```

---

## 🎯 优势分析

### vs. 单一智能体

| 维度 | 单一智能体 | 多智能体协作 |
|------|-----------|-------------|
| 质量控制 | ❌ 无评估机制 | ✅ 多重评估 |
| 内容完整性 | ⚠️ 可能不足 | ✅ 自动补充 |
| 结构性 | ⚠️ 依赖提示词 | ✅ 独立大纲生成 |
| 并行化 | ❌ 串行 | ✅ 并行写作 |
| 可控性 | ⚠️ 低 | ✅ 高（迭代优化）|
| 速度 | 中等 | ⚡ 更快（并行） |

---

## 📈 性能预估

### 时间复杂度

**单一智能体**:
- 报告生成: O(N) - 一次性生成
- 总时间: ~60秒

**多智能体协作**:
- 大纲生成: O(1) - ~5秒
- 并行写作: O(1) - ~15秒 (N个段落并行)
- 评估优化: O(K) - K次迭代，~10秒/次
- 组装: O(1) - ~3秒

**总时间**: ~20-40秒（取决于迭代次数）

### 质量提升

- **完整性**: +40%
- **准确性**: +35%
- **结构性**: +50%
- **可读性**: +30%

---

## 🔧 技术实现

### 并行化策略

```python
import asyncio

async def parallel_section_writing(sections, available_content):
    """并行写作所有段落"""

    tasks = []
    for section in sections:
        writer = SectionWriter()
        task = writer.write_section(section, available_content)
        tasks.append(task)

    # 并行执行
    results = await asyncio.gather(*tasks, return_exceptions=True)

    return results
```

### 状态管理

```python
class ReportGenerationState:
    """报告生成状态"""

    def __init__(self):
        self.outline = None
        self.sections = {}  # {section_id: SectionState}
        self.iterations = {}  # {section_id: iteration_count}
        self.completed = set()  # 已完成的段落ID
        self.confidence_threshold = 0.7

    def is_section_complete(self, section_id):
        return section_id in self.completed

    def all_sections_complete(self):
        return len(self.completed) == len(self.sections)
```

---

## 📝 示例流程

### 输入查询
```
"人工智能在医疗领域的最新应用"
```

### 1. 大纲生成
```markdown
# 人工智能在医疗领域的最新应用

## 1. 引言
- 背景介绍
- 研究意义
- 报告结构

## 2. AI诊断技术
- 医学影像分析
- 疾病预测
- 案例研究

## 3. AI辅助治疗
- 个性化治疗方案
- 手术机器人
- 药物研发

## 4. 挑战与展望
- 伦理问题
- 技术限制
- 未来趋势

## 5. 总结
- 核心发现
- 建议
```

### 2. 并行写作（4个段落同时）

```
Writer-1 (引言)      ─┐
Writer-2 (AI诊断)    ─┼─→ 同时执行
Writer-3 (AI治疗)    ─┤
Writer-4 (挑战展望)  ─┘
```

### 3. 评估与优化

```
段落2评估: confidence=0.65 (< 0.7)
├─ 问题: "缺少具体案例数据"
├─ 建议: need_more_content
└─ 行动: ContentSearcher 补充案例

段落2重写: confidence=0.82 ✓
```

### 4. 最终组装

```markdown
# 人工智能在医疗领域的最新应用

[完整的、经过优化的报告内容]

## 参考来源
- [15个引用来源]

## 报告元数据
- 生成时间: 2025-10-01
- 总字数: 3500
- 置信度: 0.85
```

---

## 🚀 实施计划

### Phase 1: 核心智能体实现
- [ ] OutlineGenerator
- [ ] SectionWriter
- [ ] SectionEvaluator

### Phase 2: 辅助功能
- [ ] ContentSearcher
- [ ] ReportAssembler

### Phase 3: 协调与集成
- [ ] ReportCoordinator
- [ ] 集成到现有系统

### Phase 4: 优化与测试
- [ ] 性能优化
- [ ] 质量测试
- [ ] 用户反馈

---

## 📊 成功指标

| 指标 | 目标 |
|------|------|
| 报告质量评分 | ≥ 8.5/10 |
| 整体置信度 | ≥ 0.80 |
| 生成时间 | ≤ 40秒 |
| 信息完整性 | ≥ 90% |
| 用户满意度 | ≥ 85% |

---

**设计完成** ✅

该架构提供了一个可扩展、高质量的多智能体报告生成系统。
