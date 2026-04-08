# SSH Access & Network Drive Setup

> Complete reference for SSH configuration between all machines and L:/M: network drive mappings.
> Last updated: 2026-04-06

---

## Network Hosts

| Host | LAN IP | Tailscale IP | SSH Port | User | Notes |
|------|--------|-------------|----------|------|-------|
| devlab | 192.168.99.84 | — (via Unraid) | 25831 | jesse | Docker macvlan container on Unraid. |
| desktop | 192.168.99.145 | 100.125.236.116 | 22 | jesse | Windows 11 CMD |
| desktop-ubuntu | 192.168.99.145 | — | 2223 | jesse | WSL2 Ubuntu on desktop (direct SSH, systemd-managed) |
| laptop | 192.168.99.220 | 100.68.237.46 | 22 | jesse | Windows 10, WSL2 |
| unraid | 192.168.99.83 | 100.105.135.31 | 22 | root | Samba server for L: and M: drives. Runs Tailscale. Forwards TS traffic to devlab. |
| junipr-vps | 204.152.223.104 | 100.83.138.2 | 22 | deploy | Production VPS |

### Tailscale Network Architecture

Tailscale runs on **Unraid only** (not on devlab). Remote access to devlab goes through Unraid:

```
Laptop (TS) ──→ Unraid (100.105.135.31) ──iptables DNAT──→ devlab (192.168.99.84)
```

**Forwarded ports** (configured in `/mnt/cache/appdata/dev-lab/start-devlab.sh`):
- **25831/tcp** (SSH) → devlab:25831
- **445/tcp** (SMB) → devlab:445

**Why not Tailscale on devlab?** Devlab is a Docker macvlan container. Macvlan containers can't communicate directly with the host (and vice versa). A macvlan shim interface (`192.168.99.85`) on Unraid bridges this gap. Tailscale belongs on the host where it has full network access.

**Macvlan shim:** Created by `start-devlab.sh` on every container start. Assigns `192.168.99.85/32` to Unraid and routes `192.168.99.84` through it.

**Subnet routing:** Unraid advertises `192.168.99.0/24` via `tailscale set --advertise-routes`. Requires approval in the Tailscale admin console for full subnet access (optional — port forwarding works without it).

---

## SSH Configurations

### Devlab (`/home/jesse/.ssh/config`)

```
Host desktop
    HostName 192.168.99.145
    User jesse
    IdentityFile ~/.ssh/id_ed25519

Host desktop-ubuntu
    HostName 192.168.99.145
    Port 2223
    User jesse
    IdentityFile ~/.ssh/id_ed25519

Host laptop
    HostName 192.168.99.220
    User jesse
    IdentityFile ~/.ssh/id_ed25519

Host unraid
    HostName 192.168.99.83
    User root
    Port 22
    IdentityFile ~/.ssh/id_ed25519

Host *
  AddKeysToAgent yes
  StrictHostKeyChecking accept-new
  ServerAliveInterval 60
  ServerAliveCountMax 10
  TCPKeepAlive yes
  IPQoS throughput
```

### Desktop WSL2 (`~/.ssh/config` inside WSL)

Accessible directly from devlab via `ssh desktop-ubuntu` (port 2223). SSH server managed by systemd (auto-starts with WSL2).

**Why port 2223 (not 2222)?** WSL2 is in `networkingMode=mirrored`, which shares the Windows TCP stack. Port 2222 kept getting blocked by stale TIME_WAIT entries from prior connection attempts (mirrored mode means socket state from devlab→2222 connections lingers in Windows' TCP stack and blocks WSL2's `ssh.socket` from binding). Switching to 2223 sidesteps this. The Windows port proxy (`netsh portproxy 2222→127.0.0.1:2222`) was removed because mirrored mode makes WSL2 ports directly reachable from the LAN — no proxy needed.

The systemd unit for ssh.socket has an override at `/etc/systemd/system/ssh.socket.d/override.conf` inside WSL2:
```
[Socket]
ListenStream=
ListenStream=0.0.0.0:2223
ListenStream=[::]:2223
```

Windows firewall rule: `WSL2 SSH 2223` (TCP inbound, port 2223).

