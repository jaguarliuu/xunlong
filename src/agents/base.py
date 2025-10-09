"""TODO: Add docstring."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from loguru import logger

from ..llm import LLMManager, PromptManager


@dataclass
class AgentConfig:
    """TODO: Add docstring."""
    name: str
    description: str
    llm_config_name: str = "default"
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout_seconds: int = 60


class BaseAgent(ABC):
    """TODO: Add docstring."""
    
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
            description=""
        )
        
        # 
        self.name = self.config.name
        self.description = self.config.description
        
        logger.info(f": {self.name}")
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """TODO: Add docstring."""
        pass
    
    async def get_llm_response(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """LLM"""
        try:
            client = self.llm_manager.get_client(self.config.llm_config_name)
            response = await client.simple_chat(prompt, system_prompt)
            return response
        except Exception as e:
            logger.error(f"LLM ({self.name}): {e}")
            raise
    
    def get_prompt(self, prompt_name: str, **kwargs) -> str:
        """TODO: Add docstring."""
        try:
            # 
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
            
            # 
            available_prompts = self.prompt_manager.list_prompts()
            logger.error(f" ({self.name}):  '{prompt_name}'")
            logger.debug(f": {available_prompts}")
            return ""
            
        except Exception as e:
            logger.error(f" ({self.name}): {e}")
            return ""
    
    def get_status(self) -> Dict[str, Any]:
        """TODO: Add docstring."""
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