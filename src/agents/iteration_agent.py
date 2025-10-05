"""
迭代智能体 - 对已生成项目进行智能迭代优化
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger
from pydantic import BaseModel, Field


class IterationRequest(BaseModel):
    """迭代请求模型"""
    requirement: str = Field(description="用户的优化需求")
    modification_type: str = Field(description="修改类型: content/style/structure/data")
    modification_scope: str = Field(description="修改范围: local/global/partial")
    target_items: list[str] = Field(default=[], description="具体修改目标（如：第3页、第5章）")


class IterationAgent:
    """迭代智能体"""

    def __init__(self, base_dir: str = "storage"):
        """
        初始化迭代智能体

        Args:
            base_dir: 项目存储根目录
        """
        self.base_dir = Path(base_dir)

    async def iterate_project(
        self,
        project_id: str,
        requirement: str
    ) -> Dict[str, Any]:
        """
        对项目进行迭代优化

        Args:
            project_id: 项目ID
            requirement: 优化需求

        Returns:
            迭代结果
        """
        try:
            # 1. 查找并加载项目
            project_dir = self._find_project_dir(project_id)
            if not project_dir:
                return {
                    "status": "error",
                    "error": f"项目不存在: {project_id}"
                }

            logger.info(f"[IterationAgent] 开始迭代项目: {project_dir.name}")

            # 2. 加载项目上下文
            context = self._load_project_context(project_dir)
            if not context:
                return {
                    "status": "error",
                    "error": "无法加载项目上下文"
                }

            project_type = context['project_type']
            logger.info(f"[IterationAgent] 项目类型: {project_type}")

            # 3. 分析用户需求
            logger.info(f"[IterationAgent] 分析需求: {requirement}")
            iteration_request = await self._analyze_requirement(
                requirement,
                project_type,
                context
            )

            logger.info(f"[IterationAgent] 修改类型: {iteration_request.modification_type}")
            logger.info(f"[IterationAgent] 修改范围: {iteration_request.modification_scope}")

            # 4. 创建版本备份
            backup_version = self._create_backup(project_dir)
            logger.info(f"[IterationAgent] 创建备份: {backup_version}")

            # 5. 根据项目类型调用对应的迭代处理器
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
                    "error": f"不支持的项目类型: {project_type}"
                }

            # 6. 更新元数据
            if result["status"] == "success":
                self._update_metadata(project_dir, iteration_request, backup_version)

            result["project_type"] = project_type
            result["modification_scope"] = iteration_request.modification_scope
            result["backup_version"] = backup_version

            return result

        except Exception as e:
            logger.error(f"[IterationAgent] 迭代失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "error": str(e)
            }

    def _find_project_dir(self, project_id: str) -> Optional[Path]:
        """查找项目目录"""
        for project_dir in self.base_dir.iterdir():
            if project_dir.is_dir() and project_id in project_dir.name:
                return project_dir
        return None

    def _load_project_context(self, project_dir: Path) -> Optional[Dict[str, Any]]:
        """
        加载项目上下文

        Returns:
            项目上下文信息
        """
        context = {}

        # 加载元数据
        metadata_file = project_dir / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                context['metadata'] = json.load(f)

        # 检测项目类型
        reports_dir = project_dir / "reports"

        if (reports_dir / "PPT_DATA.json").exists():
            context['project_type'] = "ppt"
            # 加载PPT数据
            with open(reports_dir / "PPT_DATA.json", 'r', encoding='utf-8') as f:
                context['ppt_data'] = json.load(f)

        elif "fiction" in str(context.get('metadata', {}).get('query', '')).lower():
            context['project_type'] = "fiction"

        elif (reports_dir / "FINAL_REPORT.md").exists():
            context['project_type'] = "report"

        else:
            return None

        # 加载中间文件
        intermediate_dir = project_dir / "intermediate"

        # 加载大纲/任务分解
        if (intermediate_dir / "01_task_decomposition.json").exists():
            with open(intermediate_dir / "01_task_decomposition.json", 'r', encoding='utf-8') as f:
                context['task_decomposition'] = json.load(f)

        # 加载搜索结果
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
        使用LLM分析用户需求

        Returns:
            结构化的迭代请求
        """
        from src.llm.manager import LLMManager

        llm_manager = LLMManager()
        llm_client = llm_manager.get_client("default")

        prompt = f"""你是一个项目迭代需求分析专家。请仔细分析用户的优化需求，并以结构化格式输出。

# 项目类型
{project_type}

# 用户需求
{requirement}

# 项目上下文
- 原始查询: {context.get('metadata', {}).get('query', '未知')}
- 生成时间: {context.get('metadata', {}).get('created_at', '未知')}

# 分析任务

请深入理解用户需求，分析以下三个维度：

## 1. modification_type (修改类型)
选择最贴切的修改类型：
- **content**: 内容修改 - 改写文字、更新数据、修改章节内容、调整论述逻辑
- **style**: 样式修改 - 调整配色方案、修改字体布局、改变视觉风格
- **structure**: 结构修改 - 增删页面/章节、重新组织内容架构、调整篇章顺序
- **data**: 数据修改 - 需要重新搜索资料、更新数据源、补充新的信息

## 2. modification_scope (修改范围)
评估修改影响的范围：
- **local**: 局部修改 - 仅涉及单个页面、单个章节或单个段落的修改
- **partial**: 部分修改 - 涉及多个页面/章节，但不超过整体的50%
- **global**: 全局修改 - 整体风格调整、大范围重写或全面改版

## 3. target_items (具体目标)
精确提取需求中的目标对象：
- 如果用户提到具体页码（如"第3页"），提取页码编号
- 如果用户提到章节（如"第五章"、"结论部分"），提取章节名称或编号
- 如果用户提到具体元素（如"所有图表"、"标题部分"），列出这些元素
- 如果没有明确指定，留空数组 []

# 输出格式
请以严格的JSON格式输出，确保字段完整且类型正确。
"""

        response = await llm_client.get_structured_response(
            prompt=prompt,
            response_model=IterationRequest
        )

        return response

    def _create_backup(self, project_dir: Path) -> str:
        """
        创建版本备份

        Returns:
            备份版本号
        """
        import shutil

        # 生成版本号
        version = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 创建版本目录
        versions_dir = project_dir / "versions"
        versions_dir.mkdir(exist_ok=True)

        backup_dir = versions_dir / version

        # 备份reports目录
        reports_dir = project_dir / "reports"
        if reports_dir.exists():
            shutil.copytree(reports_dir, backup_dir / "reports")

        logger.info(f"[IterationAgent] 备份完成: {backup_dir}")

        return version

    async def _iterate_ppt(
        self,
        project_dir: Path,
        context: Dict[str, Any],
        iteration_request: IterationRequest
    ) -> Dict[str, Any]:
        """PPT项目迭代处理"""
        from src.agents.ppt.ppt_coordinator import PPTCoordinator
        from src.llm.manager import LLMManager
        from src.llm.prompts import PromptManager

        logger.info("[IterationAgent] 执行PPT迭代...")

        llm_manager = LLMManager()
        prompt_manager = PromptManager()
        ppt_coordinator = PPTCoordinator(llm_manager, prompt_manager)

        # 准备迭代上下文
        ppt_data = context['ppt_data']
        search_results = context.get('search_results', {}).get('all_content', [])

        # 构建修改指令
        modification_instruction = f"""
原始需求: {iteration_request.requirement}
修改类型: {iteration_request.modification_type}
修改范围: {iteration_request.modification_scope}
目标项目: {', '.join(iteration_request.target_items) if iteration_request.target_items else '全局'}
"""

        # 调用PPT Coordinator进行迭代
        # 这里简化处理：重新生成PPT，但加入修改指令
        result = await ppt_coordinator.generate_ppt_v2(
            topic=f"{ppt_data['title']} [迭代: {iteration_request.requirement}]",
            search_results=search_results,
            ppt_config={
                'style': ppt_data['metadata'].get('style', 'business'),
                'slides': ppt_data['metadata'].get('slide_count', 10),
                'modification_instruction': modification_instruction
            }
        )

        if result["status"] == "success":
            # 保存新版本
            self._save_updated_ppt(project_dir, result)

            return {
                "status": "success",
                "output_file": str(project_dir / "reports" / "FINAL_REPORT.html"),
                "new_version": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "changes": [
                    f"根据需求 '{iteration_request.requirement}' 更新了PPT",
                    f"修改范围: {iteration_request.modification_scope}"
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
        """报告项目迭代处理"""
        logger.info("[IterationAgent] 执行报告迭代...")

        from src.llm.manager import LLMManager

        llm_manager = LLMManager()
        llm_client = llm_manager.get_client("default")

        # 读取当前报告
        report_file = project_dir / "reports" / "FINAL_REPORT.md"
        if not report_file.exists():
            return {
                "status": "error",
                "error": "找不到报告文件"
            }

        with open(report_file, 'r', encoding='utf-8') as f:
            current_content = f.read()

        # 根据修改范围决定迭代策略
        if iteration_request.modification_scope == "local":
            # 局部修改：只修改特定章节
            new_content = await self._modify_report_section(
                llm_client,
                current_content,
                iteration_request,
                context
            )
        elif iteration_request.modification_scope == "partial":
            # 部分修改：修改多个章节或添加新章节
            new_content = await self._modify_report_partial(
                llm_client,
                current_content,
                iteration_request,
                context
            )
        else:
            # 全局修改：整体重写或大幅调整
            new_content = await self._modify_report_global(
                llm_client,
                current_content,
                iteration_request,
                context
            )

        # 保存新版本
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(new_content)

        # 如果有HTML版本，也需要重新生成
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
                f"根据需求 '{iteration_request.requirement}' 更新了报告",
                f"修改范围: {iteration_request.modification_scope}",
                f"修改类型: {iteration_request.modification_type}"
            ]
        }

    async def _iterate_fiction(
        self,
        project_dir: Path,
        context: Dict[str, Any],
        iteration_request: IterationRequest
    ) -> Dict[str, Any]:
        """小说项目迭代处理"""
        logger.info("[IterationAgent] 执行小说迭代...")

        from src.llm.manager import LLMManager

        llm_manager = LLMManager()
        llm_client = llm_manager.get_client("default")

        # 读取当前小说
        fiction_file = project_dir / "reports" / "FINAL_REPORT.md"
        if not fiction_file.exists():
            return {
                "status": "error",
                "error": "找不到小说文件"
            }

        with open(fiction_file, 'r', encoding='utf-8') as f:
            current_content = f.read()

        # 根据修改范围决定迭代策略
        if iteration_request.modification_scope == "local":
            # 局部修改：重写单个章节
            new_content = await self._modify_fiction_chapter(
                llm_client,
                current_content,
                iteration_request,
                context
            )
        elif iteration_request.modification_scope == "partial":
            # 部分修改：修改多个章节或添加新章节
            new_content = await self._modify_fiction_partial(
                llm_client,
                current_content,
                iteration_request,
                context
            )
        else:
            # 全局修改：整体重写或大幅调整剧情
            new_content = await self._modify_fiction_global(
                llm_client,
                current_content,
                iteration_request,
                context
            )

        # 保存新版本
        with open(fiction_file, 'w', encoding='utf-8') as f:
            f.write(new_content)

        # 如果有HTML版本，也需要重新生成
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
                f"根据需求 '{iteration_request.requirement}' 更新了小说",
                f"修改范围: {iteration_request.modification_scope}",
                f"修改类型: {iteration_request.modification_type}"
            ]
        }

    async def _modify_report_section(
        self,
        llm_client,
        current_content: str,
        iteration_request: IterationRequest,
        context: Dict[str, Any]
    ) -> str:
        """修改报告的特定章节"""

        # 提取目标章节信息
        target_info = ", ".join(iteration_request.target_items) if iteration_request.target_items else "用户指定的部分"

        prompt = f"""你是一个专业的报告编辑和内容优化专家。请根据用户的具体需求，精准修改报告中的指定部分。

# 修改任务
{iteration_request.requirement}

# 目标位置
{target_info}

# 当前完整报告
{current_content}

# 可用数据资源
{self._format_search_results(context.get('search_results', {}))}

# 修改要求

## 核心原则
1. **精准定位**: 只修改用户明确指定的章节或段落，其他部分保持原样
2. **风格一致**: 新内容的语言风格、专业程度、行文逻辑必须与原报告完全一致
3. **数据准确**: 如需补充数据，优先使用上述搜索结果中的可靠信息
4. **结构完整**: 确保修改后的报告结构完整，标题层级正确，Markdown格式规范

## 输出要求
- 输出**完整的**修改后的报告（包含所有未修改的部分）
- 使用标准的Markdown格式
- 保持原有的章节编号和结构
- 确保所有链接、引用、图表说明完整

请开始修改：
"""

        response = await llm_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=8000,
            temperature=0.7
        )

        new_content = response.get("content", "").strip()

        # 清理markdown代码块标记
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
        """部分修改报告（多个章节或添加新章节）"""

        # 检查是否需要截取内容
        content_to_show = current_content
        is_truncated = False
        if len(current_content) > 6000:
            content_to_show = current_content[:6000] + "\n\n... (内容已截取，请基于已有结构和风格进行修改)"
            is_truncated = True

        prompt = f"""你是一个专业的报告编辑和内容架构专家。请根据用户需求对报告进行部分修改或扩展。

# 修改任务
{iteration_request.requirement}

# 当前报告内容
{content_to_show}

# 可用数据资源
{self._format_search_results(context.get('search_results', {}))}

# 原始项目背景
- 项目主题: {context.get('metadata', {}).get('query', '未知')}
- 项目类型: {context.get('metadata', {}).get('type', '未知')}

# 修改要求

## 核心任务
根据用户需求，你可能需要：
- **添加新章节**: 在合适的位置插入新的内容章节
- **删除章节**: 移除不再需要的内容
- **重组结构**: 调整章节顺序，优化内容组织
- **扩展内容**: 在现有章节基础上补充更多信息

## 质量标准
1. **内容连贯**: 新增或修改的内容要与前后章节自然衔接
2. **风格统一**: 保持与原报告相同的专业性、语言风格和叙述方式
3. **结构清晰**: 合理的章节层级，清晰的逻辑结构
4. **数据可靠**: 使用上述搜索结果中的可靠数据，避免虚构
5. **格式规范**: 标准Markdown格式，正确的标题层级

## 特别注意
{"- 由于内容较长已截取，请保持原有的整体结构框架" if is_truncated else ""}
- 如果添加新章节，请确保章节编号连续
- 如果删除章节，请相应调整后续编号
- 保持目录（如果有）与实际章节一致

请输出完整的修改后的报告：
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
        """全局修改报告"""
        # 全局修改通常意味着重新生成，这里简化处理
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
        """修改小说的特定章节"""

        target_info = ", ".join(iteration_request.target_items) if iteration_request.target_items else "用户指定的章节"

        prompt = f"""你是一个经验丰富的小说编辑和创意作家。请根据用户的具体需求，重写或优化小说的指定章节。

