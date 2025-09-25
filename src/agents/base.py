"""智能体基类"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from loguru import logger

from ..llm import LLMManager, PromptManager


@dataclass
class AgentConfig:
    """智能体配置"""
    name: str
    description: str
    llm_config_name: str = "default"
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout_seconds: int = 60


class BaseAgent(ABC):
    """智能体基类"""
    
    def __init__(
        self, 
        llm_manager: LLMManager,
        prompt_manager: Optional[PromptManager] = None,
        config: Optional[AgentConfig] = None
    ):
        self.llm_manager = llm_manager
        self.prompt_manager = prompt_manager or llm_manager.get_prompt_manager()
        self.config = config or AgentConfig(
            name=self.__class__.__name__,
            description="基础智能体"
        )
        
        # 从配置中获取属性
        self.name = self.config.name
        self.description = self.config.description
        
        logger.info(f"初始化智能体: {self.name}")
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理输入数据"""
        pass
    
    async def get_llm_response(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """获取LLM响应"""
        try:
            client = self.llm_manager.get_client(self.config.llm_config_name)
            response = await client.simple_chat(prompt, system_prompt)
            return response
        except Exception as e:
            logger.error(f"LLM响应失败 ({self.name}): {e}")
            raise
    
    def get_prompt(self, prompt_name: str, **kwargs) -> str:
        """获取提示词"""
        try:
            # 尝试不同的路径格式
            possible_keys = [
                prompt_name,
                prompt_name.replace('/', '\\'),
                prompt_name.replace('\\', '/')
            ]
            
            for key in possible_keys:
                try:
                    return self.prompt_manager.get_prompt(key, **kwargs)
                except KeyError:
                    continue
            
            # 如果都失败了，列出可用的提示词
            available_prompts = self.prompt_manager.list_prompts()
            logger.error(f"获取提示词失败 ({self.name}): 找不到 '{prompt_name}'")
            logger.debug(f"可用提示词: {available_prompts}")
            return ""
            
        except Exception as e:
            logger.error(f"获取提示词失败 ({self.name}): {e}")
            return ""
    
    def get_status(self) -> Dict[str, Any]:
        """获取智能体状态"""
        return {
            "name": self.name,
            "description": self.description,
            "config": {
                "llm_config_name": self.config.llm_config_name,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
                "timeout_seconds": self.config.timeout_seconds
            },
            "status": "active"
        }