```
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_github2
    IdentitiesOnly yes

Host junipr-vps
    HostName 204.152.223.104
    User deploy
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes

Host devlab
    HostName 192.168.99.84
    Port 25831
    User jesse

Host laptop
    HostName 192.168.99.220
    User jesse

Host unraid
    HostName 192.168.99.83
    User root
    Port 22

Host *
  ServerAliveInterval 60
  ServerAliveCountMax 10
  TCPKeepAlive yes
  IPQoS throughput
  AddKeysToAgent yes
```

### Desktop Windows (`C:\Users\Jesse\.ssh\config`)

This is the native Windows OpenSSH client config — used when Jesse SSHes into devlab from the desktop (the connection carrying Claude/Codex sessions).

```
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_github2
    IdentitiesOnly yes

Host junipr-vps
    HostName 204.152.223.104
    User deploy
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes

Host devlab
    HostName 192.168.99.84
    Port 25831
    User jesse

Host laptop
    HostName 192.168.99.220
    User jesse

Host unraid
    HostName 192.168.99.83
    User root
    Port 22

Host *
    ServerAliveInterval 60
    ServerAliveCountMax 10
    TCPKeepAlive yes
    IPQoS throughput
```

### Laptop WSL2 (`~/.ssh/config` inside WSL)

```
Host devlab dev-lab
    HostName 100.105.135.31
    User jesse
    Port 25831
    IdentityFile ~/.ssh/id_ed25519
    StrictHostKeyChecking no

Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_github2
    IdentitiesOnly yes

Host junipr-vps
    HostName 204.152.223.104
    User deploy
    IdentityFile ~/.ssh/id_ed25519_win
    IdentitiesOnly yes

Host desktop
    HostName 192.168.99.145
    User jesse

Host unraid
    HostName 100.105.135.31
    User root
    Port 22
    IdentityFile ~/.ssh/id_ed25519_win
    IdentitiesOnly yes

Host *
  ServerAliveInterval 60
  ServerAliveCountMax 10
  TCPKeepAlive yes
  IPQoS throughput
  AddKeysToAgent yes
```

**NOTE: Laptop SSH config needs updating next time it's online.** Currently has old values. Also needs L: drive remapped (see pending tasks in memory).

**Note:** `devlab` points to Unraid's Tailscale IP (`100.105.135.31`). Unraid forwards port 25831 to devlab via iptables DNAT. Changed from `100.72.27.27` (devlab's old direct Tailscale IP) on 2026-02-20.

---

## SSH Keepalive Settings

**Client-side** (applied to ALL machines: devlab, desktop Windows, desktop WSL2, laptop WSL2):

```
ServerAliveInterval 60      # SSH-level keepalive ping every 60 seconds (encrypted, through tunnel)
ServerAliveCountMax 10      # Tolerate 10 missed pings (10 minutes) before disconnecting
TCPKeepAlive yes            # OS-level TCP keepalive (additional layer, detects dead sockets)
IPQoS throughput            # Prevents DSCP marking issues with some network gear/Windows OpenSSH
```

**Server-side** (devlab SSHD — `/etc/ssh/sshd_config`, baked into Dockerfile AND applied at runtime by `container-startup.sh`):

```
TCPKeepAlive yes
ClientAliveInterval 120     # Server probes client every 2 minutes (encrypted)
ClientAliveCountMax 10      # Tolerate 10 missed responses (20 minutes) before dropping session
```

**How it works:** Two independent keepalive layers operate simultaneously:
- **SSH-level** (`ServerAliveInterval` / `ClientAliveInterval`): encrypted pings through the SSH tunnel. The primary mechanism. Works through NAT, tunable per-connection.
- **TCP-level** (`TCPKeepAlive`): OS kernel probes on the raw socket. Secondary safety net. Detects dead peers at the network layer.

Both client and server send probes independently. If a connection dies, both sides detect it within minutes and clean up.

**`IPQoS throughput`**: Windows OpenSSH sets DSCP markings (`af21`) on interactive sessions. Some network equipment mishandles these packets, causing silent drops. `IPQoS throughput` disables this marking.

**Previous mistakes (do not repeat):**
- `TCPKeepAlive no` on client — removed a safety layer for no benefit on LAN
- `ClientAliveCountMax 2880` / `ServerAliveCountMax 1440` — 24 hours before detecting dead connections, causing zombie sessions to accumulate
- Missing `IPQoS` — left a known Windows OpenSSH issue unaddressed

