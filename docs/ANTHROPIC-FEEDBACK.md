# Claude Code Feature Requests & Feedback

> **For Anthropic Engineers:** This document details limitations encountered while building an auto-handoff system for Claude Code, along with suggested improvements. Each section explains what we built, why it was necessary, and what native support would look like.

**GitHub Issue:** https://github.com/anthropics/claude-code/issues/18417
**Author:** Jesse Eldridge + Claude (Opus 4.5)
**Date:** February 2026

---

## Executive Summary

We built an "auto-handoff" system that monitors context usage and automatically preserves state before hitting the context limit. This enables Claude to work autonomously on long tasks without losing context to auto-compaction.

**The system works**, but required significant workarounds due to missing APIs and hooks. This document details each limitation and proposes solutions.

---

## 1. No Context Usage API

### The Problem

There is no way to programmatically query Claude Code's current context usage (tokens used, tokens remaining, percentage).

### What We Built

We **estimate** context usage by:
1. Finding the current session's transcript file (`.jsonl`)
2. Parsing for `cache_read_input_tokens` values
3. Calculating percentage against the 200k limit

```bash
TOKENS=$(strings "$TRANSCRIPT" | grep "cache_read_input_tokens" | tail -1 | grep -o '"cache_read_input_tokens":[0-9]*' | cut -d: -f2)
PERCENT=$((TOKENS * 100 / 200000))
```

### Why This Is Inadequate

1. **Inaccurate** - `cache_read_input_tokens` doesn't include:
   - System prompts
   - User messages not yet in transcript
   - Tool definitions
   - MCP server context
   - The preloaded `additionalContext` from SessionStart hooks

2. **Laggy** - We can only measure after tool calls (PostToolUse hook), not in real-time

3. **Fragile** - Depends on transcript file format which could change

### Suggested Solution

**Option A: Environment variable**
```bash
# Available to hooks
$CLAUDE_CONTEXT_TOKENS=156234
$CLAUDE_CONTEXT_PERCENT=78
$CLAUDE_CONTEXT_LIMIT=200000
```

**Option B: Hook input field**
```json
{
  "hook_type": "PostToolUse",
  "context": {
    "tokens_used": 156234,
    "tokens_limit": 200000,
    "percent": 78
  }
}
```

**Option C: Status API endpoint**
```bash
claude --status --json
# {"context_tokens": 156234, "context_limit": 200000, ...}
```

---

## 2. No "Context Critical" Hook

### The Problem

There's no native hook that fires when context reaches a critical threshold. We must poll after every tool call.

### What We Built

A `PostToolUse` hook that runs after **every single tool call**, checks context, and triggers handoff if critical:

```bash
# Runs hundreds of times per session
if [ "$TOKENS" -ge "$CRITICAL_TOKENS" ]; then
    # Create handoff and signal restart
fi
```

### Why This Is Inadequate

1. **Performance overhead** - Hook runs after every tool call
2. **Can miss the window** - Large tool outputs could push past critical before we check
3. **No pre-warning** - We can't prepare for compaction, only react

### Suggested Solution

**New hook type: `ContextThreshold`**
```json
{
  "hooks": {
    "ContextThreshold": [{
      "threshold": 0.90,
      "hooks": [{"type": "command", "command": "~/.claude/hooks/context-warning.sh"}]
    }, {
      "threshold": 0.96,
      "hooks": [{"type": "command", "command": "~/.claude/hooks/context-critical.sh"}]
    }]
  }
}
```

This would:
- Only fire when thresholds are crossed (not every tool call)
- Allow multiple thresholds (warn, critical)
- Enable preparation before critical (Claude can wrap up cleanly)

---

## 3. "Context Low" Warning Cannot Be Disabled

### The Problem

When `autoCompact: false` is set, Claude Code still shows a "Context low" warning in the terminal. This warning:
1. Shows **incorrect percentages** (seems to use different calculation)
2. Cannot be hidden or customized
3. Conflicts with our own accurate status display

