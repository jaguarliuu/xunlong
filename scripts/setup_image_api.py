#!/usr/bin/env python
"""
图片 API 配置助手

帮助用户快速配置 Unsplash 或 Pexels API
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown

console = Console()


def display_welcome():
    """显示欢迎信息"""
    welcome_text = """
# 🎨 XunLong 图片功能配置向导

欢迎使用图片功能！本向导将帮助你快速配置图片 API。

## 📸 可用的图片源

1. **Unsplash** (推荐)
   - 高质量专业摄影作品
   - 免费额度: 5000次/小时
   - 需要注册账号

2. **Pexels** (备选)
   - 多样化免费图片
   - 无限制免费使用
   - 需要注册账号

你可以配置一个或两个，系统会自动选择最佳源。
"""
    console.print(Panel(Markdown(welcome_text), title="欢迎", border_style="green"))


def get_unsplash_guide():
    """获取 Unsplash 配置指南"""
    guide = """
## 🔑 获取 Unsplash API Key

### 步骤:

1. 访问 https://unsplash.com/developers
2. 点击 "Register as a developer"（如果未注册）
3. 登录后，点击 "New Application"
4. 填写应用信息:
   - Application name: XunLong Image Search
   - Description: AI document illustration tool
5. 同意服务条款
6. 创建成功后，复制 **Access Key**

### 注意:
- Access Key 格式类似: `abc123def456...`
- 保存好密钥，不要分享给他人
"""
    return guide


def get_pexels_guide():
    """获取 Pexels 配置指南"""
    guide = """
## 🔑 获取 Pexels API Key

### 步骤:

1. 访问 https://www.pexels.com/api/
2. 点击 "Get Started"
3. 注册或登录账号
4. 在 API 页面点击 "Your API Key"
5. 复制显示的 API Key

### 注意:
- API Key 会直接显示，无需创建应用
- 保存好密钥，不要分享给他人
"""
    return guide


def update_env_file(key: str, value: str):
    """更新 .env 文件"""
    env_file = Path(".env")
    env_example = Path(".env.example")

    # 如果 .env 不存在，从 .env.example 复制
    if not env_file.exists():
        if env_example.exists():
            env_file.write_text(env_example.read_text())
            console.print("✓ 已从 .env.example 创建 .env 文件", style="green")
        else:
            env_file.write_text("")
            console.print("✓ 已创建新的 .env 文件", style="green")

    # 读取现有内容
    lines = env_file.read_text().split('\n')

    # 检查是否已存在该配置
    key_exists = False
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={value}"
            key_exists = True
            break

    # 如果不存在，添加新配置
    if not key_exists:
        # 找到图片配置区域
        for i, line in enumerate(lines):
            if "图片搜索API配置" in line or "IMAGE" in line.upper():
                # 在该区域后添加
                lines.insert(i + 1, f"{key}={value}")
                break
        else:
            # 如果找不到区域，添加到文件末尾
            lines.append(f"\n# 图片API配置")
            lines.append(f"{key}={value}")

    # 写回文件
    env_file.write_text('\n'.join(lines))


def configure_unsplash():
    """配置 Unsplash"""
    console.print("\n")
    console.print(Panel(Markdown(get_unsplash_guide()), title="Unsplash 配置", border_style="blue"))

    if Confirm.ask("\n是否已获取 Unsplash Access Key？"):
        access_key = Prompt.ask("请输入 Access Key", password=True)

        if access_key and len(access_key) > 10:
            update_env_file("UNSPLASH_ACCESS_KEY", access_key)
            console.print("✓ Unsplash API 配置成功！", style="bold green")
            return True
        else:
            console.print("✗ API Key 格式不正确，请重新输入", style="bold red")
            return False
    else:
        console.print("请先获取 API Key 后再运行此脚本", style="yellow")
        return False


def configure_pexels():
    """配置 Pexels"""
    console.print("\n")
    console.print(Panel(Markdown(get_pexels_guide()), title="Pexels 配置", border_style="blue"))

    if Confirm.ask("\n是否已获取 Pexels API Key？"):
        api_key = Prompt.ask("请输入 API Key", password=True)

        if api_key and len(api_key) > 10:
            update_env_file("PEXELS_API_KEY", api_key)
            console.print("✓ Pexels API 配置成功！", style="bold green")
            return True
        else:
            console.print("✗ API Key 格式不正确，请重新输入", style="bold red")
            return False
    else:
        console.print("请先获取 API Key 后再运行此脚本", style="yellow")
        return False


def configure_settings():
    """配置图片功能设置"""
    console.print("\n")
    console.print(Panel("图片功能设置", border_style="cyan"))

    # 是否启用
    enable = Confirm.ask("是否启用文档配图功能？", default=True)
    update_env_file("ENABLE_DOCUMENT_IMAGES", "true" if enable else "false")

    if enable:
        # 每章节图片数量
        images_per_section = Prompt.ask(
            "每个章节配图数量",
            choices=["1", "2", "3", "4", "5"],
            default="2"
        )
        update_env_file("IMAGES_PER_SECTION", images_per_section)

        # 插入模式
        console.print("\n插入模式说明:")
        console.print("  - smart: 智能插入（推荐）")
        console.print("  - top: 集中在开头")
        console.print("  - bottom: 附录模式")
        console.print("  - distribute: 均匀分布")

        insert_mode = Prompt.ask(
            "选择图片插入模式",
            choices=["smart", "top", "bottom", "distribute"],
            default="smart"
        )
        update_env_file("IMAGE_INSERT_MODE", insert_mode)

    console.print("\n✓ 图片功能设置完成！", style="bold green")


def test_configuration():
    """测试配置"""
    console.print("\n")
    if Confirm.ask("是否运行测试以验证配置？"):
        console.print("\n正在运行测试...\n", style="bold cyan")
        os.system("python examples/image_feature_test.py")


def main():
    """主流程"""
    display_welcome()

    console.print("\n")

    # 选择配置哪个 API
    choice = Prompt.ask(
        "请选择要配置的图片源",
        choices=["1", "2", "3"],
        default="1"
    )

    unsplash_configured = False
    pexels_configured = False

    if choice == "1":
        console.print("\n[bold]配置 Unsplash[/bold]")
        unsplash_configured = configure_unsplash()

    elif choice == "2":
        console.print("\n[bold]配置 Pexels[/bold]")
        pexels_configured = configure_pexels()

    elif choice == "3":
        console.print("\n[bold]配置两个图片源[/bold]")
        unsplash_configured = configure_unsplash()
        if unsplash_configured:
            pexels_configured = configure_pexels()

    # 配置功能设置
    if unsplash_configured or pexels_configured:
        configure_settings()

        # 显示总结
        console.print("\n")
        console.print(Panel.fit(
            """
[bold green]✅ 配置完成！[/bold green]

已配置的图片源:
""" +
            (f"  • Unsplash API ✓\n" if unsplash_configured else "") +
            (f"  • Pexels API ✓\n" if pexels_configured else "") +
            """
接下来可以:
  1. 运行测试: python examples/image_feature_test.py
  2. 生成报告: python xunlong.py report "你的主题"
  3. 查看文档: docs/IMAGE_FEATURE_GUIDE.md
""",
            title="设置完成",
            border_style="green"
        ))

        # 运行测试
        test_configuration()

    else:
        console.print("\n[yellow]未完成任何配置，请重新运行此脚本[/yellow]")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]配置已取消[/yellow]")
        sys.exit(0)
