#!/usr/bin/env python
"""
 API 

 Unsplash  Pexels API
"""

import os
import sys
from pathlib import Path

# 
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown

console = Console()


def display_welcome():
    """"""
    welcome_text = """
#  XunLong 

 API

##  

1. **Unsplash** ()
   - 
   - : 5000/
   - 

2. **Pexels** ()
   - 
   - 
   - 


"""
    console.print(Panel(Markdown(welcome_text), title="", border_style="green"))


def get_unsplash_guide():
    """ Unsplash """
    guide = """
##   Unsplash API Key

### :

1.  https://unsplash.com/developers
2.  "Register as a developer"
3.  "New Application"
4. :
   - Application name: XunLong Image Search
   - Description: AI document illustration tool
5. 
6.  **Access Key**

### :
- Access Key : `abc123def456...`
- 
"""
    return guide


def get_pexels_guide():
    """ Pexels """
    guide = """
##   Pexels API Key

### :

1.  https://www.pexels.com/api/
2.  "Get Started"
3. 
4.  API  "Your API Key"
5.  API Key

### :
- API Key 
- 
"""
    return guide


def update_env_file(key: str, value: str):
    """ .env """
    env_file = Path(".env")
    env_example = Path(".env.example")

    #  .env  .env.example 
    if not env_file.exists():
        if env_example.exists():
            env_file.write_text(env_example.read_text())
            console.print("  .env.example  .env ", style="green")
        else:
            env_file.write_text("")
            console.print("  .env ", style="green")

    # 
    lines = env_file.read_text().split('\n')

    # 
    key_exists = False
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={value}"
            key_exists = True
            break

    # 
    if not key_exists:
        # 
        for i, line in enumerate(lines):
            if "API" in line or "IMAGE" in line.upper():
                # 
                lines.insert(i + 1, f"{key}={value}")
                break
        else:
            # 
            lines.append(f"\n# API")
            lines.append(f"{key}={value}")

    # 
    env_file.write_text('\n'.join(lines))


def configure_unsplash():
    """ Unsplash"""
    console.print("\n")
    console.print(Panel(Markdown(get_unsplash_guide()), title="Unsplash ", border_style="blue"))

    if Confirm.ask("\n Unsplash Access Key"):
        access_key = Prompt.ask(" Access Key", password=True)

        if access_key and len(access_key) > 10:
            update_env_file("UNSPLASH_ACCESS_KEY", access_key)
            console.print(" Unsplash API ", style="bold green")
            return True
        else:
            console.print(" API Key ", style="bold red")
            return False
    else:
        console.print(" API Key ", style="yellow")
        return False


def configure_pexels():
    """ Pexels"""
    console.print("\n")
    console.print(Panel(Markdown(get_pexels_guide()), title="Pexels ", border_style="blue"))

    if Confirm.ask("\n Pexels API Key"):
        api_key = Prompt.ask(" API Key", password=True)

        if api_key and len(api_key) > 10:
            update_env_file("PEXELS_API_KEY", api_key)
            console.print(" Pexels API ", style="bold green")
            return True
        else:
            console.print(" API Key ", style="bold red")
            return False
    else:
        console.print(" API Key ", style="yellow")
        return False


def configure_settings():
    """"""
    console.print("\n")
    console.print(Panel("", border_style="cyan"))

    # 
    enable = Confirm.ask("", default=True)
    update_env_file("ENABLE_DOCUMENT_IMAGES", "true" if enable else "false")

    if enable:
        # 
        images_per_section = Prompt.ask(
            "",
            choices=["1", "2", "3", "4", "5"],
            default="2"
        )
        update_env_file("IMAGES_PER_SECTION", images_per_section)

        # 
        console.print("\n:")
        console.print("  - smart: ")
        console.print("  - top: ")
        console.print("  - bottom: ")
        console.print("  - distribute: ")

        insert_mode = Prompt.ask(
            "",
            choices=["smart", "top", "bottom", "distribute"],
            default="smart"
        )
        update_env_file("IMAGE_INSERT_MODE", insert_mode)

    console.print("\n ", style="bold green")


def test_configuration():
    """"""
    console.print("\n")
    if Confirm.ask(""):
        console.print("\n...\n", style="bold cyan")
        os.system("python examples/image_feature_test.py")


def main():
    """"""
    display_welcome()

    console.print("\n")

    #  API
    choice = Prompt.ask(
        "",
        choices=["1", "2", "3"],
        default="1"
    )

    unsplash_configured = False
    pexels_configured = False

    if choice == "1":
        console.print("\n[bold] Unsplash[/bold]")
        unsplash_configured = configure_unsplash()

    elif choice == "2":
        console.print("\n[bold] Pexels[/bold]")
        pexels_configured = configure_pexels()

    elif choice == "3":
        console.print("\n[bold][/bold]")
        unsplash_configured = configure_unsplash()
        if unsplash_configured:
            pexels_configured = configure_pexels()

    # 
    if unsplash_configured or pexels_configured:
        configure_settings()

        # 
        console.print("\n")
        console.print(Panel.fit(
            """
[bold green] [/bold green]

:
""" +
            (f"   Unsplash API \n" if unsplash_configured else "") +
            (f"   Pexels API \n" if pexels_configured else "") +
            """
:
  1. : python examples/image_feature_test.py
  2. : python xunlong.py report ""
  3. : docs/IMAGE_FEATURE_GUIDE.md
""",
            title="",
            border_style="green"
        ))

        # 
        test_configuration()

    else:
        console.print("\n[yellow][/yellow]")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[yellow][/yellow]")
        sys.exit(0)
