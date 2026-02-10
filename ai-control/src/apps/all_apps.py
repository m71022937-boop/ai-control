"""
App Controllers - Support for all applications
"""

import subprocess
import os
from src.apps.base import AppController
from src.utils.logger import get_logger
logger = get_logger()


class MT4Controller(AppController):
    """Controls MetaTrader 4"""
    
    def __init__(self, config):
        super().__init__(config)
        self.app_name = "MetaTrader 4"
    
    def open(self) -> str:
        """Open MT4"""
        # Try common MT4 locations
        commands = [
            'wine ~/.wine/drive_c/Program\\ Files/MetaTrader4/terminal.exe 2>/dev/null',
            '/opt/mt4/terminal.exe 2>/dev/null',
            'metatrader4 2>/dev/null',
        ]
        for cmd in commands:
            try:
                subprocess.Popen(cmd, shell=True)
                return "MT4 opening..."
            except:
                continue
        return "MT4 not found. Install or add to PATH."
    
    def run_command(self, command: str) -> str:
        """Run MT4-related command"""
        return f"MT4 command: {command}"
    
    def check_balance(self) -> str:
        """Check account balance"""
        return "Run 'terminal' with: tail -50 ~/.wine/drive_c/Program\\ Files/MetaTrader4/Tester/Experts/logs.log"


