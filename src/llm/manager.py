"""LLM管理器 - 统一管理多种大模型提供商"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from .config import LLMConfig, LLMProvider, create_llm_config
from .client import LLMClient
from .prompts import PromptManager


class LLMManager:
    """LLM管理器 - 支持多种大模型提供商"""
    
    def __init__(self, config_path: str = "config/llm_config.yaml"):
        self.config_path = Path(config_path)
        self.configs: Dict[str, LLMConfig] = {}
        self.clients: Dict[str, LLMClient] = {}
        self.prompt_manager = PromptManager()
        self.provider_info = {}
        
        self._load_configurations()
        logger.info("LLM管理器初始化完成")
    
    def _load_configurations(self):
        """加载配置文件"""
        if not self.config_path.exists():
            logger.warning(f"配置文件不存在: {self.config_path}，使用默认配置")
            self._create_default_configs()
            return
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            # 保存提供商信息
            self.provider_info = config_data.get("providers", {})
            
            # 加载默认配置
            default_config = config_data.get("default", {})
            self.configs["default"] = self._create_config_with_env(default_config)
            
            # 加载智能体专用配置
            agents_config = config_data.get("agents", {})
            for agent_name, agent_config in agents_config.items():
                # 合并默认配置和智能体配置
                merged_config = {**default_config, **agent_config}
                self.configs[agent_name] = self._create_config_with_env(merged_config)
            
            logger.info(f"已加载 {len(self.configs)} 个LLM配置")
            
            # 显示检测到的API密钥
            self._log_detected_api_keys()
            
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            self._create_default_configs()
    
    def _create_config_with_env(self, config_dict: Dict[str, Any]) -> LLMConfig:
        """创建配置并自动检测环境变量"""
        provider = config_dict.get("provider", "qwen")
        
        # 自动检测API密钥
        api_key = self._detect_api_key(provider)
        if api_key:
            config_dict["api_key"] = api_key
        
        # 自动检测base_url
        base_url = self._detect_base_url(provider)
        if base_url:
            config_dict["base_url"] = base_url
        
        return LLMConfig(**config_dict)
    
    def _detect_api_key(self, provider: str) -> Optional[str]:
        """自动检测API密钥"""
        # 优先级顺序的环境变量名
        env_keys = []
        
        # 特定提供商的环境变量
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
            return None  # Ollama不需要API密钥
        else:
            env_keys = ["LLM_API_KEY"]
        
        # 按优先级检查环境变量
        for env_key in env_keys:
            api_key = os.getenv(env_key)
            if api_key:
                return api_key
        
        return None
    
    def _detect_base_url(self, provider: str) -> Optional[str]:
        """自动检测base_url"""
        # 首先检查环境变量
        base_url = os.getenv("LLM_BASE_URL")
        if base_url:
            return base_url
        
        # 使用默认URL
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
        """记录检测到的API密钥"""
        detected_keys = []
        
        env_vars = [
            ("OPENAI_API_KEY", "OpenAI"),
            ("AZURE_OPENAI_API_KEY", "Azure OpenAI"),
            ("ANTHROPIC_API_KEY", "Anthropic"),
            ("ZHIPU_API_KEY", "智谱AI"),
            ("DASHSCOPE_API_KEY", "通义千问"),
            ("QWEN_API_KEY", "通义千问"),
            ("DEEPSEEK_API_KEY", "DeepSeek"),
            ("LLM_API_KEY", "通用LLM")
        ]
        
        for env_key, provider_name in env_vars:
            if os.getenv(env_key):
                detected_keys.append(f"{provider_name}({env_key})")
        
        if detected_keys:
            logger.info(f"检测到API密钥: {', '.join(detected_keys)}")
        else:
            logger.warning("未检测到任何API密钥，某些功能可能无法使用")
    
    def _create_default_configs(self):
        """创建默认配置"""
        # 自动检测最佳可用的提供商
        best_provider = self._detect_best_provider()
        
        # 默认配置
        self.configs["default"] = create_llm_config(
            provider=LLMProvider(best_provider),
            model_name=self._get_default_model(best_provider),
            temperature=0.7,
            max_tokens=4000
        )
        
        # 智能体配置
        self.configs["query_optimizer"] = create_llm_config(
            provider=LLMProvider(best_provider),
            model_name=self._get_default_model(best_provider),
            temperature=0.3,
            max_tokens=2000
        )
        
        self.configs["search_analyzer"] = create_llm_config(
            provider=LLMProvider(best_provider),
            model_name=self._get_default_model(best_provider),
            temperature=0.5,
            max_tokens=4000
        )
        
        self.configs["content_synthesizer"] = create_llm_config(
            provider=LLMProvider(best_provider),
            model_name=self._get_default_model(best_provider),
            temperature=0.7,
            max_tokens=6000
        )
        
        logger.info(f"使用默认配置，提供商: {best_provider}")
    
    def _detect_best_provider(self) -> str:
        """检测最佳可用的提供商"""
        # 按优先级检查可用的提供商
        providers_priority = [
            ("qwen", ["DASHSCOPE_API_KEY", "QWEN_API_KEY"]),
            ("deepseek", ["DEEPSEEK_API_KEY"]),
            ("zhipu", ["ZHIPU_API_KEY"]),
            ("openai", ["OPENAI_API_KEY"]),
            ("anthropic", ["ANTHROPIC_API_KEY"]),
            ("ollama", [])  # Ollama不需要API密钥
        ]
        
        # 检查通用API密钥
        if os.getenv("LLM_API_KEY"):
            return "qwen"  # 默认使用通义千问
        
        # 检查特定提供商的API密钥
        for provider, env_keys in providers_priority:
            if not env_keys:  # Ollama情况
                continue
            
            for env_key in env_keys:
                if os.getenv(env_key):
                    return provider
        
        # 如果都没有，默认使用Ollama（本地模型）
        return "ollama"
    
    def _get_default_model(self, provider: str) -> str:
        """获取提供商的默认模型"""
        default_models = {
            "openai": "gpt-4o-mini",
            "anthropic": "claude-3-sonnet-20240229",
            "zhipu": "glm-4",
            "qwen": "qwen-turbo",
            "deepseek": "deepseek-chat",
            "ollama": "llama3"
        }
        
        return default_models.get(provider, "gpt-4o-mini")
    
    def get_client(self, config_name: str = "default") -> LLMClient:
        """获取LLM客户端"""
        if config_name not in self.clients:
            if config_name not in self.configs:
                logger.warning(f"配置不存在: {config_name}，使用默认配置")
                config_name = "default"
            
            config = self.configs[config_name]
            self.clients[config_name] = LLMClient(config)
        
        return self.clients[config_name]
    
    def get_config(self, config_name: str = "default") -> LLMConfig:
        """获取LLM配置"""
        if config_name not in self.configs:
            logger.warning(f"配置不存在: {config_name}，使用默认配置")
            config_name = "default"
        
        return self.configs[config_name]
    
    def get_all_configs(self) -> Dict[str, LLMConfig]:
        """获取所有配置"""
        return self.configs.copy()
    
    def add_config(self, name: str, config: LLMConfig):
        """添加配置"""
        self.configs[name] = config
        # 清除对应的客户端缓存
        if name in self.clients:
            del self.clients[name]
        
        logger.info(f"已添加配置: {name}")
    
    def update_config(self, name: str, **kwargs):
        """更新配置"""
        if name not in self.configs:
            raise KeyError(f"配置不存在: {name}")
        
        # 获取当前配置数据
        current_config = self.configs[name]
        config_dict = current_config.model_dump()
        
        # 更新配置
        config_dict.update(kwargs)
        
        # 创建新配置
        self.configs[name] = LLMConfig(**config_dict)
        
        # 清除客户端缓存
        if name in self.clients:
            del self.clients[name]
        
        logger.info(f"已更新配置: {name}")
    
    def remove_config(self, name: str):
        """移除配置"""
        if name == "default":
            raise ValueError("不能移除默认配置")
        
        if name in self.configs:
            del self.configs[name]
        
        if name in self.clients:
            del self.clients[name]
        
        logger.info(f"已移除配置: {name}")
    
    def get_prompt_manager(self) -> PromptManager:
        """获取提示词管理器"""
        return self.prompt_manager
    
    def reload_prompts(self):
        """重新加载提示词"""
        self.prompt_manager.reload_prompts()
        logger.info("提示词已重新加载")
    
    def test_connection(self, config_name: str = "default") -> bool:
        """测试连接"""
        try:
            client = self.get_client(config_name)
            # 使用异步测试
            import asyncio
            
            async def test():
                return await client.test_connection()
            
            result = asyncio.run(test())
            logger.info(f"配置 {config_name} 连接测试{'成功' if result else '失败'}")
            return result
            
        except Exception as e:
            logger.error(f"配置 {config_name} 连接测试失败: {e}")
            return False
    
    def get_available_providers(self) -> Dict[str, Dict[str, Any]]:
        """获取可用的提供商信息"""
        available = {}
        
        for provider in LLMProvider:
            provider_name = provider.value
            api_key = self._detect_api_key(provider_name)
            base_url = self._detect_base_url(provider_name)
            
            available[provider_name] = {
                "has_api_key": api_key is not None,
                "base_url": base_url,
                "default_model": self._get_default_model(provider_name),
                "status": "可用" if api_key or provider_name == "ollama" else "需要API密钥"
            }
        
        return available
    
    def get_manager_info(self) -> Dict[str, Any]:
        """获取管理器信息"""
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


# 全局LLM管理器实例
llm_manager = LLMManager()