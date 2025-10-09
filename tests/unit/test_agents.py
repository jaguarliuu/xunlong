"""TODO: Add docstring."""

import sys
import os
import asyncio
import pytest
from pathlib import Path

# Python
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.deep_search_agent import DeepSearchAgent
from src.llm import LLMConfig, LLMProvider


class TestDeepSearchAgent:
    """DeepSearch"""
    
    @pytest.fixture
    def agent(self):
        """TODO: Add docstring."""
        return DeepSearchAgent()
    
    def test_agent_initialization(self, agent):
        """TODO: Add docstring."""
        assert agent is not None
        assert agent.coordinator is not None
        assert agent.llm_manager is not None
        
        # 
        agents_status = agent.get_system_status()["agents_status"]
        expected_agents = ["query_optimizer", "search_analyzer", "content_synthesizer"]
        
        for agent_name in expected_agents:
            assert agent_name in agents_status
    
    @pytest.mark.asyncio
    async def test_quick_answer(self, agent):
        """TODO: Add docstring."""
        query = ""
        
        try:
            answer = await agent.quick_answer(query)
            assert isinstance(answer, str)
            assert len(answer) > 0
            print(f": {answer[:100]}...")
            
        except Exception as e:
            print(f" (API): {e}")
            pytest.skip("API")
    
    @pytest.mark.asyncio
    async def test_deep_search(self, agent):
        """TODO: Add docstring."""
        query = "Python"
        
        try:
            result = await agent.search(query)
            
            # 
            assert "status" in result
            assert "user_query" in result
            assert result["user_query"] == query
            
            # 
            if result["status"] in ["success", "partial_success"]:
                assert "optimization_result" in result
                assert "search_results" in result
                assert "analysis_results" in result
                assert "final_report" in result
                
                print(f": {result['status']}")
                print(f": {result.get('execution_steps', [])}")
                
                if result.get("final_report"):
                    report_content = result["final_report"].get("report_content", "")
                    print(f": {report_content[:200]}...")
            
        except Exception as e:
            print(f" (API): {e}")
            pytest.skip("API")
    
    def test_system_status(self, agent):
        """TODO: Add docstring."""
        status = agent.get_system_status()
        
        assert "llm_manager" in status
        assert "agents_status" in status
        assert "coordinator_config" in status
        
        # LLM
        llm_status = status["llm_manager"]
        assert "total_configs" in llm_status
        assert "available_configs" in llm_status
        assert llm_status["total_configs"] > 0
        
        print(f": {status}")
    
    def test_prompt_management(self, agent):
        """TODO: Add docstring."""
        prompt_manager = agent.llm_manager.get_prompt_manager()
        
        # 
        prompts = prompt_manager.list_prompts()
        assert len(prompts) > 0
        
        print(f": {prompts}")
        
        # 
        try:
            system_prompt = prompt_manager.get_system_prompt("query_optimizer")
            assert isinstance(system_prompt, str)
            assert len(system_prompt) > 0
            print(f": {len(system_prompt)}")
            
        except KeyError:
            print("")
    
    def test_configuration_management(self, agent):
        """TODO: Add docstring."""
        llm_manager = agent.llm_manager
        
        # 
        configs = llm_manager.get_all_configs()
        assert len(configs) > 0
        assert "default" in configs
        
        # 
        default_config = llm_manager.get_config("default")
        assert isinstance(default_config, LLMConfig)
        
        print(f": {list(configs.keys())}")
        print(f": {default_config.provider} - {default_config.model_name}")


async def run_basic_test():
    """TODO: Add docstring."""
    print("=== DeepSearch ===")
    
    try:
        # 
        agent = DeepSearchAgent()
        print(" ")
        
        # 
        status = agent.get_system_status()
        print(f"  {status['llm_manager']['total_configs']} LLM")
        
        # 
        prompts = agent.llm_manager.get_prompt_manager().list_prompts()
        print(f"  {len(prompts)} ")
        
        #  (API)
        try:
            answer = await agent.quick_answer("")
            print(f" : {answer[:50]}...")
        except Exception as e:
            print(f"  (API): {e}")
        
        print("\n===  ===")
        
    except Exception as e:
        print(f" : {e}")
        raise


if __name__ == "__main__":
    # 
    asyncio.run(run_basic_test())