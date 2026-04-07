# Unraid System Logging

## Overview

Persistent logging is managed by `/mnt/cache/appdata/system-logs/setup-logging.sh` on Unraid. It runs at boot from `/boot/config/go` (inside a cache-wait subshell) and launches background monitors that log to `/mnt/cache/appdata/system-logs/`.

## Log Locations

### Our logging framework (`/mnt/cache/appdata/system-logs/`)

| Log | Path | Interval | What it captures |
|-----|------|----------|-----------------|
| Boot meta | `.meta.log` | on event | Startup sequence, rotation events, cleanup actions |
| Kernel | `kernel/kernel-{timestamp}.log` | real-time | dmesg -Tw continuous capture: OOM kills, hardware errors, crashes |
| Syslog | `syslog/syslog-{timestamp}.log` | real-time | tail -F /var/log/syslog |
| Docker events | `docker/events-{timestamp}.log` | real-time | Container start/stop/die/OOM/restart with exit codes |
| Docker health | `docker/health.log` | 60s | Container resource usage (CPU/mem/PIDs), state changes, OOM kills, restart counts |
| SMART disk health | `smart/smart-{timestamp}.log` | 6hr | Reallocated sectors, pending sectors, temperatures, error logs, overall health |
| System snapshots | `snapshots/system-{timestamp}.log` | 5min | Memory, CPU, load, swap, I/O, top processes, file descriptors, zombies |
| Disk space | `snapshots/diskspace.log` | 5min | Filesystem usage, alerts when >90% full |
| Temperatures | `snapshots/temperatures.log` | 5min | lm-sensors output |
| Network state | `network/network-{timestamp}.log` | 5min | Interface changes, iptables DNAT rules, macvlan shim status, Tailscale, devlab container status. Alerts on missing plumbing. |

PID files: `.pid.{monitor-name}` — tracked per monitor, cleaned up on boot.

### Unraid system logs

| Log | Path | Notes |
|-----|------|-------|
| Live syslog | `/var/log/syslog` | Volatile, lost on reboot |
| Persistent syslog | `/boot/logs/syslog` | Copied from /var/log/syslog by go script, survives reboots. Rotated to syslog.1-5. |
| Docker daemon | `/var/log/docker.log` | |
| Tailscale | `/var/log/tailscale.log` | |
| Unraid API | `/var/log/graphql-api.log` | |
| Boot watchdog | `/boot/logs/watchdog.log` | |
| Container logs | `/var/lib/docker/containers/{id}/{id}-json.log` | Per-container, no rotation configured |

### Diagnostics

| File | Path |
|------|------|
| Unraid diagnostics | `/boot/logs/eldridgeserver-diagnostics-*.zip` |

## Auto-cleanup

Runs daily inside the logging script:
- Deletes log files older than 30 days
- Hard cap at 500MB total — prunes compressed archives first, then rotated files, then oldest logs
- Never touches current boot's logs or scripts
- Per-file rotation at 50MB before archiving

## Checking logs

See the "System Health Check" section in `/home/jesse/infrastructure/CLAUDE.md` for the mandatory session-start check commands.
