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
    """TODO: Add docstring."""

    def __init__(self, llm_manager: LLMManager, prompt_manager: PromptManager):
        self.llm_manager = llm_manager
        self.prompt_manager = prompt_manager
        self.web_searcher = WebSearcher()
        self.content_extractor = ContentExtractor()
        self.name = ""

        # Import analyzer and synthesizer for subtask-level processing
        from .search_analyzer import SearchAnalyzerAgent
        from .content_synthesizer import ContentSynthesizerAgent
        self.analyzer = SearchAnalyzerAgent(llm_manager, prompt_manager)
        self.synthesizer = ContentSynthesizerAgent(llm_manager, prompt_manager)
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """TODO: Add docstring."""
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
        """
        Execute deep search with subtask-level content refinement.
        NEW: Each subtask is now searched, analyzed, and synthesized individually.
        """

        logger.info(f"[{self.name}] ")

        #
        if not time_context:
            time_context = time_tool.parse_date_query(query)

        subtasks = decomposition.get("subtasks", [])
        all_content = []
        refined_subtasks = []  # NEW: Store refined content for each subtask
        search_summary = []

        logger.info(f"[{self.name}]  {len(subtasks)} ")

        # NEW: Process each subtask sequentially with refinement
        for i, subtask in enumerate(subtasks):
            # type"search"
            if subtask.get("type") == "search" or not subtask.get("type"):
                logger.info(f"[{self.name}]  {i+1}/{len(subtasks)}: {subtask.get('title', 'Unknown')}")

                # Step 1: Search for this subtask
                search_result = await self._execute_subtask_search(subtask, time_context, i)

                if isinstance(search_result, Exception):
                    logger.error(f"[{self.name}]  {i} : {search_result}")
                    continue

                if not search_result or not search_result.get("content"):
                    logger.warning(f"[{self.name}]  {i} ")
                    continue

                subtask_content = search_result["content"]
                logger.info(f"[{self.name}]  {i}  {len(subtask_content)} ")

                # Step 2: Analyze this subtask's results
                logger.info(f"[{self.name}]  {i} ...")
                analysis_result = await self.analyzer.analyze_subtask(
                    query=subtask.get("title", ""),
                    search_results=subtask_content,
                    subtask_context=subtask
                )

                # Step 3: Synthesize this subtask's content
                logger.info(f"[{self.name}]  {i} ...")
                synthesis_result = await self.synthesizer.synthesize_subtask(
                    query=subtask.get("title", ""),
                    search_results=subtask_content,
                    analysis_results=analysis_result,
                    subtask_context=subtask
                )

                # Step 4: Store refined subtask content
                refined_subtask = {
                    "subtask_id": subtask.get("id", f"task_{i}"),
                    "subtask_title": subtask.get("title", ""),
                    "subtask_index": i,
                    "raw_results": subtask_content,
                    "analysis": analysis_result.get("result", {}),
                    "refined_content": synthesis_result.get("result", {}).get("synthesized_content", ""),
                    "key_points": synthesis_result.get("result", {}).get("key_points", []),
                    "metadata": {
                        "results_count": len(subtask_content),
                        "analysis_quality": analysis_result.get("status", "unknown"),
                        "synthesis_quality": synthesis_result.get("status", "unknown")
                    }
                }

                refined_subtasks.append(refined_subtask)
                all_content.extend(subtask_content)  # Keep raw content for backward compatibility

                search_summary.append({
                    "subtask_id": subtask.get("id", f"task_{i}"),
                    "title": subtask.get("title", ""),
                    "results_count": len(subtask_content),
                    "refined": True,
                    "status": "success"
                })

                logger.info(f"[{self.name}]  {i}  {len(refined_subtask['refined_content'])} ")

            else:
                logger.info(f"[{self.name}]  {i}: type={subtask.get('type')}")

        #
        all_content = self._deduplicate_content(all_content)
        all_content = self._rank_content_by_relevance(all_content, query, time_context)

        logger.info(f"[{self.name}]  {len(refined_subtasks)} , {len(all_content)} ")

        return {
            "all_content": all_content,  # Keep for backward compatibility
            "refined_subtasks": refined_subtasks,  # NEW: Refined content organized by subtask
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
        """TODO: Add docstring."""
        
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
        """TODO: Add docstring."""

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
        """TODO: Add docstring."""
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
        """TODO: Add docstring."""
        
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