# 修改任务
{iteration_request.requirement}

# 目标章节
{target_info}

# 当前完整小说内容
{current_content}

# 小说背景信息
- 原始创作主题: {context.get('metadata', {}).get('query', '未知')}
- 体裁风格: {context.get('metadata', {}).get('style', '未指定')}

# 创作要求

## 核心原则
1. **人物一致性**:
   - 保持已有人物的性格特征、说话方式、行为习惯
   - 人物发展要符合逻辑，不能突然性格大变

2. **剧情连贯性**:
   - 新章节必须与前后章节的情节自然衔接
   - 不能出现逻辑矛盾或时间线错乱
   - 伏笔和铺垫要合理延续

3. **风格统一性**:
   - 保持原有的叙事视角（第一人称/第三人称）
   - 延续原有的语言风格和节奏感
   - 保持相同的情感基调和氛围营造方式

4. **质量提升**:
   - 优化对话的生动性和真实感
   - 增强场景描写的画面感
   - 提升情节的张力和吸引力

## 输出要求
- 输出**完整的**修改后的小说（包含所有章节）
- 使用标准Markdown格式
- 保持原有的章节编号和结构
- 只修改指定章节，其他章节保持原样

请开始创作：
"""

        response = await llm_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=8000,
            temperature=0.8  # 创作类内容温度稍高
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
        """部分修改小说"""

        # 检查是否需要截取内容
        content_to_show = current_content
        is_truncated = False
        if len(current_content) > 6000:
            content_to_show = current_content[:6000] + "\n\n... (内容已截取，请基于已建立的人物和剧情进行创作)"
            is_truncated = True

        prompt = f"""你是一个专业的小说编辑和创意作家。请根据用户需求对小说进行部分修改或扩展。