---

## Network Drive Mappings

### Drive Letters

| Drive | UNC Path | Server | SMB User | Password | Content |
|-------|----------|--------|----------|----------|---------|
| L: | `\\192.168.99.83\home` | Unraid | jesse | media123 | Devlab `/home/jesse` directory (via Unraid Samba share of `/mnt/user/appdata/dev-lab/home`) |
| M: | `\\192.168.99.83\media` | Unraid | jesse | media123 | Media shares (movies, tv, downloads, prerolls, etc.) |

### How It Works (Current Setup — Feb 20, 2026)

No recurring scripts or scheduled tasks. Drives are mapped with:
- **`cmdkey`** — stores credentials in Windows Credential Manager (persists across reboots)
- **`net use /persistent:yes`** — stores the mapping in the registry (auto-reconnects at login)
- **`EnableLinkedConnections`** registry key — makes drives visible in Explorer across UAC elevation boundaries

This is a one-time setup. Once configured, Windows handles reconnection at login automatically.

### L: Drive Samba Config (Unraid — `/boot/config/smb-extra.conf`)

L: drive is now served by Unraid's native Samba (not devlab container Samba). The share is defined in `smb-extra.conf`:

```ini
[home]
	path = /mnt/user/appdata/dev-lab/home
	comment = Devlab home directory
	browseable = yes
	writeable = no
	write list = jesse
	valid users = jesse
	case sensitive = auto
	preserve case = yes
	short preserve case = yes
	vfs objects = catia fruit streams_xattr
	fruit:encoding = native
```

This is more reliable than running Samba inside devlab — Unraid's Samba is always running and doesn't depend on the container. Both L: and M: now use the same Samba instance, same credentials (`jesse` / `media123`).

### Fix/Setup Runbook (from devlab via SSH)

When drives break on a Windows machine, run this from devlab. Replace `TARGET_IP` with the machine's LAN IP (`192.168.99.220` for laptop, `192.168.99.145` for desktop).

Both drives now point to Unraid (`192.168.99.83`) with the same credentials (`jesse` / `media123`).

**Step 1: Nuclear cleanup — remove all old state**

```bash
ssh jesse@TARGET_IP "net use L: /delete /y 2>&1 & net use M: /delete /y 2>&1 & reg delete \"HKCU\Network\L\" /f 2>&1 & reg delete \"HKCU\Network\M\" /f 2>&1"
```

**Step 2: Create a one-time setup bat file**

```bash
ssh jesse@TARGET_IP "echo @echo off > C:\Users\Jesse\setup-drives.bat && echo cmdkey /delete:192.168.99.84 >> C:\Users\Jesse\setup-drives.bat && echo cmdkey /add:192.168.99.83 /user:jesse /pass:media123 >> C:\Users\Jesse\setup-drives.bat && echo net use L: \\\\192.168.99.83\\home /persistent:yes >> C:\Users\Jesse\setup-drives.bat && echo net use M: \\\\192.168.99.83\\media /persistent:yes >> C:\Users\Jesse\setup-drives.bat && echo schtasks /delete /tn SetupDrivesOnce /f >> C:\Users\Jesse\setup-drives.bat && echo del C:\Users\Jesse\setup-drives.bat >> C:\Users\Jesse\setup-drives.bat"
```

**Step 3: Run it in the interactive Windows session (NOT elevated)**

```bash
ssh jesse@TARGET_IP "schtasks /create /tn SetupDrivesOnce /tr \"cmd /c C:\\Users\\Jesse\\setup-drives.bat\" /sc once /st 00:00 /f /it 2>&1 && schtasks /run /tn SetupDrivesOnce 2>&1"
```

**CRITICAL: Do NOT use `/rl highest`.** Elevated tasks create drive mappings invisible to non-elevated Explorer. The `/it` flag (interactive only) is required so cmdkey can access Credential Manager.

The bat file and scheduled task self-delete after running.

**Step 4: Enable linked connections (one-time per machine, needs sign-out/in)**

```bash
ssh jesse@TARGET_IP "reg add \"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\" /v EnableLinkedConnections /t REG_DWORD /d 1 /f"
```

