# SSH Access & Network Drive Setup

> Complete reference for SSH configuration between all machines and L:/M: network drive mappings.
> Last updated: 2026-02-20

---

## Network Hosts

| Host | LAN IP | Tailscale IP | SSH Port | User | Notes |
|------|--------|-------------|----------|------|-------|
| devlab | 192.168.99.84 | — (via Unraid) | 25831 | jesse | Samba server for L: drive. Docker macvlan container on Unraid. |
| desktop | 192.168.99.145 | 100.125.236.116 | 22 | jesse | Windows 11, WSL2 |
| laptop | 192.168.99.220 | 100.68.237.46 | 22 | jesse | Windows 10, WSL2 |
| unraid | 192.168.99.83 | 100.105.135.31 | 22 | root | Samba server for M: drive. Runs Tailscale. Forwards TS traffic to devlab. |
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
Host *
  AddKeysToAgent yes
  StrictHostKeyChecking accept-new
  ServerAliveInterval 60
  ServerAliveCountMax 1440
  TCPKeepAlive no
```

### Desktop WSL2 (`~/.ssh/config` inside WSL)

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
  ServerAliveCountMax 1440
  TCPKeepAlive no
  AddKeysToAgent yes
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
  ServerAliveCountMax 1440
  TCPKeepAlive no
  AddKeysToAgent yes
```

**Note:** `devlab` points to Unraid's Tailscale IP (`100.105.135.31`). Unraid forwards port 25831 to devlab via iptables DNAT. Changed from `100.72.27.27` (devlab's old direct Tailscale IP) on 2026-02-20.

---

## SSH Keepalive Settings

Applied to ALL three machines (devlab, desktop WSL2, laptop WSL2) on Feb 9 to fix "broken pipe" disconnections:

```
ServerAliveInterval 60      # Send keepalive ping every 60 seconds
ServerAliveCountMax 1440    # Tolerate 1440 missed pings (24 hours)
TCPKeepAlive no             # Disable OS-level TCP keepalives (the main culprit)
```

**Key insight:** `ServerAliveInterval` is a **client-side** setting only. Setting it on the SSH server does nothing for inbound connections. The fix must be in the SSH *client* config on the machine initiating the connection.

**Root cause:** WSL2's virtual NAT aggressively times out idle TCP connections. OS-level `TCPKeepAlive` detects the connection as "dead" and kills it.

---

## Network Drive Mappings

### Drive Letters

| Drive | UNC Path | Server | SMB User | Password | Content |
|-------|----------|--------|----------|----------|---------|
| L: | `\\192.168.99.84\home` | Devlab | jesse | devlab123 | `/home` directory (jesse/ subdirectory inside) |
| M: | `\\192.168.99.83\media` | Unraid | jesse | media123 | Media shares (movies, tv, downloads, prerolls, etc.) |

### How It Works (Current Setup — Feb 20, 2026)

No recurring scripts or scheduled tasks. Drives are mapped with:
- **`cmdkey`** — stores credentials in Windows Credential Manager (persists across reboots)
- **`net use /persistent:yes`** — stores the mapping in the registry (auto-reconnects at login)
- **`EnableLinkedConnections`** registry key — makes drives visible in Explorer across UAC elevation boundaries

This is a one-time setup. Once configured, Windows handles reconnection at login automatically.

### Devlab Samba Config (`/etc/samba/smb.conf`)

```ini
[global]
   workgroup = WORKGROUP
   server string = Dev-Lab
   security = user
   map to guest = Never
   log level = 2
   server min protocol = SMB2
   server signing = auto

[home]
   path = /home
   browseable = yes
   writeable = yes
   valid users = jesse
   force user = jesse
   create mask = 0664
   directory mask = 0775
   guest ok = no
```

- Share name is `home`, path is `/home` (so L: shows `jesse/` as a subdirectory)
- `map to guest = Never` prevents fallback to guest access
- `force user = jesse` means all file operations run as jesse
- `server min protocol = SMB2` enforces modern SMB

### Fix/Setup Runbook (from devlab via SSH)

When drives break on a Windows machine, run this from devlab. Replace `TARGET_IP` with the machine's LAN IP (`192.168.99.220` for laptop, `192.168.99.145` for desktop).

**Step 1: Nuclear cleanup — remove all old state**

```bash
ssh jesse@TARGET_IP "net use L: /delete /y 2>&1 & net use M: /delete /y 2>&1 & reg delete \"HKCU\Network\L\" /f 2>&1 & reg delete \"HKCU\Network\M\" /f 2>&1"
```

**Step 2: Create a one-time setup bat file**

```bash
ssh jesse@TARGET_IP "powershell -Command \"'cmdkey /add:192.168.99.84 /user:jesse /pass:devlab123','cmdkey /add:192.168.99.83 /user:jesse /pass:media123','net use L: \\\\192.168.99.84\\home /persistent:yes','net use M: \\\\192.168.99.83\\media /persistent:yes','schtasks /delete /tn SetupDrivesOnce /f','del C:\\Users\\Jesse\\setup-drives.bat' | Set-Content C:\\Users\\Jesse\\setup-drives.bat\""
```

**Step 3: Run it in the interactive Windows session (NOT elevated)**

```bash
ssh jesse@TARGET_IP "schtasks /create /tn \"SetupDrivesOnce\" /tr \"C:\Users\Jesse\setup-drives.bat\" /sc once /st 00:00 /f /it 2>&1 && schtasks /run /tn \"SetupDrivesOnce\" 2>&1"
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
6. **`ServerAliveInterval` is client-side only.** Must be set on the SSH client, not the server.
7. **WSL2 tries to mount all lettered drives** regardless of `[automount] enabled=false`. Remove unwanted drive letters.

---

## Known Issues / Potential Problems

- **Drive mappings use LAN IPs** (192.168.99.84 and 192.168.99.83). When laptop is remote (Tailscale only), LAN IPs won't be reachable. Unraid forwards SMB port 445 from TS to devlab, so for remote L: drive access the UNC path would need to be `\\100.105.135.31\home`. M: drive would need Unraid Samba to listen on the Tailscale interface.
- **Samba password database lives in devlab container storage.** Another docker.img recovery could wipe it again. Fix: `sudo bash -c 'echo -e "devlab123\ndevlab123" | smbpasswd -s -a jesse' && sudo smbpasswd -e jesse && sudo /etc/init.d/smbd restart`
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

---

## Source Conversations

These details were extracted from Claude Code sessions:
- **Feb 7** (`f454cd4b`) - Original SSH + drive setup history / dev-lab migration handoff
- **Feb 8** (`94e67e07`) - Fixed M: and L: drives on DESKTOP after docker.img recovery
- **Feb 9** (`37bd8e00`) - Applied same fix to LAPTOP + SSH keepalive fix
- **Feb 20** - Removed Tailscale from devlab, set up Unraid port forwarding for TS access, rebuilt drive mappings on both machines
