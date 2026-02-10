"""
Action Executor - Executes planned actions on the PC
"""

import time
import subprocess
from typing import Dict, Any, List
from src.utils.config import Config
from src.utils.logger import logger
from src.apps.base import AppController


class ActionExecutor:
    """Executes planned actions on the PC"""
    
    def __init__(self, config: Config):
        self.config = config
        self.controllers: Dict[str, AppController] = {}
        logger.info("Action Executor initialized")
    
    def execute(self, app: str, steps: List[Dict[str, Any]]) -> str:
        """Execute a series of steps for an app"""
        if not app:
            return "No app specified"
        
        if not steps:
            return "No steps to execute"
        
        try:
            # Get or create app controller
            controller = self._get_controller(app)
            
            # Execute each step
            results = []
            for step in steps:
                action = step.get('action', '')
                
                try:
                    result = self._execute_step(controller, step)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Step '{action}' failed: {e}")
                    results.append(f"❌ {action}: {e}")
                    
                    # Continue with next step (resilient)
                    continue
            
            # Summarize results
            success_count = sum(1 for r in results if r.startswith('✓'))
            total = len(results)
            
            if success_count == total:
                return f"✅ All {total} steps completed successfully!"
            else:
                return f"⚠️ {success_count}/{total} steps completed. Results:\n" + "\n".join(results)
                
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            return f"❌ Execution failed: {e}"
    
    def _get_controller(self, app: str) -> AppController:
        """Get or create an app controller"""
        if app not in self.controllers:
            self.controllers[app] = self._create_controller(app)
        
        return self.controllers[app]
    
    def _create_controller(self, app: str) -> AppController:
        """Create a controller for the specified app"""
        from src.apps.all_apps import (
            MT4Controller, ChromeController, VSCodeController,
            ExcelController, TelegramController, SpotifyController,
            VLCController, SystemController, GitController, DockerController
        )
        
        controllers = {
            'terminal': TerminalController,
            'shell': TerminalController,
            'bash': TerminalController,
            'chrome': ChromeController,
            'browser': ChromeController,
            'google': ChromeController,
            'mt4': MT4Controller,
            'metatrader': MT4Controller,
            'vscode': VSCodeController,
            'code': VSCodeController,
            'excel': ExcelController,
            'spreadsheet': ExcelController,
            'telegram': TelegramController,
            'spotify': SpotifyController,
            'vlc': VLCController,
            'system': SystemController,
            'git': GitController,
            'docker': DockerController,
        }
        
        controller_class = controllers.get(app)
        if controller_class:
            return controller_class(self.config)
        else:
            return GenericController(self.config, app)
    
    def _execute_step(self, controller: AppController, step: Dict[str, Any]) -> str:
        """Execute a single step"""
        action = step.get('action', '')
        
        # Map actions to controller methods
        action_map = {
            'open_app': lambda: controller.open(),
            'close_app': lambda: controller.close(),
            'click': lambda: controller.click(step.get('x', 0), step.get('y', 0)),
            'type': lambda: controller.type_text(step.get('text', '')),
            'press_key': lambda: controller.press_key(step.get('key', '')),
            'wait': lambda: controller.wait(step.get('seconds', 1)),
            'take_screenshot': lambda: controller.screenshot(),
            'run_command': lambda: controller.run_command(step.get('command', '')),
            'navigate_url': lambda: controller.navigate_url(step.get('url', '')),
            'create_file': lambda: controller.create_file(step.get('filename', ''), step.get('content', '')),
            'edit_file': lambda: controller.edit_file(step.get('filename', ''), step.get('content', '')),
            'organize_folder': lambda: controller.organize_folder(step.get('path', '')),
        }
        
        if action in action_map:
            result = action_map[action]()
            return f"✓ {action}" + (f": {result}" if result else "")
        else:
            # Try generic method
            method = getattr(controller, action, None)
            if method:
                result = method(**step)
                return f"✓ {action}" + (f": {result}" if result else "")
            else:
                return f"⚠️ Unknown action: {action}"


