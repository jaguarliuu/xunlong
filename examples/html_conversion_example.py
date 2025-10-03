"""
HTML转换示例

演示如何使用HTML转换智能体将Markdown内容转换为HTML
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.html import (
    DocumentHTMLAgent,
    FictionHTMLAgent,
    PPTHTMLAgent,
    get_template_registry
)


def example_document_conversion():
    """示例1：文档转换"""
    print("\n=== 文档转换示例 ===\n")

    # 创建文档HTML转换智能体
    agent = DocumentHTMLAgent()

    # 示例文档内容
    content = """
# 人工智能在医疗领域的应用研究

## 摘要

本文探讨了人工智能技术在医疗领域的应用现状和未来发展趋势。通过分析深度学习、自然语言处理等关键技术，总结了AI在疾病诊断、药物研发、患者管理等方面的创新应用。

## 1. 引言

人工智能（Artificial Intelligence, AI）正在深刻改变医疗行业的面貌。随着计算能力的提升和大数据的积累，AI技术在医疗领域展现出巨大的应用潜力。

## 2. 关键技术

### 2.1 深度学习

深度学习技术在医学影像分析中表现出色，能够：

- 自动识别病灶
- 辅助诊断决策
- 预测疾病风险

### 2.2 自然语言处理

NLP技术可以处理海量医疗文献和病历，实现：

- 知识图谱构建
- 临床决策支持
- 病历自动生成

## 3. 应用案例

### 医学影像诊断

AI系统在肺癌、乳腺癌等疾病的影像诊断中达到了专家级水平。

### 药物研发

通过AI加速药物筛选和优化过程，大幅缩短研发周期。

## 4. 结论

人工智能技术将继续推动医疗行业的数字化转型，为人类健康事业做出更大贡献。
"""

    # 元数据
    metadata = {
        'title': '人工智能在医疗领域的应用研究',
        'author': '张三',
        'date': '2025-10-02',
        'keywords': ['人工智能', '医疗', '深度学习', 'AI应用']
    }

    # 转换为HTML
    html = agent.convert_to_html(
        content=content,
        metadata=metadata,
        template='academic',
        theme='light',
        output_path=Path('output/document_example.html')
    )

    print(f"✅ 文档已转换为HTML，保存在: output/document_example.html")
    print(f"📄 生成的HTML长度: {len(html)} 字符")


def example_fiction_conversion():
    """示例2：小说转换"""
    print("\n=== 小说转换示例 ===\n")

    # 创建小说HTML转换智能体
    agent = FictionHTMLAgent()

    # 示例小说内容
    content = """
# 暴风雪山庄

## 第一章 意外邀请

秋末的一个午后，侦探林墨收到了一封神秘的邀请函。

邀请函上写着：诚邀您参加在雪山庄园举办的周末聚会。落款是一个陌生的名字：白川雪子。

林墨仔细端详着这封邀请函，精美的纸张，优雅的字迹，但总感觉有些不寻常。

"雪山庄园..."他喃喃自语，"那不是多年前发生过命案的地方吗？"

## 第二章 暴风来临

周五傍晚，林墨如约来到了位于山顶的雪山庄园。

庄园建在悬崖边上，四周是茫茫的雪山。此时天色渐暗，一场暴风雪正在酝酿。

管家白川次郎在门口迎接："林侦探，主人已经等候多时了。"

大厅里已经聚集了其他六位客人，每个人的表情都显得有些紧张不安。

就在晚餐即将开始的时候，外面的暴风雪骤然而至，所有通往山下的道路都被封死了。

## 第三章 密室谜案

第二天清晨，一声尖叫打破了庄园的宁静。

主人白川雪子被发现死在她的书房里，门窗紧锁，现场没有任何打斗的痕迹。

"这是一起典型的密室杀人案！"林墨说道。

调查开始了，每个人都有嫌疑，每个人都有秘密...
"""

    # 元数据
    metadata = {
        'title': '暴风雪山庄',
        'author': '李四',
        'genre': '推理小说',
        'synopsis': '一场暴风雪将几位陌生人困在山顶庄园，当密室杀人案发生时，真相究竟是什么？'
    }

    # 转换为HTML
    html = agent.convert_to_html(
        content=content,
        metadata=metadata,
        template='novel',
        theme='sepia',
        output_path=Path('output/fiction_example.html')
    )

    print(f"✅ 小说已转换为HTML，保存在: output/fiction_example.html")
    print(f"📖 生成的HTML长度: {len(html)} 字符")


def example_ppt_conversion():
    """示例3：PPT转换"""
    print("\n=== PPT转换示例 ===\n")

    # 创建PPT HTML转换智能体
    agent = PPTHTMLAgent(framework='reveal')

    # 示例PPT内容
    content = """
