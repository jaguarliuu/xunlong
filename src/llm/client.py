"""LLM客户端实现 - 支持多种大模型提供商"""

import asyncio
import time
from typing import List, Dict, Any, Optional, AsyncGenerator, Union
from loguru import logger
import json

# 导入监控模块
try:
    from ..monitoring.langfuse_monitor import monitor
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False
    logger.warning("监控模块不可用")

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI库未安装，无法使用OpenAI相关功能")

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic库未安装，无法使用Claude相关功能")

from .config import LLMConfig, LLMProvider


class LLMClient:
    """统一的LLM客户端 - 支持多种大模型提供商"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self._client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """初始化客户端"""
        try:
            if self.config.provider == LLMProvider.OPENAI:
                self._initialize_openai()
            elif self.config.provider == LLMProvider.AZURE_OPENAI:
                self._initialize_azure_openai()
            elif self.config.provider == LLMProvider.ANTHROPIC:
                self._initialize_anthropic()
            elif self.config.provider in [
                LLMProvider.ZHIPU, 
                LLMProvider.QWEN, 
                LLMProvider.DEEPSEEK,
                LLMProvider.OLLAMA
            ]:
                self._initialize_openai_compatible()
            else:
                raise ValueError(f"不支持的LLM提供商: {self.config.provider}")
                
            logger.info(f"LLM客户端初始化成功: {self.config.provider} - {self.config.model_name}")
            
        except Exception as e:
            logger.error(f"LLM客户端初始化失败: {e}")
            raise
    
    def _initialize_openai(self):
        """初始化OpenAI客户端"""
        if not OPENAI_AVAILABLE:
            raise ImportError("请安装openai库: pip install openai")
        
        if not self.config.api_key:
            raise ValueError("OpenAI API密钥未设置")
        
        self._client = AsyncOpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            max_retries=self.config.max_retries
        )
    
    def _initialize_azure_openai(self):
        """初始化Azure OpenAI客户端"""
        if not OPENAI_AVAILABLE:
            raise ImportError("请安装openai库: pip install openai")
        
        if not self.config.api_key:
            raise ValueError("Azure OpenAI API密钥未设置")
        
        if not self.config.azure_deployment:
            raise ValueError("Azure部署名称未设置")
        
        # Azure OpenAI的URL格式
        azure_base_url = self.config.base_url
        if not azure_base_url.endswith('/'):
            azure_base_url += '/'
        
        self._client = AsyncOpenAI(
            api_key=self.config.api_key,
            base_url=f"{azure_base_url}openai/deployments/{self.config.azure_deployment}",
            api_version=self.config.azure_api_version,
            timeout=self.config.timeout,
            max_retries=self.config.max_retries
        )
    
    def _initialize_anthropic(self):
        """初始化Anthropic客户端"""
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("请安装anthropic库: pip install anthropic")
        
        if not self.config.api_key:
            raise ValueError("Anthropic API密钥未设置")
        
        self._client = anthropic.AsyncAnthropic(
            api_key=self.config.api_key,
            timeout=self.config.timeout,
            max_retries=self.config.max_retries
        )
    
    def _initialize_openai_compatible(self):
        """初始化OpenAI兼容的客户端（支持国产大模型和Ollama）"""
        if not OPENAI_AVAILABLE:
            raise ImportError("请安装openai库: pip install openai")
        
        # Ollama不需要API密钥，其他需要
        if self.config.provider == LLMProvider.OLLAMA:
            api_key = "ollama"  # Ollama使用占位符
        else:
            if not self.config.api_key:
                raise ValueError(f"{self.config.provider} API密钥未设置")
            api_key = self.config.api_key
        
        # 确保base_url正确设置
        base_url = self.config.base_url
        if not base_url:
            # 为不同提供商设置默认URL
            if self.config.provider == LLMProvider.ZHIPU:
                base_url = "https://open.bigmodel.cn/api/paas/v4"
            elif self.config.provider == LLMProvider.QWEN:
                base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
            elif self.config.provider == LLMProvider.DEEPSEEK:
                base_url = "https://api.deepseek.com/v1"
            elif self.config.provider == LLMProvider.OLLAMA:
                base_url = "http://localhost:11434/v1"
            else:
                raise ValueError(f"未设置 {self.config.provider} 的base_url")
        
        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=self.config.timeout,
            max_retries=self.config.max_retries
        )
        
        logger.info(f"初始化OpenAI兼容客户端: {self.config.provider} @ {base_url}")
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        trace_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """聊天补全"""
        start_time = time.time()
        
        try:
            # 合并参数
            params = {
                "model": self.config.model_name,
                "messages": messages,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
                "top_p": self.config.top_p,
                "stream": self.config.stream,
                **kwargs
            }
            
            if self.config.provider == LLMProvider.ANTHROPIC:
                result = await self._anthropic_chat_completion(messages, **kwargs)
            else:
                result = await self._openai_chat_completion(params)
            
            # 记录LLM调用到Langfuse
            if MONITORING_AVAILABLE and trace_id:
                execution_time = time.time() - start_time
                monitor.log_llm_call(
                    trace_id=trace_id,
                    model=self.config.model_name,
                    input_messages=messages,
                    output=result.get("content", ""),
                    usage=result.get("usage"),
                    metadata={
                        "provider": self.config.provider.value,
                        "execution_time": execution_time,
                        "temperature": self.config.temperature,
                        "max_tokens": self.config.max_tokens
                    }
                )
            
            return result
                
        except Exception as e:
            # 记录错误到Langfuse
            if MONITORING_AVAILABLE and trace_id:
                execution_time = time.time() - start_time
                monitor.log_llm_call(
                    trace_id=trace_id,
                    model=self.config.model_name,
                    input_messages=messages,
                    output="",
                    usage=None,
                    metadata={
                        "provider": self.config.provider.value,
                        "execution_time": execution_time,
                        "error": str(e),
                        "temperature": self.config.temperature,
                        "max_tokens": self.config.max_tokens
                    }
                )
            
            logger.error(f"聊天补全失败 ({self.config.provider}): {e}")
            # 提供更详细的错误信息
            if "api_key" in str(e).lower():
                raise ValueError(f"API密钥错误 ({self.config.provider}): 请检查API密钥是否正确设置")
            elif "model" in str(e).lower():
                raise ValueError(f"模型错误 ({self.config.provider}): 模型 {self.config.model_name} 可能不存在或无权限访问")
            elif "base_url" in str(e).lower() or "connection" in str(e).lower():
                raise ValueError(f"连接错误 ({self.config.provider}): 请检查base_url是否正确: {self.config.base_url}")
            else:
                raise

    async def get_structured_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_model: Any = None,
        trace_id: Optional[str] = None,
        **kwargs
    ):
        """
        获取结构化输出（使用Pydantic模型）

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            response_model: Pydantic模型类
            trace_id: 追踪ID
            **kwargs: 其他参数

        Returns:
            Pydantic模型实例
        """
        try:
            # 使用instructor包装客户端
            import instructor
            from pydantic import BaseModel

            # 包装客户端
            # 支持OpenAI兼容的provider都可以使用instructor
            openai_compatible_providers = [
                LLMProvider.OPENAI,
                LLMProvider.AZURE_OPENAI,
                LLMProvider.DEEPSEEK,
                LLMProvider.ZHIPU,
                LLMProvider.QWEN
            ]

            if self.config.provider in openai_compatible_providers:
                client = instructor.from_openai(self._client)
            else:
                # 对于不支持的provider，回退到JSON模式
                logger.warning(f"{self.config.provider} 不支持结构化输出，使用JSON回退方案")
                return await self._fallback_structured_response(prompt, system_prompt, response_model)

            # 构建消息
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            # 调用结构化输出
            response = await client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                response_model=response_model,
                temperature=kwargs.get("temperature", self.config.temperature),
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            )

            logger.info(f"结构化输出成功: {response_model.__name__}")
            return response

        except ImportError:
            logger.warning("instructor包未安装，使用JSON回退方案")
            return await self._fallback_structured_response(prompt, system_prompt, response_model)
        except Exception as e:
            logger.error(f"结构化输出失败: {e}")
            # 回退到JSON模式
            return await self._fallback_structured_response(prompt, system_prompt, response_model)

    async def _fallback_structured_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_model: Any = None
    ):
        """回退方案：使用JSON模式 + 手动解析"""
        import json
        from pydantic import BaseModel

        # 添加JSON schema到提示词
        if response_model and hasattr(response_model, 'model_json_schema'):
            schema = response_model.model_json_schema()
            enhanced_prompt = f"""{prompt}

