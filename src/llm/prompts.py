"""提示词管理系统"""

import os
import json
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path
from loguru import logger
from jinja2 import Template, Environment, FileSystemLoader


class PromptManager:
    """提示词管理器"""
    
    def __init__(self, prompts_dir: str = "prompts"):
        self.prompts_dir = Path(prompts_dir)
        self.prompts_cache: Dict[str, Dict[str, Any]] = {}
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.prompts_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        self._load_all_prompts()
    
    def _load_all_prompts(self):
        """加载所有提示词文件"""
        if not self.prompts_dir.exists():
            logger.warning(f"提示词目录不存在: {self.prompts_dir}")
            return
        
        # 支持的文件格式
        supported_extensions = ['.json', '.yaml', '.yml', '.txt', '.md']
        
        for file_path in self.prompts_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                try:
                    self._load_prompt_file(file_path)
                except Exception as e:
                    logger.error(f"加载提示词文件失败 {file_path}: {e}")
        
        logger.info(f"已加载 {len(self.prompts_cache)} 个提示词文件")
    
    def _load_prompt_file(self, file_path: Path):
        """加载单个提示词文件"""
        # 生成相对路径作为key
        relative_path = file_path.relative_to(self.prompts_dir)
        key = str(relative_path.with_suffix(''))  # 去掉扩展名
        
        if file_path.suffix.lower() == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        elif file_path.suffix.lower() in ['.yaml', '.yml']:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        else:  # .txt, .md
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                data = {"content": content}
        
        self.prompts_cache[key] = data
        logger.debug(f"已加载提示词: {key}")
    
    def get_prompt(self, key: str, **kwargs) -> str:
        """获取提示词内容"""
        if key not in self.prompts_cache:
            raise KeyError(f"提示词不存在: {key}")
        
        prompt_data = self.prompts_cache[key]
        
        # 如果是简单字符串格式
        if isinstance(prompt_data, str):
            template = Template(prompt_data)
            return template.render(**kwargs)
        
        # 如果是字典格式，获取content字段
        content = prompt_data.get("content", "")
        if not content:
            raise ValueError(f"提示词内容为空: {key}")
        
        # 使用Jinja2模板渲染
        template = Template(content)
        return template.render(**kwargs)
    
    def get_prompt_metadata(self, key: str) -> Dict[str, Any]:
        """获取提示词元数据"""
        if key not in self.prompts_cache:
            raise KeyError(f"提示词不存在: {key}")
        
        prompt_data = self.prompts_cache[key]
        
        if isinstance(prompt_data, dict):
            # 返回除content外的所有字段
            metadata = {k: v for k, v in prompt_data.items() if k != "content"}
            return metadata
        
        return {}
    
    def list_prompts(self) -> List[str]:
        """列出所有可用的提示词"""
        return list(self.prompts_cache.keys())
    
    def reload_prompts(self):
        """重新加载所有提示词"""
        self.prompts_cache.clear()
        self._load_all_prompts()
    
    def add_prompt(self, key: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """动态添加提示词"""
        prompt_data = {"content": content}
        if metadata:
            prompt_data.update(metadata)
        
        self.prompts_cache[key] = prompt_data
        logger.info(f"已添加提示词: {key}")
    
    def render_template_file(self, template_name: str, **kwargs) -> str:
        """直接渲染模板文件"""
        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(**kwargs)
        except Exception as e:
            logger.error(f"渲染模板文件失败 {template_name}: {e}")
            raise
    
    def get_system_prompt(self, agent_name: str, **kwargs) -> str:
        """获取智能体系统提示词"""
        key = f"agents/{agent_name}/system"
        return self.get_prompt(key, **kwargs)
    
    def get_task_prompt(self, task_name: str, **kwargs) -> str:
        """获取任务提示词"""
        key = f"tasks/{task_name}"
        return self.get_prompt(key, **kwargs)
    
    def get_tool_prompt(self, tool_name: str, **kwargs) -> str:
        """获取工具使用提示词"""
        key = f"tools/{tool_name}"
        return self.get_prompt(key, **kwargs)


# 全局提示词管理器实例
prompt_manager = PromptManager()