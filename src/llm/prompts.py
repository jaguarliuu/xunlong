"""TODO: Add docstring."""

import os
import json
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path
from loguru import logger
from jinja2 import Template, Environment, FileSystemLoader


class PromptManager:
    """TODO: Add docstring."""
    
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
        """TODO: Add docstring."""
        if not self.prompts_dir.exists():
            logger.warning(f": {self.prompts_dir}")
            return
        
        # 
        supported_extensions = ['.json', '.yaml', '.yml', '.txt', '.md']
        
        for file_path in self.prompts_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                try:
                    self._load_prompt_file(file_path)
                except Exception as e:
                    logger.error(f" {file_path}: {e}")
        
        logger.info(f" {len(self.prompts_cache)} ")
    
    def _load_prompt_file(self, file_path: Path):
        """TODO: Add docstring."""
        # key
        relative_path = file_path.relative_to(self.prompts_dir)
        key = relative_path.with_suffix('').as_posix()  # 
        
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
        logger.debug(f": {key}")
    
    def get_prompt(self, key: str, **kwargs) -> str:
        """TODO: Add docstring."""
        if key not in self.prompts_cache:
            raise KeyError(f": {key}")
        
        prompt_data = self.prompts_cache[key]
        
        # 
        if isinstance(prompt_data, str):
            template = Template(prompt_data)
            return template.render(**kwargs)
        
        # content
        content = prompt_data.get("content", "")
        if not content:
            raise ValueError(f": {key}")
        
        # Jinja2
        template = Template(content)
        return template.render(**kwargs)
    
    def get_prompt_metadata(self, key: str) -> Dict[str, Any]:
        """TODO: Add docstring."""
        if key not in self.prompts_cache:
            raise KeyError(f": {key}")
        
        prompt_data = self.prompts_cache[key]
        
        if isinstance(prompt_data, dict):
            # content
            metadata = {k: v for k, v in prompt_data.items() if k != "content"}
            return metadata
        
        return {}
    
    def list_prompts(self) -> List[str]:
        """TODO: Add docstring."""
        return list(self.prompts_cache.keys())
    
    def reload_prompts(self):
        """TODO: Add docstring."""
        self.prompts_cache.clear()
        self._load_all_prompts()
    
    def add_prompt(self, key: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """TODO: Add docstring."""
        prompt_data = {"content": content}
        if metadata:
            prompt_data.update(metadata)
        
        self.prompts_cache[key] = prompt_data
        logger.info(f": {key}")
    
    def render_template_file(self, template_name: str, **kwargs) -> str:
        """TODO: Add docstring."""
        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(**kwargs)
        except Exception as e:
            logger.error(f" {template_name}: {e}")
            raise
    
    def get_system_prompt(self, agent_name: str, **kwargs) -> str:
        """TODO: Add docstring."""
        key = f"agents/{agent_name}/system"
        return self.get_prompt(key, **kwargs)
    
    def get_task_prompt(self, task_name: str, **kwargs) -> str:
        """TODO: Add docstring."""
        key = f"tasks/{task_name}"
        return self.get_prompt(key, **kwargs)
    
    def get_tool_prompt(self, tool_name: str, **kwargs) -> str:
        """TODO: Add docstring."""
        key = f"tools/{tool_name}"
        return self.get_prompt(key, **kwargs)


# 
prompt_manager = PromptManager()