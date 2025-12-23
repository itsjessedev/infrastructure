# Desktop/Laptop Sync Setup

Syncthing + Tailscale configuration for syncing ~/home/jesse between machines.

## Tailscale

Both machines connected via Tailscale mesh VPN for direct P2P sync.

| Machine | Tailscale IP | Hostname |
|---------|--------------|----------|
| Desktop (WSL) | 100.125.236.116 | jesse-desktop |
| Laptop (WSL) | 100.78.98.78 | jesse-laptop |

**Login:** jeldridge2583@gmail.com

### Commands
```bash
# Check status
tailscale status

# Reconnect if needed
sudo tailscale up

# Admin console
# https://login.tailscale.com/admin/machines
```

## Syncthing

Syncs `~/` (home folder) between both machines.

### Device IDs

| Machine | Device ID |
|---------|-----------|
| Desktop | JZ33BAM-2R4H57F-NHNBK4U-NHEA4UJ-5HUXT5V-ESWXPJK-7HBKOCP-GGUCIAQ |
| Laptop | K42WERT-V243B4F-S47OD3C-CCUKUWG-LJZVYQR-GGHOJRE-QGVY7LA-QP727AB |

### Folder Config

- **Folder ID:** home
- **Path:** ~ (/home/jesse)
- **Type:** Send & Receive (bidirectional)

### Ignore Patterns

Located at `~/.stignore`:
- .ssh (machine-specific keys)
- .config/syncthing, .local/state/syncthing (prevent recursion)
- node_modules, venv, __pycache__ (regenerable)
- .cache, .npm, build, dist (caches/artifacts)
- .idea, .vscode, *.swp (IDE files)

### Commands
```bash
# Check status
systemctl --user status syncthing

# Restart
systemctl --user restart syncthing

# Web UI
# http://localhost:8384

# View logs
journalctl --user -u syncthing -f
```

### Config Location
- `~/.local/state/syncthing/config.xml`

## Addresses

Desktop connects to laptop at: `tcp://100.78.98.78:22000`
Laptop connects to desktop at: `tcp://100.125.236.116:22000`

## Troubleshooting

### Syncthing not syncing
1. Check both machines are on Tailscale: `tailscale status`
2. Check Syncthing is running: `systemctl --user status syncthing`
3. Check web UI for errors: http://localhost:8384

### WSL Auto-Start
WSL must be running for Syncthing to work.

**Solution:** In Windows Terminal Preview settings:
1. Enable "Launch on machine startup"
2. Set Ubuntu as the default profile

This opens a terminal window at boot, which starts WSL and keeps Syncthing running.

### Relay vs Direct
If Tailscale shows "relay" instead of "direct", the machines are going through a relay server (slower).
Usually fixes itself after a few minutes. Check `tailscale status` for connection type.