请严格按照以下JSON Schema返回数据：
```json
{json.dumps(schema, indent=2, ensure_ascii=False)}
```

只返回JSON数据，不要有其他文字。"""
        else:
            enhanced_prompt = prompt

        # 构建消息
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": enhanced_prompt})

        # 调用chat_completion with JSON mode
        result = await self.chat_completion(
            messages=messages,
            response_format={"type": "json_object"}
        )

        # 解析JSON
        content = result.get("content", "")

        # 清理markdown代码块
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        # 解析为JSON
        data = json.loads(content)

        # 转换为Pydantic模型
        if response_model:
            return response_model(**data)
        return data

    async def _openai_chat_completion(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """OpenAI风格的聊天补全"""
        try:
            response = await self._client.chat.completions.create(**params)
            
            return {
                "content": response.choices[0].message.content,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0
                },
                "finish_reason": response.choices[0].finish_reason
            }
        except Exception as e:
            # 针对不同提供商的特殊错误处理
            if self.config.provider == LLMProvider.QWEN:
                if "InvalidApiKey" in str(e):
                    raise ValueError("通义千问API密钥无效，请检查DASHSCOPE_API_KEY环境变量")
                elif "ModelNotFound" in str(e):
                    raise ValueError(f"通义千问模型 {self.config.model_name} 不存在，请检查模型名称")
            elif self.config.provider == LLMProvider.ZHIPU:
                if "invalid_api_key" in str(e):
                    raise ValueError("智谱AI API密钥无效，请检查API密钥")
            elif self.config.provider == LLMProvider.DEEPSEEK:
                if "invalid_api_key" in str(e):
                    raise ValueError("DeepSeek API密钥无效，请检查API密钥")
            elif self.config.provider == LLMProvider.OLLAMA:
                if "Connection" in str(e):
                    raise ValueError("无法连接到Ollama服务，请确保Ollama正在运行 (ollama serve)")
            
            raise
    
    async def _anthropic_chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> Dict[str, Any]:
        """Anthropic风格的聊天补全"""
        # 转换消息格式
        system_message = None
        converted_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                converted_messages.append(msg)
        
        params = {
            "model": self.config.model_name,
            "messages": converted_messages,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            **kwargs
        }
        
        if system_message:
            params["system"] = system_message
        
        response = await self._client.messages.create(**params)
        
        return {
            "content": response.content[0].text,
            "model": response.model,
            "usage": {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            },
            "finish_reason": response.stop_reason
        }
    
    async def stream_chat_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """流式聊天补全"""
        try:
            params = {
                "model": self.config.model_name,
                "messages": messages,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
                "top_p": self.config.top_p,
                "stream": True,
                **kwargs
            }
            
            if self.config.provider == LLMProvider.ANTHROPIC:
                async for chunk in self._anthropic_stream_chat(messages, **kwargs):
                    yield chunk
            else:
                async for chunk in self._openai_stream_chat(params):
                    yield chunk
                    
        except Exception as e:
            logger.error(f"流式聊天补全失败: {e}")
            raise
    
    async def _openai_stream_chat(self, params: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """OpenAI风格的流式聊天"""
        stream = await self._client.chat.completions.create(**params)
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def _anthropic_stream_chat(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Anthropic风格的流式聊天"""
        # 转换消息格式
        system_message = None
        converted_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                converted_messages.append(msg)
        
        params = {
            "model": self.config.model_name,
            "messages": converted_messages,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "stream": True,
            **kwargs
        }
        
        if system_message:
            params["system"] = system_message
        
        stream = await self._client.messages.create(**params)
        
        async for chunk in stream:
            if chunk.type == "content_block_delta":
                yield chunk.delta.text
    
    async def simple_chat(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """简单聊天接口"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        response = await self.chat_completion(messages)
        return response["content"]
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "provider": self.config.provider,
            "model_name": self.config.model_name,
            "base_url": self.config.base_url,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }
    
    async def test_connection(self) -> bool:
        """测试连接"""
        try:
            response = await self.simple_chat(
                "Hello", 
                "You are a helpful assistant. Please respond with 'OK' only."
            )
            return len(response.strip()) > 0
        except Exception as e:
            logger.error(f"连接测试失败 ({self.config.provider}): {e}")
            return False