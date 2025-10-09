"""
 - 
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger


class ExportManager:
    """TODO: Add docstring."""

    def __init__(self, base_dir: str = "storage"):
        """
        

        Args:
            base_dir: 
        """
        self.base_dir = Path(base_dir)

    async def export_project(
        self,
        project_id: str,
        export_type: str,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        

        Args:
            project_id: ID
            export_type:  (pptx/pdf/docx/md)
            output_path: 

        Returns:
            
        """
        try:
            # 1. 
            project_dir = self._find_project_dir(project_id)
            if not project_dir:
                return {
                    "status": "error",
                    "error": f": {project_id}"
                }

            # 2. 
            metadata = self._load_metadata(project_dir)
            if not metadata:
                return {
                    "status": "error",
                    "error": ""
                }

            # 3. 
            project_type = self._detect_project_type(project_dir)
            logger.info(f": {project_type}, : {export_type}")

            # 4. 
            validation_result = self._validate_export_type(project_type, export_type)
            if validation_result:
                return validation_result

            # 5. 
            if export_type == "pptx":
                from .pptx_exporter import PPTXExporter
                exporter = PPTXExporter()
                result = await exporter.export(project_dir, output_path)

            elif export_type == "pdf":
                from .pdf_exporter import PDFExporter
                exporter = PDFExporter()
                result = await exporter.export(project_dir, output_path)

            elif export_type == "docx":
                from .docx_exporter import DOCXExporter
                exporter = DOCXExporter()
                result = await exporter.export(project_dir, output_path)

            elif export_type == "md":
                from .md_exporter import MDExporter
                exporter = MDExporter()
                result = await exporter.export(project_dir, output_path)

            else:
                return {
                    "status": "error",
                    "error": f": {export_type}"
                }

            return result

        except Exception as e:
            logger.error(f": {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "error": str(e)
            }

    def _find_project_dir(self, project_id: str) -> Optional[Path]:
        """TODO: Add docstring."""
        # ID
        for project_dir in self.base_dir.iterdir():
            if project_dir.is_dir() and project_id in project_dir.name:
                return project_dir
        return None

    def _load_metadata(self, project_dir: Path) -> Optional[Dict[str, Any]]:
        """TODO: Add docstring."""
        metadata_file = project_dir / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def _detect_project_type(self, project_dir: Path) -> str:
        """
        

        Returns:
            'ppt', 'report', 'fiction'  'unknown'
        """
        reports_dir = project_dir / "reports"

        # PPT
        if (reports_dir / "PPT_DATA.json").exists():
            return "ppt"

        # 
        metadata = self._load_metadata(project_dir)
        if metadata and "fiction" in str(metadata.get("query", "")).lower():
            return "fiction"

        # 
        if (reports_dir / "FINAL_REPORT.md").exists():
            return "report"

        return "unknown"

    def _validate_export_type(self, project_type: str, export_type: str) -> Optional[Dict[str, Any]]:
        """
        

        Returns:
            None
        """
        # PPTPPTX
        if project_type == "ppt" and export_type != "pptx":
            return {
                "status": "error",
                "error": f"PPTPPTX{export_type.upper()}"
            }

        # /PPTX
        if project_type in ["report", "fiction"] and export_type == "pptx":
            return {
                "status": "error",
                "error": f"{project_type}PPTXPDFDOCXMD"
            }

        return None
