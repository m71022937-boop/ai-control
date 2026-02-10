#!/usr/bin/env python3
"""
AI Control - Main Entry Point

Usage:
    python -m src                    # CLI mode
    python -m src --telegram          # Telegram bot mode
    python -m src --daemon            # Run as daemon
"""

import sys
import signal
import argparse
from src.utils.config import Config
from src.utils.logger import get_logger
from src.agent.parser import IntentParser
from src.agent.planner import ActionPlanner
from src.agent.executor import ActionExecutor
from src.ai.model_router import ModelRouter


logger = get_logger()


def run_cli():
    """Run in CLI interactive mode"""
    print("\n🤖 AI Control - PC Automation Agent")
    print("Type 'quit' to exit\n")
    
    # Initialize components
    config = Config()
    model_router = ModelRouter(config)
    parser = IntentParser(model_router)
    planner = ActionPlanner(model_router)
    executor = ActionExecutor(config)
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Process request
            intent = parser.parse(user_input)
            
            if not intent.app:
                print("AI: Please specify an app. Example: 'Use terminal to check disk space'")
                continue
            
            steps = planner.plan(intent)
            
            if not steps:
                print("AI: Could not understand how to do that.")
                continue
            
            result = executor.execute(intent.app, steps)
            print(f"AI: {result}\n")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"❌ Error: {e}\n")


def run_telegram():
    """Run Telegram bot mode"""
    print("Starting Telegram bot...")
    
    config = Config()
    
    if not config.telegram_enabled:
        print("❌ Telegram not configured. Set token in config.yaml")
        return
    
    from src.connections.telegram import TelegramBot
    
    model_router = ModelRouter(config)
    parser = IntentParser(model_router)
    planner = ActionPlanner(model_router)
    executor = ActionExecutor(config)
    
    bot = TelegramBot(parser, executor, config)
    
    import asyncio
    try:
        asyncio.run(bot.start())
    except KeyboardInterrupt:
        print("\n👋 Telegram bot stopped")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='AI Control - PC Automation Agent')
    parser.add_argument('--telegram', action='store_true', help='Run Telegram bot mode')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    args = parser.parse_args()
    
    # Handle signals
    def signal_handler(signum, frame):
        print("\n👋 Shutting down...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    if args.telegram:
        run_telegram()
    else:
        run_cli()


if __name__ == "__main__":
    main()