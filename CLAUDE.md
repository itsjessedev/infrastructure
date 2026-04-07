# Infrastructure Project

This repo manages devlab (dev environment), Unraid server config, system utilities, and self-hosted services. Sessions in `~/infrastructure` are for devlab/Unraid/connectivity/infra work.

## Architecture

### Devlab (dev-lab)
- **What:** Ubuntu Docker container on Unraid, macvlan network
- **LAN IP:** `192.168.99.84`, **SSH port:** `25831`
- **Home dir on host:** `/mnt/user/appdata/dev-lab/home` (bind-mounted to `/home/jesse`)
- **Startup script:** `/mnt/cache/appdata/dev-lab/start-devlab.sh` on Unraid
- **Container image:** `dev-lab:latest` (built locally on Unraid)

### Unraid (EldridgeServer)
- **LAN IP:** `192.168.99.83`, **Tailscale IP:** `100.105.135.31`
- **SSH:** `ssh -J desktop root@192.168.99.83` (can't reach from devlab directly due to macvlan isolation)
- **Tailscale:** Runs on Unraid host only. Forwards TS traffic to devlab via iptables DNAT.
- **Go script:** `/boot/config/go` (startup commands)

### Macvlan Isolation
Devlab and Unraid **cannot communicate directly** (macvlan limitation). A shim interface (`192.168.99.85`) on Unraid bridges this gap. Created automatically by `start-devlab.sh`.

To reach Unraid from devlab, proxy through desktop:
```bash
ssh -J desktop root@192.168.99.83 "<command>"
```

### Network

| Host | LAN IP | Tailscale IP | SSH Port |
|------|--------|-------------|----------|
| devlab | 192.168.99.84 | — (via Unraid) | 25831 |
| unraid | 192.168.99.83 | 100.105.135.31 | 22 |
| desktop | 192.168.99.145 | 100.125.236.116 | 22 |
| laptop | 192.168.99.220 | 100.68.237.46 | 22 |

Laptop reaches devlab via: `Laptop -> Tailscale -> Unraid (100.105.135.31:25831) -> iptables DNAT -> devlab (192.168.99.84:25831)`

## Key Files

| File | Purpose |
|------|---------|
| `docs/ssh-and-network-drives.md` | Complete SSH config, Samba, drive mappings, troubleshooting history |
| `docs/devlab-process-management.md` | OOM prevention, orphan cleanup, process watchdog, container memory limit |
| `docs/unraid-logging.md` | Unraid persistent logging framework — log paths, monitor intervals, auto-cleanup |
| `bin/claude-wrapper` | Claude Code wrapper with wall detection, auto-restart, cleanup |
| `claude-drop/main.py` | Claude Drop file sharing service (deployed to VPS) |
| `reddit-relay/` | Reddit relay service |
| `system-utilities/` | Shared binaries, scripts, claude commands |

## Working on Unraid

Since devlab can't reach Unraid directly, always use the desktop as a jump host:

```bash
# Run a command on Unraid
ssh -J desktop root@192.168.99.83 "command here"

# Interactive session
ssh -J desktop root@192.168.99.83
```

Desktop is at `192.168.99.145` and is reachable from devlab over LAN.

## Tailscale

- Tailscale runs on **Unraid only**, not on devlab
- Unraid forwards ports 25831 (SSH) and 445 (SMB) from Tailscale interface (currently `tailscale1`) to devlab
- Forwarding rules are in `start-devlab.sh` and recreated on container restart
- Subnet routes (`192.168.99.0/24`) are advertised but may need admin approval in the TS console
- Never install Tailscale inside the devlab container

## Services on Unraid (arr-network)

Docker bridge network `arr-network` runs media services:
- Radarr, Sonarr, Bazarr, qBittorrent, Jellyseerr, Prowlarr, Tautulli
- These are separate from devlab (which uses macvlan `br0`)

## System Health Check — MANDATORY

**This is NOT optional. Every session in `~/infrastructure` MUST run these checks before doing any other work. Do NOT skip this. Do NOT summarize without actually running the commands. Do NOT ask Jesse if he wants you to check — just do it.**

### When to run
- At the start of EVERY `~/infrastructure` session, immediately after pre-work git verification
- When Jesse asks about system health, logs, or status
- After any reboot or infrastructure change

### Log locations to check

Run all checks in parallel via SSH (`ssh -J desktop root@192.168.99.83`):

**1. Kernel & hardware errors:**
```bash
dmesg -T --level=err,warn,crit,alert,emerg | tail -30
```

**2. Syslog (recent errors/warnings):**
```bash
grep -iE 'error|fail|warn|crit|panic|oom|kill' /var/log/syslog | tail -20
```

**3. Persistent system logs (our logging framework):**
```bash
# Boot meta log
tail -20 /mnt/cache/appdata/system-logs/.meta.log
# Network alerts (macvlan shim, iptables DNAT, Tailscale)
grep -i 'ALERT\|WARNING' /mnt/cache/appdata/system-logs/network/network-*.log 2>/dev/null | tail -10
# Docker health warnings (OOM, restarts, crashes)
grep -i 'WARNING' /mnt/cache/appdata/system-logs/docker/health.log 2>/dev/null | tail -10
# SMART disk alerts
grep -i 'ERROR\|Pending\|Reallocated' /mnt/cache/appdata/system-logs/smart/smart-*.log 2>/dev/null | tail -10
# Disk space alerts
grep -i 'ALERT' /mnt/cache/appdata/system-logs/snapshots/diskspace.log 2>/dev/null | tail -5
```

**4. Boot logs (persistent across reboots):**
```bash
grep -iE 'error|fail|warn|crit|No such file' /boot/logs/syslog | tail -15
```

**5. Docker container status:**
```bash
# Crashed, OOM'd, or restarting containers
docker ps -a --format '{{.Names}}|{{.Status}}|{{.State}}' | grep -v running
# Restart counts and OOM flags
docker inspect --format '{{.Name}} restarts={{.RestartCount}} oom={{.State.OOMKilled}}' $(docker ps -aq) 2>/dev/null | grep -E 'oom=true|restarts=[1-9]'
```

**6. SMART disk health:** Still check silently, but do NOT report unless critical (SMART overall health = FAILED, or pending sectors jump by 50+ since last check). Known baseline: disk2 has 72 pending sectors as of 2026-03-14. Disk space warnings are also suppressed — drives are pending replacement.
```bash
for dev in /dev/sd{b,c,d,e}; do
  smartctl -H "$dev" 2>/dev/null | grep -q FAILED && echo "CRITICAL: $dev SMART FAILED"
done
```

**7. Process health (inside devlab):**
```bash
# Run from devlab (not via SSH to Unraid)
cat /tmp/process-alerts.txt 2>/dev/null || echo "No alerts"
cat /tmp/process-health.log 2>/dev/null | tail -5
```

**8. Tailscale & network plumbing:**
```bash
tailscale status | head -5
ip addr show macvlan_shim 2>/dev/null | head -2 || echo "WARNING: macvlan_shim missing"
iptables -t nat -L PREROUTING -n 2>/dev/null | grep -E '25831|445' || echo "WARNING: DNAT rules missing"
```

### Reporting

After checking, report a compact summary. Only expand on items that need attention:
```
## Infra Health
- Kernel/dmesg: OK or [issues]
- Syslog: OK or [issues]
- System logs: OK or [issues]
- Boot logs: OK or [issues]
- Docker: N running, N stopped [details if abnormal]
- Processes: sessions=N mem=N% zombies=N orphans=N [alert if any nonzero]
- SMART: OK or [drive issues]
- Network: shim=OK/MISSING ts=OK/DOWN dnat=OK/MISSING
```

If everything is clean, a one-line "Infra health: all clear" is fine. If ANY issue is found, flag it clearly — especially SMART warnings, OOM kills, or missing network plumbing.

### Process buildup response — MANDATORY

**When Jesse asks you to investigate process buildups, orphans, zombies, or high memory usage, you MUST:**

1. **Investigate carefully** — determine if each process is an orphan or intentional. Many background processes are expected (sync daemons, monitors, sleep loops). Only flag processes that are ACCUMULATING or have no reason to exist.
2. **Kill** only the actual orphans/zombies, not legitimate background processes
3. **Add them to the auto-cleanup** — update `~/bin/ssh-session-cleanup` (PAM hook) and/or `~/bin/process-health-check` (monitor's `KNOWN_BACKGROUND` allowlist if legitimate, or detection patterns if orphan-prone). Do NOT just kill them and move on. The same type of process must never appear as a buildup again.
4. **Verify** the cleanup rules work by confirming the orphans are gone and the new rules would catch them
5. **Report** what you changed — which processes were orphans vs legitimate, and what was added to auto-cleanup

The goal is that every time a new type of orphan/zombie is discovered, the system learns to handle it. Over time, the auto-cleanup becomes comprehensive and nothing slips through.

**Key files:**
- `~/bin/ssh-session-cleanup` — PAM hook, kills all descendants on SSH disconnect (instant)
- `~/bin/process-health-check` — monitor, runs every 5 min, writes alerts to `/tmp/process-alerts.txt`
- `~/.config/container-startup.sh` — sets up PAM hook + monitor on container start
- Container memory limit: 12GB (`--memory=12g` in `start-devlab.sh`)

### Known issues (do NOT nag about these)

- **Disk drives:** Pending sectors on disk2 (72 as of 2026-03-14), disks 1+2 nearly full, no parity. Jesse is aware — drives pending replacement. **Only report if a drive's SMART overall health changes to FAILED or pending sectors spike dramatically (50+). Otherwise stay silent about disk issues.**
- **Overseerr container log:** ~290MB, Prowlarr: ~365MB — no Docker log rotation configured
