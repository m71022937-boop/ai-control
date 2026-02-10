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
            'open chart': ['open_mt4', 'navigate_symbol'],
            'open buy': ['open_mt4', 'navigate_symbol', 'click_buy'],
            'open sell': ['open_mt4', 'navigate_symbol', 'click_sell'],
            'close order': ['open_mt4', 'close_position'],
            'check balance': ['open_mt4', 'check_balance'],
        },
        'chrome': {
            'search': ['open_chrome', 'navigate_url', 'type_search', 'press_enter'],
            'open': ['open_chrome', 'navigate_url'],
            'download': ['open_chrome', 'download_file'],
        },
        'vscode': {
            'create file': ['open_vscode', 'create_file'],
            'open project': ['open_vscode', 'open_folder'],
            'run code': ['open_vscode', 'run_terminal'],
        },
        'terminal': {
            'install': ['open_terminal', 'run_command'],
            'update': ['open_terminal', 'run_command'],
            'run': ['open_terminal', 'run_command'],
            'check': ['open_terminal', 'run_command'],
        },
        'files': {
            'organize': ['open_files', 'organize_folder'],
            'delete': ['open_files', 'delete_file'],
            'move': ['open_files', 'move_file'],
            'create folder': ['open_files', 'create_folder'],
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
            # Add parameters to steps
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
- click (click on screen coordinates or UI element)
- type (type text)
- press_key (press a key like Enter, Escape, etc.)
- wait (wait for something)
- take_screenshot (capture the screen)
- run_command (run a shell command)
- navigate_url (go to a URL)
- create_file (create a file)
- edit_file (edit a file)
- close_app (close the application)

Respond with a JSON array of actions. Example:
[
  {{"action": "open_app", "app": "chrome"}},
  {{"action": "navigate_url", "url": "https://google.com"}},
  {{"action": "type_search", "query": "AI news"}},
  {{"action": "press_key", "key": "Enter"}}
]

Only respond with the JSON array, nothing else.
"""
        
        try:
            response = self.model_router.complete(prompt)
            
            # Parse JSON response
            import json
            steps = json.loads(response)
            
            logger.debug(f"AI planned {len(steps)} steps")
            return steps
            
        except Exception as e:
            logger.error(f"AI planning failed: {e}")
            return self._fallback_plan(app, task)
    
    def _fallback_plan(self, app: str, task: str) -> List[Dict[str, Any]]:
        """Fallback simple plan"""
        steps = [{'action': 'open_app', 'app': app}]
        
        # Add basic task action
        if 'search' in task.lower():
            steps.append({'action': 'navigate_url', 'url': 'https://google.com'})
            steps.append({'action': 'type_search'})
        elif 'create' in task.lower() or 'new' in task.lower():
            steps.append({'action': 'create_file'})
        else:
            steps.append({'action': 'do_task', 'task': task})
        
        return steps
