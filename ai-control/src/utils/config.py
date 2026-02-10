"""
Config Management
"""

import os
import yaml
from typing import Any, Dict, Optional
from src.utils.logger import logger


class Config:
    """Configuration management"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.path.expanduser('~/.ai-control/config.yaml')
        self.data = self._load_config()
        logger.info(f"Config loaded from {self.config_path}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        defaults = {
            'app': {
                'name': 'AI Control',
                'version': '1.0.0',
            },
            'telegram': {
                'enabled': False,
                'token': '',
                'chat_id': '',
            },
            'ai': {
                'provider': 'ollama',  # ollama, openrouter, anthropic
                'model': 'llama3',
                'ollama_url': 'http://localhost:11434',
                'openrouter_key': '',
            },
            'automation': {
                'default_browser': 'chrome',
                'screenshot_path': '/tmp/ai-control',
                'confirm_destructive': True,
            },
            'safety': {
                'max_task_duration': 300,  # 5 minutes
                'max_daily_runtime': 36000,  # 10 hours
                'allow_shutdown': False,
            }
        }
        
        # Try to load from file
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    user_config = yaml.safe_load(f) or {}
                # Merge with defaults
                defaults.update(user_config)
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
        
        # Create config directory if not exists
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        return defaults
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a config value using dot notation"""
        keys = key.split('.')
        value = self.data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set a config value"""
        keys = key.split('.')
        current = self.data
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
        self._save_config()
    
    def _save_config(self) -> None:
        """Save config to file"""
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(self.data, f, default_flow_style=False)
            logger.debug("Config saved")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    @property
    def telegram_token(self) -> str:
        """Get Telegram bot token"""
        return self.get('telegram.token', '')
    
    @property
    def telegram_enabled(self) -> bool:
        """Check if Telegram is enabled"""
        return self.get('telegram.enabled', False) and bool(self.telegram_token)
    
    @property
    def ollama_url(self) -> str:
        """Get Ollama URL"""
        return self.get('ai.ollama_url', 'http://localhost:11434')
    
    @property
    def openrouter_key(self) -> str:
        """Get OpenRouter API key"""
        return self.get('ai.openrouter_key', '')
