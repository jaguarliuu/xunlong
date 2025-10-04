"""
PDF导出器 - 将报告/小说导出为PDF文件
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger


# 设置weasyprint所需的环境变量（macOS）
if os.path.exists('/opt/homebrew/lib'):
    os.environ['DYLD_LIBRARY_PATH'] = f"/opt/homebrew/lib:{os.environ.get('DYLD_LIBRARY_PATH', '')}"


class PDFExporter:
    """PDF导出器"""

    async def export(
        self,
        project_dir: Path,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        导出为PDF文件

        Args:
            project_dir: 项目目录
            output_path: 输出文件路径

        Returns:
            导出结果
        """
        try:
            # 查找HTML文件
            html_file = project_dir / "reports" / "FINAL_REPORT.html"
            if not html_file.exists():
                return {
                    "status": "error",
                    "error": "找不到HTML报告文件"
                }

            # 确定输出路径
            if not output_path:
                output_path = project_dir / "exports" / "report.pdf"
            else:
                output_path = Path(output_path)

            output_path.parent.mkdir(parents=True, exist_ok=True)

            logger.info(f"开始导出PDF: {html_file} -> {output_path}")

            # 使用weasyprint将HTML转为PDF
            try:
                from weasyprint import HTML
                HTML(filename=str(html_file)).write_pdf(str(output_path))
            except ImportError:
                # Fallback: 使用markdown2 + pdfkit
                return await self._export_from_markdown(project_dir, output_path)

            # 获取文件大小
            file_size = output_path.stat().st_size
            file_size_str = self._format_file_size(file_size)

            logger.info(f"PDF导出成功: {output_path}")

            return {
                "status": "success",
                "output_file": str(output_path),
                "file_size": file_size_str
            }

        except ImportError:
            return {
                "status": "error",
                "error": "需要安装weasyprint库: pip install weasyprint"
            }
        except Exception as e:
            logger.error(f"PDF导出失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "error": str(e)
            }

    async def _export_from_markdown(self, project_dir: Path, output_path: Path) -> Dict[str, Any]:
        """从Markdown导出PDF（备用方案）"""
        md_file = project_dir / "reports" / "FINAL_REPORT.md"
        if not md_file.exists():
            return {
                "status": "error",
                "error": "找不到Markdown报告文件"
            }

        # 读取Markdown内容
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # 转换为HTML
        import markdown2
        html_content = markdown2.markdown(md_content, extras=['tables', 'fenced-code-blocks'])

        # 创建完整HTML
        full_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'PingFang SC', 'Microsoft YaHei', Arial, sans-serif; line-height: 1.6; padding: 20px; }}
        h1, h2, h3 {{ color: #333; }}
        code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
        pre {{ background: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }}
    </style>
</head>
<body>
{html_content}
</body>
</html>
"""

        # 保存临时HTML
        temp_html = output_path.parent / "temp.html"
        with open(temp_html, 'w', encoding='utf-8') as f:
            f.write(full_html)

        # 转换为PDF
        from weasyprint import HTML
        HTML(filename=str(temp_html)).write_pdf(str(output_path))

        # 删除临时文件
        temp_html.unlink()

        file_size = output_path.stat().st_size
        file_size_str = self._format_file_size(file_size)

        return {
            "status": "success",
            "output_file": str(output_path),
            "file_size": file_size_str
        }

    def _format_file_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
