"""
Action Planner - Plans steps to accomplish a task
"""

from typing import List, Dict, Any
from src.agent.parser import Intent
from src.ai.model_router import ModelRouter
from src.utils.logger import logger


class ActionPlanner:
    """Plans actions to accomplish a user intent"""
    
    # Task templates for common actions
    TASK_TEMPLATES = {
        'mt4': {
            'open chart': ['open_app', 'run_command'],
            'open buy': ['open_app', 'run_command'],
            'open sell': ['open_app', 'run_command'],
            'close order': ['open_app', 'run_command'],
            'check balance': ['open_app', 'run_command'],
        },
        'chrome': {
            'search': ['open_app', 'run_command'],
            'open': ['open_app', 'run_command'],
            'download': ['open_app', 'run_command'],
        },
        'vscode': {
            'create file': ['open_app', 'run_command'],
            'open project': ['open_app', 'run_command'],
            'run code': ['open_app', 'run_command'],
        },
        'terminal': {
            'install': ['run_command'],
            'update': ['run_command'],
            'run': ['run_command'],
            'check': ['run_command'],
            'disk': ['run_command'],
            'list': ['run_command'],
            'memory': ['run_command'],
            'process': ['run_command'],
        },
        'files': {
            'organize': ['run_command'],
            'delete': ['run_command'],
            'move': ['run_command'],
            'create folder': ['run_command'],
            'create file': ['create_file'],
            'read file': ['run_command'],
            'edit file': ['create_file'],
        },
        'excel': {
            'create spreadsheet': ['run_command'],
            'open excel': ['run_command'],
            'import csv': ['run_command'],
        },
        'telegram': {
            'send message': ['run_command'],
            'check messages': ['run_command'],
        },
        'spotify': {
            'play music': ['run_command'],
            'open spotify': ['run_command'],
        },
        'vlc': {
            'open video': ['run_command'],
            'open vlc': ['run_command'],
        },
    }
    
    def __init__(self, model_router: ModelRouter):
        self.model_router = model_router
        logger.info("Action Planner initialized")
    
    def plan(self, intent: Intent) -> List[Dict[str, Any]]:
        """Plan actions to accomplish the intent"""
        if not intent.app:
            return []
        
        app = intent.app
        task = intent.task or ""
        
        # Try template matching first (fast)
        steps = self._match_template(app, task)
        
        if steps:
            steps = self._add_params_to_steps(steps, intent.params)
            return steps
        
        # Fall back to AI planning
        steps = self._ai_plan(app, task, intent.params)
        
        return steps
    
    def _match_template(self, app: str, task: str) -> List[str]:
        """Match task to a known template"""
        task_lower = task.lower()
        
        if app not in self.TASK_TEMPLATES:
            return []
        
        templates = self.TASK_TEMPLATES[app]
        
        for pattern, actions in templates.items():
            if pattern in task_lower:
                logger.debug(f"Matched template: {pattern}")
                return actions.copy()
        
        return []
    
    def _add_params_to_steps(self, steps: List[str], params: dict) -> List[Dict[str, Any]]:
        """Add parameters to action steps"""
        result = []
        for step in steps:
            action = {'action': step}
            
            if 'filename' in params:
                action['filename'] = params['filename']
            if 'url' in params:
                action['url'] = params['url']
            if 'query' in params:
                action['query'] = params['query']
            if 'lots' in params:
                action['lots'] = params['lots']
                
            result.append(action)
        
        return result
    
    def _ai_plan(self, app: str, task: str, params: dict) -> List[Dict[str, Any]]:
        """Use AI to plan actions for unknown tasks"""
        if not self.model_router:
            logger.warning("No AI model available, using fallback planning")
            return self._fallback_plan(app, task)
        
        prompt = f"""
You are an AI assistant that plans PC automation tasks.

App: {app}
Task: {task}
Parameters: {params}

Break this down into specific action steps. Each step should be one of:
- open_app (open the application)
- run_command (run a shell command)
- create_file (create a file)
- take_screenshot (capture the screen)
- navigate_url (go to a URL)

Respond with a JSON array of actions. Example:
[
  {{"action": "open_app", "app": "chrome"}},
  {{"action": "run_command", "command": "ls -la"}},
  {{"action": "create_file", "filename": "test.txt", "content": "Hello"}}
]

Only respond with the JSON array, nothing else.
"""
        
        try:
            response = self.model_router.complete(prompt)
            
            import json
            steps = json.loads(response)
            
            logger.debug(f"AI planned {len(steps)} steps")
            return steps
            
        except Exception as e:
            logger.error(f"AI planning failed: {e}")
            return self._fallback_plan(app, task)
    
    def _fallback_plan(self, app: str, task: str) -> List[Dict[str, Any]]:
        """Fallback simple plan"""
        steps = [{'action': 'run_command', 'command': f'echo {app}: {task}'}]
        return steps