"""
AI Model Router - Routes requests to appropriate AI model
"""

from typing import Optional
from src.utils.config import Config
from src.utils.logger import logger


class ModelRouter:
    """Routes AI requests to appropriate model"""
    
    def __init__(self, config: Config):
        self.config = config
        self.provider = config.get('ai.provider', 'ollama')
        self.model = config.get('ai.model', 'llama3')
        self.ollama_url = config.get('ai.ollama_url', 'http://localhost:11434')
        self.openrouter_key = config.get('ai.openrouter_key', '')
        
        logger.info(f"Model Router initialized: provider={self.provider}, model={self.model}")
    
    def complete(self, prompt: str) -> str:
        """Complete a prompt using the configured model"""
        
        if self.provider == 'ollama':
            return self._ollama_complete(prompt)
        elif self.provider == 'openrouter':
            return self._openrouter_complete(prompt)
        elif self.provider == 'anthropic':
            return self._anthropic_complete(prompt)
        else:
            return self._fallback_complete(prompt)
    
    def _ollama_complete(self, prompt: str) -> str:
        """Complete using local Ollama"""
        try:
            import requests
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', '')
            else:
                logger.error(f"Ollama error: {response.status_code}")
                return f"Error: Ollama returned {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return "Error: Ollama not running. Start with: `ollama serve`"
        except Exception as e:
            return f"Error: {e}"
    
    def _openrouter_complete(self, prompt: str) -> str:
        """Complete using OpenRouter API"""
        try:
            import requests
            
            if not self.openrouter_key:
                return "Error: OpenRouter API key not configured"
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openrouter_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content']
            else:
                logger.error(f"OpenRouter error: {response.status_code}")
                return f"Error: OpenRouter returned {response.status_code}"
                
        except Exception as e:
            return f"Error: {e}"
    
    def _anthropic_complete(self, prompt: str) -> str:
        """Complete using Anthropic API"""
        # Placeholder - implement similar to OpenRouter
        return "Error: Anthropic not implemented yet"
    
    def _fallback_complete(self, prompt: str) -> str:
        """Fallback simple response"""
        return "AI model not configured. Please set up Ollama or OpenRouter."
    
    def list_models(self) -> list:
        """List available models"""
        if self.provider == 'ollama':
            try:
                import requests
                response = requests.get(f"{self.ollama_url}/api/tags", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    return [m['name'] for m in data.get('models', [])]
            except:
                pass
        
        return [self.model]