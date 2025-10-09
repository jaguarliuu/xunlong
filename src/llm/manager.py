"""LLM - """

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

# 
load_dotenv()

from .config import LLMConfig, LLMProvider, create_llm_config
from .client import LLMClient
from .prompts import PromptManager


class LLMManager:
    """LLM - """
    
    def __init__(self, config_path: str = "config/llm_config.yaml"):
        self.config_path = Path(config_path)
        self.configs: Dict[str, LLMConfig] = {}
        self.clients: Dict[str, LLMClient] = {}
        self.prompt_manager = PromptManager()
        self.provider_info = {}
        
        self._load_configurations()
        logger.info("LLM")
    
    def _load_configurations(self):
        """TODO: Add docstring."""
        if not self.config_path.exists():
            logger.warning(f": {self.config_path}")
            self._create_default_configs()
            return
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            # 
            self.provider_info = config_data.get("providers", {})
            
            # 
            default_config = config_data.get("default", {})
            self.configs["default"] = self._create_config_with_env(default_config)
            
            # 
            agents_config = config_data.get("agents", {})
            for agent_name, agent_config in agents_config.items():
                # 
                merged_config = {**default_config, **agent_config}
                self.configs[agent_name] = self._create_config_with_env(merged_config)
            
            logger.info(f" {len(self.configs)} LLM")
            
            # API
            self._log_detected_api_keys()
            
        except Exception as e:
            logger.error(f": {e}")
            self._create_default_configs()
    
    def _create_config_with_env(self, config_dict: Dict[str, Any]) -> LLMConfig:
        """TODO: Add docstring."""
        provider = config_dict.get("provider", "qwen")
        
        # API
        api_key = self._detect_api_key(provider)
        if api_key:
            config_dict["api_key"] = api_key
        
        # base_url
        base_url = self._detect_base_url(provider)
        if base_url:
            config_dict["base_url"] = base_url
        
        return LLMConfig(**config_dict)
    
    def _detect_api_key(self, provider: str) -> Optional[str]:
        """API"""
        # 
        env_keys = []
        
        # 
        if provider == "openai":
            env_keys = ["OPENAI_API_KEY", "LLM_API_KEY"]
        elif provider == "azure_openai":
            env_keys = ["AZURE_OPENAI_API_KEY", "LLM_API_KEY"]
        elif provider == "anthropic":
            env_keys = ["ANTHROPIC_API_KEY", "LLM_API_KEY"]
        elif provider == "zhipu":
            env_keys = ["ZHIPU_API_KEY", "LLM_API_KEY"]
        elif provider == "qwen":
            env_keys = ["DASHSCOPE_API_KEY", "QWEN_API_KEY", "LLM_API_KEY"]
        elif provider == "deepseek":
            env_keys = ["DEEPSEEK_API_KEY", "LLM_API_KEY"]
        elif provider == "ollama":
            return None  # OllamaAPI
        else:
            env_keys = ["LLM_API_KEY"]
        
        # 
        for env_key in env_keys:
            api_key = os.getenv(env_key)
            if api_key:
                return api_key
        
        return None
    
    def _detect_base_url(self, provider: str) -> Optional[str]:
        """base_url"""
        # 
        base_url = os.getenv("LLM_BASE_URL")
        if base_url:
            return base_url
        
        # URL
        default_urls = {
            "openai": "https://api.openai.com/v1",
            "anthropic": "https://api.anthropic.com",
            "zhipu": "https://open.bigmodel.cn/api/paas/v4",
            "qwen": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "deepseek": "https://api.deepseek.com/v1",
            "ollama": "http://localhost:11434/v1"
        }
        
        return default_urls.get(provider)
    
    def _log_detected_api_keys(self):
        """API"""
        detected_keys = []
        
        env_vars = [
            ("OPENAI_API_KEY", "OpenAI"),
            ("AZURE_OPENAI_API_KEY", "Azure OpenAI"),
            ("ANTHROPIC_API_KEY", "Anthropic"),
            ("ZHIPU_API_KEY", "AI"),
            ("DASHSCOPE_API_KEY", ""),
            ("QWEN_API_KEY", ""),
            ("DEEPSEEK_API_KEY", "DeepSeek"),
            ("LLM_API_KEY", "LLM")
        ]
        
        for env_key, provider_name in env_vars:
            if os.getenv(env_key):
                detected_keys.append(f"{provider_name}({env_key})")
        
        if detected_keys:
            logger.info(f"API: {', '.join(detected_keys)}")
        else:
            logger.warning("API")
    
    def _create_default_configs(self):
        """TODO: Add docstring."""
        # 
        best_provider = self._detect_best_provider()

        # 
        default_temperature = float(os.getenv("DEFAULT_LLM_TEMPERATURE", "0.7"))
        default_max_tokens = int(os.getenv("DEFAULT_LLM_MAX_TOKENS", "4000"))

        # API
        api_key = self._detect_api_key(best_provider)
        if not api_key and best_provider != "ollama":
            logger.warning(f" {best_provider} API")

        # base_url
        base_url = self._detect_base_url(best_provider)

        # 
        self.configs["default"] = create_llm_config(
            provider=LLMProvider(best_provider),
            api_key=api_key,
            base_url=base_url,
            model_name=self._get_default_model(best_provider),
            temperature=default_temperature,
            max_tokens=default_max_tokens
        )

        # 
        self.configs["query_optimizer"] = create_llm_config(
            provider=LLMProvider(best_provider),
            api_key=api_key,
            base_url=base_url,
            model_name=self._get_default_model(best_provider),
            temperature=0.3,
            max_tokens=2000
        )

        self.configs["search_analyzer"] = create_llm_config(
            provider=LLMProvider(best_provider),
            api_key=api_key,
            base_url=base_url,
            model_name=self._get_default_model(best_provider),
            temperature=0.5,
            max_tokens=4000
        )

        self.configs["content_synthesizer"] = create_llm_config(
            provider=LLMProvider(best_provider),
            api_key=api_key,
            base_url=base_url,
            model_name=self._get_default_model(best_provider),
            temperature=default_temperature,
            max_tokens=6000
        )

        logger.info(f": {best_provider}, : {self._get_default_model(best_provider)}, API: {'' if api_key else ''}")
    
    def _detect_best_provider(self) -> str:
        """TODO: Add docstring."""
        # 
        default_provider = os.getenv("DEFAULT_LLM_PROVIDER")
        if default_provider:
            # API
            provider_env_keys = {
                "qwen": ["DASHSCOPE_API_KEY", "QWEN_API_KEY"],
                "deepseek": ["DEEPSEEK_API_KEY"],
                "zhipu": ["ZHIPU_API_KEY"],
                "openai": ["OPENAI_API_KEY"],
                "anthropic": ["ANTHROPIC_API_KEY"],
                "ollama": []  # OllamaAPI
            }

            env_keys = provider_env_keys.get(default_provider, [])

            # ollamaAPI
            if not env_keys or any(os.getenv(key) for key in env_keys):
                logger.info(f": {default_provider}")
                return default_provider
            else:
                logger.warning(f" {default_provider} API")

        # 
        providers_priority = [
            ("deepseek", ["DEEPSEEK_API_KEY"]),
            ("qwen", ["DASHSCOPE_API_KEY", "QWEN_API_KEY"]),
            ("zhipu", ["ZHIPU_API_KEY"]),
            ("openai", ["OPENAI_API_KEY"]),
            ("anthropic", ["ANTHROPIC_API_KEY"]),
            ("ollama", [])  # OllamaAPI
        ]

        # API
        if os.getenv("LLM_API_KEY"):
            return "deepseek"  # DeepSeek

        # API
        for provider, env_keys in providers_priority:
            if not env_keys:  # Ollama
                continue

            for env_key in env_keys:
                if os.getenv(env_key):
                    logger.info(f": {provider}")
                    return provider

        # Ollama
        logger.warning("APIOllama")
        return "ollama"
    
    def _get_default_model(self, provider: str) -> str:
        """TODO: Add docstring."""
        # 
        env_model = os.getenv("DEFAULT_LLM_MODEL")
        if env_model:
            logger.info(f": {env_model}")
            return env_model

        default_models = {
            "openai": "gpt-4o-mini",
            "anthropic": "claude-3-sonnet-20250229",
            "zhipu": "glm-4",
            "qwen": "qwen-turbo",
            "deepseek": "deepseek-chat",
            "ollama": "llama3"
        }

        return default_models.get(provider, "gpt-4o-mini")
    
    def get_client(self, config_name: str = "default") -> LLMClient:
        """LLM"""
        if config_name not in self.clients:
            if config_name not in self.configs:
                logger.warning(f": {config_name}")
                config_name = "default"
            
            config = self.configs[config_name]
            self.clients[config_name] = LLMClient(config)
        
        return self.clients[config_name]
    
    def get_config(self, config_name: str = "default") -> LLMConfig:
        """LLM"""
        if config_name not in self.configs:
            logger.warning(f": {config_name}")
            config_name = "default"
        
        return self.configs[config_name]
    
    def get_all_configs(self) -> Dict[str, LLMConfig]:
        """TODO: Add docstring."""
        return self.configs.copy()
    
    def add_config(self, name: str, config: LLMConfig):
        """TODO: Add docstring."""
        self.configs[name] = config
        # 
        if name in self.clients:
            del self.clients[name]
        
        logger.info(f": {name}")
    
    def update_config(self, name: str, **kwargs):
        """TODO: Add docstring."""
        if name not in self.configs:
            raise KeyError(f": {name}")
        
        # 
        current_config = self.configs[name]
        config_dict = current_config.model_dump()
        
        # 
        config_dict.update(kwargs)
        
        # 
        self.configs[name] = LLMConfig(**config_dict)
        
        # 
        if name in self.clients:
            del self.clients[name]
        
        logger.info(f": {name}")
    
    def remove_config(self, name: str):
        """TODO: Add docstring."""
        if name == "default":
            raise ValueError("")
        
        if name in self.configs:
            del self.configs[name]
        
        if name in self.clients:
            del self.clients[name]
        
        logger.info(f": {name}")
    
    def get_prompt_manager(self) -> PromptManager:
        """TODO: Add docstring."""
        return self.prompt_manager
    
    def reload_prompts(self):
        """TODO: Add docstring."""
        self.prompt_manager.reload_prompts()
        logger.info("")
    
    def test_connection(self, config_name: str = "default") -> bool:
        """TODO: Add docstring."""
        try:
            client = self.get_client(config_name)
            # 
            import asyncio
            
            async def test():
                return await client.test_connection()
            
            result = asyncio.run(test())
            logger.info(f" {config_name} {'' if result else ''}")
            return result
            
        except Exception as e:
            logger.error(f" {config_name} : {e}")
            return False
    
    def get_available_providers(self) -> Dict[str, Dict[str, Any]]:
        """TODO: Add docstring."""
        available = {}
        
        for provider in LLMProvider:
            provider_name = provider.value
            api_key = self._detect_api_key(provider_name)
            base_url = self._detect_base_url(provider_name)
            
            available[provider_name] = {
                "has_api_key": api_key is not None,
                "base_url": base_url,
                "default_model": self._get_default_model(provider_name),
                "status": "" if api_key or provider_name == "ollama" else "API"
            }
        
        return available
    
    def get_manager_info(self) -> Dict[str, Any]:
        """TODO: Add docstring."""
        return {
            "config_path": str(self.config_path),
            "total_configs": len(self.configs),
            "active_clients": len(self.clients),
            "available_configs": list(self.configs.keys()),
            "available_providers": self.get_available_providers(),
            "prompt_manager_info": {
                "prompts_count": len(self.prompt_manager.list_prompts()),
                "prompts_dir": str(self.prompt_manager.prompts_dir)
            }
        }


# LLM
llm_manager = LLMManager()