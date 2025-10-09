"""
Markdown - Markdown
"""
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger


class MDExporter:
    """Markdown"""

    async def export(
        self,
        project_dir: Path,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Markdown

        Args:
            project_dir: 
            output_path: 

        Returns:
            
        """
        try:
            # Markdown
            md_file = project_dir / "reports" / "FINAL_REPORT.md"
            if not md_file.exists():
                return {
                    "status": "error",
                    "error": "Markdown"
                }

            # 
            if not output_path:
                output_path = project_dir / "exports" / "report.md"
            else:
                output_path = Path(output_path)

            output_path.parent.mkdir(parents=True, exist_ok=True)

            logger.info(f"Markdown: {md_file} -> {output_path}")

            # 
            shutil.copy(md_file, output_path)

            # 
            file_size = output_path.stat().st_size
            file_size_str = self._format_file_size(file_size)

            logger.info(f"Markdown: {output_path}")

            return {
                "status": "success",
                "output_file": str(output_path),
                "file_size": file_size_str
            }

        except Exception as e:
            logger.error(f"Markdown: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "error": str(e)
            }

    def _format_file_size(self, size_bytes: int) -> str:
        """TODO: Add docstring."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
