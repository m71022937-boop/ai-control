"""
AI Control - Main Entry Point
A powerful AI agent that controls your PC and apps.
"""

import sys
import signal
from src.agent.parser import IntentParser
from src.agent.planner import ActionPlanner
from src.agent.executor import ActionExecutor
from src.ai.model_router import ModelRouter
from src.connections.telegram import TelegramBot
from src.utils.config import Config
from src.utils.logger import logger


class AIControl:
    """Main AI Control Agent"""
    
    def __init__(self):
        self.config = Config()
        self.model_router = ModelRouter(self.config)
        self.parser = IntentParser(self.model_router)
        self.planner = ActionPlanner(self.model_router)
        self.executor = ActionExecutor(self.config)
        self.telegram = TelegramBot(self)
        
        logger.info("AI Control initialized")
    
    def start(self):
        """Start the agent"""
        logger.info("Starting AI Control...")
        
        # Start Telegram bot
        if self.config.get('telegram.enabled', False):
            self.telegram.start()
        else:
            # CLI mode
            self.cli_loop()
    
    def cli_loop(self):
        """CLI interaction loop"""
        print("\n🤖 AI Control - PC Automation Agent")
        print("Type 'quit' to exit\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                # Process request
                response = self.process(user_input)
                print(f"\nAI: {response}\n")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                print(f"\n❌ Error: {e}\n")
    
    def process(self, user_input: str) -> str:
        """Process a user request"""
        try:
            # Step 1: Parse intent
            intent = self.parser.parse(user_input)
            
            if not intent.app:
                return "I need to know which app to use. Try: 'Use [app] to [task]'"
            
            # Step 2: Plan actions
            steps = self.planner.plan(intent)
            
            if not steps:
                return "I couldn't figure out how to do that."
            
            # Step 3: Execute actions
            result = self.executor.execute(intent.app, steps)
            
            return result
            
        except Exception as e:
            logger.error(f"Processing error: {e}")
            return f"❌ Error: {e}"
    
    def stop(self):
        """Stop the agent"""
        logger.info("Stopping AI Control...")
        if self.telegram.running:
            self.telegram.stop()
        sys.exit(0)


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print("\n👋 Shutting down...")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    agent = AIControl()
    agent.start()