# AI驱动的未来

副标题：探索人工智能的无限可能

---

## 什么是AI？

人工智能（Artificial Intelligence）是计算机科学的一个分支，旨在创建能够模拟人类智能的系统。

---

## AI的核心技术

- 机器学习
- 深度学习
- 自然语言处理
- 计算机视觉
- 强化学习

---

## 应用场景

### 医疗健康

- 疾病诊断
- 药物研发
- 个性化治疗

### 金融科技

- 风险评估
- 智能投顾
- 反欺诈检测

---

## 未来展望

AI将继续改变我们的生活方式，创造更多可能性！

![Future](https://via.placeholder.com/600x400?text=AI+Future)
"""

    # 元数据
    metadata = {
        'title': 'AI驱动的未来',
        'author': '王五',
        'date': '2025-10-02',
        'subtitle': '探索人工智能的无限可能'
    }

    # 转换为HTML
    html = agent.convert_to_html(
        content=content,
        metadata=metadata,
        template='default',
        theme='sky',
        output_path=Path('output/ppt_example.html')
    )

    print(f"✅ PPT已转换为HTML，保存在: output/ppt_example.html")
    print(f"🎬 生成的HTML长度: {len(html)} 字符")
    print(f"💡 提示：在浏览器中打开，使用方向键切换幻灯片")


def example_template_registry():
    """示例4：使用模板注册中心"""
    print("\n=== 模板注册中心示例 ===\n")

    # 获取模板注册中心
    registry = get_template_registry()

    # 列出所有文档模板
    print("📄 可用的文档模板：")
    doc_templates = registry.list_templates('document')
    for template in doc_templates:
        print(f"  - {template.name}: {template.description}")

    # 列出所有小说模板
    print("\n📖 可用的小说模板：")
    fiction_templates = registry.list_templates('fiction')
    for template in fiction_templates:
        print(f"  - {template.name}: {template.description}")

    # 列出所有PPT模板
    print("\n🎬 可用的PPT模板：")
    ppt_templates = registry.list_templates('ppt')
    for template in ppt_templates:
        print(f"  - {template.name} ({template.framework}): {template.description}")

    # 列出所有主题
    print("\n🎨 可用的主题：")
    themes = registry.list_themes()
    for theme in themes:
        print(f"  - {theme.name}: {theme.display_name} - {theme.description}")

    # 推荐模板
    print("\n🤖 模板推荐：")
    content = "本文探讨了深度学习在图像识别领域的应用..."
    recommended = registry.recommend_template('document', content)
    print(f"  推荐模板: {recommended}")


def example_custom_template():
    """示例5：自定义模板和主题"""
    print("\n=== 自定义模板示例 ===\n")

    from src.agents.html import TemplateInfo, ThemeInfo

    registry = get_template_registry()

    # 注册自定义模板
    custom_template = TemplateInfo(
        name="custom_doc",
        agent_type="document",
        file_path="custom_doc.html",
        description="我的自定义文档模板",
        supports_themes=['light', 'dark', 'custom'],
        tags=['custom', 'personal']
    )
    registry.register_template(custom_template)
    print(f"✅ 已注册自定义模板: {custom_template.name}")

    # 注册自定义主题
    custom_theme = ThemeInfo(
        name="ocean",
        display_name="海洋主题",
        description="清新的海洋蓝配色",
        css_vars={
            "--bg-color": "#e8f4f8",
            "--text-color": "#1e3a5f",
            "--primary-color": "#0077be",
            "--secondary-color": "#00a8cc"
        },
        applies_to=['document', 'fiction']
    )
    registry.register_theme(custom_theme)
    print(f"✅ 已注册自定义主题: {custom_theme.name}")

    # 保存配置
    registry.save_config()
    print(f"💾 配置已保存")


def main():
    """运行所有示例"""
    print("=" * 60)
    print("HTML转换智能体使用示例")
    print("=" * 60)

    # 创建输出目录
    Path('output').mkdir(exist_ok=True)

    # 运行示例
    example_document_conversion()
    example_fiction_conversion()
    example_ppt_conversion()
    example_template_registry()
    example_custom_template()

    print("\n" + "=" * 60)
    print("✅ 所有示例运行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
