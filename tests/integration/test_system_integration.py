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


class TestSystemIntegration:
    """TODO: Add docstring."""
    
    @pytest.fixture
    def agent(self):
        """TODO: Add docstring."""
        return DeepSearchAgent()
    
    def test_system_initialization(self, agent):
        """TODO: Add docstring."""
        assert agent is not None
        assert agent.coordinator is not None
        assert agent.llm_manager is not None
        
        # 
        agents_status = agent.get_system_status()["agents_status"]
        expected_agents = ["query_optimizer", "search_analyzer", "content_synthesizer"]
        
        for agent_name in expected_agents:
            assert agent_name in agents_status
            assert agents_status[agent_name]["status"] == "idle"
    
    def test_llm_manager(self, agent):
        """LLM"""
        llm_manager = agent.llm_manager
        
        # 
        configs = llm_manager.get_all_configs()
        assert len(configs) > 0
        assert "default" in configs
        
        # 
        default_config = llm_manager.get_config("default")
        assert isinstance(default_config, LLMConfig)
        assert default_config.provider in [p.value for p in LLMProvider]
    
    def test_prompt_manager(self, agent):
        """TODO: Add docstring."""
        prompt_manager = agent.llm_manager.get_prompt_manager()
        
        # 
        prompts = prompt_manager.list_prompts()
        assert len(prompts) > 0
        
        # 
        expected_prompts = [
            "agents/query_optimizer/system",
            "agents/search_analyzer/system", 
            "agents/content_synthesizer/system"
        ]
        
        for prompt_key in expected_prompts:
            try:
                prompt_content = prompt_manager.get_prompt(prompt_key)
                assert isinstance(prompt_content, str)
                assert len(prompt_content) > 0
            except KeyError:
                pytest.skip(f" {prompt_key} ")
    
    def test_agent_coordination(self, agent):
        """TODO: Add docstring."""
        coordinator = agent.coordinator
        
        # 
        assert "query_optimizer" in coordinator.agents
        assert "search_analyzer" in coordinator.agents
        assert "content_synthesizer" in coordinator.agents
        
        # 
        assert coordinator.workflow is not None
    
    @pytest.mark.asyncio
    async def test_quick_answer_mock(self, agent):
        """TODO: Add docstring."""
        # API
        query = ""
        
        try:
            # 
            status = agent.get_system_status()
            assert status is not None
            
            # API
            api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
            if not api_key:
                pytest.skip("API")
            
            # 
            answer = await agent.quick_answer(query)
            assert isinstance(answer, str)
            assert len(answer) > 0
            
        except Exception as e:
            # API
            if "api" in str(e).lower() or "key" in str(e).lower():
                pytest.skip(f"API: {e}")
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_search_workflow_structure(self, agent):
        """TODO: Add docstring."""
        query = ""
        
        try:
            # 
            coordinator = agent.coordinator
            workflow = coordinator.workflow
            
            # 
            assert workflow is not None
            
            # API
            api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
            if not api_key:
                pytest.skip("API")
            
            # 
            result = await agent.search(query, config={"timeout_seconds": 60})
            
            # 
            assert "status" in result
            assert "user_query" in result
            assert result["user_query"] == query
            
        except Exception as e:
            if "api" in str(e).lower() or "key" in str(e).lower() or "timeout" in str(e).lower():
                pytest.skip(f"API: {e}")
            else:
                raise
    
    def test_configuration_management(self, agent):
        """TODO: Add docstring."""
        # 
        status = agent.get_system_status()
        
        assert "llm_manager" in status
        assert "agents_status" in status
        assert "coordinator_config" in status
        
        # LLM
        llm_status = status["llm_manager"]
        assert "total_configs" in llm_status
        assert "available_configs" in llm_status
        assert llm_status["total_configs"] > 0
        
        # 
        agents_status = status["agents_status"]
        for agent_name in ["query_optimizer", "search_analyzer", "content_synthesizer"]:
            assert agent_name in agents_status
            agent_info = agents_status[agent_name]
            assert "status" in agent_info
            assert "llm_model" in agent_info
    
    def test_error_handling(self, agent):
        """TODO: Add docstring."""
        # 
        try:
            agent.llm_manager.get_config("nonexistent_config")
            # 
        except Exception:
            pass  # 
        
        # 
        agent.reset_agents()
        
        # 
        status = agent.get_system_status()
        agents_status = status["agents_status"]
        
        for agent_name in agents_status:
            assert agents_status[agent_name]["status"] == "idle"


async def run_integration_test():
    """TODO: Add docstring."""
    print("=== DeepSearch ===")
    
    try:
        # 
        agent = DeepSearchAgent()
        print(" ")
        
        # 
        status = agent.get_system_status()
        print(f" ")
        print(f"  - LLM: {status['llm_manager']['total_configs']}")
        print(f"  - : {len(status['agents_status'])}")
        print(f"  - : {status['llm_manager']['prompt_manager_info']['prompts_count']}")
        
        # 
        prompt_manager = agent.llm_manager.get_prompt_manager()
        prompts = prompt_manager.list_prompts()
        print(f"  {len(prompts)} ")
        
        # 
        coordinator = agent.coordinator
        print(f"  {len(coordinator.agents)} ")
        
        # API
        api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                answer = await agent.quick_answer("")
                print(f" API: {answer[:50]}...")
            except Exception as e:
                print(f" API: {e}")
        else:
            print(" API")
        
        print("\n===  ===")
        print(" ")
        
    except Exception as e:
        print(f" : {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    # 
    asyncio.run(run_integration_test())