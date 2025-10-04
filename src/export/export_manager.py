"""
导出管理器 - 统一管理项目导出功能
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger


class ExportManager:
    """导出管理器"""

    def __init__(self, base_dir: str = "storage"):
        """
        初始化导出管理器

        Args:
            base_dir: 项目存储根目录
        """
        self.base_dir = Path(base_dir)

    async def export_project(
        self,
        project_id: str,
        export_type: str,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        导出项目到指定格式

        Args:
            project_id: 项目ID
            export_type: 导出格式 (pptx/pdf/docx/md)
            output_path: 输出文件路径（可选）

        Returns:
            导出结果
        """
        try:
            # 1. 查找项目目录
            project_dir = self._find_project_dir(project_id)
            if not project_dir:
                return {
                    "status": "error",
                    "error": f"项目不存在: {project_id}"
                }

            # 2. 加载项目元数据
            metadata = self._load_metadata(project_dir)
            if not metadata:
                return {
                    "status": "error",
                    "error": "无法读取项目元数据"
                }

            # 3. 判断项目类型
            project_type = self._detect_project_type(project_dir)
            logger.info(f"项目类型: {project_type}, 导出格式: {export_type}")

            # 4. 验证导出格式是否支持
            validation_result = self._validate_export_type(project_type, export_type)
            if validation_result:
                return validation_result

            # 5. 根据格式调用相应的导出器
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
                    "error": f"不支持的导出格式: {export_type}"
                }

            return result

        except Exception as e:
            logger.error(f"导出失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "error": str(e)
            }

    def _find_project_dir(self, project_id: str) -> Optional[Path]:
        """查找项目目录"""
        # 支持完整ID或部分匹配
        for project_dir in self.base_dir.iterdir():
            if project_dir.is_dir() and project_id in project_dir.name:
                return project_dir
        return None

    def _load_metadata(self, project_dir: Path) -> Optional[Dict[str, Any]]:
        """加载项目元数据"""
        metadata_file = project_dir / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def _detect_project_type(self, project_dir: Path) -> str:
        """
        检测项目类型

        Returns:
            'ppt', 'report', 'fiction' 或 'unknown'
        """
        reports_dir = project_dir / "reports"

        # 检查是否有PPT相关文件
        if (reports_dir / "PPT_DATA.json").exists():
            return "ppt"

        # 检查是否有小说相关文件
        metadata = self._load_metadata(project_dir)
        if metadata and "fiction" in str(metadata.get("query", "")).lower():
            return "fiction"

        # 检查是否有报告文件
        if (reports_dir / "FINAL_REPORT.md").exists():
            return "report"

        return "unknown"

    def _validate_export_type(self, project_type: str, export_type: str) -> Optional[Dict[str, Any]]:
        """
        验证导出格式是否支持

        Returns:
            错误信息字典，如果验证通过返回None
        """
        # PPT项目只能导出为PPTX
        if project_type == "ppt" and export_type != "pptx":
            return {
                "status": "error",
                "error": f"PPT项目只能导出为PPTX格式，不支持{export_type.upper()}"
            }

        # 报告/小说项目不能导出为PPTX
        if project_type in ["report", "fiction"] and export_type == "pptx":
            return {
                "status": "error",
                "error": f"{project_type}项目不支持导出为PPTX，请使用PDF、DOCX或MD格式"
            }

        return None
