"""
 - 
"""
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from loguru import logger


class SearchStorage:
    """"""

    def __init__(self, base_dir: str = "storage"):
        """
        

        Args:
            base_dir: 
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        self.current_project_dir: Optional[Path] = None
        self.project_id: Optional[str] = None

    def create_project(self, query: str) -> str:
        """
        

        Args:
            query: 

        Returns:
            ID
        """
        # ID + 
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        query_slug = self._slugify(query)[:30]  # 
        self.project_id = f"{timestamp}_{query_slug}"

        # 
        self.current_project_dir = self.base_dir / self.project_id
        self.current_project_dir.mkdir(exist_ok=True)

        # 
        (self.current_project_dir / "intermediate").mkdir(exist_ok=True)
        (self.current_project_dir / "reports").mkdir(exist_ok=True)
        (self.current_project_dir / "search_results").mkdir(exist_ok=True)

        # 
        metadata = {
            "project_id": self.project_id,
            "query": query,
            "created_at": datetime.now().isoformat(),
            "status": "running"
        }
        self.save_metadata(metadata)

        logger.info(f"[SearchStorage] : {self.project_id}")
        return self.project_id

    def save_metadata(self, metadata: Dict[str, Any]):
        """"""
        if not self.current_project_dir:
            return

        metadata_file = self.current_project_dir / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

    def save_task_decomposition(self, decomposition: Dict[str, Any]):
        """"""
        if not self.current_project_dir:
            return

        file_path = self.current_project_dir / "intermediate" / "01_task_decomposition.json"
        self._save_json(file_path, decomposition)
        logger.info(f"[SearchStorage] : {file_path}")

    def save_search_results(self, search_results: Dict[str, Any]):
        """"""
        if not self.current_project_dir:
            return

        file_path = self.current_project_dir / "intermediate" / "02_search_results.json"
        self._save_json(file_path, search_results)

        # 
        text_path = self.current_project_dir / "search_results" / "search_results.txt"
        self._save_search_results_text(text_path, search_results)

        logger.info(f"[SearchStorage] : {file_path}")

    def save_content_evaluation(self, evaluation: Dict[str, Any]):
        """"""
        if not self.current_project_dir:
            return

        file_path = self.current_project_dir / "intermediate" / "03_content_evaluation.json"
        self._save_json(file_path, evaluation)
        logger.info(f"[SearchStorage] : {file_path}")

    def save_search_analysis(self, analysis: Dict[str, Any]):
        """"""
        if not self.current_project_dir:
            return

        file_path = self.current_project_dir / "intermediate" / "04_search_analysis.json"
        self._save_json(file_path, analysis)
        logger.info(f"[SearchStorage] : {file_path}")

    def save_content_synthesis(self, synthesis: Dict[str, Any]):
        """"""
        if not self.current_project_dir:
            return

        file_path = self.current_project_dir / "intermediate" / "05_content_synthesis.json"
        self._save_json(file_path, synthesis)

        # Markdown
        if synthesis.get("report_content"):
            md_path = self.current_project_dir / "reports" / "synthesis_report.md"
            self._save_text(md_path, synthesis["report_content"])

        logger.info(f"[SearchStorage] : {file_path}")

    def save_final_report(self, report: Dict[str, Any], query: str):
        """"""
        if not self.current_project_dir:
            return

        # JSON
        json_path = self.current_project_dir / "intermediate" / "06_final_report.json"
        self._save_json(json_path, report)

        # 
        html_path = None

        # PPT
        if report.get("ppt"):
            ppt_data = report["ppt"]

            # PPT HTML
            html_path = self.current_project_dir / "reports" / "FINAL_REPORT.html"
            if report.get("html_content"):
                self._save_text(html_path, report["html_content"])
                logger.info(f"[SearchStorage] PPT HTML: {html_path}")

            # PPT JSON
            ppt_json_path = self.current_project_dir / "reports" / "PPT_DATA.json"
            self._save_json(ppt_json_path, ppt_data)
            logger.info(f"[SearchStorage] PPT: {ppt_json_path}")

            # 
            if report.get("speech_notes"):
                speech_notes_path = self.current_project_dir / "reports" / "SPEECH_NOTES.txt"
                speech_content = self._format_speech_notes(report["speech_notes"], ppt_data)
                self._save_text(speech_notes_path, speech_content)
                logger.info(f"[SearchStorage] : {speech_notes_path}")

                # JSON
                speech_json_path = self.current_project_dir / "reports" / "SPEECH_NOTES.json"
                self._save_json(speech_json_path, {"speech_notes": report["speech_notes"]})
                logger.info(f"[SearchStorage] JSON: {speech_json_path}")

        # /
        elif report.get("report"):
            report_data = report["report"]

            # Markdown
            md_path = self.current_project_dir / "reports" / "FINAL_REPORT.md"
            report_content = self._format_final_report(report_data, query)
            self._save_text(md_path, report_content)

            # 
            summary_path = self.current_project_dir / "reports" / "SUMMARY.md"
            summary_content = self._format_summary_report(report_data, query)
            self._save_text(summary_path, summary_content)

            # HTML
            if report.get("html_content"):
                html_path = self.current_project_dir / "reports" / "FINAL_REPORT.html"
                self._save_text(html_path, report["html_content"])
                logger.info(f"[SearchStorage] HTML: {html_path}")

        # 
        metadata = self.load_metadata()
        if metadata:
            metadata["status"] = "completed"
            metadata["completed_at"] = datetime.now().isoformat()
            metadata["report_path"] = str(self.current_project_dir / "reports" / "FINAL_REPORT.md")
            metadata["output_format"] = report.get("output_format", "md")
            if html_path:
                metadata["html_report_path"] = str(html_path)
            self.save_metadata(metadata)

        logger.info(f"[SearchStorage] : {self.current_project_dir / 'reports' / 'FINAL_REPORT.md'}")

        # 
        print(f"\n{'='*60}")
        print(f" : {self.current_project_dir}")

        # PPT
        if report.get("ppt"):
            if html_path:
                print(f" PPT HTML: {html_path}")
            ppt_json = self.current_project_dir / "reports" / "PPT_DATA.json"
            if ppt_json.exists():
                print(f" PPT: {ppt_json}")
            speech_notes_txt = self.current_project_dir / "reports" / "SPEECH_NOTES.txt"
            if speech_notes_txt.exists():
                print(f" : {speech_notes_txt}")
                print(f"   JSON: {self.current_project_dir / 'reports' / 'SPEECH_NOTES.json'}")
        else:
            # /
            print(f" : {self.current_project_dir / 'reports' / 'FINAL_REPORT.md'}")
            if html_path:
                print(f" HTML: {html_path}")
            print(f" : {self.current_project_dir / 'reports' / 'SUMMARY.md'}")

        print(f" : {self.current_project_dir / 'search_results' / 'search_results.txt'}")
        print(f"{'='*60}\n")

    def save_execution_log(self, messages: list):
        """"""
        if not self.current_project_dir:
            return

        log_path = self.current_project_dir / "execution_log.json"
        self._save_json(log_path, {"messages": messages})

        # 
        text_path = self.current_project_dir / "execution_log.txt"
        log_content = self._format_execution_log(messages)
        self._save_text(text_path, log_content)

        logger.info(f"[SearchStorage] : {log_path}")

    def load_metadata(self) -> Optional[Dict[str, Any]]:
        """"""
        if not self.current_project_dir:
            return None

        metadata_file = self.current_project_dir / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def _save_json(self, file_path: Path, data: Dict[str, Any]):
        """JSON"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _save_text(self, file_path: Path, content: str):
        """"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def _save_search_results_text(self, file_path: Path, search_results: Dict[str, Any]):
        """"""
        content = "# \n\n"

        all_content = search_results.get("all_content", [])
        content += f": {len(all_content)} \n\n"
        content += "=" * 80 + "\n\n"

        for i, item in enumerate(all_content, 1):
            content += f"## {i}. {item.get('title', '')}\n\n"
            content += f"**URL**: {item.get('url', 'N/A')}\n\n"
            content += f"****: {item.get('search_query', 'N/A')}\n\n"
            content += f"****: {item.get('subtask_title', 'N/A')}\n\n"
            content += f"****:\n{item.get('content', '')[:500]}...\n\n"
            content += "-" * 80 + "\n\n"

        self._save_text(file_path, content)

    def _format_final_report(self, report_data: Dict[str, Any], query: str) -> str:
        """"""
        content = f"# \n\n"
        content += f"****: {query}\n\n"
        content += f"****: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        content += f"**ID**: {self.project_id}\n\n"
        content += "=" * 80 + "\n\n"

        # 
        report_content = report_data.get("content", "")
        content += report_content

        # 
        content += "\n\n" + "=" * 80 + "\n\n"
        content += "##  \n\n"

        metadata = report_data.get("metadata", {})
        content += f"- ****: {metadata.get('report_type', 'N/A')}\n"
        content += f"- ****: {metadata.get('content_sources', 'N/A')}\n"
        content += f"- ****: {metadata.get('word_count', 'N/A')}\n"
        content += f"- ****: {metadata.get('generation_time', 'N/A')}\n"

        return content

    def _format_summary_report(self, report_data: Dict[str, Any], query: str) -> str:
        """"""
        content = f"# \n\n"
        content += f"****: {query}\n\n"
        content += f"****: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        # 
        report_content = report_data.get("content", "")
        sections = report_data.get("sections", [])

        if sections:
            # 
            for section in sections[:2]:
                content += f"## {section.get('title', '')}\n\n"
                content += f"{section.get('content', '')[:500]}...\n\n"
        else:
            # 1000
            content += report_content[:1000] + "...\n\n"

        content += f"\n\n: `FINAL_REPORT.md`\n"

        return content


    def _format_execution_log(self, messages: list) -> str:
        """"""
        content = "# \n\n"
        content += f"****: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        content += "=" * 80 + "\n\n"

        for i, msg in enumerate(messages, 1):
            agent = msg.get("agent", "Unknown")
            msg_content = msg.get("content", "")

            content += f"## {i}. {agent}\n\n"
            content += f"{msg_content}\n\n"
            content += "-" * 80 + "\n\n"

        return content

    def _format_speech_notes(self, speech_notes: list, ppt_data: Dict[str, Any]) -> str:
        """"""
        content = f"# PPT\n\n"
        content += f"**PPT**: {ppt_data.get('title', '')}\n"
        content += f"****: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        content += f"****: {ppt_data.get('metadata', {}).get('slide_count', 0)}\n\n"
        content += "=" * 80 + "\n\n"

        for note in speech_notes:
            slide_number = note.get("slide_number", 0)
            speech_text = note.get("speech_notes", "")

            content += f"##  {slide_number} \n\n"
            content += f"{speech_text}\n\n"
            content += "-" * 80 + "\n\n"

        return content

    def _slugify(self, text: str) -> str:
        """URLslug"""
        # 
        import re
        text = re.sub(r'[^\w\s-]', '', text)
        # 
        text = re.sub(r'[\s]+', '_', text)
        return text.lower()

    def get_project_dir(self) -> Optional[Path]:
        """"""
        return self.current_project_dir

    def list_projects(self) -> list:
        """"""
        projects = []

        for project_dir in self.base_dir.iterdir():
            if project_dir.is_dir():
                metadata_file = project_dir / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                        projects.append({
                            "project_id": metadata.get("project_id"),
                            "query": metadata.get("query"),
                            "created_at": metadata.get("created_at"),
                            "status": metadata.get("status"),
                            "path": str(project_dir)
                        })

        # 
        projects.sort(key=lambda x: x["created_at"], reverse=True)
        return projects
