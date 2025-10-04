"""
DOCX导出器 - 将报告/小说导出为Word文档
"""
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger


class DOCXExporter:
    """DOCX导出器"""

    async def export(
        self,
        project_dir: Path,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        导出为DOCX文件

        Args:
            project_dir: 项目目录
            output_path: 输出文件路径

        Returns:
            导出结果
        """
        try:
            from docx import Document
            from docx.shared import Pt, RGBColor, Inches
            from docx.enum.text import WD_ALIGN_PARAGRAPH

            # 查找Markdown文件
            md_file = project_dir / "reports" / "FINAL_REPORT.md"
            if not md_file.exists():
                return {
                    "status": "error",
                    "error": "找不到Markdown报告文件"
                }

            # 读取内容
            with open(md_file, 'r', encoding='utf-8') as f:
                md_content = f.read()

            logger.info(f"开始导出DOCX: {md_file}")

            # 创建Word文档
            doc = Document()

            # 解析Markdown并添加到文档
            self._parse_markdown_to_docx(doc, md_content)

            # 确定输出路径
            if not output_path:
                output_path = project_dir / "exports" / "report.docx"
            else:
                output_path = Path(output_path)

            output_path.parent.mkdir(parents=True, exist_ok=True)

            # 保存文件
            doc.save(str(output_path))

            # 获取文件大小
            file_size = output_path.stat().st_size
            file_size_str = self._format_file_size(file_size)

            logger.info(f"DOCX导出成功: {output_path}")

            return {
                "status": "success",
                "output_file": str(output_path),
                "file_size": file_size_str
            }

        except ImportError:
            return {
                "status": "error",
                "error": "需要安装python-docx库: pip install python-docx"
            }
        except Exception as e:
            logger.error(f"DOCX导出失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "error": str(e)
            }

    def _parse_markdown_to_docx(self, doc, md_content: str):
        """
        简单的Markdown到DOCX转换
        """
        from docx.shared import Pt

        lines = md_content.split('\n')

        for line in lines:
            line = line.strip()

            if not line:
                continue

            # 标题
            if line.startswith('# '):
                p = doc.add_heading(line[2:], level=1)
            elif line.startswith('## '):
                p = doc.add_heading(line[3:], level=2)
            elif line.startswith('### '):
                p = doc.add_heading(line[4:], level=3)

            # 列表
            elif line.startswith('- ') or line.startswith('* '):
                p = doc.add_paragraph(line[2:], style='List Bullet')

            # 数字列表
            elif line[0].isdigit() and '. ' in line[:4]:
                parts = line.split('. ', 1)
                if len(parts) == 2:
                    p = doc.add_paragraph(parts[1], style='List Number')

            # 普通段落
            else:
                p = doc.add_paragraph(line)
                p.paragraph_format.line_spacing = 1.5

    def _format_file_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