class ChromeController(AppController):
    """Controls Google Chrome"""
    
    def __init__(self, config):
        super().__init__(config)
        self.app_name = "Chrome"
    
    def open(self) -> str:
        """Open Chrome"""
        subprocess.Popen(['google-chrome', '--new-window'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return "Chrome opened"
    
    def navigate_url(self, url: str) -> str:
        """Navigate to URL"""
        subprocess.run(['xdotool', 'key', 'Ctrl+l'], timeout=2)
        subprocess.run(['xdotool', 'type', url], timeout=2)
        subprocess.run(['xdotool', 'key', 'Return'], timeout=2)
        return f"Navigated to {url}"
    
    def search(self, query: str) -> str:
        """Search Google"""
        subprocess.run(['xdotool', 'key', 'Ctrl+l'], timeout=2)
        subprocess.run(['xdotool', 'type', f'https://www.google.com/search?q={query}'], timeout=5)
        subprocess.run(['xdotool', 'key', 'Return'], timeout=2)
        return f"Searching for: {query}"


class VSCodeController(AppController):
    """Controls VS Code"""
    
    def __init__(self, config):
        super().__init__(config)
        self.app_name = "VS Code"
    
    def open(self) -> str:
        """Open VS Code"""
        subprocess.Popen(['code'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return "VS Code opened"
    
    def create_file(self, filename: str, content: str = "") -> str:
        """Create file in VS Code"""
        # Create via command line
        path = os.path.expanduser(filename)
        with open(path, 'w') as f:
            f.write(content)
        subprocess.Popen(['code', path])
        return f"Created: {filename}"
    
    def run_command(self, command: str) -> str:
        """Run command in VS Code terminal"""
        return f"VS Code command: {command}"


class ExcelController(AppController):
    """Controls Excel/Spreadsheets"""
    
    def __init__(self, config):
        super().__init__(config)
        self.app_name = "Excel"
    
    def open(self) -> str:
        """Open Excel"""
        try:
            subprocess.Popen(['libreoffice', '--calc'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return "Excel (LibreOffice) opened"
        except:
            subprocess.Popen(['excel'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return "Excel opened"
    
    def create_spreadsheet(self, filename: str, content: str = "") -> str:
        """Create spreadsheet"""
        path = os.path.expanduser(filename)
        with open(path, 'w') as f:
            f.write(content)
        return f"Spreadsheet created: {filename}"
    
    def import_csv(self, filename: str) -> str:
        """Import CSV"""
        return f"Importing CSV: {filename}"


class TelegramController(AppController):
    """Controls Telegram"""
    
    def __init__(self, config):
        super().__init__(config)
        self.app_name = "Telegram"
    
    def open(self) -> str:
        """Open Telegram"""
        subprocess.Popen(['telegram-desktop'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return "Telegram opened"
    
    def send_message(self, chat: str, message: str) -> str:
        """Send message"""
        return "Use /use telegram in AI Control for bot commands"
    
    def check_messages(self) -> str:
        """Check messages"""
        return "Open Telegram desktop app to check messages"


class SpotifyController(AppController):
    """Controls Spotify"""
    
    def __init__(self, config):
        super().__init__(config)
        self.app_name = "Spotify"
    
    def open(self) -> str:
        """Open Spotify"""
        subprocess.Popen(['spotify'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return "Spotify opened"
    
    def play_music(self, track: str) -> str:
        """Play music"""
        return f"Playing: {track}"


class VLCController(AppController):
    """Controls VLC Media Player"""
    
    def __init__(self, config):
        super().__init__(config)
        self.app_name = "VLC"
    
    def open(self) -> str:
        """Open VLC"""
        subprocess.Popen(['vlc'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return "VLC opened"
    
    def play_video(self, filename: str) -> str:
        """Play video"""
        subprocess.Popen(['vlc', filename])
        return f"Playing: {filename}"


class SystemController(AppController):
    """Controls system operations"""
    
    def __init__(self, config):
        super().__init__(config)
        self.app_name = "System"
    
    def open(self) -> str:
        """System info"""
        return "System operations available"
    
    def get_info(self) -> str:
        """Get system info"""
        try:
            result = subprocess.run(['uname', '-a'], capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "System info unavailable"
    
    def check_processes(self) -> str:
        """Check running processes"""
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        return result.stdout.strip()
    
    def check_memory(self) -> str:
        """Check memory usage"""
        result = subprocess.run(['free', '-h'], capture_output=True, text=True)
        return result.stdout.strip()
    
    def check_disk(self) -> str:
        """Check disk usage"""
        result = subprocess.run(['df', '-h'], capture_output=True, text=True)
        return result.stdout.strip()


class GitController(AppController):
    """Controls Git operations"""
    
    def __init__(self, config):
        super().__init__(config)
        self.app_name = "Git"
    
    def open(self) -> str:
        """Git status"""
        return "Git operations ready"
    
    def status(self) -> str:
        """Check git status"""
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        return result.stdout.strip()
    
    def commit(self, message: str) -> str:
        """Create commit"""
        result = subprocess.run(['git', 'add', '.'], capture_output=True, text=True)
        result = subprocess.run(['git', 'commit', '-m', message], capture_output=True, text=True)
        return result.stdout.strip()
    
    def push(self, remote: str = "origin", branch: str = "main") -> str:
        """Push to remote"""
        result = subprocess.run(['git', 'push', remote, branch], capture_output=True, text=True)
        return result.stdout.strip()
    
    def pull(self, remote: str = "origin", branch: str = "main") -> str:
        """Pull from remote"""
        result = subprocess.run(['git', 'pull', remote, branch], capture_output=True, text=True)
        return result.stdout.strip()


class DockerController(AppController):
    """Controls Docker"""
    
    def __init__(self, config):
        super().__init__(config)
        self.app_name = "Docker"
    
    def open(self) -> str:
        """Docker status"""
        return "Docker operations ready"
    
    def ps(self) -> str:
        """List containers"""
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        return result.stdout.strip()
    
    def images(self) -> str:
        """List images"""
        result = subprocess.run(['docker', 'images'], capture_output=True, text=True)
        return result.stdout.strip()
    
    def start(self, container: str) -> str:
        """Start container"""
        result = subprocess.run(['docker', 'start', container], capture_output=True, text=True)
        return result.stdout.strip()
    
    def stop(self, container: str) -> str:
        """Stop container"""
        result = subprocess.run(['docker', 'stop', container], capture_output=True, text=True)
        return result.stdout.strip()


# Export all controllers
__all__ = [
    'MT4Controller',
    'ChromeController', 
    'VSCodeController',
    'ExcelController',
    'TelegramController',
    'SpotifyController',
    'VLCController',
    'SystemController',
    'GitController',
    'DockerController',
]