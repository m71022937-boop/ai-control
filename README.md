# AI Control - PC Automation Agent

A powerful AI agent that controls your PC and uses apps exactly as you instruct.

## Installation

```bash
# Clone the repository
git clone https://github.com/m71022937-boop/ai-control.git
cd ai-control

# Install dependencies
pip install -r requirements.txt

# Configure
cp config/config.yaml.example config/config.yaml
# Edit config.yaml with your settings

# Run
python -m ai_control
```

## Configuration

Edit `config/config.yaml`:

```yaml
telegram:
  enabled: false
  token: "YOUR_BOT_TOKEN_HERE"

ai:
  provider: "ollama"  # ollama, openrouter, anthropic
  model: "llama3"
  ollama_url: "http://localhost:11434"
  openrouter_key: "YOUR_OPENROUTER_KEY"
```

## Requirements

- Python 3.11+
- Ollama (optional, for local AI)
- PyAutoGUI (cross-platform automation)
- python-telegram-bot (optional, for Telegram control)

## Features

- ✅ Control ANY app (click, type, navigate)
- ✅ Shell commands execution
- ✅ File operations
- ✅ Browser automation
- ✅ Multi-step task handling
- ✅ Vision/OCR for reading app screens
- ✅ Telegram bot integration
- ✅ Cross-platform (Linux + Windows)

## Usage

### CLI Mode

```
You: Use terminal to check disk space
AI: ✓ Terminal opened
    ✓ Executed: df -h
    Result: Filesystem      Size  Used Avail Use% Mounted on
    ...

You: Use chrome to search for AI news
AI: ✓ Chrome opened
    ✓ Navigated to Google
    ✓ Searched for AI news
```

### Telegram Mode

```
/use mt4 "open EURUSD chart"
/use vscode "create new file called bot.py"
/use chrome "search for Bitcoin price"
/use terminal "apt update"
/use files "organize Downloads folder"
```

## Supported Apps

| App | Commands |
|-----|----------|
| **MT4** | open chart, place buy/sell, check balance |
| **Chrome** | open URL, search, download |
| **VS Code** | create file, open project, run code |
| **Terminal** | run any command |
| **Files** | organize, delete, move, create folder |
| **Excel** | create spreadsheet, import CSV |

## Architecture

```
User Input → Intent Parser → Action Planner → App Controller → Execute
                ↓                    ↓
         Detect app/task      Plan steps
```

## License

MIT

## Author

[m71022937-boop](https://github.com/m71022937-boop)