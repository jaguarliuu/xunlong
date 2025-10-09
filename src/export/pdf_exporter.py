"""
PDF - /PDF
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger


# weasyprintmacOS
if os.path.exists('/opt/homebrew/lib'):
    os.environ['DYLD_LIBRARY_PATH'] = f"/opt/homebrew/lib:{os.environ.get('DYLD_LIBRARY_PATH', '')}"


class PDFExporter:
    """PDF"""

    async def export(
        self,
        project_dir: Path,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        PDF

        Args:
            project_dir: 
            output_path: 

        Returns:
            
        """
        try:
            # HTML
            html_file = project_dir / "reports" / "FINAL_REPORT.html"
            if not html_file.exists():
                return {
                    "status": "error",
                    "error": "HTML"
                }

            # 
            if not output_path:
                output_path = project_dir / "exports" / "report.pdf"
            else:
                output_path = Path(output_path)

            output_path.parent.mkdir(parents=True, exist_ok=True)

            logger.info(f"PDF: {html_file} -> {output_path}")

            # weasyprintHTMLPDF
            try:
                from weasyprint import HTML
                HTML(filename=str(html_file)).write_pdf(str(output_path))
            except ImportError:
                # Fallback: markdown2 + pdfkit
                return await self._export_from_markdown(project_dir, output_path)

            # 
            file_size = output_path.stat().st_size
            file_size_str = self._format_file_size(file_size)

            logger.info(f"PDF: {output_path}")

            return {
                "status": "success",
                "output_file": str(output_path),
                "file_size": file_size_str
            }

        except ImportError:
            return {
                "status": "error",
                "error": "weasyprint: pip install weasyprint"
            }
        except Exception as e:
            logger.error(f"PDF: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "error": str(e)
            }

    async def _export_from_markdown(self, project_dir: Path, output_path: Path) -> Dict[str, Any]:
        """MarkdownPDF"""
        md_file = project_dir / "reports" / "FINAL_REPORT.md"
        if not md_file.exists():
            return {
                "status": "error",
                "error": "Markdown"
            }

        # Markdown
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # HTML
        import markdown2
        html_content = markdown2.markdown(md_content, extras=['tables', 'fenced-code-blocks'])

        # HTML
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

        # HTML
        temp_html = output_path.parent / "temp.html"
        with open(temp_html, 'w', encoding='utf-8') as f:
            f.write(full_html)

        # PDF
        from weasyprint import HTML
        HTML(filename=str(temp_html)).write_pdf(str(output_path))

        # 
        temp_html.unlink()

        file_size = output_path.stat().st_size
        file_size_str = self._format_file_size(file_size)

        return {
            "status": "success",
            "output_file": str(output_path),
            "file_size": file_size_str
        }

    def _format_file_size(self, size_bytes: int) -> str:
        """TODO: Add docstring."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
