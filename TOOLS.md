# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without sharing your infrastructure.

---

## Installed Skills

### GitHub
- **Skill**: github
- **Requires**: `gh` CLI installed
- **Uses**: Issues, PRs, workflow runs, API queries
- **Note**: Requires GitHub CLI binary (`brew install gh` or `apt install gh`)

### Coding Agent
- **Skill**: coding-agent
- **Requires**: One of `claude`, `codex`, `opencode`, `pi`
- **Uses**: Run AI coding agents for programming tasks
- **Note**: ALWAYS use `pty:true` for coding agents

### SAG (ElevenLabs TTS)
- **Skill**: sag
- **Uses**: Text-to-speech voice output
- **Note**: Requires ElevenLabs API key

### Session Logs
- **Skill**: session-logs
- **Uses**: Debug and review session history

## GitHub Setup

To use the GitHub skill, install the GitHub CLI:
```bash
# macOS
brew install gh

# Linux
apt install gh
```

Then authenticate:
```bash
gh auth login
```

## Gmail

**Not configured yet.** To add Gmail:
1. Set up Gmail API credentials at https://console.cloud.google.com/
2. Add credentials to `/root/.openclaw/credentials/` or via `openclaw configure`
3. Install `himalaya` skill for email management