# 修改任务
{iteration_request.requirement}

# 当前小说内容
{content_to_show}

# 小说创作背景
- 原始主题: {context.get('metadata', {}).get('query', '未知')}
- 体裁风格: {context.get('metadata', {}).get('style', '未指定')}

# 创作要求

## 核心任务
根据用户需求，你可能需要：
- **添加新章节**: 在合适的位置插入新的情节发展
- **删除章节**: 移除不必要的章节
- **重写多章**: 优化多个章节的内容质量
- **调整结构**: 重新组织章节顺序，优化叙事节奏

## 创作标准

### 1. 剧情连贯性
- 新增或修改的情节要与整体故事线自然融合
- 保持时间线、因果关系的逻辑一致
- 伏笔和铺垫要有呼应，不能虎头蛇尾
- 冲突和高潮的设置要合理推进

### 2. 人物塑造
- 保持已有人物的性格特征和成长轨迹
- 新增人物要有明确的作用和特点
- 人物对话要符合各自的语言风格
- 人物关系的发展要自然合理

### 3. 风格统一
- 保持原有的叙事视角和语言风格
- 场景描写的详略程度要一致
- 情感表达和氛围营造的方式要统一
- 章节长度和节奏要协调

### 4. 质量提升
- 增强对话的生动性和推动力
- 丰富场景描写的层次感
- 提升情节的张力和悬念
- 深化主题表达和情感共鸣

