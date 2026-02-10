"""
AI Model Router - Routes requests to appropriate AI model
"""

from typing import Optional
from src.utils.config import Config
from src.utils.logger import get_logger

logger = get_logger()


class ModelRouter:
    """Routes AI requests to appropriate model with proper error handling"""
    
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
        """Complete using local Ollama with proper error handling"""
        import requests
        import socket
        
        # First check if Ollama is reachable
        try:
            socket.setdefaulttimeout(5)
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code != 200:
                raise RuntimeError("Ollama server not responding properly")
        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                "❌ Ollama server not running!\n\n"
                "To start Ollama:\n"
                "  1. Install: curl -fsSL https://ollama.ai/install.sh | sh\n"
                "  2. Start: ollama serve\n"
                "  3. Pull model: ollama pull llama3\n\n"
                "Or switch to cloud AI in config.yaml"
            )
        except requests.exceptions.Timeout:
            raise RuntimeError("Ollama server timeout - check if running on port 11434")
        
        # Make the request with timeout
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": 1024,
                        "temperature": 0.7,
                    }
                },
                timeout=60  # 60 second timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', '')
            elif response.status_code == 404:
                raise RuntimeError(
                    f"Model '{self.model}' not found!\n\n"
                    "To download: ollama pull {self.model}"
                )
            else:
                logger.error(f"Ollama error: {response.status_code} - {response.text}")
                raise RuntimeError(f"Ollama returned error: {response.status_code}")
                
        except requests.exceptions.Timeout:
            raise RuntimeError("Ollama request timed out after 60 seconds")
        except Exception as e:
            logger.error(f"Ollama request failed: {e}")
            raise RuntimeError(f"Ollama error: {e}")
    
    def _openrouter_complete(self, prompt: str) -> str:
        """Complete using OpenRouter API"""
        import requests
        
        if not self.openrouter_key:
            raise RuntimeError(
                "❌ OpenRouter API key not set!\n\n"
                "Get a key at: https://openrouter.ai/account\n"
                "Then set it in config.yaml: ai.openrouter_key"
            )
        
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openrouter_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/m71022937-boop/ai-control",
                    "X-Title": "AI Control"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 1024,
                    "temperature": 0.7,
                },
                timeout=60
            )
            
            if response.status_code == 401:
                raise RuntimeError("❌ Invalid OpenRouter API key")
            elif response.status_code == 402:
                raise RuntimeError("❌ OpenRouter credits insufficient. Add credits at openrouter.ai/account")
            elif response.status_code == 429:
                raise RuntimeError("❌ OpenRouter rate limit. Try again in a moment.")
            elif response.status_code != 200:
                logger.error(f"OpenRouter error: {response.status_code} - {response.text}")
                raise RuntimeError(f"OpenRouter error: {response.status_code}")
            
            data = response.json()
            if 'choices' not in data or not data['choices']:
                raise RuntimeError("Empty response from OpenRouter")
            
            return data['choices'][0]['message']['content']
            
        except requests.exceptions.Timeout:
            raise RuntimeError("OpenRouter request timed out")
        except Exception as e:
            if "credits" in str(e).lower() or "key" in str(e).lower():
                raise
            logger.error(f"OpenRouter request failed: {e}")
            raise RuntimeError(f"OpenRouter error: {e}")
    
    def _anthropic_complete(self, prompt: str) -> str:
        """Complete using Anthropic API"""
        raise RuntimeError(
            "❌ Anthropic not fully implemented yet.\n\n"
            "Use OpenRouter or Ollama instead."
        )
    
    def _fallback_complete(self, prompt: str) -> str:
        """Fallback simple response"""
        return "AI model not configured. Set provider in config.yaml (ollama, openrouter, anthropic)"
    
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
    
    def test_connection(self) -> dict:
        """Test model connection and return status"""
        result = {
            'provider': self.provider,
            'model': self.model,
            'status': 'unknown',
            'message': ''
        }
        
        if self.provider == 'ollama':
            try:
                import requests
                response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    models = [m['name'] for m in data.get('models', [])]
                    result['status'] = 'connected'
                    result['message'] = f"Ollama running. Models: {', '.join(models)}"
                    result['available_models'] = models
                else:
                    result['status'] = 'error'
                    result['message'] = f"Ollama returned {response.status_code}"
            except Exception as e:
                result['status'] = 'disconnected'
                result['message'] = str(e)
        elif self.provider == 'openrouter':
            if not self.openrouter_key:
                result['status'] = 'error'
                result['message'] = "API key not set"
            else:
                result['status'] = 'configured'
                result['message'] = f"OpenRouter configured for model: {self.model}"
        
        return result