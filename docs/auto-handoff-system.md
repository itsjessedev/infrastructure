# Auto-Handoff System Documentation

> **Last updated:** 2026-02-02
> **Status:** WORKING - Full walk-away automation tested and confirmed
> **Author:** Jesse + Claude (Opus 4.5)

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Components](#components)
4. [Complete Code](#complete-code)
5. [The Full Flow](#the-full-flow)
6. [Configuration](#configuration)
7. [Troubleshooting](#troubleshooting)
8. [Edge Cases & Limitations](#edge-cases--limitations)
9. [Development History](#development-history)

---

## Overview

### Problem Statement

Claude Code has a context window limit. When working on long tasks, the context fills up and triggers "auto-compact" which summarizes the conversation, losing detailed state. This breaks complex multi-step workflows and requires manual re-orientation.

### Solution

The auto-handoff system allows Claude to work autonomously for extended periods by:

1. **Monitoring** - Detecting when context is approaching limits
2. **Saving** - Writing task state to a handoff file before it's too late
3. **Signaling** - Creating a restart signal file
4. **Killing** - Background monitor terminates the Claude process
5. **Restarting** - Wrapper script starts fresh Claude with continuation prompt
6. **Instant Resume** - Hook includes handoff content inline (zero tool calls needed)

### Key Innovation

Unlike auto-compact which loses detail, this system:
- Preserves exact task state (user-defined, not summarized)
- Maintains file references and progress markers
- Allows Claude to pick up exactly where it left off
- Requires ZERO user intervention after initial start

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         WRAPPER SCRIPT                                   │
│                    ~/infrastructure/bin/claude-wrapper                   │
│                                                                          │
│  ┌────────────────────┐    ┌────────────────────────────────────────┐   │
│  │  Background        │    │  Main Loop                              │   │
│  │  Monitor           │    │                                         │   │
│  │  (subshell)        │    │  while true; do                         │   │
│  │                    │    │    start_monitor()                      │   │
│  │  Checks every 0.5s │    │    run Claude                           │   │
│  │  for restart signal│───▶│    check exit code                      │   │
│  │                    │    │    if killed by monitor → restart       │   │
│  │  Kills Claude when │    │    else → exit                          │   │
│  │  signal found      │    │  done                                   │   │
│  └────────────────────┘    └────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         CLAUDE CODE SESSION                              │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  PostToolUse Hook: context-monitor.sh                            │    │
│  │                                                                   │    │
│  │  After EVERY tool call:                                          │    │
│  │  1. Find current transcript file                                 │    │
│  │  2. Check file size                                              │    │
│  │  3. Write STATUS:SIZE to ~/.claude/.context-status               │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                      │                                   │
│                                      ▼                                   │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Claude's Behavior (per CLAUDE.md instructions)                  │    │
│  │                                                                   │    │
│  │  1. Periodically check ~/.claude/.context-status                 │    │
│  │  2. When CRITICAL:                                               │    │
│  │     a. Create handoff file with task state                       │    │
│  │     b. Create restart signal file                                │    │
│  │     c. Make one more tool call (triggers monitor check)          │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                      │                                   │
└──────────────────────────────────────│───────────────────────────────────┘
                                       │
            ┌──────────────────────────┴──────────────────────────┐
            ▼                                                      ▼
┌───────────────────────────┐                    ┌───────────────────────────┐
│  ~/.claude/.restart-session│                    │  ~/.claude/handoff/       │
│  (contains working dir)   │                    │  {channel}-{pid}.md       │
│                           │                    │  (contains task state)    │
└───────────────────────────┘                    └───────────────────────────┘
            │
            │  Monitor detects this file
            ▼
┌───────────────────────────────────────────────────────────────────────────┐
│  KILL & RESTART SEQUENCE                                                   │
│                                                                            │
│  1. Monitor sees ~/.claude/.restart-session exists                         │
│  2. Monitor finds Claude PID (child of wrapper, excluding self)            │
│  3. Monitor creates ~/.claude/.killed-by-monitor flag                      │
│  4. Monitor sends SIGTERM to Claude, waits 1s, sends SIGKILL               │
│  5. Monitor exits                                                          │
│  6. Wrapper sees Claude exited + killed-by-monitor flag exists             │
│  7. Wrapper increments restart count, cleans up signal files               │
│  8. Wrapper starts new Claude with prompt: "Continue from handoff..."      │
│  9. New Claude reads CLAUDE.md, sees prompt, finds handoff file            │
│  10. New Claude loads state and continues working                          │
└───────────────────────────────────────────────────────────────────────────┘
```

### File Relationships

```
~/.claude/
├── .context-status-{PID}    # Per-wrapper status: "CRITICAL:192000tok (96%)"
├── .current-session-{PID}   # Per-wrapper: session_id:transcript_path:wrapper_pid
├── .restart-session-{PID}   # Per-wrapper restart signal: session_id:dir:handoff_id
├── .killed-by-monitor-{PID} # Per-wrapper: signals intentional kill
├── .critical-triggered-{ID} # Per-session: prevents duplicate handoffs
├── .wrapper-pid             # Legacy: current wrapper PID
├── .test-mode               # Optional: enables low thresholds (5%)
├── .last-handoff-id         # Written by handoff: ID for restart signal
├── auto-session.log         # Wrapper logging
├── handoff/
│   ├── {channel}-CURRENT.md # Active handoff file
│   ├── {channel}.manifest.json  # Handoff tracking (active/consumed)
│   ├── {channel}.lock.d/    # Lock directory for parallel sessions
│   └── archive/             # Consumed handoffs
├── hooks/
│   ├── context-monitor.sh   # PostToolUse hook
│   ├── session-start-from-handoff.sh  # SessionStart hook
│   ├── pre-compact-handoff.sh  # Creates handoff at CRITICAL
│   ├── zombie-killer.sh     # Cleanup hook
│   ├── archive-manager.sh   # Transcript archival
│   └── lib/
│       ├── get-channel.sh   # Channel detection utility
│       └── handoff-manifest.sh  # Manifest system functions
├── channel-registry.json    # Directory → channel mapping
└── settings.json            # Hook configuration

~/infrastructure/bin/
└── claude-wrapper           # Main wrapper script
```

---

## Components

### 1. Context Monitor Hook

**File:** `~/.claude/hooks/context-monitor.sh`
**Type:** PostToolUse hook (runs after every tool call)
**Purpose:** Track context size and update status file

**How it works:**
1. Finds the most recent `.jsonl` transcript file in `~/.claude/projects/`
2. Gets file size in bytes using `stat`
3. Compares against thresholds
4. Writes `STATUS:SIZE` to `~/.claude/.context-status`

**Thresholds:**

| Mode | EARLY_WARN | WARN | CRITICAL |
|------|------------|------|----------|
| Production | 4MB | 6MB | 8MB |
| Test | 5KB | 10KB | 15KB |

**Why silent output:** Claude Code shows "hook error" when hooks output JSON with `additionalContext`. Silent hooks that write to files are more reliable.

### 2. Wrapper Script

**File:** `~/infrastructure/bin/claude-wrapper`
**Purpose:** Wrap Claude with auto-restart capability

**Key features:**
- Stores its PID in `~/.claude/.wrapper-pid`
- Starts a background monitor subprocess before each Claude run
- Passes `--dangerously-skip-permissions` by default
- On restart, passes continuation prompt to Claude
- Detects Ctrl+C (exit code 130) and exits cleanly without restart
- Logs all actions to `~/.claude/auto-session.log`

**Monitor subprocess:**
- Runs in background, checks for restart signal every 0.5s
- Uses `$BASHPID` (not `$$`) to get its own PID in subshell
- Finds Claude as child of wrapper, excluding itself
- Kills Claude with SIGTERM, then SIGKILL after 1s
- Sets `~/.claude/.killed-by-monitor` flag before killing

### 3. Session Start Hook

**File:** `~/.claude/hooks/session-start-from-handoff.sh`
**Type:** SessionStart hook
**Purpose:** Load handoff content instantly into session context

**How it works:**
1. Check if `~/.claude/.load-handoff` flag exists (set by wrapper on auto-restart)
2. Use atomic `mkdir`-based locking to handle parallel sessions
3. Find valid handoff (< 2 hours old, dead PID)
4. **INSTANT LOAD:** JSON-escape content and include directly in `additionalContext`
5. Delete handoff file after including content
6. Claude sees full handoff immediately - zero tool calls needed

**Conditions for auto-loading:**
- `~/.claude/.load-handoff` flag must exist (prevents stale handoffs on fresh starts)
- Handoff file exists for current channel
- Handoff is less than 2 hours old
- Handoff's PID (in filename) is dead (not another active session)

**Manual start behavior:**
- If handoffs exist but flag is absent, shows notification: "⚠️ PENDING HANDOFFS FOUND"
- User can choose to read manually or ignore

### 4. Channel Registry

**File:** `~/.claude/channel-registry.json`
**Purpose:** Map directories to logical channels for handoff organization

```json
{
  "registry": {
    "/home/jesse/handoff-test": "handoff-test",
    "/home/jesse/games/mmo-engine": "mmo-engine",
    "/home/jesse/junipr": "junipr",
    "/home/jesse": "global"
  }
}
```

**Matching:** Longest path prefix wins. `/home/jesse/games/mmo-engine/src` matches `mmo-engine`, not `global`.

### 5. Channel Detection Utility

**File:** `~/.claude/hooks/lib/get-channel.sh`
**Purpose:** Shared function for consistent channel detection

```bash
source ~/.claude/hooks/lib/get-channel.sh
CHANNEL=$(get_channel)  # or get_channel "/specific/path"
```

---

## Complete Code

### context-monitor.sh

```bash
#!/bin/bash
# Context Monitor - Check usage and warn when approaching limits

SESSION_DIR="$HOME/.claude/projects"
STATUS_FILE="$HOME/.claude/.context-status"
TEST_MODE_FILE="$HOME/.claude/.test-mode"

# Find main session transcript (not subagent files)
CURRENT_TRANSCRIPT=$(find "$SESSION_DIR" -maxdepth 2 -name "*.jsonl" -mmin -60 -type f 2>/dev/null | \
    grep -v "/subagents/" | \
    xargs -r ls -t 2>/dev/null | \
    head -1)

[ -z "$CURRENT_TRANSCRIPT" ] && exit 0
[ ! -f "$CURRENT_TRANSCRIPT" ] && exit 0

SIZE_BYTES=$(stat -c %s "$CURRENT_TRANSCRIPT" 2>/dev/null)
[ -z "$SIZE_BYTES" ] && exit 0

SIZE_KB=$((SIZE_BYTES / 1024))

# Display format
if [ "$SIZE_BYTES" -ge 1048576 ]; then
    SIZE_DISPLAY=$(awk "BEGIN {printf \"%.1fMB\", $SIZE_BYTES / 1048576}")
else
    SIZE_DISPLAY="${SIZE_KB}KB"
fi

# Thresholds
if [ -f "$TEST_MODE_FILE" ]; then
    EARLY_WARN_KB=5
    WARN_KB=10
    CRITICAL_KB=15
else
    EARLY_WARN_KB=$((4 * 1024))
    WARN_KB=$((6 * 1024))
    CRITICAL_KB=$((8 * 1024))
fi

if [ "$SIZE_KB" -ge "$CRITICAL_KB" ]; then
    echo "CRITICAL:${SIZE_DISPLAY}" > "$STATUS_FILE"
elif [ "$SIZE_KB" -ge "$WARN_KB" ]; then
    echo "WARN:${SIZE_DISPLAY}" > "$STATUS_FILE"
elif [ "$SIZE_KB" -ge "$EARLY_WARN_KB" ]; then
    echo "EARLY_WARN:${SIZE_DISPLAY}" > "$STATUS_FILE"
else
    echo "OK:${SIZE_DISPLAY}" > "$STATUS_FILE"
fi

# Silent exit - Claude checks status file periodically per CLAUDE.md instructions
exit 0
```

### claude-wrapper (complete)

```bash
#!/bin/bash
# Claude Auto-Session Wrapper
#
# Only restarts if the monitor killed Claude (not on manual Ctrl+C exit)

LOG_FILE="$HOME/.claude/auto-session.log"
RESTART_FILE="$HOME/.claude/.restart-session"
HANDOFF_DIR="$HOME/.claude/handoff"
LOAD_HANDOFF_FLAG="$HOME/.claude/.load-handoff"
WRAPPER_PID_FILE="$HOME/.claude/.wrapper-pid"
KILLED_BY_MONITOR="$HOME/.claude/.killed-by-monitor"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"
}

find_claude() {
    for c in "$HOME/.local/bin/claude" "/usr/local/bin/claude" "/usr/bin/claude"; do
        [ -x "$c" ] && [ ! "$c" -ef "$0" ] && echo "$c" && return
    done
    command -v claude
}

CLAUDE_BIN=$(find_claude)
[ -z "$CLAUDE_BIN" ] && echo "ERROR: Cannot find claude" && exit 1

CLAUDE_DEFAULT_FLAGS="--dangerously-skip-permissions"

source "$HOME/.claude/hooks/lib/get-channel.sh" 2>/dev/null || true

get_current_channel() {
    type get_channel &>/dev/null && get_channel "$1" || echo "global"
}

find_handoff_for_channel() {
    local channel="$1"
    for f in "$HANDOFF_DIR/${channel}"-*.md "$HANDOFF_DIR/${channel}.md"; do
        [ -f "$f" ] || continue
        local age=$(( $(date +%s) - $(stat -c %Y "$f" 2>/dev/null || echo 0) ))
        [ "$age" -gt 7200 ] && continue
        echo "$f"
        return
    done
}

# Store our PID
echo $$ > "$WRAPPER_PID_FILE"

# Monitor PID will be set per-iteration
MONITOR_PID=""

cleanup() {
    rm -f "$WRAPPER_PID_FILE"
    [ -n "$MONITOR_PID" ] && kill $MONITOR_PID 2>/dev/null
}
trap cleanup EXIT

# Function to start monitor subprocess
start_monitor() {
    # Kill any existing monitor
    [ -n "$MONITOR_PID" ] && kill $MONITOR_PID 2>/dev/null

    (
        while true; do
            sleep 0.5
            [ ! -f "$WRAPPER_PID_FILE" ] && exit 0

            if [ -f "$RESTART_FILE" ]; then
                MY_PID=$BASHPID
                # Find Claude (child of wrapper that isn't this monitor subprocess)
                CLAUDE_PID=$(pgrep -P "$(cat "$WRAPPER_PID_FILE" 2>/dev/null)" 2>/dev/null | grep -v "^${MY_PID}$" | head -1)
                if [ -n "$CLAUDE_PID" ]; then
                    log "Monitor: Killing Claude PID $CLAUDE_PID (my PID: $MY_PID)"
                    # Mark that WE killed it (not user Ctrl+C)
                    touch "$KILLED_BY_MONITOR"
                    kill -TERM "$CLAUDE_PID" 2>/dev/null
                    sleep 1
                    kill -9 "$CLAUDE_PID" 2>/dev/null
                fi
                exit 0
            fi
        done
    ) &
    MONITOR_PID=$!
}

# Check for resume flags
USER_WANTS_RESUME=false
for arg in "$@"; do
    case "$arg" in
        -r|-c|--resume|--continue) USER_WANTS_RESUME=true ;;
    esac
done

RESTART_COUNT=0
MAX_RESTARTS=10
WORKING_DIR="${PWD}"

log "=== Wrapper $$ started in $WORKING_DIR ==="

while true; do
    # Clean up signals from previous iterations
    rm -f "$RESTART_FILE" "$KILLED_BY_MONITOR"

    CHANNEL=$(get_current_channel "$WORKING_DIR")
    log "Channel: $CHANNEL, Restart #$RESTART_COUNT"

    # Set load flag if needed
    if [ $RESTART_COUNT -eq 0 ] && [ "$USER_WANTS_RESUME" = true ]; then
        touch "$LOAD_HANDOFF_FLAG"
    elif [ $RESTART_COUNT -gt 0 ]; then
        touch "$LOAD_HANDOFF_FLAG"
    fi

    # Start fresh monitor for this Claude instance
    start_monitor
    log "Monitor PID: $MONITOR_PID"

    # Run Claude
    if [ $RESTART_COUNT -eq 0 ]; then
        log "Starting: $CLAUDE_BIN $CLAUDE_DEFAULT_FLAGS $*"
        $CLAUDE_BIN $CLAUDE_DEFAULT_FLAGS "$@"
    else
        log "Restarting with handoff prompt"
        $CLAUDE_BIN $CLAUDE_DEFAULT_FLAGS "Continue from handoff. Check ~/.claude/handoff/ for handoff file, read it, then continue the task."
    fi
    EXIT_CODE=$?
    log "Claude exited: $EXIT_CODE"

    # Exit code 130 = SIGINT (Ctrl+C) - user wants to quit, never restart
    if [ $EXIT_CODE -eq 130 ]; then
        log "User pressed Ctrl+C - clean exit, no restart"
        rm -f "$RESTART_FILE" "$KILLED_BY_MONITOR"
        break
    fi

    # Only restart if MONITOR killed Claude (not user Ctrl+C)
    if [ -f "$KILLED_BY_MONITOR" ]; then
        rm -f "$KILLED_BY_MONITOR"

        if [ -f "$RESTART_FILE" ]; then
            SIGNAL_DIR=$(cat "$RESTART_FILE" 2>/dev/null)
            log "Auto-restart triggered (monitor killed session)"
            rm -f "$RESTART_FILE"

            [ -n "$SIGNAL_DIR" ] && [ -d "$SIGNAL_DIR" ] && WORKING_DIR="$SIGNAL_DIR" && cd "$WORKING_DIR"

            RESTART_COUNT=$((RESTART_COUNT + 1))
            [ $RESTART_COUNT -ge $MAX_RESTARTS ] && echo "Max restarts reached" && exit 1

            echo ""
            echo "=== Auto-restarting (#$RESTART_COUNT) ==="
            echo ""
            # Extra cleanup before restart to prevent stale signals
            rm -f "$RESTART_FILE" "$KILLED_BY_MONITOR"
            sleep 1
            continue
        fi
    fi

    # Clean exit - don't restart
    rm -f "$RESTART_FILE"  # Clean up any stale signal

    HANDOFF=$(find_handoff_for_channel "$CHANNEL")
    [ -n "$HANDOFF" ] && echo "Handoff at: $HANDOFF (run with wrapper to auto-load)"

    log "Clean exit"
    break
done

log "=== Wrapper finished ==="
exit $EXIT_CODE
```

### get-channel.sh

```bash
#!/bin/bash
# Channel detection utility - shared by all hooks

REGISTRY_FILE="$HOME/.claude/channel-registry.json"

get_channel() {
    local cwd="${1:-$PWD}"

    if [ ! -f "$REGISTRY_FILE" ]; then
        echo "global"
        return
    fi

    local best_match=""
    local best_channel="global"

    while IFS=: read -r path channel; do
        path=$(echo "$path" | tr -d ' "' | sed 's/,$//')
        channel=$(echo "$channel" | tr -d ' "' | sed 's/,$//')

        if [[ "$cwd" == "$path"* ]]; then
            if [ ${#path} -gt ${#best_match} ]; then
                best_match="$path"
                best_channel="$channel"
            fi
        fi
    done < <(grep -E '^\s*"/' "$REGISTRY_FILE" | sed 's/^\s*//')

    echo "$best_channel"
}

# If sourced, function is available. If run directly, output channel.
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    get_channel "$@"
fi
```

---

## The Full Flow

### Step-by-Step Execution

```
TIME    ACTION                                      FILES AFFECTED
─────   ──────────────────────────────────────────  ─────────────────────────
T+0     User runs: ~/infrastructure/bin/claude-wrapper

T+0.1   Wrapper writes PID to file                  ~/.claude/.wrapper-pid
        Wrapper starts monitor subprocess           (background process)
        Wrapper runs: claude --dangerously-skip-permissions

T+1     Claude starts, loads CLAUDE.md
        User begins working with Claude

T+N     [After each tool call]
        Hook runs context-monitor.sh
        Hook checks transcript size                 ~/.claude/projects/.../*.jsonl
        Hook writes status                          ~/.claude/.context-status

T+X     Claude (per CLAUDE.md) checks status
        Status shows "CRITICAL:7.5MB"

T+X+1   Claude creates handoff file                 ~/.claude/handoff/{channel}-{pid}.md
        Claude creates restart signal               ~/.claude/.restart-session
        Claude makes one more tool call

T+X+1.5 Monitor (checking every 0.5s) sees signal
        Monitor finds Claude PID via pgrep
        Monitor creates killed-by-monitor flag      ~/.claude/.killed-by-monitor
        Monitor sends SIGTERM to Claude

T+X+2.5 Monitor sends SIGKILL to Claude
        Monitor exits

T+X+3   Wrapper sees Claude exited
        Wrapper checks: killed-by-monitor exists? YES
        Wrapper checks: restart-session exists? YES
        Wrapper increments restart count
        Wrapper cleans up signal files
        Wrapper displays "=== Auto-restarting (#1) ==="

T+X+4   Wrapper starts new monitor
        Wrapper runs: claude --dangerously-skip-permissions \
                      "Continue from handoff..."

T+X+5   New Claude starts, loads CLAUDE.md
        Claude sees prompt about handoff
        Claude finds handoff file
        Claude reads task state
        Claude announces: "Continuing from handoff..."
        Claude deletes handoff file
        Claude continues working
```

### Handoff File Format

```markdown
# Handoff State

**Task:** [What was being worked on]
**Progress:** [What's been completed]
**Current File:** [File being edited, if any]
**Next Steps:** [What to do next]

## Context
[Any important context that would be lost]

## Commands in Progress
[Any multi-step operations that were interrupted]
```

---

## Configuration

### settings.json Hook Configuration

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "$HOME/.claude/hooks/context-monitor.sh",
            "timeout": 5
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "command",
            "command": "$HOME/.claude/hooks/session-start-from-handoff.sh"
          }
        ]
      }
    ]
  }
}
```

### CLAUDE.md Instructions (Add to Project)

```markdown
## Auto-Handoff Protocol

**Periodically check context status:**
```bash
cat ~/.claude/.context-status
```

**When status shows CRITICAL:**
1. Stop current task at safe point
2. Create handoff file:
```bash
cat > ~/.claude/handoff/{channel}-$$.md << 'EOF'
# Handoff State
**Task:** [description]
**Progress:** [what's done]
**Next:** [next steps]
EOF
```
3. Create restart signal:
```bash
echo "$(pwd)" > ~/.claude/.restart-session
```
4. Make one more tool call (triggers the kill)

**On startup with "Continue from handoff" prompt:**
1. Check for handoff: `ls ~/.claude/handoff/*.md`
2. Read the handoff file
3. Report recovered state
4. Delete handoff file
5. Continue task
```

---

## Troubleshooting

### Monitor Not Killing Claude

**Symptom:** Handoff created, restart signal exists, but Claude keeps running.

**Check 1:** Is the wrapper running?
```bash
cat ~/.claude/.wrapper-pid
ps aux | grep claude-wrapper
```

**Check 2:** Is the monitor subprocess running?
```bash
# Monitor is a child of wrapper
pgrep -P $(cat ~/.claude/.wrapper-pid)
```

**Check 3:** Can monitor find Claude?
```bash
# This is what monitor does
WRAPPER_PID=$(cat ~/.claude/.wrapper-pid)
pgrep -P $WRAPPER_PID
# Should show at least 2 PIDs: monitor and Claude
```

**Common fix:** The monitor might have exited. Restart the wrapper.

### Ctrl+C Triggers Restart

**Symptom:** Pressing Ctrl+C restarts Claude instead of exiting.

**Cause:** Exit code isn't 130, or stale signal files exist.

**Fix:** The wrapper now explicitly checks for exit code 130. If still happening:
```bash
rm -f ~/.claude/.restart-session ~/.claude/.killed-by-monitor
```

### "Hook Error" Messages

**Symptom:** "PostToolUse:Read hook error" appears after every tool.

**Cause:** Hook outputting JSON that Claude Code can't display.

**Fix:** Hooks should be silent (exit 0 with no output). Write to files instead.

### New Session Doesn't Continue

**Symptom:** After restart, Claude waits for input instead of continuing.

**Cause:** No continuation prompt passed on restart.

**Fix:** Wrapper should pass prompt on restart:
```bash
$CLAUDE_BIN "Continue from handoff. Check ~/.claude/handoff/..."
```

### Monitor Kills Itself

**Symptom:** Log shows monitor killing its own PID.

**Cause:** Using `$$` instead of `$BASHPID` in subshell.

**Fix:** In monitor subshell, use `$BASHPID` to get actual subprocess PID:
```bash
MY_PID=$BASHPID  # NOT $$
```

### Wrong Channel Detected

**Symptom:** Handoff saved to wrong channel.

**Fix:** Always detect channel dynamically:
```bash
source ~/.claude/hooks/lib/get-channel.sh
CHANNEL=$(get_channel)
```

---

## Edge Cases & Limitations

### Limitations

1. **Transcript detection is approximate** - Hook finds most recent transcript across all projects, not necessarily current session. Works for triggering but may show wrong size.

2. **Requires CLAUDE.md cooperation** - Claude must be instructed to check status and create handoffs. Without proper CLAUDE.md, system won't work.

3. **No state persistence beyond handoff file** - Memory-keeper integration is separate. Handoff files are simple markdown.

4. **Max 10 restarts** - Wrapper limits restarts to prevent infinite loops.

5. **2-hour handoff expiry** - Old handoffs are ignored to prevent loading stale state.

### Edge Cases Handled

1. **Parallel sessions** - PID-based handoff files prevent conflicts. Each session has its own handoff.

2. **Clean exit vs kill** - `killed-by-monitor` flag distinguishes intentional kills from user exits.

3. **Ctrl+C during handoff** - Exit code 130 detection prevents restart.

4. **Stale signal files** - Cleaned up at start of each loop iteration.

5. **Monitor subprocess death** - New monitor started before each Claude invocation.

### Not Handled (Known Gaps)

1. **Network interruption** - If connection drops, no handoff created.

2. **Crash before handoff** - If Claude crashes before creating handoff, state lost.

3. **Very large handoffs** - No size limit on handoff files (could get large).

4. **Concurrent wrapper instances** - Multiple wrappers might conflict.

---

## Development History

### Session 1 (2026-02-01)
- Initial implementation of context-monitor hook
- First version of wrapper script
- Discovered `additionalContext` doesn't display in Claude Code

### Session 2 (2026-02-01 - 2026-02-02)
- Fixed wrapper to use background monitor instead of backgrounding Claude
- Fixed Ctrl+C handling (exit code 130)
- Fixed monitor killing itself (`$BASHPID` vs `$$`)
- Fixed monitor not restarting with each Claude instance
- Added continuation prompt on restart
- **FULL SYSTEM WORKING**

### Key Bugs Fixed

| Bug | Symptom | Fix |
|-----|---------|-----|
| Monitor killing itself | Log shows same PID for monitor and "Claude" | Use `$BASHPID` not `$$` |
| Monitor not persisting | Second restart didn't work | Start new monitor each iteration |
| Ctrl+C restart | User exit triggered restart | Check exit code 130 |
| Hook errors | "hook error" spam | Silent hooks, write to files |
| Session not continuing | New session waited for input | Pass prompt on restart |

---

## Testing

### Quick Test
```bash
~/handoff-test/run-test.sh
# Say "go" when prompted
# Watch for automatic restart and continuation
```

### Manual Test
```bash
# Terminal 1: Watch logs
tail -f ~/.claude/auto-session.log

# Terminal 2: Run wrapper
~/infrastructure/bin/claude-wrapper

# In Claude: work until context fills, or manually:
echo "test" > ~/.claude/.restart-session

# Should see kill and restart in logs
```

### Verify Components
```bash
# Test channel detection
~/.claude/hooks/lib/get-channel.sh

# Test context monitor
~/.claude/hooks/context-monitor.sh
cat ~/.claude/.context-status

# Check wrapper can find Claude
which claude
ls -la ~/.local/bin/claude
```

---

## Dependencies

### Required

| Dependency | Purpose | Installation |
|------------|---------|--------------|
| Claude Code CLI | The AI assistant | `npm install -g @anthropic-ai/claude-code` |
| Node.js 18+ | Runtime for MCPs | Via nvm or package manager |
| mcp-memory-keeper | Persistent context storage | `claude mcp add memory-keeper -- npx mcp-memory-keeper` |

### Optional

| Dependency | Purpose | Installation |
|------------|---------|--------------|
| context7 | Documentation lookup | Via Claude plugins |
| playwright | Browser automation | Via Claude plugins |

### memory-keeper MCP Setup

```bash
# Add memory-keeper to user config (available in all projects)
claude mcp add memory-keeper -- npx mcp-memory-keeper

# Verify it's connected
claude mcp list
# Should show: memory-keeper: npx mcp-memory-keeper - ✓ Connected

# Data is stored in ~/mcp-data/memory-keeper/context.db
```

---

## Wrapper CLI Usage

```bash
# Fresh session (default) - ignores any existing handoffs
claude

# Load handoff if one exists (manual failsafe)
claude --handoff
claude -h

# Bypass wrapper entirely
claude-direct

# Auto-restart after context fills continues automatically
# (no flag needed - wrapper handles this)
```

---

## Session Transfer (Moving Conversations)

To move a conversation to a different project directory:

### 1. Find the session ID

```bash
ls -lt ~/.claude/projects/-home-jesse/*.jsonl | head -1
# Most recently modified .jsonl is usually the current session
```

### 2. Create target project directory

```bash
mkdir -p ~/.claude/projects/-home-jesse-your-project-name
# Pattern: dashes replace slashes in path
```

### 3. Copy the session file

```bash
cp ~/.claude/projects/-home-jesse/SESSION_ID.jsonl \
   ~/.claude/projects/-home-jesse-your-project-name/
```

### 4. Create sessions-index.json

```json
{
  "version": 1,
  "entries": [
    {
      "sessionId": "SESSION_ID_HERE",
      "fullPath": "/home/USER/.claude/projects/-home-USER-your-project-name/SESSION_ID.jsonl",
      "fileMtime": TIMESTAMP_MS,
      "firstPrompt": "First message from user...",
      "summary": "Brief description of conversation",
      "messageCount": N,
      "created": "ISO_DATE",
      "modified": "ISO_DATE",
      "gitBranch": "",
      "projectPath": "/home/USER/your/project/path",
      "isSidechain": false
    }
  ],
  "originalPath": "/home/USER/your/project/path"
}
```

### 5. Resume in new location

```bash
cd /home/USER/your/project/path && claude -r
```

---

## Archive System

### Archive Location

```
~/.claude/archives/{channel}/
├── {uuid}-{timestamp}.jsonl.gz
└── ...
```

### Archive a Conversation

```bash
# Gzip and move to archives
gzip -c ~/.claude/projects/{project}/{uuid}.jsonl > \
    ~/.claude/archives/{channel}/{uuid}-$(date +%Y%m%d-%H%M%S).jsonl.gz

# Remove original
rm ~/.claude/projects/{project}/{uuid}.jsonl
rm -r ~/.claude/projects/{project}/{uuid}/  # subagents dir
```

### Access Archived Conversations

```bash
# List archives for a channel
ls ~/.claude/archives/{channel}/

# Read archived conversation
zcat ~/.claude/archives/{channel}/{uuid}-{timestamp}.jsonl.gz | less

# Search across archives
zgrep "search term" ~/.claude/archives/{channel}/*.gz
```

### Archive Criteria (Default)

- Conversations older than 10 days → Archive
- Test/demo conversations → Archive
- Active work (last 10 days) → Keep

---

## Backup & Restore

### Create Backup

```bash
BACKUP_DIR="/tmp/claude-backups/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r ~/.claude/projects "$BACKUP_DIR/"
cp -r ~/.claude/archives "$BACKUP_DIR/"
cp -r ~/.claude/hooks "$BACKUP_DIR/"
cp ~/.claude/channel-registry.json "$BACKUP_DIR/"
cp ~/.claude/settings.json "$BACKUP_DIR/"
cp ~/infrastructure/bin/claude-wrapper "$BACKUP_DIR/"
echo "Backup at: $BACKUP_DIR"
```

### Restore from Backup

```bash
BACKUP_DIR="/tmp/claude-backups/TIMESTAMP"
cp -r "$BACKUP_DIR/projects" ~/.claude/
cp -r "$BACKUP_DIR/archives" ~/.claude/
cp -r "$BACKUP_DIR/hooks" ~/.claude/
cp "$BACKUP_DIR/channel-registry.json" ~/.claude/
cp "$BACKUP_DIR/settings.json" ~/.claude/
cp "$BACKUP_DIR/claude-wrapper" ~/infrastructure/bin/
echo "Restored from: $BACKUP_DIR"
```
