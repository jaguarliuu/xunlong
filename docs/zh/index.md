---
layout: home

hero:
  name: "XunLong (寻龙)"
  text: "AI驱动的内容生成系统"
  tagline: 多模态内容创作系统 - 报告、小说、演示文稿
  image:
    src: /icon.png
    alt: XunLong
  actions:
    - theme: brand
      text: 快速开始
      link: /zh/guide/getting-started
    - theme: alt
      text: GitHub
      link: https://github.com/jaguarliuu/xunlong

features:
  - icon: 🤖
    title: 多智能体协作
    details: 基于LangGraph的智能体编排，任务分解与并行执行
  - icon: 📊
    title: 多模态生成
    details: 支持报告、小说、PPT三种内容模式，专业品质输出
  - icon: 🔍
    title: 智能搜索
    details: 自动网络搜索、内容提取、知识整合
  - icon: 🎨
    title: 专业导出
    details: 支持Markdown、HTML、PDF、DOCX、PPTX多种格式
  - icon: 🔄
    title: 迭代优化
    details: 对已生成内容进行局部或全局修改
  - icon: 📈
    title: 可观测性
    details: 集成LangFuse，全流程追踪和监控

---

## 快速示例

```bash
# 生成研究报告
python xunlong.py report "2025年人工智能行业趋势分析"

# 生成小说
python xunlong.py fiction "一个关于时间旅行的科幻故事" --chapters 10

# 生成PPT
python xunlong.py ppt "2025年产品发布会" --slides 15
```

## 为什么选择XunLong？

XunLong将大语言模型的强大能力与精心设计的多智能体架构相结合，自动化完成从研究规划到内容生成、格式导出的全流程。

::: tip 适用场景
- 📄 **研究人员** - 生成全面的研究报告
- ✍️ **作家** - 创作引人入胜的小说故事
- 📊 **商务人士** - 制作专业的演示文稿
- 🎓 **学生** - 完成学术论文和作业
:::

## 可信赖的技术栈

基于业界领先的开源技术构建：

- **LangChain & LangGraph** - 强大的LLM应用框架
- **OpenAI / Anthropic / DeepSeek** - 先进的语言模型
- **Playwright** - 可靠的浏览器自动化
- **WeasyPrint** - 高质量PDF生成

---

<div style="text-align: center; margin-top: 48px;">
  <p>基于<a href="https://opensource.org/licenses/MIT">MIT许可证</a>发布</p>
  <p>Copyright © 2025-present XunLong Team</p>
</div>
