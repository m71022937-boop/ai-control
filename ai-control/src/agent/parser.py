"""
Intent Parser - Parses "Use X to do Y" requests
"""

import re
from dataclasses import dataclass
from typing import Optional
from src.ai.model_router import ModelRouter
from src.utils.logger import logger


@dataclass
class Intent:
    """Parsed user intent"""
    raw: str
    app: Optional[str] = None
    task: Optional[str] = None
    params: dict = None
    
    def __post_init__(self):
        if self.params is None:
            self.params = {}


class IntentParser:
    """Parses natural language intents"""
    
    # Known apps and their aliases
    APPS = {
        # Trading
        'mt4': ['mt4', 'metatrader', 'meta trader', 'metatrader 4'],
        'mt5': ['mt5', 'metatrader 5', 'meta trader 5'],
        # Browsers
        'chrome': ['chrome', 'google chrome', 'browser', 'web browser'],
        'firefox': ['firefox', 'mozilla'],
        # Editors
        'vscode': ['vscode', 'vs code', 'visual studio code', 'code'],
        'vim': ['vim', 'vi'],
        'nano': ['nano'],
        # Terminal/Shells
        'terminal': ['terminal', 'bash', 'shell', 'cmd', 'command line', 'console'],
        'files': ['files', 'file manager', 'nautilus', 'dolphin', 'explorer', 'file'],
        # Office
        'excel': ['excel', 'spreadsheet', 'ms excel'],
        'word': ['word', 'ms word'],
        # Communication
        'telegram': ['telegram', 'telegram app'],
        'discord': ['discord'],
        # Media
        'spotify': ['spotify', 'spotify app'],
        'vlc': ['vlc', 'vlc player'],
        # System/Dev
        'system': ['system', 'os', 'operating system'],
        'git': ['git', 'github'],
        'docker': ['docker', 'container'],
        'python': ['python', 'python3'],
        'node': ['node', 'nodejs', 'npm'],
    }
    
    def __init__(self, model_router: ModelRouter):
        self.model_router = model_router
        logger.info("Intent Parser initialized")
    
    def parse(self, user_input: str) -> Intent:
        """Parse user input into intent"""
        intent = Intent(raw=user_input)
        
        # Try to detect app first
        intent.app = self._detect_app(user_input)
        
        # Extract task (remove "use X to" pattern)
        intent.task = self._extract_task(user_input, intent.app)
        
        # Extract parameters
        intent.params = self._extract_params(user_input, intent.app)
        
        logger.debug(f"Parsed intent: app={intent.app}, task={intent.task}")
        
        return intent
    
    def _detect_app(self, text: str) -> Optional[str]:
        """Detect which app the user wants to use"""
        text_lower = text.lower()
        
        for app, aliases in self.APPS.items():
            for alias in aliases:
                if alias in text_lower:
                    return app
        
        return None
    
    def _extract_task(self, text: str, app: str) -> str:
        """Extract the task from user input"""
        text_lower = text.lower()
        
        # Pattern: "Use [app] to [task]"
        patterns = [
            r'use\s+.*?\s+to\s+(.+)',
            r'open\s+.*?\s+and\s+(.+)',
            r'start\s+.*?\s+then\s+(.+)',
            r'with\s+.*?\s+(.+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                task = match.group(1).strip()
                # Clean up the task
                task = re.sub(r'^the\s+', '', task)
                return task
        
        # If no pattern matched, return cleaned version
        if app:
            # Remove app name and "use" from beginning
            task = re.sub(rf'use\s+{app}(\s+.*?)?', '', text_lower, flags=re.IGNORECASE)
            task = re.sub(rf'^{app}(\s+.*?)?', '', task)
            task = task.strip()
            # Remove leading "to", "and", "then"
            task = re.sub(r'^(to|and|then)\s+', '', task)
            return task
        
        return text.strip()
    
    def _extract_params(self, text: str, app: str) -> dict:
        """Extract parameters from user input"""
        params = {}
        text_lower = text.lower()
        
        # Common patterns
        # File names
        file_pattern = r'(?:called?|named?|create|file)\s+[\'"]?([^\'"]+)[\'"]?'
        file_match = re.search(file_pattern, text_lower)
        if file_match:
            params['filename'] = file_match.group(1)
        
        # URLs
        url_pattern = r'(?:open|go to|visit)\s+(https?://[^\s]+)'
        url_match = re.search(url_pattern, text_lower)
        if url_match:
            params['url'] = url_match.group(1)
        
        # Numbers (lots, prices, etc.)
        number_pattern = r'(\d+\.?\d*)\s*(lots?|lots)'
        number_match = re.search(number_pattern, text_lower)
        if number_match:
            params['lots'] = float(number_match.group(1))
        
        # Search queries
        if app == 'chrome':
            search_pattern = r'search\s+(?:for\s+)?[\'"]?([^\'"]+)[\'"]?'
            search_match = re.search(search_pattern, text_lower)
            if search_match:
                params['query'] = search_match.group(1)
        
        return params


# Simple pattern-based parser (no AI needed for basic intents)
class SimpleIntentParser(IntentParser):
    """Fast pattern-based parser without AI"""
    
    def __init__(self):
        super().__init__(None)
        logger.info("Simple Intent Parser initialized")
    
    def parse(self, user_input: str) -> Intent:
        """Parse using simple patterns (no AI)"""
        return super().parse(user_input)
