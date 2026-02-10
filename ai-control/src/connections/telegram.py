"""
Telegram Bot Integration with validation and error handling
"""

import asyncio
import re
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from telegram.error import TelegramError
from src.agent.parser import IntentParser
from src.agent.planner import ActionPlanner
from src.agent.executor import ActionExecutor
from src.utils.config import Config
from src.utils.logger import get_logger
logger = get_logger()


class TelegramBot:
    """Telegram bot for AI Control"""
    
    def __init__(self, parser, executor, config):
        self.parser = parser
        self.executor = executor
        self.config = config
        self.running = False
        self.application = None
        self.bot = None
        self.token = self.config.telegram_token
        
        # Validate token format
        self._validate_token()
        
        logger.info("Telegram Bot initialized")
    
    def _validate_token(self):
        """Validate Telegram bot token format"""
        if not self.token:
            logger.warning("Telegram token not set")
            self.token_valid = False
            return
        
        # Telegram bot tokens are like: 123456:ABC-DEF1234ghIkl-456
        token_pattern = r'^\d+:[-A-Za-z0-9_]+$'
        if re.match(token_pattern, self.token):
            self.token_valid = True
            logger.info("Telegram token validated")
        else:
            self.token_valid = False
            logger.error(f"Invalid Telegram token format: {self.token[:10]}...")
    
    async def start(self):
        """Start the Telegram bot with error handling"""
        if not self.token:
            logger.warning("Telegram not configured - token missing")
            return
        
        if not self.token_valid:
            logger.error("Telegram token invalid - cannot start")
            return
        
        try:
            # Test bot connection
            test_bot = Bot(token=self.token)
            me = await test_bot.get_me()
            logger.info(f"Connected as @{me.username}")
            
            # Build application
            self.application = Application.builder().token(self.token).build()
            
            # Add handlers
            self.application.add_handler(CommandHandler("start", self.cmd_start))
            self.application.add_handler(CommandHandler("help", self.cmd_help))
            self.application.add_handler(CommandHandler("status", self.cmd_status))
            self.application.add_handler(CommandHandler("stop", self.cmd_stop))
            self.application.add_handler(CommandHandler("screenshot", self.cmd_screenshot))
            self.application.add_handler(CommandHandler("use", self.cmd_use))
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
            
            # Initialize and start
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            self.running = True
            logger.info("Telegram Bot started successfully")
            
        except TelegramError as e:
            logger.error(f"Telegram error: {e}")
            raise RuntimeError(f"Telegram failed: {e}")
        except Exception as e:
            logger.error(f"Failed to start Telegram bot: {e}")
            raise
        
        # Add handlers
        self.application.add_handler(CommandHandler("start", self.cmd_start))
        self.application.add_handler(CommandHandler("help", self.cmd_help))
        self.application.add_handler(CommandHandler("status", self.cmd_status))
        self.application.add_handler(CommandHandler("stop", self.cmd_stop))
        self.application.add_handler(CommandHandler("screenshot", self.cmd_screenshot))
        self.application.add_handler(CommandHandler("use", self.cmd_use))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Start bot
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        self.running = True
        logger.info("Telegram Bot started")
    
    async def stop(self):
        """Stop the Telegram bot"""
        if self.application:
            await self.application.stop()
            await self.application.shutdown()
        self.running = False
        logger.info("Telegram Bot stopped")
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome = """
🤖 Welcome to AI Control!

Your powerful PC automation assistant.

Commands:
• /use <app> "<task>" - Use an app to do something
• /status - Check system status
• /screenshot - Get current screen
• /help - Show this message

Examples:
/use chrome "search for AI news"
/use terminal "apt update"
/use files "organize Downloads folder"
"""
        await update.message.reply_text(welcome)
    
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
📚 AI Control Commands

Main Command:
/use <app> "<task>" - Use an app to perform a task

Supported Apps:
• mt4 - MetaTrader 4
• chrome - Google Chrome
• vscode - VS Code
• terminal - Terminal/Bash
• files - File Manager
• excel - Excel/Spreadsheets

Examples:
/use mt4 "open EURUSD chart"
/use vscode "create new file called bot.py"
/use chrome "search for Bitcoin price"
/use terminal "check disk space"
/use files "organize Downloads folder"

Tips:
• Be specific about what you want
• Use quotes for the task description
• The AI will confirm before making changes
"""
        await update.message.reply_text(help_text)
    
    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        import platform
        import psutil
        
        status = f"""
�Status Report

System: {platform.system()} {platform.machine()}
Python: {platform.python_version()}
CPU: {psutil.cpu_percent()}%
Memory: {psutil.virtual_memory().percent}%
Disk: {psutil.disk_usage('/').percent}%

AI Provider: {self.config.get('ai.provider', 'unknown')}
Model: {self.config.get('ai.model', 'unknown')}

Active Controllers: {len(self.executor.controllers)}
"""
        await update.message.reply_text(status)
    
    async def cmd_stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stop command (emergency)"""
        await update.message.reply_text("🛑 Stopping all tasks...")
        self.executor.controllers.clear()
        await update.message.reply_text("✅ All tasks stopped")
    
    async def cmd_screenshot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /screenshot command"""
        try:
            import pyautogui
            import os
            from datetime import datetime
            
            path = f"/tmp/ai-control-screenshot.png"
            pyautogui.screenshot().save(path)
            
            await update.message.reply_photo(photo=path, caption="📸 Current Screen")
            
            # Clean up
            os.remove(path)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Screenshot failed: {e}")
    
    async def cmd_use(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /use command"""
        if not context.args:
            await update.message.reply_text(
                "❌ Usage: /use <app> \"<task>\"\n\nExample: /use chrome \"search for AI news\""
            )
            return
        
        app = context.args[0]
        task = " ".join(context.args[1:]).strip('"')
        
        if not task:
            await update.message.reply_text("❌ Please specify a task")
            return
        
        await update.message.reply_text(f"🎯 Processing: Use {app} to {task}...")
        
        # Process the request
        intent = self.parser.parse(f"use {app} to {task}")
        steps = self.planner.plan(intent)
        
        if not steps:
            await update.message.reply_text("❌ Could not understand the task")
            return
        
        # Execute
        result = self.executor.execute(app, steps)
        
        await update.message.reply_text(f"✅ {result}")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages"""
        user_input = update.message.text
        
        # Check if it's a "use X to Y" pattern
        if 'use' in user_input.lower() and ' to ' in user_input.lower():
            await self.cmd_use(update, context)
        else:
            await update.message.reply_text(
                "🤖 I understand 'Use [app] to [task]' commands.\n\n"
                "Example: 'Use chrome to search for AI news'\n"
                "Or use /use chrome \"search for AI news\""
            )