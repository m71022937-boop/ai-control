# AI Control - PC Automation Agent

A powerful AI agent that controls your PC and apps. Just say **"Use [App] to [task]"** and it will execute.

## Quick Start

```bash
cd /root/.openclaw/workspace/ai-control
python3 -c "
from src.agent.executor import ActionExecutor
from src.utils.config import Config

e = ActionExecutor(Config())
e.execute('terminal', [{'action': 'run_command', 'command': 'echo Hello!'}])

e.execute('files', [{'action': 'create_file', 'filename': '/tmp/test.txt', 'content': 'Hello from AI Control!'}])
"
```

## Supported Apps

| App | Examples |
|-----|----------|
| **terminal/shell** | Run any command |
| **chrome/browser** | Open, navigate, search |
| **vscode** | Create files, open projects |
| **mt4** | Trading operations |
| **files** | Create, read, organize files |
| **excel** | Spreadsheet operations |
| **telegram** | Bot commands |
| **spotify** | Play music |
| **vlc** | Play videos |
| **system** | Get info, processes, memory, disk |
| **git** | Status, commit, push, pull |
| **docker** | Containers, images |

## Example Commands

```bash
# Terminal
Use terminal to check disk space
Use terminal to list files
Use terminal to show memory

# Files
Use files to create file /tmp/test.txt
Use files to read /etc/hosts

# Git
Use git to check status
Use git to commit "message"
Use git to push

# System
Use system to check processes
Use system to check memory
Use system to check disk
```

## AI Models Guide

AI Control supports both **local** and **cloud** AI models.

### Local Models (Free, Private)

**Install Ollama:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
ollama pull llama3
```

**Configure:**
```yaml
ai:
  provider: "ollama"
  model: "llama3"
  ollama_url: "http://localhost:11434"
```

### Cloud Models (Powerful)

**OpenRouter (Recommended):**
```yaml
ai:
  provider: "openrouter"
  model: "anthropic/claude-3-haiku"
  openrouter_key: "sk-or-your-key"
```

Get API key: https://openrouter.ai/account

### Comparison

| Aspect | Local (Ollama) | Cloud (OpenRouter) |
|--------|----------------|-------------------|
| Cost | Free | Pay-per-use |
| Privacy | 100% private | Data sent to cloud |
| Speed | Hardware dependent | Fast |
| Offline | ✅ Works | ❌ Needs internet |

## Telegram Bot

Bot: **@CLAW_4832_bot**

Commands:
```
/start - Welcome message
/help - Help
/use <app> "<task>" - Use an app
/status - System status
/screenshot - Get screenshot
/stop - Emergency stop
```

## Project Structure

```
ai-control/
├── src/
│   ├── agent/
│   │   ├── parser.py      # Parse "Use X to Y"
│   │   ├── planner.py    # Plan actions
│   │   └── executor.py   # Execute on PC
│   ├── apps/
│   │   ├── base.py       # Base controller
│   │   └── all_apps.py   # All app controllers
│   ├── ai/
│   │   └── model_router.py  # AI model routing
│   └── connections/
│       └── telegram.py   # Telegram bot
├── config/
│   └── config.yaml      # Configuration
├── docs/
│   └── MODELS.md        # AI model guide
└── requirements.txt
```

## Requirements

```bash
pip install python-telegram-bot pyyaml pyautogui Pillow requests psutil
```

## License

MIT

## Author

[m71022937-boop](https://github.com/m71022937-boop)