### What We Built

We attempted ANSI escape codes to clear the bottom terminal lines where the warning appears:

```bash
# Attempt to clear warning (unreliable)
printf '\033[s\033[%d;1H\033[K\033[u' "$row" > /dev/tty
```

This is fragile, terminal-dependent, and doesn't fully work.

### Suggested Solution

**Option A: Make warning respect `autoCompact: false`**
- If auto-compact is disabled, don't show the built-in warning
- Let users implement their own status display

**Option B: Add setting to disable warning**
```json
{
  "contextWarning": false
}
```

**Option C: Make warning accurate**
- Show correct percentage even when auto-compact is disabled
- Or show token counts instead of percentages

---

## 4. No Session ID Accessible to Hooks

### The Problem

Hooks cannot reliably identify which session they belong to. This is critical for:
- Multi-session isolation (multiple terminals)
- Matching handoffs to sessions
- Preventing cross-session interference

### What We Built

We walk the process tree from the hook to find the wrapper, then read session info from a file the wrapper created:

```bash
find_wrapper_pid() {
    local pid=$$
    while [ $depth -lt 10 ]; do
        local ppid=$(ps -o ppid= -p "$pid" | tr -d ' ')
        [ -f "$HOME/.claude/.current-session-${ppid}" ] && echo "$ppid" && return
        pid=$ppid
    done
}
```

### Why This Is Inadequate

1. **Complex** - Walking process tree is error-prone
2. **Race conditions** - Session file might not exist yet at SessionStart
3. **Platform-dependent** - `ps` flags vary across systems

### Suggested Solution

**Pass session ID to hooks:**
```json
{
  "hook_type": "PostToolUse",
  "session_id": "abc123-def456-...",
  "session_start_time": "2026-02-02T17:00:00Z"
}
```

Or via environment:
```bash
$CLAUDE_SESSION_ID=abc123-def456-...
```

---

## 5. No Graceful Handoff Mechanism

### The Problem

There's no way to tell Claude "save your state and restart." We must kill the process and hope our handoff was created in time.

### What We Built

A wrapper script that:
1. Monitors for a restart signal file
2. Kills Claude with SIGTERM/SIGKILL
3. Restarts with a handoff prompt

```bash
# Kill Claude and restart
kill -TERM "$CLAUDE_PID"
sleep 0.2
kill -9 "$CLAUDE_PID"
# Start new session with handoff
$CLAUDE_BIN --session-id "$NEW_SESSION" "$HANDOFF_PROMPT"
```

### Why This Is Inadequate

1. **Abrupt** - No chance for Claude to finish current thought
2. **Data loss risk** - If kill happens mid-write
3. **User experience** - Jarring transition

### Suggested Solution

**Graceful restart API:**
```bash
# Signal Claude to finish current operation and restart
claude --restart --handoff-file /path/to/handoff.md

# Or via hook output
{
  "action": "restart",
  "handoff": "/path/to/handoff.md",
  "message": "Context limit reached, restarting with handoff..."
}
```

This would:
- Let Claude finish current tool operation
- Display a message to user
- Clean restart with handoff content injected

---

## 6. No Mid-Session Context Injection

### The Problem

`additionalContext` only works at SessionStart. There's no way to inject context mid-session (e.g., when resuming from handoff after restart).

### What We Built

We inject handoff content at SessionStart via the hook:

```json
{
  "additionalContext": "=== HANDOFF LOADED ===\n...\n=== END HANDOFF ==="
}
```

But if we want to inject context later (e.g., user runs `/handoff` command), we can't.

### Suggested Solution

**PromptSubmit hook with context injection:**
```json
{
  "hooks": {
    "PromptSubmit": [{
      "matcher": ".*",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/hooks/inject-context.sh"
      }]
    }]
  }
}
```

Where the hook can output:
```json
{
  "injectContext": "Additional context to add to this turn...",
  "continuePrompt": true
}
```

---

## 7. Auto-Compact Cannot Be Fully Disabled

### The Problem

