"""LLM - """

import asyncio
import time
from typing import List, Dict, Any, Optional, AsyncGenerator, Union
from loguru import logger
import json

# 
try:
    from ..monitoring.langfuse_monitor import monitor
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False
    logger.warning("")

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAIOpenAI")

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("AnthropicClaude")

from .config import LLMConfig, LLMProvider


class LLMClient:
    """LLM - """
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self._client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """"""
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
                raise ValueError(f"LLM: {self.config.provider}")
                
            logger.info(f"LLM: {self.config.provider} - {self.config.model_name}")
            
        except Exception as e:
            logger.error(f"LLM: {e}")
            raise
    
    def _initialize_openai(self):
        """OpenAI"""
        if not OPENAI_AVAILABLE:
            raise ImportError("openai: pip install openai")
        
        if not self.config.api_key:
            raise ValueError("OpenAI API")
        
        self._client = AsyncOpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            max_retries=self.config.max_retries
        )
    
    def _initialize_azure_openai(self):
        """Azure OpenAI"""
        if not OPENAI_AVAILABLE:
            raise ImportError("openai: pip install openai")
        
        if not self.config.api_key:
            raise ValueError("Azure OpenAI API")
        
        if not self.config.azure_deployment:
            raise ValueError("Azure")
        
        # Azure OpenAIURL
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
        """Anthropic"""
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic: pip install anthropic")
        
        if not self.config.api_key:
            raise ValueError("Anthropic API")
        
        self._client = anthropic.AsyncAnthropic(
            api_key=self.config.api_key,
            timeout=self.config.timeout,
            max_retries=self.config.max_retries
        )
    
    def _initialize_openai_compatible(self):
        """OpenAIOllama"""
        if not OPENAI_AVAILABLE:
            raise ImportError("openai: pip install openai")
        
        # OllamaAPI
        if self.config.provider == LLMProvider.OLLAMA:
            api_key = "ollama"  # Ollama
        else:
            if not self.config.api_key:
                raise ValueError(f"{self.config.provider} API")
            api_key = self.config.api_key
        
        # base_url
        base_url = self.config.base_url
        if not base_url:
            # URL
            if self.config.provider == LLMProvider.ZHIPU:
                base_url = "https://open.bigmodel.cn/api/paas/v4"
            elif self.config.provider == LLMProvider.QWEN:
                base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
            elif self.config.provider == LLMProvider.DEEPSEEK:
                base_url = "https://api.deepseek.com/v1"
            elif self.config.provider == LLMProvider.OLLAMA:
                base_url = "http://localhost:11434/v1"
            else:
                raise ValueError(f" {self.config.provider} base_url")
        
        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=self.config.timeout,
            max_retries=self.config.max_retries
        )
        
        logger.info(f"OpenAI: {self.config.provider} @ {base_url}")
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        trace_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """"""
        start_time = time.time()
        
        try:
            # 
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
            
            # LLMLangfuse
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
            # Langfuse
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
            
            logger.error(f" ({self.config.provider}): {e}")
            # 
            if "api_key" in str(e).lower():
                raise ValueError(f"API ({self.config.provider}): API")
            elif "model" in str(e).lower():
                raise ValueError(f" ({self.config.provider}):  {self.config.model_name} ")
            elif "base_url" in str(e).lower() or "connection" in str(e).lower():
                raise ValueError(f" ({self.config.provider}): base_url: {self.config.base_url}")
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
        Pydantic

        Args:
            prompt: 
            system_prompt: 
            response_model: Pydantic
            trace_id: ID
            **kwargs: 

        Returns:
            Pydantic
        """
        try:
            # instructor
            import instructor
            from pydantic import BaseModel

            # 
            # OpenAIproviderinstructor
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
                # providerJSON
                logger.warning(f"{self.config.provider} JSON")
                return await self._fallback_structured_response(prompt, system_prompt, response_model)

            # 
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            # 
            response = await client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                response_model=response_model,
                temperature=kwargs.get("temperature", self.config.temperature),
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            )

            logger.info(f": {response_model.__name__}")
            return response

        except ImportError:
            logger.warning("instructorJSON")
            return await self._fallback_structured_response(prompt, system_prompt, response_model)
        except Exception as e:
            logger.error(f": {e}")
            # JSON
            return await self._fallback_structured_response(prompt, system_prompt, response_model)

    async def _fallback_structured_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_model: Any = None
    ):
        """JSON + """
        import json
        from pydantic import BaseModel

        # JSON schema
        if response_model and hasattr(response_model, 'model_json_schema'):
            schema = response_model.model_json_schema()
            enhanced_prompt = f"""{prompt}

JSON Schema
```json
{json.dumps(schema, indent=2, ensure_ascii=False)}
```

JSON"""
        else:
            enhanced_prompt = prompt

        # 
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": enhanced_prompt})

        # chat_completion with JSON mode
        result = await self.chat_completion(
            messages=messages,
            response_format={"type": "json_object"}
        )

        # JSON
        content = result.get("content", "")

        # markdown
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        # JSON
        data = json.loads(content)

        # Pydantic
        if response_model:
            return response_model(**data)
        return data

    async def _openai_chat_completion(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """OpenAI"""
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
            # 
            if self.config.provider == LLMProvider.QWEN:
                if "InvalidApiKey" in str(e):
                    raise ValueError("APIDASHSCOPE_API_KEY")
                elif "ModelNotFound" in str(e):
                    raise ValueError(f" {self.config.model_name} ")
            elif self.config.provider == LLMProvider.ZHIPU:
                if "invalid_api_key" in str(e):
                    raise ValueError("AI APIAPI")
            elif self.config.provider == LLMProvider.DEEPSEEK:
                if "invalid_api_key" in str(e):
                    raise ValueError("DeepSeek APIAPI")
            elif self.config.provider == LLMProvider.OLLAMA:
                if "Connection" in str(e):
                    raise ValueError("OllamaOllama (ollama serve)")
            
            raise
    
    async def _anthropic_chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> Dict[str, Any]:
        """Anthropic"""
        # 
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
        """"""
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
            logger.error(f": {e}")
            raise
    
    async def _openai_stream_chat(self, params: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """OpenAI"""
        stream = await self._client.chat.completions.create(**params)
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def _anthropic_stream_chat(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Anthropic"""
        # 
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
        """"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        response = await self.chat_completion(messages)
        return response["content"]
    
    def get_model_info(self) -> Dict[str, Any]:
        """"""
        return {
            "provider": self.config.provider,
            "model_name": self.config.model_name,
            "base_url": self.config.base_url,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }
    
    async def test_connection(self) -> bool:
        """"""
        try:
            response = await self.simple_chat(
                "Hello", 
                "You are a helpful assistant. Please respond with 'OK' only."
            )
            return len(response.strip()) > 0
        except Exception as e:
            logger.error(f" ({self.config.provider}): {e}")
            return False