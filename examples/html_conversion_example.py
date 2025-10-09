"""
HTML

HTMLMarkdownHTML
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


def example_document_conversion():
    """1"""
    print("\n===  ===\n")

    # HTML
    agent = DocumentHTMLAgent()

    # 
    content = """
# 

## 

AI

## 1. 

Artificial Intelligence, AIAI

## 2. 

### 2.1 



- 
- 
- 

### 2.2 

NLP

- 
- 
- 

## 3. 

### 

AI

### 

AI

## 4. 


"""

    # 
    metadata = {
        'title': '',
        'author': '',
        'date': '2025-10-02',
        'keywords': ['', '', '', 'AI']
    }

    # HTML
    html = agent.convert_to_html(
        content=content,
        metadata=metadata,
        template='academic',
        theme='light',
        output_path=Path('output/document_example.html')
    )

    print(f" HTML: output/document_example.html")
    print(f" HTML: {len(html)} ")


def example_fiction_conversion():
    """2"""
    print("\n===  ===\n")

    # HTML
    agent = FictionHTMLAgent()

    # 
    content = """
# 

##  







"..."""

##  





""





##  





""

...
"""

    # 
    metadata = {
        'title': '',
        'author': '',
        'genre': '',
        'synopsis': ''
    }

    # HTML
    html = agent.convert_to_html(
        content=content,
        metadata=metadata,
        template='novel',
        theme='sepia',
        output_path=Path('output/fiction_example.html')
    )

    print(f" HTML: output/fiction_example.html")
    print(f" HTML: {len(html)} ")


def example_ppt_conversion():
    """3PPT"""
    print("\n=== PPT ===\n")

    # PPT HTML
    agent = PPTHTMLAgent(framework='reveal')

    # PPT
    content = """
# AI



---

## AI

Artificial Intelligence

---

## AI

- 
- 
- 
- 
- 

---

## 

### 

- 
- 
- 

### 

- 
- 
- 

---

## 

AI

![Future](https://via.placeholder.com/600x400?text=AI+Future)
"""

    # 
    metadata = {
        'title': 'AI',
        'author': '',
        'date': '2025-10-02',
        'subtitle': ''
    }

    # HTML
    html = agent.convert_to_html(
        content=content,
        metadata=metadata,
        template='default',
        theme='sky',
        output_path=Path('output/ppt_example.html')
    )

    print(f" PPTHTML: output/ppt_example.html")
    print(f" HTML: {len(html)} ")
    print(f" ")


def example_template_registry():
    """4"""
    print("\n===  ===\n")

    # 
    registry = get_template_registry()

    # 
    print(" ")
    doc_templates = registry.list_templates('document')
    for template in doc_templates:
        print(f"  - {template.name}: {template.description}")

    # 
    print("\n ")
    fiction_templates = registry.list_templates('fiction')
    for template in fiction_templates:
        print(f"  - {template.name}: {template.description}")

    # PPT
    print("\n PPT")
    ppt_templates = registry.list_templates('ppt')
    for template in ppt_templates:
        print(f"  - {template.name} ({template.framework}): {template.description}")

    # 
    print("\n ")
    themes = registry.list_themes()
    for theme in themes:
        print(f"  - {theme.name}: {theme.display_name} - {theme.description}")

    # 
    print("\n ")
    content = "..."
    recommended = registry.recommend_template('document', content)
    print(f"  : {recommended}")


def example_custom_template():
    """5"""
    print("\n===  ===\n")

    from src.agents.html import TemplateInfo, ThemeInfo

    registry = get_template_registry()

    # 
    custom_template = TemplateInfo(
        name="custom_doc",
        agent_type="document",
        file_path="custom_doc.html",
        description="",
        supports_themes=['light', 'dark', 'custom'],
        tags=['custom', 'personal']
    )
    registry.register_template(custom_template)
    print(f" : {custom_template.name}")

    # 
    custom_theme = ThemeInfo(
        name="ocean",
        display_name="",
        description="",
        css_vars={
            "--bg-color": "#e8f4f8",
            "--text-color": "#1e3a5f",
            "--primary-color": "#0077be",
            "--secondary-color": "#00a8cc"
        },
        applies_to=['document', 'fiction']
    )
    registry.register_theme(custom_theme)
    print(f" : {custom_theme.name}")

    # 
    registry.save_config()
    print(f" ")


def main():
    """TODO: Add docstring."""
    print("=" * 60)
    print("HTML")
    print("=" * 60)

    # 
    Path('output').mkdir(exist_ok=True)

    # 
    example_document_conversion()
    example_fiction_conversion()
    example_ppt_conversion()
    example_template_registry()
    example_custom_template()

    print("\n" + "=" * 60)
    print(" ")
    print("=" * 60)


if __name__ == "__main__":
    main()
