"""
Action Planner - Plans steps with JSON validation and safety
"""

import json
from typing import List, Dict, Any
from src.agent.parser import Intent
from src.ai.model_router import ModelRouter
from src.utils.logger import get_logger

logger = get_logger()


class ActionPlanner:
    """Plans actions to accomplish a user intent with safety"""
    
    # ALLOWED ACTIONS - Only these actions can be executed
    ALLOWED_ACTIONS = {
        'run_command': 'Execute shell command',
        'create_file': 'Create a file',
        'open_app': 'Open an application',
        'close_app': 'Close an application',
        'take_screenshot': 'Take a screenshot',
        'wait': 'Wait for specified seconds',
        'navigate_url': 'Navigate to URL',
        'type_text': 'Type text',
        'click': 'Click at coordinates',
        'press_key': 'Press a key',
    }
    
    # Task templates for common actions
    TASK_TEMPLATES = {
        'mt4': {
            'open chart': [{'action': 'run_command', 'command': 'echo Opening MT4 chart'}],
            'check balance': [{'action': 'run_command', 'command': 'echo Checking MT4 balance'}],
        },
        'chrome': {
            'search': [{'action': 'run_command', 'command': 'echo Opening Chrome'}],
            'open': [{'action': 'run_command', 'command': 'echo Opening browser'}],
        },
        'vscode': {
            'create file': [{'action': 'create_file', 'filename': 'example.py', 'content': '# Created by AI Control'}],
            'open': [{'action': 'run_command', 'command': 'echo Opening VS Code'}],
        },
        'terminal': {
            'install': [{'action': 'run_command', 'command': 'echo Running command'}],
            'update': [{'action': 'run_command', 'command': 'echo Running command'}],
            'run': [{'action': 'run_command', 'command': 'echo Running command'}],
            'check': [{'action': 'run_command', 'command': 'echo Checking'}],
            'disk': [{'action': 'run_command', 'command': 'df -h'}],
            'list': [{'action': 'run_command', 'command': 'ls -la'}],
            'memory': [{'action': 'run_command', 'command': 'free -h'}],
            'process': [{'action': 'run_command', 'command': 'ps aux'}],
        },
        'files': {
            'create file': [{'action': 'create_file', 'filename': 'file.txt', 'content': ''}],
            'read file': [{'action': 'run_command', 'command': 'cat file.txt'}],
            'organize': [{'action': 'run_command', 'command': 'echo Organizing files'}],
        },
        'system': {
            'check memory': [{'action': 'run_command', 'command': 'free -h'}],
            'check disk': [{'action': 'run_command', 'command': 'df -h'}],
            'check process': [{'action': 'run_command', 'command': 'ps aux'}],
            'info': [{'action': 'run_command', 'command': 'uname -a'}],
        },
        'git': {
            'status': [{'action': 'run_command', 'command': 'git status'}],
            'commit': [{'action': 'run_command', 'command': 'git status'}],
            'push': [{'action': 'run_command', 'command': 'git status'}],
            'pull': [{'action': 'run_command', 'command': 'git pull'}],
        },
        'docker': {
            'list container': [{'action': 'run_command', 'command': 'docker ps'}],
            'list image': [{'action': 'run_command', 'command': 'docker images'}],
            'ps': [{'action': 'run_command', 'command': 'docker ps'}],
        },
        'python': {
            'version': [{'action': 'run_command', 'command': 'python3 --version'}],
            'run': [{'action': 'run_command', 'command': 'python3 script.py'}],
        },
        'excel': {
            'spreadsheet': [{'action': 'run_command', 'command': 'echo Opening spreadsheet'}],
        },
        'telegram': {
            'message': [{'action': 'run_command', 'command': 'echo Use Telegram bot'}],
        },
        'spotify': {
            'music': [{'action': 'run_command', 'command': 'echo Opening Spotify'}],
        },
        'vlc': {
            'video': [{'action': 'run_command', 'command': 'echo Opening VLC'}],
        },
    }
    
    def __init__(self, model_router: ModelRouter):
        self.model_router = model_router
        logger.info("Action Planner initialized")
    
    def plan(self, intent: Intent) -> List[Dict[str, Any]]:
        """Plan actions with safety checks"""
        if not intent.app:
            return []
        
        app = intent.app
        task = intent.task or ""
        
        # Try template matching first (fast and safe)
        steps = self._match_template(app, task)
        
        if steps:
            steps = self._add_params_to_steps(steps, intent.params)
            return self._validate_steps(steps)
        
        # AI planning with JSON validation
        steps = self._ai_plan(app, task, intent.params)
        
        return self._validate_steps(steps)
    
    def _match_template(self, app: str, task: str) -> List[str]:
        """Match task to a known template"""
        task_lower = task.lower()
        
        if app not in self.TASK_TEMPLATES:
            return []
        
        templates = self.TASK_TEMPLATES[app]
        
        for pattern, actions in templates.items():
            if pattern in task_lower:
                logger.debug(f"Matched template: {pattern}")
                return [a.copy() for a in actions]
        
        return []
    
    def _add_params_to_steps(self, steps: List[Dict[str, Any]], params: dict) -> List[Dict[str, Any]]:
        """Add parameters to action steps"""
        result = []
        for step in steps:
            action = {'action': step.get('action', '')}
            
            if 'filename' in params:
                action['filename'] = params['filename']
            if 'url' in params:
                action['url'] = params['url']
            if 'query' in params:
                action['query'] = params['query']
            if 'lots' in params:
                action['lots'] = params['lots']
            if 'command' in step:
                action['command'] = step['command']
            if 'content' in step:
                action['content'] = step['content']
                
            result.append(action)
        
        return result
    
    def _ai_plan(self, app: str, task: str, params: dict) -> List[Dict[str, Any]]:
        """Use AI to plan actions with JSON validation"""
        if not self.model_router:
            logger.warning("No AI model available, using fallback")
            return self._fallback_plan(app, task)
        
        prompt = f"""
You are an AI assistant that plans PC automation tasks.

App: {app}
Task: {task}

Available actions:
{json.dumps(list(self.ALLOWED_ACTIONS.keys()), indent=2)}

You must respond with ONLY valid JSON in this format:
{{"actions": [{{"action": "action_name", "command": "echo example"}}]}}

Example response:
{{"actions": [{{"action": "run_command", "command": "ls -la"}}]}}

Do not include any other text. JSON only.
"""
        
        try:
            response = self.model_router.complete(prompt)
            
            # Parse JSON response
            try:
                data = json.loads(response)
                actions = data.get('actions', [])
                
                if not isinstance(actions, list):
                    logger.error(f"AI returned non-list actions: {actions}")
                    return self._fallback_plan(app, task)
                
                return actions
                
            except json.JSONDecodeError as e:
                logger.error(f"AI response not valid JSON: {response[:100]}")
                return self._fallback_plan(app, task)
            
        except Exception as e:
            logger.error(f"AI planning failed: {e}")
            return self._fallback_plan(app, task)
    
    def _validate_steps(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate steps against allowlist"""
        validated = []
        
        for step in steps:
            action = step.get('action', '')
            
            # Check if action is allowed
            if action not in self.ALLOWED_ACTIONS:
                logger.warning(f"Action '{action}' not in allowlist, skipping")
                continue
            
            # For run_command, validate the command
            if action == 'run_command':
                command = step.get('command', '')
                if self._is_safe_command(command):
                    validated.append(step)
                else:
                    logger.warning(f"Command potentially unsafe: {command[:50]}...")
            else:
                validated.append(step)
        
        if len(validated) != len(steps):
            logger.info(f"Validated {len(validated)}/{len(steps)} steps")
        
        return validated
    
    def _is_safe_command(self, command: str) -> bool:
        """Check if command is safe (basic check)"""
        # Block dangerous commands
        dangerous = ['rm -rf', 'mkfs', 'dd if=', ':(){:|:&};:', 'wget', 'curl']
        
        cmd_lower = command.lower()
        
        for pattern in dangerous:
            if pattern in cmd_lower:
                return False
        
        return True
    
    def _fallback_plan(self, app: str, task: str) -> List[Dict[str, Any]]:
        """Fallback simple plan"""
        return [{'action': 'run_command', 'command': f'echo {app}: {task}'}]