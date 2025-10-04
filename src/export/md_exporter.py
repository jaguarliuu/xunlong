"""
Markdown导出器 - 复制Markdown文件
"""
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger


class MDExporter:
    """Markdown导出器"""

    async def export(
        self,
        project_dir: Path,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        导出为Markdown文件（复制）

        Args:
            project_dir: 项目目录
            output_path: 输出文件路径

        Returns:
            导出结果
        """
        try:
            # 查找Markdown文件
            md_file = project_dir / "reports" / "FINAL_REPORT.md"
            if not md_file.exists():
                return {
                    "status": "error",
                    "error": "找不到Markdown报告文件"
                }

            # 确定输出路径
            if not output_path:
                output_path = project_dir / "exports" / "report.md"
            else:
                output_path = Path(output_path)

            output_path.parent.mkdir(parents=True, exist_ok=True)

            logger.info(f"开始导出Markdown: {md_file} -> {output_path}")

            # 复制文件
            shutil.copy(md_file, output_path)

            # 获取文件大小
            file_size = output_path.stat().st_size
            file_size_str = self._format_file_size(file_size)

            logger.info(f"Markdown导出成功: {output_path}")

            return {
                "status": "success",
                "output_file": str(output_path),
                "file_size": file_size_str
            }

        except Exception as e:
            logger.error(f"Markdown导出失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "error": str(e)
            }

    def _format_file_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
