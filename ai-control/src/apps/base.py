"""
App Controller Base Class
"""

from abc import ABC, abstractmethod
from typing import Optional
from src.utils.config import Config
from src.utils.logger import logger


class AppController(ABC):
    """Base class for all app controllers"""
    
    def __init__(self, config: Config):
        self.config = config
        self.app_name = "Unknown"
        logger.info(f"App Controller initialized: {self.app_name}")
    
    @abstractmethod
    def open(self) -> str:
        """Open the application"""
        pass
    
    def close(self) -> str:
        """Close the application (default implementation)"""
        return f"{self.app_name} closed"
    
    def click(self, x: int, y: int) -> str:
        """Click at coordinates"""
        try:
            import pyautogui
            pyautogui.click(x, y)
            return f"Clicked at ({x}, {y})"
        except Exception as e:
            return f"Click failed: {e}"
    
    def type_text(self, text: str) -> str:
        """Type text"""
        try:
            import pyautogui
            pyautogui.write(text)
            return f"Typed: {text[:20]}..."
        except Exception as e:
            return f"Type failed: {e}"
    
    def press_key(self, key: str) -> str:
        """Press a key"""
        try:
            import pyautogui
            pyautogui.press(key)
            return f"Pressed: {key}"
        except Exception as e:
            return f"Key press failed: {e}"
    
    def wait(self, seconds: float = 1.0) -> str:
        """Wait for specified seconds"""
        import time
        time.sleep(seconds)
        return f"Waited {seconds}s"
    
    def screenshot(self) -> str:
        """Take a screenshot"""
        try:
            import pyautogui
            import time
            timestamp = int(time.time())
            path = f"/tmp/screenshot_{timestamp}.png"
            pyautogui.screenshot(path)
            return f"Screenshot saved: {path}"
        except Exception as e:
            return f"Screenshot failed: {e}"
    
    def run_command(self, command: str) -> str:
        """Run a shell command"""
        import subprocess
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.stdout or result.stderr
        except Exception as e:
            return f"Command failed: {e}"
    
    def navigate_url(self, url: str) -> str:
        """Navigate to URL (for browsers)"""
        return f"Navigate to: {url}"
    
    def create_file(self, filename: str, content: str = "") -> str:
        """Create a file"""
        try:
            import os
            with open(filename, 'w') as f:
                f.write(content)
            return f"Created: {filename}"
        except Exception as e:
            return f"Create failed: {e}"
    
    def edit_file(self, filename: str, content: str = "") -> str:
        """Edit a file"""
        return self.create_file(filename, content)
    
    def organize_folder(self, path: str) -> str:
        """Organize folder"""
        return f"Organize: {path}"