This makes mapped drives visible across UAC boundaries (elevated and non-elevated Explorer). Already applied to both desktop and laptop as of Feb 20.

**Step 5: Restart Explorer if drives don't appear in nav pane**

Kill Explorer from Task Manager or:
```bash
ssh jesse@TARGET_IP "taskkill /f /im explorer.exe"
```
Then the user restarts it from Task Manager (File → Run new task → `explorer.exe`). Or sign out and back in (also activates the EnableLinkedConnections key if newly applied).

### SSH Limitations with Windows Drive Mapping

- **`cmdkey` cannot run from SSH sessions** — Windows Credential Manager is tied to the interactive logon session. SSH uses a Network logon type that has no access to it.
- **`net use` from SSH creates per-session mappings** — they show as "OK" in the SSH session but are invisible to the interactive desktop and show "Unavailable" in Explorer.
- **The schtasks workaround** is the only way to run drive setup commands in the interactive session context from SSH. The task must use `/it` (interactive only) and must NOT use `/rl highest` (elevation).

---

## Troubleshooting History & Gotchas

### Feb 8: DESKTOP drive fix after docker.img recovery

**Problem:** docker.img recovery on devlab wiped Samba password database. Desktop drives showed "Unavailable".

**Server fix:** Reset Samba password:
```bash
sudo bash -c 'echo -e "devlab123\ndevlab123" | smbpasswd -s -a jesse'
sudo smbpasswd -e jesse
sudo /etc/init.d/smbd restart
```

**Client issues encountered (in order):**

1. **Stale persistent mappings** - Old entries showed "Unavailable". Fixed by deleting and re-mapping.

2. **Windows NTLM collision** - Desktop Windows username is also "jesse", so Windows auto-sent `JESSE-DESKTOP\jesse` with the Windows password hash (not the Samba password). Caused `Access denied`.

3. **Cached SMB sessions** - Windows Redirector cached failed sessions. Fix:
   ```cmd
   net stop LanmanWorkstation /y
   net start LanmanWorkstation
   ```

