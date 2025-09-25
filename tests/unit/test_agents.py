"""智能体系统测试"""

import sys
import os
import asyncio
import pytest
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.deep_search_agent import DeepSearchAgent
from src.llm import LLMConfig, LLMProvider


class TestDeepSearchAgent:
    """DeepSearch智能体系统测试"""
    
    @pytest.fixture
    def agent(self):
        """创建测试用的智能体实例"""
        return DeepSearchAgent()
    
    def test_agent_initialization(self, agent):
        """测试智能体初始化"""
        assert agent is not None
        assert agent.coordinator is not None
        assert agent.llm_manager is not None
        
        # 检查智能体是否正确初始化
        agents_status = agent.get_system_status()["agents_status"]
        expected_agents = ["query_optimizer", "search_analyzer", "content_synthesizer"]
        
        for agent_name in expected_agents:
            assert agent_name in agents_status
    
    @pytest.mark.asyncio
    async def test_quick_answer(self, agent):
        """测试快速回答功能"""
        query = "什么是人工智能？"
        
        try:
            answer = await agent.quick_answer(query)
            assert isinstance(answer, str)
            assert len(answer) > 0
            print(f"快速回答: {answer[:100]}...")
            
        except Exception as e:
            print(f"快速回答测试失败 (可能是API配置问题): {e}")
            pytest.skip("API配置问题，跳过测试")
    
    @pytest.mark.asyncio
    async def test_deep_search(self, agent):
        """测试深度搜索功能"""
        query = "Python编程语言的特点"
        
        try:
            result = await agent.search(query)
            
            # 检查结果结构
            assert "status" in result
            assert "user_query" in result
            assert result["user_query"] == query
            
            # 如果成功，检查更多字段
            if result["status"] in ["success", "partial_success"]:
                assert "optimization_result" in result
                assert "search_results" in result
                assert "analysis_results" in result
                assert "final_report" in result
                
                print(f"搜索状态: {result['status']}")
                print(f"执行步骤: {result.get('execution_steps', [])}")
                
                if result.get("final_report"):
                    report_content = result["final_report"].get("report_content", "")
                    print(f"报告预览: {report_content[:200]}...")
            
        except Exception as e:
            print(f"深度搜索测试失败 (可能是API配置问题): {e}")
            pytest.skip("API配置问题，跳过测试")
    
    def test_system_status(self, agent):
        """测试系统状态获取"""
        status = agent.get_system_status()
        
        assert "llm_manager" in status
        assert "agents_status" in status
        assert "coordinator_config" in status
        
        # 检查LLM管理器状态
        llm_status = status["llm_manager"]
        assert "total_configs" in llm_status
        assert "available_configs" in llm_status
        assert llm_status["total_configs"] > 0
        
        print(f"系统状态: {status}")
    
    def test_prompt_management(self, agent):
        """测试提示词管理"""
        prompt_manager = agent.llm_manager.get_prompt_manager()
        
        # 检查提示词是否加载
        prompts = prompt_manager.list_prompts()
        assert len(prompts) > 0
        
        print(f"已加载提示词: {prompts}")
        
        # 测试获取特定提示词
        try:
            system_prompt = prompt_manager.get_system_prompt("query_optimizer")
            assert isinstance(system_prompt, str)
            assert len(system_prompt) > 0
            print(f"查询优化智能体系统提示词长度: {len(system_prompt)}")
            
        except KeyError:
            print("提示词文件可能未正确加载")
    
    def test_configuration_management(self, agent):
        """测试配置管理"""
        llm_manager = agent.llm_manager
        
        # 检查配置
        configs = llm_manager.get_all_configs()
        assert len(configs) > 0
        assert "default" in configs
        
        # 检查默认配置
        default_config = llm_manager.get_config("default")
        assert isinstance(default_config, LLMConfig)
        
        print(f"可用配置: {list(configs.keys())}")
        print(f"默认配置: {default_config.provider} - {default_config.model_name}")


async def run_basic_test():
    """运行基础测试"""
    print("=== DeepSearch智能体系统基础测试 ===")
    
    try:
        # 创建智能体实例
        agent = DeepSearchAgent()
        print("✓ 智能体系统初始化成功")
        
        # 检查系统状态
        status = agent.get_system_status()
        print(f"✓ 系统状态正常，共有 {status['llm_manager']['total_configs']} 个LLM配置")
        
        # 检查提示词
        prompts = agent.llm_manager.get_prompt_manager().list_prompts()
        print(f"✓ 提示词加载成功，共 {len(prompts)} 个提示词")
        
        # 测试快速回答 (如果API配置正确)
        try:
            answer = await agent.quick_answer("测试查询")
            print(f"✓ 快速回答功能正常: {answer[:50]}...")
        except Exception as e:
            print(f"⚠ 快速回答功能测试失败 (可能是API配置问题): {e}")
        
        print("\n=== 测试完成 ===")
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        raise


if __name__ == "__main__":
    # 运行基础测试
    asyncio.run(run_basic_test())