## 特别注意
{"- 由于内容较长已截取，请确保保持已建立的人物设定和剧情走向" if is_truncated else ""}
- 如果添加新章节，请确保章节编号连续
- 如果删除章节，请调整后续章节编号
- 保持章节标题的命名风格一致

请输出完整的修改后的小说：
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
        """全局修改小说"""
        return await self._modify_fiction_partial(
            llm_client,
            current_content,
            iteration_request,
            context
        )

    def _format_search_results(self, search_results: Dict[str, Any]) -> str:
        """格式化搜索结果为可读文本"""
        all_content = search_results.get('all_content', [])

        if not all_content:
            return "无可用搜索结果"

        formatted = []
        for i, item in enumerate(all_content[:5], 1):  # 只取前5条
            formatted.append(f"{i}. {item.get('title', '未知标题')}")
            formatted.append(f"   内容摘要: {item.get('content', '')[:200]}...")
            formatted.append("")

        return "\n".join(formatted)

    async def _regenerate_html_from_markdown(
        self,
        project_dir: Path,
        markdown_content: str,
        context: Dict[str, Any]
    ):
        """从Markdown重新生成HTML"""
        # 这里可以调用HTML转换工具
        # 简化实现：使用markdown2库
        try:
            import markdown2

            html_content = markdown2.markdown(
                markdown_content,
                extras=['tables', 'fenced-code-blocks', 'header-ids']
            )

            # 包装完整HTML
            full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{context.get('metadata', {}).get('query', '报告')}</title>
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

            logger.info(f"[IterationAgent] HTML已重新生成: {html_file}")

        except ImportError:
            logger.warning("[IterationAgent] markdown2未安装，跳过HTML生成")
        except Exception as e:
            logger.error(f"[IterationAgent] HTML生成失败: {e}")

    def _save_updated_ppt(self, project_dir: Path, result: Dict[str, Any]):
        """保存更新后的PPT"""
        reports_dir = project_dir / "reports"

        # 保存HTML
        if result.get('html_content'):
            html_file = reports_dir / "FINAL_REPORT.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(result['html_content'])

        # 保存PPT数据
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
        """更新项目元数据"""
        metadata_file = project_dir / "metadata.json"

        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            # 添加迭代记录
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
