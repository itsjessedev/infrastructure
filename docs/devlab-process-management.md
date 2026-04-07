# Devlab Process Management & OOM Prevention

> Multi-layer system to prevent orphaned processes from accumulating and OOMing the devlab container or Unraid host.
> Last updated: 2026-04-06

---

## Background

Devlab runs Claude/Codex CLI sessions over SSH. When SSH disconnects unexpectedly (broken pipe, network blip, container restart), child processes spawned by tool calls (rg, find, grep, python3, node, etc.) sometimes escape their parent's process group and survive as orphans reparented to PID 1.

These orphans accumulate over days/weeks. Eventually they consume enough memory to trigger the host OOM killer, which can kill Docker daemon and crash the entire Unraid server (this happened on 2026-04-06 — recovery required physical server reboot).

---

## The Defense Layers

### Layer 1: SSH Keepalives (prevention)

If SSH never disconnects, processes never orphan. See `ssh-and-network-drives.md` for full keepalive config. Both client-side and server-side keepalives are configured with appropriate timeouts.

### Layer 2: PAM Session Cleanup (instant cleanup on disconnect)

**File:** `~/bin/ssh-session-cleanup`
**Hook:** `/etc/pam.d/sshd` — `session optional pam_exec.so type=close_session`

When SSH disconnects, PAM fires this script. It walks the process tree from the dying sshd PID and kills every descendant. No polling, no delay.

**Limitation:** Processes that have already been reparented to PID 1 (orphaned before PAM fires) won't be caught by tree walking.

### Layer 3: Process Watchdog (active orphan killer)

**File:** `~/bin/claude-watchdog`
**Schedule:** Every 5 minutes via background loop in `~/.config/container-startup.sh`
**Log:** `/tmp/claude-watchdog.log`

Three passes:

1. **Tool-call orphans (instant kill)** — Common Claude tool subprocesses with `PPID=1` and no tty:
   ```
   rg, grep, fgrep, egrep, find, fd, ag, ack, sed, awk, cat, head, tail, sort,
   uniq, wc, cut, tr, tee, xargs, du, ls, stat, file, tree, tar, gzip, gunzip,
   bzip2, unzip, zip, curl, wget, jq, yq, python3, node, npm, npx, pnpm, yarn,
   git, rsync, scp, ssh, nc, nmap, ping, dig, nslookup, host, whois, md5sum,
   sha1sum, sha256sum, tsc, eslint, prettier, vite, webpack, next, nuxt,
   astro, playwright, puppeteer
   ```
   These should never outlive their parent SSH session — if they're orphaned, kill instantly.

2. **CLI process orphans (>5 min)** — `claude`, `node`, `codex` processes orphaned for more than 5 minutes.

3. **Runaway CPU (>10 min)** — Any detached process using >80% CPU for more than 10 minutes.

**Skip list (never killed):**
- Our own monitor loops (`claude-watchdog`, `process-health-check`)
- Codex sync daemon (`start-sync-daemon`, `codex.*sync`)
- `sleep` (used by monitor loops)
- `sshd` (the SSH server itself)

### Layer 4: Process Health Monitor (alerting)

**File:** `~/bin/process-health-check`
**Schedule:** Every 5 minutes via background loop in `~/.config/container-startup.sh`
**Alert file:** `/tmp/process-alerts.txt`
**Log:** `/tmp/process-health.log`

Lightweight monitor that tracks:
- Zombie processes (any count alerts)
- Orphaned claude/node/codex processes (any count alerts)
- Runaway detached processes using >80% CPU
- Total memory used by jesse processes (>60% threshold)

**Visibility:**
- Yellow banner shown on SSH login if `/tmp/process-alerts.txt` exists (via `~/.bashrc`)
- Checked at start of every infrastructure session by Claude (per `CLAUDE.md` mandatory rule)
- On-demand: `process-health-check` (interactive output)

**Allowlist:** `KNOWN_BACKGROUND` regex in the script — legitimate background processes that shouldn't trigger alerts. Add new entries here when a legitimate background is found.

### Layer 5: Container Memory Limit (final backstop)

**Configured in:** `start-devlab.sh` on Unraid (`docker run --memory=12g --memory-swap=14g`)
**Live update:** `docker update --memory=12g --memory-swap=14g dev-lab`

If all other layers fail and devlab consumes 12GB of RAM, the cgroup OOM killer fires INSIDE the container — kills the heaviest process. Host stays healthy. Docker auto-restarts the container if it dies (`--restart unless-stopped`).

This is the change that makes "physical server reboot" no longer necessary. Worst case now: container restart, host untouched.

---

## Operational Rules

### When investigating buildups (see `CLAUDE.md` mandatory rule)

1. **Investigate carefully** — determine if each process is an orphan or intentional. Many background processes are expected (sync daemons, monitors, sleep loops).
2. **Kill only actual orphans/zombies**, not legitimate background processes.
3. **Add to auto-cleanup** — update `~/bin/claude-watchdog` (`TOOL_ORPHAN_PATTERN` regex) and/or `~/bin/process-health-check` (`KNOWN_BACKGROUND` allowlist) so the same type never appears as a buildup again.
4. **Verify** the cleanup rules work.
5. **Report** what was added.

The goal is that every new orphan type discovered teaches the system. Auto-cleanup becomes more comprehensive over time.

---

## File Reference

| File | Purpose | Persistence |
|------|---------|-------------|
| `~/bin/ssh-session-cleanup` | PAM hook — kills descendants on SSH disconnect | Bind-mounted home dir |
| `~/bin/claude-watchdog` | Active orphan killer (every 5 min) | Bind-mounted home dir |
| `~/bin/process-health-check` | Lightweight monitor + alerts | Bind-mounted home dir |
| `~/.config/container-startup.sh` | Re-applies SSHD config + PAM hook + starts monitor loops | Bind-mounted home dir |
| `/etc/pam.d/sshd` | PAM hook entry (re-added on container start) | Container ephemeral |
| `/etc/ssh/sshd_config` | Keepalive config (re-applied on container start, baked in Dockerfile) | Container ephemeral |
| `start-devlab.sh` (Unraid) | Container `docker run` with `--memory=12g` | `/mnt/cache/appdata/dev-lab/` |
| `Dockerfile` (Unraid) | Bakes keepalive config into image | `/mnt/cache/appdata/dev-lab/` |

## Tuning

If alerts are too noisy or kills too aggressive, edit:

- **Add to allowlist:** `KNOWN_BACKGROUND` in `~/bin/process-health-check`
- **Remove from kill list:** `TOOL_ORPHAN_PATTERN` in `~/bin/claude-watchdog`
- **Change thresholds:** `MAX_AGE_CLI`, `MAX_AGE_RUNAWAY`, `ALERT_MEMORY_PCT`, `ALERT_ZOMBIE_COUNT`
- **Memory limit:** `docker update --memory=Xg --memory-swap=Yg dev-lab` (then update `start-devlab.sh` to persist)