class TerminalController(AppController):
    """Controls terminal/shell"""
    
    def open(self) -> str:
        """Open terminal"""
        import os
        if os.name == 'nt':
            subprocess.Popen(['cmd.exe'])
        else:
            subprocess.Popen(['x-terminal-emulator', '-e', 'bash'])
        return "Terminal opened"
    
    def run_command(self, command: str) -> str:
        """Run a shell command"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            output = result.stdout or result.stderr
            return output[:500] if output else "Command completed"
        except subprocess.TimeoutExpired:
            return "Command timed out"
        except Exception as e:
            return f"Error: {e}"


class BrowserController(AppController):
    """Controls web browser"""
    
    def open(self) -> str:
        """Open browser"""
        subprocess.Popen(['google-chrome', '--new-window'])
        time.sleep(2)
        return "Chrome opened"
    
    def navigate_url(self, url: str) -> str:
        """Navigate to URL"""
        subprocess.run(['xdotool', 'key', 'Ctrl+l'])  # Focus address bar
        time.sleep(0.5)
        subprocess.run(['xdotool', 'type', url])
        subprocess.run(['xdotool', 'key', 'Return'])
        return f"Navigated to {url}"
    
    def type_search(self, query: str) -> str:
        """Type search query"""
        subprocess.run(['xdotool', 'type', query])
        return f"Typed: {query}"


class MT4Controller(AppController):
    """Controls MetaTrader 4"""
    
    def open(self) -> str:
        """Open MT4"""
        # Try common MT4 locations
        paths = [
            '/usr/bin/metatrader4',
            '/opt/mt4/terminal.exe',
            'wine ~/.wine/drive_c/Program Files/MetaTrader4/terminal.exe',
        ]
        for path in paths:
            try:
                subprocess.Popen(path.split())
                time.sleep(3)
                return "MT4 opened"
            except:
                continue
        return "MT4 not found"


class VSCodeController(AppController):
    """Controls VS Code"""
    
    def open(self) -> str:
        """Open VS Code"""
        subprocess.Popen(['code'])
        time.sleep(3)
        return "VS Code opened"
    
    def create_file(self, filename: str, content: str = "") -> str:
        """Create a new file in VS Code"""
        # Use code CLI to create file
        subprocess.run(['code', '--new-window', filename])
        time.sleep(2)
        return f"Created: {filename}"


class FileController(AppController):
    """Controls file manager"""
    
    def open(self) -> str:
        """Open file manager"""
        import os
        if os.name == 'nt':
            subprocess.Popen(['explorer'])
        else:
            subprocess.Popen(['nautilus'])
        return "File manager opened"
    
    def organize_folder(self, path: str) -> str:
        """Organize folder by file type"""
        import os
        import shutil
        
        path = path or os.path.expanduser('~/Downloads')
        
        if not os.path.exists(path):
            return f"Path not found: {path}"
        
        # Create subfolders
        categories = {
            'Images': ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp'],
            'Documents': ['.pdf', '.doc', '.docx', '.txt', '.xls', '.xlsx'],
            'Videos': ['.mp4', '.mov', '.avi', '.mkv'],
            'Archives': ['.zip', '.tar', '.gz', '.rar'],
            'Scripts': ['.py', '.js', '.sh', '.bash'],
        }
        
        for folder, extensions in categories.items():
            folder_path = os.path.join(path, folder)
            os.makedirs(folder_path, exist_ok=True)
        
        # Move files
        moved = []
        for file in os.listdir(path):
            file_path = os.path.join(path, file)
            if os.path.isfile(file):
                ext = os.path.splitext(file)[1].lower()
                for category, extensions in categories.items():
                    if ext in extensions:
                        dest = os.path.join(path, category, file)
                        shutil.move(file_path, dest)
                        moved.append(file)
                        break
        
        return f"Organized {len(moved)} files"


class GenericController(AppController):
    """Generic controller for unknown apps"""
    
    def __init__(self, config: Config, app_name: str):
        super().__init__(config)
        self.app_name = app_name
    
    def open(self) -> str:
        """Try to open the app"""
        try:
            subprocess.Popen([self.app_name])
            time.sleep(2)
            return f"{self.app_name} opened"
        except:
            return f"Could not open {self.app_name}"
