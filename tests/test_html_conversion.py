"""
HTML转换功能测试
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


def test_document_agent():
    """测试文档转换"""
    agent = DocumentHTMLAgent()
    content = """
# 测试文档

## 第一章

这是第一章的内容。

## 第二章

这是第二章的内容。
"""

    html = agent.convert_to_html(
        content=content,
        metadata={'title': '测试文档', 'author': '测试'},
        template='academic',
        theme='light'
    )

    assert '<h1' in html
    assert '测试文档' in html
    print("✅ 文档转换测试通过")


def test_fiction_agent():
    """测试小说转换"""
    agent = FictionHTMLAgent()
    content = """
# 测试小说

## 第一章 开始

故事开始了...

## 第二章 转折

发生了转折...
"""

    html = agent.convert_to_html(
        content=content,
        metadata={'title': '测试小说', 'author': '作者'},
        template='novel',
        theme='sepia'
    )

    assert '<h1' in html or '<h2' in html
    assert '测试小说' in html
    print("✅ 小说转换测试通过")


def test_ppt_agent():
    """测试PPT转换"""
    agent = PPTHTMLAgent(framework='reveal')
    content = """
# 测试PPT

---

## 第一页

- 要点1
- 要点2

---

## 第二页

内容...
"""

    html = agent.convert_to_html(
        content=content,
        metadata={'title': '测试PPT'},
        template='default',
        theme='white'
    )

    assert 'reveal' in html.lower()
    assert '测试PPT' in html
    print("✅ PPT转换测试通过")


def test_template_registry():
    """测试模板注册中心"""
    registry = get_template_registry()

    # 测试列出模板
    doc_templates = registry.list_templates('document')
    assert len(doc_templates) > 0

    # 测试推荐
    recommended = registry.recommend_template('document', '这是一篇学术论文')
    assert recommended in ['academic', 'technical']

    print("✅ 模板注册中心测试通过")


def test_chapter_extraction():
    """测试章节提取"""
    agent = DocumentHTMLAgent()
    content = """
# 主标题

## 第一章

内容1

### 1.1 小节

内容1.1

## 第二章

内容2
"""

    parsed = agent.parse_content(content)
    assert len(parsed['sections']) > 0
    assert parsed['title'] == '主标题'
    print("✅ 章节提取测试通过")


def test_ppt_smart_split():
    """测试PPT智能分页"""
    agent = PPTHTMLAgent(framework='reveal')
    content = """
# 演示标题

这是一个长内容的文档，需要被智能分割成多个幻灯片。

## 第一部分

这是第一部分的内容。

## 第二部分

这是第二部分的内容。
"""

    parsed = agent.parse_content(content)
    slides = parsed['slides']

    # 应该至少有标题页和内容页
    assert len(slides) >= 2
    assert slides[0]['layout'] == 'title'
    print("✅ PPT智能分页测试通过")


if __name__ == "__main__":
    print("=" * 60)
    print("HTML转换功能测试")
    print("=" * 60)

    test_document_agent()
    test_fiction_agent()
    test_ppt_agent()
    test_template_registry()
    test_chapter_extraction()
    test_ppt_smart_split()

    print("\n" + "=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)
