"""
深度搜索智能体 - 执行多轮深度搜索
"""
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger

from ..llm.manager import LLMManager
from ..llm.prompts import PromptManager
from ..tools.web_searcher import WebSearcher
from ..tools.content_extractor import ContentExtractor
from ..tools.time_tool import time_tool

class DeepSearcher:
    """深度搜索智能体"""
    
    def __init__(self, llm_manager: LLMManager, prompt_manager: PromptManager):
        self.llm_manager = llm_manager
        self.prompt_manager = prompt_manager
        self.web_searcher = WebSearcher()
        self.content_extractor = ContentExtractor()
        self.name = "深度搜索智能体"
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理深度搜索请求"""
        query = data.get("query", "")
        decomposition = data.get("decomposition", {})
        time_context = data.get("time_context")
        
        result = await self.execute_deep_search(query, decomposition, time_context)
        return {
            "agent": self.name,
            "result": result,
            "status": "success" if result.get("all_content") else "failed"
        }
        
    async def execute_deep_search(
        self, 
        query: str, 
        decomposition: Dict[str, Any],
        time_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """执行深度搜索"""
        
        logger.info(f"[{self.name}] 开始执行深度搜索")
        
        # 获取时间上下文
        if not time_context:
            time_context = time_tool.parse_date_query(query)
        
        subtasks = decomposition.get("subtasks", [])
        all_content = []
        search_summary = []
        
        logger.info(f"[{self.name}] 获得 {len(subtasks)} 个子任务")
        for i, subtask in enumerate(subtasks):
            logger.info(f"[{self.name}] 子任务 {i}: {subtask}")
        
        # 并行执行所有搜索子任务
        search_tasks = []
        for i, subtask in enumerate(subtasks):
            # 修改条件：处理所有子任务，不仅仅是type为"search"的
            if subtask.get("type") == "search" or not subtask.get("type"):
                logger.info(f"[{self.name}] 准备执行子任务 {i}: {subtask.get('title', 'Unknown')}")
                task = self._execute_subtask_search(subtask, time_context, i)
                search_tasks.append(task)
            else:
                logger.info(f"[{self.name}] 跳过非搜索子任务 {i}: type={subtask.get('type')}")
        
        if search_tasks:
            search_results = await asyncio.gather(*search_tasks, return_exceptions=True)
            
            # 处理搜索结果
            for i, result in enumerate(search_results):
                if isinstance(result, Exception):
                    logger.error(f"[{self.name}] 子任务 {i} 搜索失败: {result}")
                    continue
                
                if result and result.get("content"):
                    all_content.extend(result["content"])
                    search_summary.append({
                        "subtask_id": subtasks[i].get("id", f"task_{i}"),
                        "title": subtasks[i].get("title", "未知任务"),
                        "results_count": len(result["content"]),
                        "status": "success"
                    })
        
        # 去重和排序
        all_content = self._deduplicate_content(all_content)
        all_content = self._rank_content_by_relevance(all_content, query, time_context)
        
        logger.info(f"[{self.name}] 深度搜索完成，获得 {len(all_content)} 个内容项")
        
        return {
            "all_content": all_content,
            "content_count": len(all_content),
            "search_summary": search_summary,
            "subtasks_executed": len(subtasks),
            "time_context": time_context
        }
    
    async def _execute_subtask_search(
        self, 
        subtask: Dict[str, Any], 
        time_context: Dict[str, Any],
        task_index: int
    ) -> Dict[str, Any]:
        """执行单个子任务搜索"""
        
        try:
            logger.info(f"[{self.name}] 执行子任务 {task_index}: {subtask.get('title', 'Unknown')}")
            subtask_time_context = subtask.get("time_context") or time_context or {}
            time_filter = subtask.get("time_filter") or subtask_time_context.get("time_filter")

            search_queries = subtask.get("search_queries", [])
            expected_results = subtask.get("expected_results", 5)

            all_task_content = []

            # 并行执行每个搜索查询
            query_tasks = []
            for query in search_queries[:3]:  # 限制每个子任务最多3个查询
                task = self._execute_single_query(
                    query, subtask, expected_results, task_index, subtask_time_context, time_filter
                )
                query_tasks.append(task)

            if query_tasks:
                query_results = await asyncio.gather(*query_tasks, return_exceptions=True)

                # 收集所有查询的结果
                for result in query_results:
                    if isinstance(result, Exception):
                        logger.error(f"[{self.name}] 查询执行失败: {result}")
                        continue

                    if result and isinstance(result, list):
                        all_task_content.extend(result)
            
            logger.info(f"[{self.name}] 子任务 {task_index} 完成，获得 {len(all_task_content)} 个内容项")
            
            return {
                "subtask": subtask,
                    "content": all_task_content,
                    "queries_executed": len(search_queries)
                }
            
        except Exception as e:
            logger.error(f"[{self.name}] 子任务 {task_index} 执行失败: {e}")
            return {
                "subtask": subtask,
                "content": [],
                "error": str(e)
            }

    async def _execute_single_query(
        self,
        query: str,
        subtask: Dict[str, Any],
        expected_results: int,
        task_index: int,
        time_context: Dict[str, Any],
        time_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """执行单个搜索查询（可并行）"""

        try:
            logger.info(f"[{self.name}] 子任务 {task_index} 开始搜索查询: {query}")

            # 执行搜索
            search_results = await self.web_searcher.search(
                query,
                max_results=expected_results,
                time_filter=time_filter
            )

            logger.info(f"[{self.name}] 搜索查询 '{query}' 获得 {len(search_results) if search_results else 0} 个结果")

            if not search_results:
                logger.warning(f"[{self.name}] 搜索查询 '{query}' 没有获得任何结果")
                return []

            query_content = []
            fallback_requests = []

            for rank, result in enumerate(search_results[:expected_results]):
                if not isinstance(result, dict):
                    continue

                # 读取抓取到的全文内容（已包含图片插入的Markdown）
                full_content = (result.get("full_content") or result.get("content") or result.get("snippet") or "").strip()
                images = result.get("images", []) or []

                base_record = {
                    "url": result.get("url", ""),
                    "title": result.get("title", ""),
                    "snippet": result.get("snippet", ""),
                    "content": full_content,  # 临时占位，后续若为空会回退
                    "full_content": full_content,
                    "content_length": len(full_content),
                    "search_query": query,
                    "subtask_id": subtask.get("id"),
                    "subtask_title": subtask.get("title"),
                    "extraction_time": datetime.now().isoformat(),
                    "source": result.get("source", "web"),
                    "rank": rank + 1,
                    "images": images,
                    "image_count": len(images),
                    "has_images": bool(images),
                    "images_inserted": result.get("images_inserted", False),
                    "image_insert_mode": result.get("image_insert_mode"),
                    "has_full_content": bool(full_content),
                    "extraction_status": "success" if full_content else "pending",
                    "time_context": time_context,
                    "time_filter": time_filter
                }

                if full_content:
                    query_content.append(base_record)
                else:
                    fallback_requests.append((base_record, result))

            # 对于未成功提取全文的结果，回退到内容提取器
            if fallback_requests:
                logger.info(f"[{self.name}] 对 {len(fallback_requests)} 个结果使用回退内容提取器")

                extraction_tasks = []
                valid_requests = []
                for record, result in fallback_requests:
                    url = result.get("url")
                    if url:
                        extraction_tasks.append(self.content_extractor.extract_content(url))
                        valid_requests.append((record, result))

                if extraction_tasks:
                    extracted_contents = await asyncio.gather(*extraction_tasks, return_exceptions=True)

                    for (record, result), extracted in zip(valid_requests, extracted_contents):
                        if isinstance(extracted, Exception):
                            logger.warning(f"[{self.name}] 回退内容提取失败: {extracted}")
                            record["extraction_status"] = "error"
                            record["error"] = str(extracted)
                            continue

                        if extracted and extracted.get("content"):
                            record["content"] = extracted.get("content", "")
                            record["full_content"] = record["content"]
                            record["content_length"] = extracted.get("content_length")
                            record["extraction_status"] = "success"
                            record["title"] = record["title"] or extracted.get("title", "")
                            if record["content"] or record["image_count"] > 0:
                                query_content.append(record)
                        else:
                            record["extraction_status"] = "no_content"
                            if record["content"] or record["image_count"] > 0:
                                query_content.append(record)

            logger.info(f"[{self.name}] 查询 '{query}' 完成，获得 {len(query_content)} 个有效内容")
            return query_content

        except Exception as e:
            logger.error(f"[{self.name}] 搜索查询 '{query}' 失败: {e}")
            return []

    def _deduplicate_content(self, content_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重内容"""
        seen_urls = set()
        unique_content = []
        
        for content in content_list:
            url = content.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_content.append(content)
        
        return unique_content
    
    def _rank_content_by_relevance(
        self, 
        content_list: List[Dict[str, Any]], 
        query: str,
        time_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """按相关性排序内容"""
        
        # 简单的相关性评分
        for content in content_list:
            score = 0
            
            # 标题相关性
            title = content.get("title", "").lower()
            query_words = query.lower().split()
            title_matches = sum(1 for word in query_words if word in title)
            score += title_matches * 2
            
            # 内容长度奖励
            content_length = len(content.get("content", ""))
            if content_length > 1000:
                score += 2
            elif content_length > 500:
                score += 1
            
            # 时间相关性
            if time_context.get("extracted_dates"):
                extracted_time = content.get("extracted_time")
                if extracted_time:
                    target_dates = [d["formatted"] for d in time_context["extracted_dates"]]
                    if any(time_tool.is_date_relevant(extracted_time, date) for date in target_dates):
                        score += 3
            
            content["relevance_score"] = score
        
        # 按评分排序
        return sorted(content_list, key=lambda x: x.get("relevance_score", 0), reverse=True)
