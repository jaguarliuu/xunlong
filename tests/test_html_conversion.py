"""
HTML
"""

import sys
from pathlib import Path

# Python
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.html import (
    DocumentHTMLAgent,
    FictionHTMLAgent,
    PPTHTMLAgent,
    get_template_registry
)


def test_document_agent():
    """TODO: Add docstring."""
    agent = DocumentHTMLAgent()
    content = """
# 

## 



## 


"""

    html = agent.convert_to_html(
        content=content,
        metadata={'title': '', 'author': ''},
        template='academic',
        theme='light'
    )

    assert '<h1' in html
    assert '' in html
    print(" ")


def test_fiction_agent():
    """TODO: Add docstring."""
    agent = FictionHTMLAgent()
    content = """
# 

##  

...

##  

...
"""

    html = agent.convert_to_html(
        content=content,
        metadata={'title': '', 'author': ''},
        template='novel',
        theme='sepia'
    )

    assert '<h1' in html or '<h2' in html
    assert '' in html
    print(" ")


def test_ppt_agent():
    """PPT"""
    agent = PPTHTMLAgent(framework='reveal')
    content = """
# PPT

---

## 

- 1
- 2

---

## 

...
"""

    html = agent.convert_to_html(
        content=content,
        metadata={'title': 'PPT'},
        template='default',
        theme='white'
    )

    assert 'reveal' in html.lower()
    assert 'PPT' in html
    print(" PPT")


def test_template_registry():
    """TODO: Add docstring."""
    registry = get_template_registry()

    # 
    doc_templates = registry.list_templates('document')
    assert len(doc_templates) > 0

    # 
    recommended = registry.recommend_template('document', '')
    assert recommended in ['academic', 'technical']

    print(" ")


def test_chapter_extraction():
    """TODO: Add docstring."""
    agent = DocumentHTMLAgent()
    content = """
# 

## 

1

### 1.1 

1.1

## 

2
"""

    parsed = agent.parse_content(content)
    assert len(parsed['sections']) > 0
    assert parsed['title'] == ''
    print(" ")


def test_ppt_smart_split():
    """PPT"""
    agent = PPTHTMLAgent(framework='reveal')
    content = """
# 



## 



## 


"""

    parsed = agent.parse_content(content)
    slides = parsed['slides']

    # 
    assert len(slides) >= 2
    assert slides[0]['layout'] == 'title'
    print(" PPT")


if __name__ == "__main__":
    print("=" * 60)
    print("HTML")
    print("=" * 60)

    test_document_agent()
    test_fiction_agent()
    test_ppt_agent()
    test_template_registry()
    test_chapter_extraction()
    test_ppt_smart_split()

    print("\n" + "=" * 60)
    print(" ")
    print("=" * 60)
