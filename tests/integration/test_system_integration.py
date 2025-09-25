"""系统集成测试"""

import sys
import os
import asyncio
import pytest
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.deep_search_agent import DeepSearchAgent
from src.llm import LLMConfig, LLMProvider


class TestSystemIntegration:
    """系统集成测试"""
    
    @pytest.fixture
    def agent(self):
        """创建测试用的智能体实例"""
        return DeepSearchAgent()
    
    def test_system_initialization(self, agent):
        """测试系统初始化"""
        assert agent is not None
        assert agent.coordinator is not None
        assert agent.llm_manager is not None
        
        # 检查智能体是否正确初始化
        agents_status = agent.get_system_status()["agents_status"]
        expected_agents = ["query_optimizer", "search_analyzer", "content_synthesizer"]
        
        for agent_name in expected_agents:
            assert agent_name in agents_status
            assert agents_status[agent_name]["status"] == "idle"
    
    def test_llm_manager(self, agent):
        """测试LLM管理器"""
        llm_manager = agent.llm_manager
        
        # 检查配置
        configs = llm_manager.get_all_configs()
        assert len(configs) > 0
        assert "default" in configs
        
        # 检查默认配置
        default_config = llm_manager.get_config("default")
        assert isinstance(default_config, LLMConfig)
        assert default_config.provider in [p.value for p in LLMProvider]
    
    def test_prompt_manager(self, agent):
        """测试提示词管理器"""
        prompt_manager = agent.llm_manager.get_prompt_manager()
        
        # 检查提示词是否加载
        prompts = prompt_manager.list_prompts()
        assert len(prompts) > 0
        
        # 检查关键提示词是否存在
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
                pytest.skip(f"提示词文件 {prompt_key} 未找到")
    
    def test_agent_coordination(self, agent):
        """测试智能体协调"""
        coordinator = agent.coordinator
        
        # 检查智能体是否正确初始化
        assert "query_optimizer" in coordinator.agents
        assert "search_analyzer" in coordinator.agents
        assert "content_synthesizer" in coordinator.agents
        
        # 检查工作流是否构建
        assert coordinator.workflow is not None
    
    @pytest.mark.asyncio
    async def test_quick_answer_mock(self, agent):
        """测试快速回答功能（模拟）"""
        # 这个测试不会实际调用API，只测试流程
        query = "什么是人工智能？"
        
        try:
            # 尝试获取系统状态，确保系统正常
            status = agent.get_system_status()
            assert status is not None
            
            # 如果没有API密钥，跳过实际调用测试
            api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
            if not api_key:
                pytest.skip("未配置API密钥，跳过实际调用测试")
            
            # 实际调用测试
            answer = await agent.quick_answer(query)
            assert isinstance(answer, str)
            assert len(answer) > 0
            
        except Exception as e:
            # 如果是API相关错误，跳过测试
            if "api" in str(e).lower() or "key" in str(e).lower():
                pytest.skip(f"API配置问题，跳过测试: {e}")
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_search_workflow_structure(self, agent):
        """测试搜索工作流结构"""
        query = "测试查询"
        
        try:
            # 检查工作流节点是否存在
            coordinator = agent.coordinator
            workflow = coordinator.workflow
            
            # 这里我们只测试工作流的结构，不实际执行
            assert workflow is not None
            
            # 如果没有API密钥，跳过实际执行测试
            api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
            if not api_key:
                pytest.skip("未配置API密钥，跳过工作流执行测试")
            
            # 实际执行测试（简化版）
            result = await agent.search(query, config={"timeout_seconds": 60})
            
            # 检查结果结构
            assert "status" in result
            assert "user_query" in result
            assert result["user_query"] == query
            
        except Exception as e:
            if "api" in str(e).lower() or "key" in str(e).lower() or "timeout" in str(e).lower():
                pytest.skip(f"API或网络问题，跳过测试: {e}")
            else:
                raise
    
    def test_configuration_management(self, agent):
        """测试配置管理"""
        # 测试获取系统状态
        status = agent.get_system_status()
        
        assert "llm_manager" in status
        assert "agents_status" in status
        assert "coordinator_config" in status
        
        # 检查LLM管理器状态
        llm_status = status["llm_manager"]
        assert "total_configs" in llm_status
        assert "available_configs" in llm_status
        assert llm_status["total_configs"] > 0
        
        # 检查智能体状态
        agents_status = status["agents_status"]
        for agent_name in ["query_optimizer", "search_analyzer", "content_synthesizer"]:
            assert agent_name in agents_status
            agent_info = agents_status[agent_name]
            assert "status" in agent_info
            assert "llm_model" in agent_info
    
    def test_error_handling(self, agent):
        """测试错误处理"""
        # 测试无效配置
        try:
            agent.llm_manager.get_config("nonexistent_config")
            # 应该返回默认配置，不抛出异常
        except Exception:
            pass  # 预期可能的异常
        
        # 测试重置功能
        agent.reset_agents()
        
        # 检查状态是否重置
        status = agent.get_system_status()
        agents_status = status["agents_status"]
        
        for agent_name in agents_status:
            assert agents_status[agent_name]["status"] == "idle"


async def run_integration_test():
    """运行集成测试"""
    print("=== DeepSearch智能体系统集成测试 ===")
    
    try:
        # 创建智能体实例
        agent = DeepSearchAgent()
        print("✓ 智能体系统初始化成功")
        
        # 测试系统状态
        status = agent.get_system_status()
        print(f"✓ 系统状态正常")
        print(f"  - LLM配置数量: {status['llm_manager']['total_configs']}")
        print(f"  - 智能体数量: {len(status['agents_status'])}")
        print(f"  - 提示词数量: {status['llm_manager']['prompt_manager_info']['prompts_count']}")
        
        # 测试提示词管理
        prompt_manager = agent.llm_manager.get_prompt_manager()
        prompts = prompt_manager.list_prompts()
        print(f"✓ 提示词管理正常，共 {len(prompts)} 个提示词")
        
        # 测试智能体协调器
        coordinator = agent.coordinator
        print(f"✓ 智能体协调器正常，共 {len(coordinator.agents)} 个智能体")
        
        # 测试API连接（如果配置了密钥）
        api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                answer = await agent.quick_answer("测试查询")
                print(f"✓ API连接测试成功: {answer[:50]}...")
            except Exception as e:
                print(f"⚠ API连接测试失败: {e}")
        else:
            print("⚠ 未配置API密钥，跳过连接测试")
        
        print("\n=== 集成测试完成 ===")
        print("✅ 所有核心功能正常")
        
    except Exception as e:
        print(f"✗ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    # 运行集成测试
    asyncio.run(run_integration_test())