Even with `autoCompact: false`, there appears to be a hard cutoff around 98% where something happens (possibly silent truncation or forced compaction).

### What We Observed

- Context works fine up to ~96%
- At ~98%, behavior becomes unpredictable
- We set our critical threshold at 96% to maintain a 4k token buffer

### Suggested Solution

**Explicit hard limit setting:**
```json
{
  "autoCompact": false,
  "contextHardLimit": 0.98,
  "contextHardLimitAction": "error"  // or "warn", "truncate"
}
```

And document clearly:
- What happens at the hard limit
- Whether any silent truncation occurs
- The exact token limit (is it truly 200k?)

---

## 8. Transcript Format Undocumented

### The Problem

We parse `.jsonl` transcript files to extract context usage, but the format is undocumented and could change.

### What We Depend On

```bash
# We look for this field in transcript JSON
"cache_read_input_tokens": 156234
```

### Suggested Solution

Either:
1. **Document the format** as stable API
2. **Provide an official API** for querying session info (preferred)
3. **Add deprecation warnings** if format will change

---

## 9. No Native Channel/Project System

### The Problem

Claude Code doesn't have a concept of "channels" or "projects" for organizing conversations. Different projects in different directories share the same conversation space.

### What We Built

A channel registry that maps directories to channel names:

```json
{
  "registry": {
    "/home/jesse/project-a": "project-a",
    "/home/jesse/project-b": "project-b",
    "/home/jesse": "global"
  }
}
```

Handoffs, archives, and state are organized by channel.

### Suggested Solution

**Native project/workspace support:**
```bash
claude --project "my-project"
# or auto-detect from .claude-project file in directory
```

With:
- Separate conversation history per project
- Project-specific settings
- Project-scoped MCP servers

---

## 10. No Persistent State API

### The Problem

There's no built-in way to persist state across sessions. MCP servers fill this gap, but:
- Require separate setup
- Add latency
- Not always reliable

### What We Built

We use `mcp-memory-keeper` for persistent state, but it's a workaround.

### Suggested Solution

**Built-in key-value store:**
```bash
# In Claude's context
claude.state.set("task_progress", "50%")
claude.state.get("task_progress")
```

Or exposed to hooks:
```bash
$CLAUDE_STATE_DIR=~/.claude/state/session-abc123/
```

---

## Summary of Requested Features

| Priority | Feature | Impact |
|----------|---------|--------|
| **HIGH** | Context usage API | Accurate monitoring |
| **HIGH** | ContextThreshold hook | Efficient critical detection |
| **HIGH** | Session ID in hooks | Multi-session support |
| **MEDIUM** | Disable context warning | Clean custom UI |
| **MEDIUM** | Graceful restart API | Better UX |
| **MEDIUM** | Document transcript format | Stability |
| **LOW** | Mid-session context injection | Flexibility |
| **LOW** | Native project system | Organization |

---

## Current Workaround Architecture

For reference, here's what we built to work around these limitations:

```
┌─────────────────────────────────────────────────────────────────┐
│                      claude-wrapper                              │
│  - Starts Claude with hooks configured                          │
│  - Monitors for restart signals                                 │
│  - Handles graceful restart with handoff                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   SessionStart Hook                              │
│  - Injects CRITICAL-RULES.md                                    │
│  - Loads handoff if available                                   │
│  - Initializes per-session status file                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PostToolUse Hook                               │
│  - Parses transcript for token count                            │
│  - Writes status to per-PID file                                │
│  - Triggers handoff at CRITICAL threshold                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Handoff System                                 │
│  - Creates handoff with session state                           │
│  - Manifest tracks active/consumed handoffs                     │
│  - Archive system for old handoffs/transcripts                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Contact

For questions about this implementation or to discuss these feature requests:

- **GitHub Issue:** https://github.com/anthropics/claude-code/issues/18417
- **Implementation:** https://github.com/itsjessedev/infrastructure (when public)

We're happy to collaborate on native implementations of any of these features.
