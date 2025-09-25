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
        
        # 并行执行所有搜索子任务
        search_tasks = []
        for i, subtask in enumerate(subtasks):
            if subtask.get("type") == "search":
                task = self._execute_subtask_search(subtask, time_context, i)
                search_tasks.append(task)
        
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
            
            search_queries = subtask.get("search_queries", [])
            expected_results = subtask.get("expected_results", 5)
            
            all_task_content = []
            
            # 执行每个搜索查询
            for query in search_queries[:3]:  # 限制每个子任务最多3个查询
                try:
                    # 执行搜索
                    search_results = self.web_searcher.search_sync(
                        query, 
                        max_results=expected_results
                    )
                    
                    if not search_results:
                        continue
                    
                    # 提取内容
                    extraction_tasks = []
                    for result in search_results[:expected_results]:
                        task = self.content_extractor.extract_content(result["url"])
                        extraction_tasks.append(task)
                    
                    # 并行提取内容
                    extracted_contents = await asyncio.gather(
                        *extraction_tasks, 
                        return_exceptions=True
                    )
                    
                    # 处理提取结果
                    for j, content in enumerate(extracted_contents):
                        if isinstance(content, Exception):
                            logger.warning(f"[{self.name}] 内容提取失败: {content}")
                            continue
                        
                        if content and content.get("content"):
                            # 添加搜索上下文
                            content["search_query"] = query
                            content["subtask_id"] = subtask.get("id")
                            content["subtask_title"] = subtask.get("title")
                            content["extraction_time"] = datetime.now().isoformat()
                            
                            all_task_content.append(content)
                    
                    # 避免过于频繁的请求
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"[{self.name}] 搜索查询 '{query}' 失败: {e}")
                    continue
            
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