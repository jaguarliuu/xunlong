"""
 - 
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger
from pydantic import BaseModel, Field


class IterationRequest(BaseModel):
    """TODO: Add docstring."""
    requirement: str = Field(description="")
    modification_type: str = Field(description=": content/style/structure/data")
    modification_scope: str = Field(description=": local/global/partial")
    target_items: list[str] = Field(default=[], description="35")


class IterationAgent:
    """TODO: Add docstring."""

    def __init__(self, base_dir: str = "storage"):
        """
        

        Args:
            base_dir: 
        """
        self.base_dir = Path(base_dir)

    async def iterate_project(
        self,
        project_id: str,
        requirement: str
    ) -> Dict[str, Any]:
        """
        

        Args:
            project_id: ID
            requirement: 

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

            logger.info(f"[IterationAgent] : {project_dir.name}")

            # 2. 
            context = self._load_project_context(project_dir)
            if not context:
                return {
                    "status": "error",
                    "error": ""
                }

            project_type = context['project_type']
            logger.info(f"[IterationAgent] : {project_type}")

            # 3. 
            logger.info(f"[IterationAgent] : {requirement}")
            iteration_request = await self._analyze_requirement(
                requirement,
                project_type,
                context
            )

            logger.info(f"[IterationAgent] : {iteration_request.modification_type}")
            logger.info(f"[IterationAgent] : {iteration_request.modification_scope}")

            # 4. 
            backup_version = self._create_backup(project_dir)
            logger.info(f"[IterationAgent] : {backup_version}")

            # 5. 
            if project_type == "ppt":
                result = await self._iterate_ppt(
                    project_dir,
                    context,
                    iteration_request
                )
            elif project_type == "report":
                result = await self._iterate_report(
                    project_dir,
                    context,
                    iteration_request
                )
            elif project_type == "fiction":
                result = await self._iterate_fiction(
                    project_dir,
                    context,
                    iteration_request
                )
            else:
                return {
                    "status": "error",
                    "error": f": {project_type}"
                }

            # 6. 
            if result["status"] == "success":
                self._update_metadata(project_dir, iteration_request, backup_version)

            result["project_type"] = project_type
            result["modification_scope"] = iteration_request.modification_scope
            result["backup_version"] = backup_version

            return result

        except Exception as e:
            logger.error(f"[IterationAgent] : {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "error": str(e)
            }

    def _find_project_dir(self, project_id: str) -> Optional[Path]:
        """TODO: Add docstring."""
        for project_dir in self.base_dir.iterdir():
            if project_dir.is_dir() and project_id in project_dir.name:
                return project_dir
        return None

    def _load_project_context(self, project_dir: Path) -> Optional[Dict[str, Any]]:
        """
        

        Returns:
            
        """
        context = {}

        # 
        metadata_file = project_dir / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                context['metadata'] = json.load(f)

        # 
        reports_dir = project_dir / "reports"

        if (reports_dir / "PPT_DATA.json").exists():
            context['project_type'] = "ppt"
            # PPT
            with open(reports_dir / "PPT_DATA.json", 'r', encoding='utf-8') as f:
                context['ppt_data'] = json.load(f)

        elif "fiction" in str(context.get('metadata', {}).get('query', '')).lower():
            context['project_type'] = "fiction"

        elif (reports_dir / "FINAL_REPORT.md").exists():
            context['project_type'] = "report"

        else:
            return None

        # 
        intermediate_dir = project_dir / "intermediate"

        # /
        if (intermediate_dir / "01_task_decomposition.json").exists():
            with open(intermediate_dir / "01_task_decomposition.json", 'r', encoding='utf-8') as f:
                context['task_decomposition'] = json.load(f)

        # 
        if (intermediate_dir / "02_search_results.json").exists():
            with open(intermediate_dir / "02_search_results.json", 'r', encoding='utf-8') as f:
                context['search_results'] = json.load(f)

        return context

    async def _analyze_requirement(
        self,
        requirement: str,
        project_type: str,
        context: Dict[str, Any]
    ) -> IterationRequest:
        """
        LLM

        Returns:
            
        """
        from src.llm.manager import LLMManager

        llm_manager = LLMManager()
        llm_client = llm_manager.get_client("default")

        prompt = f"""

# 
{project_type}

# 
{requirement}

# 
- : {context.get('metadata', {}).get('query', '')}
- : {context.get('metadata', {}).get('created_at', '')}

# 



## 1. modification_type ()

- **content**:  - 
- **style**:  - 
- **structure**:  - /
- **data**:  - 

## 2. modification_scope ()

- **local**:  - 
- **partial**:  - /50%
- **global**:  - 

## 3. target_items ()

- "3"
- "example_key_1"
- "example_key_2"
-  []

# 
JSON
"""

        response = await llm_client.get_structured_response(
            prompt=prompt,
            response_model=IterationRequest
        )

        return response

    def _create_backup(self, project_dir: Path) -> str:
        """
        

        Returns:
            
        """
        import shutil

        # 
        version = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 
        versions_dir = project_dir / "versions"
        versions_dir.mkdir(exist_ok=True)

        backup_dir = versions_dir / version

        # reports
        reports_dir = project_dir / "reports"
        if reports_dir.exists():
            shutil.copytree(reports_dir, backup_dir / "reports")

        logger.info(f"[IterationAgent] : {backup_dir}")

        return version

    async def _iterate_ppt(
        self,
        project_dir: Path,
        context: Dict[str, Any],
        iteration_request: IterationRequest
    ) -> Dict[str, Any]:
        """PPT"""
        from src.agents.ppt.ppt_coordinator import PPTCoordinator
        from src.llm.manager import LLMManager
        from src.llm.prompts import PromptManager

        logger.info("[IterationAgent] PPT...")

        llm_manager = LLMManager()
        prompt_manager = PromptManager()
        ppt_coordinator = PPTCoordinator(llm_manager, prompt_manager)

        # 
        ppt_data = context['ppt_data']
        search_results = context.get('search_results', {}).get('all_content', [])

        # 
        modification_instruction = f"""
: {iteration_request.requirement}
: {iteration_request.modification_type}
: {iteration_request.modification_scope}
: {', '.join(iteration_request.target_items) if iteration_request.target_items else ''}
"""

        # PPT Coordinator
        # PPT
        result = await ppt_coordinator.generate_ppt_v2(
            topic=f"{ppt_data['title']} [: {iteration_request.requirement}]",
            search_results=search_results,
            ppt_config={
                'style': ppt_data['metadata'].get('style', 'business'),
                'slides': ppt_data['metadata'].get('slide_count', 10),
                'modification_instruction': modification_instruction
            }
        )

        if result["status"] == "success":
            # 
            self._save_updated_ppt(project_dir, result)

            return {
                "status": "success",
                "output_file": str(project_dir / "reports" / "FINAL_REPORT.html"),
                "new_version": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "changes": [
                    f" '{iteration_request.requirement}' PPT",
                    f": {iteration_request.modification_scope}"
                ]
            }
        else:
            return result

    async def _iterate_report(
        self,
        project_dir: Path,
        context: Dict[str, Any],
        iteration_request: IterationRequest
    ) -> Dict[str, Any]:
        """TODO: Add docstring."""
        logger.info("[IterationAgent] ...")

        from src.llm.manager import LLMManager

        llm_manager = LLMManager()
        llm_client = llm_manager.get_client("default")

        # 
        report_file = project_dir / "reports" / "FINAL_REPORT.md"
        if not report_file.exists():
            return {
                "status": "error",
                "error": ""
            }

        with open(report_file, 'r', encoding='utf-8') as f:
            current_content = f.read()

        # 
        if iteration_request.modification_scope == "local":
            # 
            new_content = await self._modify_report_section(
                llm_client,
                current_content,
                iteration_request,
                context
            )
        elif iteration_request.modification_scope == "partial":
            # 
            new_content = await self._modify_report_partial(
                llm_client,
                current_content,
                iteration_request,
                context
            )
        else:
            # 
            new_content = await self._modify_report_global(
                llm_client,
                current_content,
                iteration_request,
                context
            )

        # 
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(new_content)

        # HTML
        html_file = project_dir / "reports" / "FINAL_REPORT.html"
        if html_file.exists():
            await self._regenerate_html_from_markdown(
                project_dir,
                new_content,
                context
            )

        return {
            "status": "success",
            "output_file": str(report_file),
            "new_version": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "changes": [
                f" '{iteration_request.requirement}' ",
                f": {iteration_request.modification_scope}",
                f": {iteration_request.modification_type}"
            ]
        }

    async def _iterate_fiction(
        self,
        project_dir: Path,
        context: Dict[str, Any],
        iteration_request: IterationRequest
    ) -> Dict[str, Any]:
        """TODO: Add docstring."""
        logger.info("[IterationAgent] ...")

        from src.llm.manager import LLMManager

        llm_manager = LLMManager()
        llm_client = llm_manager.get_client("default")

        # 
        fiction_file = project_dir / "reports" / "FINAL_REPORT.md"
        if not fiction_file.exists():
            return {
                "status": "error",
                "error": ""
            }

        with open(fiction_file, 'r', encoding='utf-8') as f:
            current_content = f.read()

        # 
        if iteration_request.modification_scope == "local":
            # 
            new_content = await self._modify_fiction_chapter(
                llm_client,
                current_content,
                iteration_request,
                context
            )
        elif iteration_request.modification_scope == "partial":
            # 
            new_content = await self._modify_fiction_partial(
                llm_client,
                current_content,
                iteration_request,
                context
            )
        else:
            # 
            new_content = await self._modify_fiction_global(
                llm_client,
                current_content,
                iteration_request,
                context
            )

        # 
        with open(fiction_file, 'w', encoding='utf-8') as f:
            f.write(new_content)

        # HTML
        html_file = project_dir / "reports" / "FINAL_REPORT.html"
        if html_file.exists():
            await self._regenerate_html_from_markdown(
                project_dir,
                new_content,
                context
            )

        return {
            "status": "success",
            "output_file": str(fiction_file),
            "new_version": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "changes": [
                f" '{iteration_request.requirement}' ",
                f": {iteration_request.modification_scope}",
                f": {iteration_request.modification_type}"
            ]
        }

    async def _modify_report_section(
        self,
        llm_client,
        current_content: str,
        iteration_request: IterationRequest,
        context: Dict[str, Any]
    ) -> str:
        """TODO: Add docstring."""

        # 
        target_info = ", ".join(iteration_request.target_items) if iteration_request.target_items else ""

        prompt = f"""

# 
{iteration_request.requirement}

# 
{target_info}

# 
{current_content}

# 
{self._format_search_results(context.get('search_results', {}))}

# 

## 
1. ****: 
2. ****: 
3. ****: 
4. ****: Markdown

## 
- ****
- Markdown
- 
- 


"""

        response = await llm_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=8000,
            temperature=0.7
        )

        new_content = response.get("content", "").strip()

        # markdown
        if new_content.startswith('```markdown'):
            new_content = new_content[11:]
        elif new_content.startswith('```'):
            new_content = new_content[3:]
        if new_content.endswith('```'):
            new_content = new_content[:-3]

        return new_content.strip()

    async def _modify_report_partial(
        self,
        llm_client,
        current_content: str,
        iteration_request: IterationRequest,
        context: Dict[str, Any]
    ) -> str:
        """TODO: Add docstring."""

        # 
        content_to_show = current_content
        is_truncated = False
        if len(current_content) > 6000:
            content_to_show = current_content[:6000] + "\n\n... ()"
            is_truncated = True

        prompt = f"""

# 
{iteration_request.requirement}

# 
{content_to_show}

# 
{self._format_search_results(context.get('search_results', {}))}

# 
- : {context.get('metadata', {}).get('query', '')}
- : {context.get('metadata', {}).get('type', '')}

# 

## 

- ****: 
- ****: 
- ****: 
- ****: 

## 
1. ****: 
2. ****: 
3. ****: 
4. ****: 
5. ****: Markdown

## 
{"- " if is_truncated else ""}
- 
- 
- 


"""

        response = await llm_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10000,
            temperature=0.7
        )

        new_content = response.get("content", "").strip()

        if new_content.startswith('```markdown'):
            new_content = new_content[11:]
        elif new_content.startswith('```'):
            new_content = new_content[3:]
        if new_content.endswith('```'):
            new_content = new_content[:-3]

        return new_content.strip()

    async def _modify_report_global(
        self,
        llm_client,
        current_content: str,
        iteration_request: IterationRequest,
        context: Dict[str, Any]
    ) -> str:
        """TODO: Add docstring."""
        # 
        return await self._modify_report_partial(
            llm_client,
            current_content,
            iteration_request,
            context
        )

    async def _modify_fiction_chapter(
        self,
        llm_client,
        current_content: str,
        iteration_request: IterationRequest,
        context: Dict[str, Any]
    ) -> str:
        """TODO: Add docstring."""

        target_info = ", ".join(iteration_request.target_items) if iteration_request.target_items else ""

        prompt = f"""

# 
{iteration_request.requirement}

# 
{target_info}

# 
{current_content}

# 
- : {context.get('metadata', {}).get('query', '')}
- : {context.get('metadata', {}).get('style', '')}

# 

## 
1. ****:
   - 
   - 

2. ****:
   - 
   - 
   - 

3. ****:
   - /
   - 
   - 

4. ****:
   - 
   - 
   - 

## 
- ****
- Markdown
- 
- 


"""

        response = await llm_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=8000,
            temperature=0.8  # 
        )

        new_content = response.get("content", "").strip()

        if new_content.startswith('```markdown'):
            new_content = new_content[11:]
        elif new_content.startswith('```'):
            new_content = new_content[3:]
        if new_content.endswith('```'):
            new_content = new_content[:-3]

        return new_content.strip()

    async def _modify_fiction_partial(
        self,
        llm_client,
        current_content: str,
        iteration_request: IterationRequest,
        context: Dict[str, Any]
    ) -> str:
        """TODO: Add docstring."""

        # 
        content_to_show = current_content
        is_truncated = False
        if len(current_content) > 6000:
            content_to_show = current_content[:6000] + "\n\n... ()"
            is_truncated = True

        prompt = f"""

# 
{iteration_request.requirement}

# 
{content_to_show}

# 
- : {context.get('metadata', {}).get('query', '')}
- : {context.get('metadata', {}).get('style', '')}

# 

## 

- ****: 
- ****: 
- ****: 
- ****: 

## 

### 1. 
- 
- 
- 
- 

### 2. 
- 
- 
- 
- 

### 3. 
- 
- 
- 
- 

### 4. 
- 
- 
- 
- 

## 
{"- " if is_truncated else ""}
- 
- 
- 


"""

        response = await llm_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10000,
            temperature=0.8
        )

        new_content = response.get("content", "").strip()

        if new_content.startswith('```markdown'):
            new_content = new_content[11:]
        elif new_content.startswith('```'):
            new_content = new_content[3:]
        if new_content.endswith('```'):
            new_content = new_content[:-3]

        return new_content.strip()

    async def _modify_fiction_global(
        self,
        llm_client,
        current_content: str,
        iteration_request: IterationRequest,
        context: Dict[str, Any]
    ) -> str:
        """TODO: Add docstring."""
        return await self._modify_fiction_partial(
            llm_client,
            current_content,
            iteration_request,
            context
        )

    def _format_search_results(self, search_results: Dict[str, Any]) -> str:
        """TODO: Add docstring."""
        all_content = search_results.get('all_content', [])

        if not all_content:
            return ""

        formatted = []
        for i, item in enumerate(all_content[:5], 1):  # 5
            formatted.append(f"{i}. {item.get('title', '')}")
            formatted.append(f"   : {item.get('content', '')[:200]}...")
            formatted.append("")

        return "\n".join(formatted)

    async def _regenerate_html_from_markdown(
        self,
        project_dir: Path,
        markdown_content: str,
        context: Dict[str, Any]
    ):
        """MarkdownHTML"""
        # HTML
        # markdown2
        try:
            import markdown2

            html_content = markdown2.markdown(
                markdown_content,
                extras=['tables', 'fenced-code-blocks', 'header-ids']
            )

            # HTML
            full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{context.get('metadata', {}).get('query', '')}</title>
    <style>
        body {{ font-family: 'PingFang SC', 'Microsoft YaHei', Arial, sans-serif; line-height: 1.8; padding: 40px; max-width: 1000px; margin: 0 auto; }}
        h1, h2, h3 {{ color: #333; margin-top: 30px; }}
        code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
        pre {{ background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background: #f2f2f2; }}
    </style>
</head>
<body>
{html_content}
</body>
</html>
"""

            html_file = project_dir / "reports" / "FINAL_REPORT.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(full_html)

            logger.info(f"[IterationAgent] HTML: {html_file}")

        except ImportError:
            logger.warning("[IterationAgent] markdown2HTML")
        except Exception as e:
            logger.error(f"[IterationAgent] HTML: {e}")

    def _save_updated_ppt(self, project_dir: Path, result: Dict[str, Any]):
        """PPT"""
        reports_dir = project_dir / "reports"

        # HTML
        if result.get('html_content'):
            html_file = reports_dir / "FINAL_REPORT.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(result['html_content'])

        # PPT
        if result.get('ppt'):
            ppt_file = reports_dir / "PPT_DATA.json"
            with open(ppt_file, 'w', encoding='utf-8') as f:
                json.dump(result['ppt'], f, ensure_ascii=False, indent=2)

    def _update_metadata(
        self,
        project_dir: Path,
        iteration_request: IterationRequest,
        backup_version: str
    ):
        """TODO: Add docstring."""
        metadata_file = project_dir / "metadata.json"

        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            # 
            if 'iterations' not in metadata:
                metadata['iterations'] = []

            metadata['iterations'].append({
                'timestamp': datetime.now().isoformat(),
                'requirement': iteration_request.requirement,
                'modification_type': iteration_request.modification_type,
                'modification_scope': iteration_request.modification_scope,
                'backup_version': backup_version
            })

            metadata['last_updated'] = datetime.now().isoformat()

            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