4. **SSH non-interactive limitation** - `net use` via SSH succeeds but cannot store credentials in Windows Credential Manager. Drive appears "OK" in `net use` but `dir L:\` fails. Fix: use schtasks to run bat file in interactive context.

5. **Stale registry entries** - Old persistent mappings in `HKCU\Network\L` and `HKCU\Network\M` caused conflicts. Fix:
   ```cmd
   reg delete "HKCU\Network\L" /f
   reg delete "HKCU\Network\M" /f
   ```

### Feb 9: LAPTOP drive fix + SSH keepalive

**Drive fix:** Same as desktop. (Previous note about `/persistent:yes` being harmful was wrong — the real issue was running cmdkey/net-use from SSH or elevated contexts. See Feb 20 fix below.)

**Laptop WSL K: drive error fix:**
```
wsl: Failed to mount K:\
```
Cause: 976 MB hidden FAT32 partition (Kali boot/EFI) had drive letter K:. WSL tried to automount it.
Fix: Removed K: drive letter via diskpart:
```cmd
echo select volume 3 > %TEMP%\dp.txt
echo remove letter=K >> %TEMP%\dp.txt
diskpart /s %TEMP%\dp.txt
del %TEMP%\dp.txt
wsl --shutdown
```

---

## Key Lessons

1. **SSH non-interactive sessions cannot save Windows Credential Manager entries.** Use schtasks with `/it` (interactive only) to run cmdkey in the user's desktop session.
2. **Never use `/rl highest` with schtasks for drive mapping.** Elevated tasks create drives invisible to non-elevated Explorer. Use `/it` only.
3. **`EnableLinkedConnections` registry key is essential.** Without it, drives mapped in one UAC context are invisible in the other.
4. **Windows NTLM collision** when local Windows username matches Samba username. Flush with `net stop LanmanWorkstation /y`.
5. **`cmdkey` + `net use /persistent:yes` is the correct one-time setup.** No recurring scripts or scheduled tasks needed. Windows auto-reconnects at login using stored credentials.
6. **Keepalives must be set on BOTH sides.** `ServerAliveInterval` on the client AND `ClientAliveInterval` on the server (devlab SSHD). Also set on the desktop Windows SSH client — this is the connection carrying Claude/Codex sessions.
7. **WSL2 tries to mount all lettered drives** regardless of `[automount] enabled=false`. Remove unwanted drive letters.

---

## Known Issues / Potential Problems

- **Drive mappings use Unraid's LAN IP** (192.168.99.83). When laptop is remote (Tailscale only), this LAN IP won't be reachable. For remote access the UNC paths would need to use Unraid's Tailscale IP (`\\100.105.135.31\home` and `\\100.105.135.31\media`).
- **Macvlan shim is not persistent on its own.** It's created by `start-devlab.sh` on container start. If the shim is lost without a container restart (e.g., network reset), re-run the script or manually recreate it.
- **iptables rules are not persistent on Unraid.** They're recreated by `start-devlab.sh`. Same caveat as the shim above.

---

### Feb 20: Removed Tailscale from devlab, fixed laptop SSH, rebuilt drive mappings

**SSH fix — Tailscale:**
- Removed Tailscale from devlab container (doesn't belong in macvlan container)
- Set up iptables DNAT on Unraid: forward ports 25831 (SSH) and 445 (SMB) from Tailscale interface to devlab
- Updated `start-devlab.sh` with auto-detecting Tailscale interface name (currently `tailscale1`)
- Updated laptop SSH config: `devlab` HostName changed from `100.72.27.27` → `100.105.135.31`
- Advertised subnet routes (`192.168.99.0/24`) from Unraid's Tailscale (pending admin approval)

**Drive mapping fix:**
- Removed old `map-drives.bat` and "Map Network Drives" scheduled task from BOTH machines
- Replaced with one-time `cmdkey` + `net use /persistent:yes` setup (no recurring scripts)
- Applied `EnableLinkedConnections` registry key to both machines
- Key discovery: schtasks with `/rl highest` creates drives in an elevated context that's invisible to normal Explorer. Must use `/it` only (no `/rl highest`)

### Mar 16: Startup script fixes, L: drive migration, SSH keepalive hardening, WSL2 direct SSH

**Startup script fixes:**
- Fixed `/boot/config/go` — `start-devlab.sh` and `setup-logging.sh` now wait for cache drive mount before running
- Rewrote `setup-logging.sh` — comprehensive monitoring (kernel, syslog, docker, SMART, network, temperatures, disk space)
- Removed dead Samba/Tailscale code from `container-startup.sh` and `start-devlab.sh`

**L: drive migration:**
- L: drive moved from devlab container Samba (`\\192.168.99.84\home`) to Unraid native Samba (`\\192.168.99.83\home`)
- Share defined in `/boot/config/smb-extra.conf`, path: `/mnt/user/appdata/dev-lab/home`
- Same credentials as M: drive (`jesse` / `media123`)
- Desktop updated. Laptop still needs update (offline).

**SSH keepalive hardening:**
- Added `ClientAliveInterval 30` / `ClientAliveCountMax 2880` to devlab SSHD (baked into Dockerfile)
- Added keepalive settings to desktop Windows SSH client config (`C:\Users\Jesse\.ssh\config`)
- Both client-side and server-side keepalives now active on all connections

**Desktop WSL2 direct SSH:**
- Installed openssh-server in WSL2, port 2222, managed by systemd
- Added Windows port forward (`netsh interface portproxy`) and firewall rule
- New alias: `ssh desktop-ubuntu` from devlab
- Devlab SSH key authorized in WSL2

### Apr 6: Crash recovery, OOM prevention, SSH keepalive correction, WSL2 SSH port change

**Server crash root cause analysis:**
- Devlab consumed all 16GB host RAM (no container memory limit set)
- Multiple orphaned claude/node/python3 processes accumulated over 2 weeks of uptime
- Final straw: 5 node processes spiked to 70-94% CPU simultaneously, allocating 7GB in 5 minutes
- Host OOM killer fired and took down Docker daemon — full server freeze, physical reboot required

**OOM prevention (multi-layer defense):**
1. **Container memory limit (12GB / 14GB swap)** — added `--memory=12g --memory-swap=14g` to `start-devlab.sh`. Devlab now contained at the cgroup level — host can never crash from devlab memory exhaustion. Docker auto-restarts container if it OOMs internally.
2. **PAM session cleanup hook** — `/etc/pam.d/sshd` runs `~/bin/ssh-session-cleanup` on session close. Walks the process tree from the dying sshd PID and kills all descendants instantly. Re-applied at container start by `container-startup.sh`.
3. **Process watchdog** — `~/bin/claude-watchdog` runs every 5 min. Three passes:
   - Tool-call orphans (rg, find, grep, sed, awk, jq, git, etc) reparented to PID 1 with no tty → kill instantly
   - Special-case orphaned Playwright daemon/browser trees matched by `cliDaemon.js` / `~/.cache/ms-playwright/` args → kill instantly
   - Claude/codex CLI processes orphaned for >5 min → kill
   - Any process using >80% CPU detached for >10 min → kill
4. **Process health monitor** — `~/bin/process-health-check` runs every 5 min. Lightweight monitor that writes alerts to `/tmp/process-alerts.txt`. Yellow banner shown on SSH login if alerts exist. Has `KNOWN_BACKGROUND` allowlist for legitimate background processes.

**SSH keepalive corrections (after research):**
- Previous values were wrong: `ServerAliveCountMax 1440` and `ClientAliveCountMax 2880` meant 24-hour timeouts before detecting dead connections — caused zombie sessions to accumulate
- Corrected to `ServerAliveCountMax 10` (10 min) and `ClientAliveCountMax 10` (20 min)
- Changed `TCPKeepAlive no` → `yes` on all clients (was removing a safety layer for no reason on LAN)
- Server-side `ClientAliveInterval 30` → `120` (less network chatter, still responsive)
- Added `IPQoS throughput` to all client configs (fixes Windows OpenSSH DSCP marking issue)
- Disabled NIC power management on desktop Ethernet adapter (`PnPCapabilities=0x18` registry)
- Applied to: devlab SSHD (live + Dockerfile + container-startup.sh), devlab outbound client, desktop Windows client, desktop WSL2 client. **Laptop still pending.**

**WSL2 SSH port change (2222 → 2223):**
- WSL2 in `networkingMode=mirrored` shares Windows TCP stack
- Port 2222 kept getting blocked by stale TIME_WAIT entries from prior connections
- Removed obsolete Windows port proxy (mirrored mode doesn't need it — WSL2 ports are directly LAN-reachable)
- Switched to port 2223 via `/etc/systemd/system/ssh.socket.d/override.conf`
- Added Windows firewall rule `WSL2 SSH 2223`

**Cache drive cleanup (~380GB freed):**
- Deleted `ab_20260401_000002-failed/` (340GB failed Appbackup snapshot)
- Deleted `rar_staging/` (14GB extraction artifacts)
- Deleted `devlab-data/` (26GB old home dir copy from January)

**Backup script rewrite:**
- Old script created `versions/{timestamp}/` folder per run, accumulating duplicates on OneDrive (filled the 100GB quota)
- Rewrote `/boot/config/plugins/rclone/sync-devlab-backups.sh` to do plain `rclone sync` to `DevLabBackups/` (one folder, always current, diffs only)
- Added comprehensive excludes (oldgrounds, boat-buys, tools, youtube, games, bof3, portfolio, cas-example, cookie-cutters, google-cloud-sdk, pnpm store, jdks, codex dirs, etc) — backup size now ~32GB instead of unbounded
- Excluded `current/**` to avoid scanning the disappearing old folder during initial sync

**Macvlan shim duplicate cleanup:**
- Found two shim interfaces (`macvlan_shim` and `macvlan-shim`) — go script and start-devlab.sh used different naming
- Cleaned up the underscore variant, kept the hyphen variant from `start-devlab.sh`

---

## Source Conversations

These details were extracted from Claude Code sessions:
- **Feb 7** (`f454cd4b`) - Original SSH + drive setup history / dev-lab migration handoff
- **Feb 8** (`94e67e07`) - Fixed M: and L: drives on DESKTOP after docker.img recovery
- **Feb 9** (`37bd8e00`) - Applied same fix to LAPTOP + SSH keepalive fix
- **Feb 20** - Removed Tailscale from devlab, set up Unraid port forwarding for TS access, rebuilt drive mappings on both machines
