"""
 - 
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
    """"""
    
    def __init__(self, llm_manager: LLMManager, prompt_manager: PromptManager):
        self.llm_manager = llm_manager
        self.prompt_manager = prompt_manager
        self.web_searcher = WebSearcher()
        self.content_extractor = ContentExtractor()
        self.name = ""
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """"""
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
        """"""
        
        logger.info(f"[{self.name}] ")
        
        # 
        if not time_context:
            time_context = time_tool.parse_date_query(query)
        
        subtasks = decomposition.get("subtasks", [])
        all_content = []
        search_summary = []
        
        logger.info(f"[{self.name}]  {len(subtasks)} ")
        for i, subtask in enumerate(subtasks):
            logger.info(f"[{self.name}]  {i}: {subtask}")
        
        # 
        search_tasks = []
        for i, subtask in enumerate(subtasks):
            # type"search"
            if subtask.get("type") == "search" or not subtask.get("type"):
                logger.info(f"[{self.name}]  {i}: {subtask.get('title', 'Unknown')}")
                task = self._execute_subtask_search(subtask, time_context, i)
                search_tasks.append(task)
            else:
                logger.info(f"[{self.name}]  {i}: type={subtask.get('type')}")
        
        if search_tasks:
            search_results = await asyncio.gather(*search_tasks, return_exceptions=True)
            
            # 
            for i, result in enumerate(search_results):
                if isinstance(result, Exception):
                    logger.error(f"[{self.name}]  {i} : {result}")
                    continue
                
                if result and result.get("content"):
                    all_content.extend(result["content"])
                    search_summary.append({
                        "subtask_id": subtasks[i].get("id", f"task_{i}"),
                        "title": subtasks[i].get("title", ""),
                        "results_count": len(result["content"]),
                        "status": "success"
                    })
        
        # 
        all_content = self._deduplicate_content(all_content)
        all_content = self._rank_content_by_relevance(all_content, query, time_context)
        
        logger.info(f"[{self.name}]  {len(all_content)} ")
        
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
        """"""
        
        try:
            logger.info(f"[{self.name}]  {task_index}: {subtask.get('title', 'Unknown')}")
            subtask_time_context = subtask.get("time_context") or time_context or {}
            time_filter = subtask.get("time_filter") or subtask_time_context.get("time_filter")

            search_queries = subtask.get("search_queries", [])
            expected_results = subtask.get("expected_results", 5)

            all_task_content = []

            # 
            query_tasks = []
            for query in search_queries[:3]:  # 3
                task = self._execute_single_query(
                    query, subtask, expected_results, task_index, subtask_time_context, time_filter
                )
                query_tasks.append(task)

            if query_tasks:
                query_results = await asyncio.gather(*query_tasks, return_exceptions=True)

                # 
                for result in query_results:
                    if isinstance(result, Exception):
                        logger.error(f"[{self.name}] : {result}")
                        continue

                    if result and isinstance(result, list):
                        all_task_content.extend(result)
            
            logger.info(f"[{self.name}]  {task_index}  {len(all_task_content)} ")
            
            return {
                "subtask": subtask,
                "content": all_task_content,
                "queries_executed": len(search_queries)
            }
            
        except Exception as e:
            logger.error(f"[{self.name}]  {task_index} : {e}")
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
        """"""

        try:
            logger.info(f"[{self.name}]  {task_index} : {query}")

            # 
            search_results = await self.web_searcher.search(
                query,
                max_results=expected_results,
                time_filter=time_filter
            )

            logger.info(f"[{self.name}]  '{query}'  {len(search_results) if search_results else 0} ")

            if not search_results:
                logger.warning(f"[{self.name}]  '{query}' ")
                return []

            query_content = []
            fallback_requests = []

            for rank, result in enumerate(search_results[:expected_results]):
                if not isinstance(result, dict):
                    continue

                # Markdown
                full_content = (result.get("full_content") or result.get("content") or result.get("snippet") or "").strip()
                images = result.get("images", []) or []

                base_record = {
                    "url": result.get("url", ""),
                    "title": result.get("title", ""),
                    "snippet": result.get("snippet", ""),
                    "content": full_content,  # 
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

            # 
            if fallback_requests:
                logger.info(f"[{self.name}]  {len(fallback_requests)} ")

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
                            logger.warning(f"[{self.name}] : {extracted}")
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

            logger.info(f"[{self.name}]  '{query}'  {len(query_content)} ")
            return query_content

        except Exception as e:
            logger.error(f"[{self.name}]  '{query}' : {e}")
            return []

    def _deduplicate_content(self, content_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """"""
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
        """"""
        
        # 
        for content in content_list:
            score = 0
            
            # 
            title = content.get("title", "").lower()
            query_words = query.lower().split()
            title_matches = sum(1 for word in query_words if word in title)
            score += title_matches * 2

            # 
            if content.get("source") == "user_document":
                score += 100
            
            # 
            content_length = len(content.get("content", ""))
            if content_length > 1000:
                score += 2
            elif content_length > 500:
                score += 1
            
            # 
            if time_context.get("extracted_dates"):
                extracted_time = content.get("extracted_time")
                if extracted_time:
                    target_dates = [d["formatted"] for d in time_context["extracted_dates"]]
                    if any(time_tool.is_date_relevant(extracted_time, date) for date in target_dates):
                        score += 3
            
            content["relevance_score"] = score
        
        # 
        return sorted(content_list, key=lambda x: x.get("relevance_score", 0), reverse=True)
