# AI Control - Model System Guide

This document explains how AI models work in AI Control - both **local** and **cloud** options.

---

## Overview

AI Control uses an AI model to:
1. **Understand commands** - Parse "Use X to do Y"
2. **Plan actions** - Figure out steps to accomplish tasks
3. **Make decisions** - Handle complex or unknown tasks

---

## Local Models (On Your Machine)

### What is Local AI?
- Runs **100% on your computer**
- No internet required
- Your data stays private
- Free to use (no API costs)

### How to Set Up Local (Ollama)

**1. Install Ollama**
```bash
# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama server
ollama serve
```

**2. Download a Model**
```bash
# Lightweight model (fast)
ollama pull llama3:latest

# Or smaller model (even faster)
ollama pull codellama:latest
ollama pull mistral:latest
```

**3. Configure AI Control**
```yaml
# config/config.yaml
ai:
  provider: "ollama"
  model: "llama3"
  ollama_url: "http://localhost:11434"
```

**4. Test It**
```bash
python3 -c "
from src.ai.model_router import ModelRouter
from src.utils.config import Config

router = ModelRouter(Config())
response = router.complete('Say hello in one word')
print(response)
```

### Available Local Models

| Model | Size | Speed | Best For |
|-------|------|-------|----------|
| llama3 | 4-5 GB | Fast | General tasks |
| mistral | 4 GB | Fast | General tasks |
| codellama | 6 GB | Medium | Coding |
| deepseek-coder | 4 GB | Fast | Coding |

---

## Cloud Models (Remote APIs)

### What is Cloud AI?
- Runs on remote servers
- Requires internet
- May have costs (pay-per-use)
- More powerful models available

### Supported Cloud Providers

#### 1. OpenRouter (Recommended)
- Access to many models (OpenAI, Anthropic, etc.)
- Unified API
- Pay per use

**Setup:**
```yaml
# config/config.yaml
ai:
  provider: "openrouter"
  model: "openrouter/minimax/minimax-m2.1"  # or "anthropic/claude-3-haiku"
  openrouter_key: "sk-or-your-key-here"
```

**Get API Key:** https://openrouter.ai/account

#### 2. Anthropic (Claude)
- Powerful reasoning
- Excellent for complex tasks

**Setup:**
```yaml
ai:
  provider: "anthropic"
  anthropic_key: "your-anthropic-key"
```

#### 3. OpenAI (GPT-4)
- Very capable
- Well-documented

**Setup:**
```yaml
ai:
  provider: "openai"
  openai_key: "sk-your-key"
```

---

## Comparison: Local vs Cloud

| Aspect | Local (Ollama) | Cloud (OpenRouter) |
|--------|----------------|-------------------|
| **Cost** | Free | Pay-per-use |
| **Privacy** | 100% private | Data sent to cloud |
| **Speed** | Depends on hardware | Fast (internet) |
| **Offline** | ✅ Works offline | ❌ Needs internet |
| **Model Size** | Limited by hardware | Unlimited |
| **Setup** | Medium (install Ollama) | Easy (just API key) |
| **Best For** | Privacy, cost-saving | Power, flexibility |

---

## Recommendations

### Use Local (Ollama) When:
- You want privacy
- You want free usage
- You have a good GPU/CPU
- Tasks are simple

### Use Cloud (OpenRouter) When:
- You need maximum power
- Complex reasoning tasks
- Hardware is limited
- Cost is not an issue

---

## Quick Setup Guide

### Option 1: Local (Free)
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
ollama pull llama3

# Configure
sed -i 's/provider: "ollama"/provider: "ollama"/' config/config.yaml
sed -i 's/model: "llama3"/model: "llama3"/' config/config.yaml
```

### Option 2: Cloud (OpenRouter)
```bash
# Get key from https://openrouter.ai/account
# Edit config/config.yaml
ai:
  provider: "openrouter"
  model: "anthropic/claude-3-haiku"
  openrouter_key: "sk-or-your-key"
```

---

## Testing Your Setup

```bash
python3 -c "
from src.ai.model_router import ModelRouter
from src.utils.config import Config

config = Config()
router = ModelRouter(config)

print('Testing AI model...')
response = router.complete('What is 2+2? Answer in one word.')
print(f'Response: {response}')

models = router.list_models()
print(f'Available models: {models}')
"
```

---

## Troubleshooting

### Local Issues
```
Error: Ollama not running
Solution: Run 'ollama serve'
```
```
Error: Model not found
Solution: Run 'ollama pull llama3'
```

### Cloud Issues
```
Error: API key not set
Solution: Set openrouter_key in config.yaml
```
```
Error: Insufficient credits
Solution: Add credits at openrouter.ai/account
```

---

## Advanced: Switching Models

```yaml
# config/config.yaml

# For fast local:
ai:
  provider: "ollama"
  model: "mistral"

# For powerful cloud:
ai:
  provider: "openrouter"
  model: "anthropic/claude-3-opus-2024-05-20"
```

---

## Summary

| Provider | Setup | Cost | Speed | Privacy |
|----------|-------|------|-------|----------|
| **Ollama** (Local) | Install + download | Free | Hardware dependent | ✅ 100% |
| **OpenRouter** (Cloud) | API key only | Pay-per-use | Fast | ❌ Cloud |
| **Anthropic** (Cloud) | API key only | Pay-per-use | Fast | ❌ Cloud |
| **OpenAI** (Cloud) | API key only | Pay-per-use | Fast | ❌ Cloud |

---

*For more info:*
- Ollama: https://ollama.ai
- OpenRouter: https://openrouter.ai
- Anthropic: https://anthropic.com
- OpenAI: https://openai.com