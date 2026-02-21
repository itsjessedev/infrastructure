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
