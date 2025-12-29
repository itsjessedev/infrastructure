# Dev Lab Migration Guide - Unraid Home Server

**Goal:** Migrate `/home/jesse` from WSL to a dedicated dev lab VM on Unraid home server with Tailscale access from anywhere.

**Hardware:** 1TB SSD
- 250GB: Dev Lab VM
- 750GB: ARR Stack (later)

**Network Config (match existing media server):**
- Static IP: `192.168.99.83` (or choose nearby like `.84`)
- SSH Port: `25831`
- User: `jesse`

---

## Accessing the Dev Lab from Windows

**You do NOT need WSL anymore.** The dev lab IS your Linux environment.

### Option 1: Windows Terminal + Native SSH (Recommended)
```powershell
# From PowerShell or Windows Terminal
ssh -p 25831 jesse@192.168.99.84  # Local network
ssh jesse@100.x.x.x              # Tailscale (from anywhere)
```

### Option 2: VS Code Remote SSH (Best for coding)
1. Install "Remote - SSH" extension
2. Add to SSH config: `jesse@TAILSCALE_IP`
3. Full VS Code on remote files with integrated terminal

### Option 3: Windows Terminal SSH Profile
Add to Windows Terminal settings.json:
```json
{
  "name": "Dev Lab",
  "commandline": "ssh jesse@100.x.x.x",
  "icon": "🖥️"
}
```

### Where Claude Code Runs
Claude Code runs **on the dev lab server**, not on Windows:
1. SSH into dev lab
2. Run `claude` command
3. Claude operates directly on Linux filesystem

**WSL is no longer needed** - uninstall it after migration is verified.

### Option 4: Mobile SSH (Emergency Only)

**iOS:** Termius (free) or Blink Shell ($20)
**Android:** Termius or JuiceSSH (free)

Setup:
1. Install Tailscale on phone, sign in with same account
2. In SSH app, connect to: `jesse@100.x.x.x` port `25831`

Use for emergency fixes, quick git ops, or checking build status. Real coding → use laptop/desktop.

---

## Phase 1: Unraid Initial Setup

### 1.1 Create Unraid Boot USB

1. Download Unraid USB Creator from https://unraid.net/download
2. Insert USB drive (at least 2GB, USB 2.0 preferred for compatibility)
3. Run USB Creator, select USB drive, download latest stable (6.12.x as of Dec 2024)
4. Click "Write" and wait for completion

### 1.2 First Boot & Basic Config

1. Insert USB into server, boot from USB (may need to set boot order in BIOS)
2. Server will boot to console showing IP address (e.g., `192.168.1.xxx`)
3. From any computer on network, open browser to: `http://tower` or `http://192.168.1.xxx`
4. **Register Unraid:**
   - Click "Get Started"
   - Create/login to Unraid.net account
   - Choose trial or enter license key
   - Server will register and reboot

### 1.3 Configure the 1TB SSD

1. Go to **Main** tab
2. Under "Array Devices", click on an empty **Disk** slot
3. Select your 1TB SSD
4. **Important:** Do NOT start the array yet
5. Go to **Settings → Disk Settings**
   - Enable auto-start: **No** (we'll start manually after VM setup)

### 1.4 Enable SSH Access (PRIORITY)

1. Go to **Settings → Management Access**
2. Scroll to "SSH"
3. Set **Enable SSH:** Yes
4. Click **Apply**
5. **Test immediately:**
   ```bash
   ssh root@tower
   # or
   ssh root@192.168.1.xxx
   ```
   Default password is blank (just press Enter) - set one now:
   ```bash
   passwd
   ```

### 1.5 Install Community Applications

1. Go to **Plugins** tab
2. Click **Install Plugin**
3. Paste: `https://raw.githubusercontent.com/Squidly271/community.applications/master/plugins/community.applications.plg`
4. Click **Install**
5. After install, you'll see **Apps** tab in the menu

---

## Phase 2: Create Dev Lab VM

### 2.1 Setup VM Infrastructure

1. Go to **Settings → VM Manager**
2. Set **Enable VMs:** Yes
3. Set **PCIe ACS Override:** On (if available)
4. Click **Apply**

### 2.2 Create Ubuntu VM

1. Go to **VMs** tab → **Add VM** → **Linux**
2. Configure:
   - **Name:** devlab
   - **CPU Mode:** Host Passthrough
   - **CPUs:** 4-8 (depending on your server's CPU)
   - **Initial Memory:** 8192 MB (8GB minimum, 16GB+ recommended)
   - **Max Memory:** Same as initial
   - **Machine:** Q35-8.1 (or latest)
   - **BIOS:** OVMF
   - **OS Install ISO:** Download Ubuntu Server 24.04 LTS ISO first (see below)
   - **Primary vDisk Size:** 250GB
   - **Primary vDisk Location:** /mnt/user/domains/ (or manual path)
   - **Graphics Card:** VNC
   - **Network:** virtio, br0

3. **Download Ubuntu Server ISO first:**
   ```bash
   # SSH into Unraid
   ssh root@tower
   mkdir -p /mnt/user/isos
   cd /mnt/user/isos
   wget https://releases.ubuntu.com/24.04/ubuntu-24.04.1-live-server-amd64.iso
   ```

4. Back in Web UI, select the ISO for "OS Install ISO"
5. Click **Create**

### 2.3 Install Ubuntu Server

1. Click the VM icon → **VNC Remote**
2. Follow Ubuntu installer:
   - Language: English
   - Keyboard: US
   - Installation type: Ubuntu Server
   - Network: DHCP (note the IP)
   - Storage: Use entire disk (the 250GB vDisk)
   - **Username:** jesse
   - **Server name:** devlab
   - **Password:** (your choice)
   - **Install OpenSSH server:** YES ✓
   - Skip additional snaps
3. Wait for install, then **Reboot Now**
4. After reboot, login via VNC and note the IP address:
   ```bash
   ip addr show
   ```

### 2.4 Initial VM Access & Static IP Setup

```bash
# From your current WSL machine (use IP shown in VNC console)
ssh jesse@DEVLAB_IP

# First thing - update system
sudo apt update && sudo apt upgrade -y
```

### 2.5 Configure Static IP (Match Media Server Subnet)

```bash
# Find your network interface name
ip link show  # Usually ens3 or enp1s0 for VMs

# Edit netplan config
sudo nano /etc/netplan/00-installer-config.yaml
```

Replace contents with:
```yaml
network:
  version: 2
  ethernets:
    ens3:  # Change to your interface name
      dhcp4: no
      addresses:
        - 192.168.99.84/24  # Static IP (near media server's .83)
      routes:
        - to: default
          via: 192.168.99.1  # Your router IP
      nameservers:
        addresses:
          - 8.8.8.8
          - 8.8.4.4
```

Apply and test:
```bash
sudo netplan apply
ip addr show  # Verify new IP
ping 8.8.8.8  # Verify internet
```

### 2.6 Configure SSH on Custom Port (25831)

```bash
# Edit SSH config
sudo nano /etc/ssh/sshd_config

# Find and change/add:
Port 25831
PermitRootLogin no
PasswordAuthentication yes  # Change to 'no' after key setup

# Restart SSH
sudo systemctl restart ssh

# Verify
sudo ss -tlnp | grep 25831
```

**Update firewall:**
```bash
sudo ufw allow 25831/tcp
sudo ufw enable
sudo ufw status
```

**Test from WSL:**
```bash
ssh -p 25831 jesse@192.168.99.84
```

---

## Phase 3: Install Tailscale (Remote Access)

### 3.1 On the Dev Lab VM

```bash
# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Start and authenticate
sudo tailscale up

# Note your Tailscale IP (100.x.x.x)
tailscale ip -4
```

### 3.2 Verify Access

From your laptop or phone (with Tailscale installed):
```bash
ssh jesse@100.x.x.x  # Use Tailscale IP
```

**You now have SSH access from anywhere!**

---

## Phase 4: Clone /home/jesse

### 4.1 Prepare Source (Current WSL Machine)

```bash
# Stop any services that might be writing
sudo systemctl stop syncthing 2>/dev/null

# Create a complete archive including hidden files and preserving permissions
cd /home
sudo tar -cvpzf /tmp/jesse-home-backup.tar.gz \
  --exclude='jesse/.cache' \
  --exclude='jesse/.npm/_cacache' \
  --exclude='jesse/.local/share/Trash' \
  --exclude='jesse/Android/Sdk' \
  --exclude='jesse/.gradle' \
  --exclude='jesse/.pub-cache' \
  --exclude='jesse/snap' \
  --exclude='jesse/.nvm/.cache' \
  --exclude='jesse/**/node_modules' \
  --exclude='jesse/**/.venv' \
  --exclude='jesse/**/venv' \
  --exclude='jesse/**/__pycache__' \
  jesse/

# Check size
ls -lh /tmp/jesse-home-backup.tar.gz
```

### 4.2 Transfer to Dev Lab

```bash
# From WSL, transfer to dev lab
scp /tmp/jesse-home-backup.tar.gz jesse@DEVLAB_TAILSCALE_IP:/tmp/
```

### 4.3 Extract on Dev Lab

```bash
# SSH into dev lab
ssh jesse@DEVLAB_TAILSCALE_IP

# Backup current home (just in case)
mv /home/jesse /home/jesse.original

# Extract archive
cd /home
sudo tar -xvpzf /tmp/jesse-home-backup.tar.gz

# Fix ownership (just in case)
sudo chown -R jesse:jesse /home/jesse

# Verify
ls -la /home/jesse
```

### 4.4 Transfer SSH Keys (MOVE, not copy)

```bash
# From WSL - verify keys exist
ls -la ~/.ssh/

# Copy SSH directory specifically (it's in the backup, but verify)
scp -r ~/.ssh/* jesse@DEVLAB_TAILSCALE_IP:~/.ssh/

# On dev lab - fix permissions
ssh jesse@DEVLAB_TAILSCALE_IP
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_*
chmod 644 ~/.ssh/*.pub
chmod 644 ~/.ssh/known_hosts
chmod 600 ~/.ssh/config

# Test GitHub access
ssh -T git@github.com
```

---

## Phase 5: Install Development Tools

### 5.1 Essential Packages

```bash
# Base development tools
sudo apt install -y \
  build-essential \
  git \
  curl \
  wget \
  unzip \
  zip \
  jq \
  htop \
  tmux \
  vim \
  ripgrep \
  fd-find \
  tree \
  software-properties-common

# Python
sudo apt install -y python3 python3-pip python3-venv

# Node.js via nvm (will reinstall fresh)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
source ~/.bashrc
nvm install --lts
nvm use --lts

# Verify
node -v
npm -v
python3 --version
```

### 5.2 Install Claude Code

```bash
# Install Claude Code CLI
npm install -g @anthropic-ai/claude-code

# Login and authenticate
claude login

# Verify installation
claude --version
```

### 5.3 Additional Tools (as needed)

```bash
# Docker (for later use)
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker jesse

# PowerShell (if needed for scripts)
sudo snap install powershell --classic
```

---

## Phase 6: Remove Syncthing from WSL

### On the OLD WSL machine (after confirming dev lab works):

```bash
# Stop and disable Syncthing
systemctl --user stop syncthing
systemctl --user disable syncthing

# Remove Syncthing
sudo apt remove syncthing
rm -rf ~/.config/syncthing
rm -rf ~/.local/state/syncthing

# Remove Tailscale from WSL (optional - keep if you want WSL access too)
# sudo tailscale down
# sudo apt remove tailscale

# Clean up .bashrc if any Syncthing-related entries
nano ~/.bashrc  # Remove any syncthing lines

# Delete old .stignore
rm -f ~/.stignore
```

---

## Phase 7: Post-Migration Claude Prompt

**Copy and paste this entire section to Claude Code on the dev lab after setup is complete:**

---

### MIGRATION COMPLETION PROMPT

```
I've just migrated my development environment from WSL to a dedicated dev lab VM on my Unraid home server. Here's what you need to know:

## New Environment Details

**Machine:** Ubuntu Server 24.04 LTS VM on Unraid
**Location:** Home server (always-on)
**Access:** Via Tailscale from desktop, laptop, or phone
**Hostname:** devlab
**User:** jesse
**Home:** /home/jesse

## What's Changed

1. **No more WSL** - This is native Linux, not Windows Subsystem
2. **No more Syncthing** - Single source of truth now (this machine)
3. **No more /mnt/c/** paths - No Windows filesystem access
4. **Always accessible** - Server is always on, connect via Tailscale from anywhere

## What I Need You to Do

1. **Recreate Python virtual environments:**
   - Scan for any projects with requirements.txt or pyproject.toml
   - Recreate venvs as needed

2. **Reinstall Node dependencies:**
   - Find all package.json files
   - Run npm install in each project directory

3. **Verify git repos:**
   - Run /check-repos to verify all repos are accessible
   - Test SSH to GitHub: ssh -T git@github.com

4. **Update global CLAUDE.md:**
   - Remove all WSL-specific instructions
   - Remove Syncthing references
   - Remove /mnt/c/ paths
   - Update to reflect new server environment

5. **Update knowledge graph:**
   - Add new server details (devlab, Tailscale, Unraid)
   - Remove Syncthing/WSL entities

6. **Test critical tools:**
   - Git operations
   - Python projects
   - Node.js projects
   - Claude Code functionality

## Directory Structure (unchanged)

/home/jesse/
├── itsjesse.dev/      # Portfolio website and projects
├── junipr/            # Junipr monorepo
├── projects/          # Personal projects
├── infrastructure/    # System utilities
├── dotfiles/          # Config files
├── media-server/      # Media server tools
├── nova-schedule/     # Nova app
└── school/            # Study Buddy

## Access Pattern

I'll be connecting from:
- Desktop (Windows) via SSH/Claude Code
- Laptop (Windows) via SSH/Claude Code
- Phone via SSH app (emergency only)

All connections use Tailscale IP: [INSERT YOUR TAILSCALE IP]

Please scan the environment, verify everything is working, and update all necessary configuration files.
```

---

## Verification Checklist

After running the migration prompt, verify:

- [ ] SSH access works from laptop via Tailscale
- [ ] GitHub SSH authentication works
- [ ] All git repos are accessible and clean
- [ ] Python projects can create venvs
- [ ] Node projects can npm install
- [ ] Claude Code runs properly
- [ ] All project-specific tools work (Expo, FastAPI, etc.)

---

## Troubleshooting

### VM Won't Start
- Check Unraid → VMs for error messages
- Verify ISO path is correct
- Try reducing memory allocation

### No Network in VM
- Verify br0 bridge exists in Unraid
- Try switching to virbr0 or e1000 network type
- Check if DHCP server is running on your network

### SSH Connection Refused
- Verify openssh-server is installed: `sudo apt install openssh-server`
- Check if SSH is running: `sudo systemctl status ssh`
- Verify firewall: `sudo ufw status` (disable or allow SSH)

### Tailscale Not Connecting
- Check Tailscale admin console for device
- Try `sudo tailscale up --reset`
- Verify no firewall blocking Tailscale

### Permission Errors After Migration
- Run: `sudo chown -R jesse:jesse /home/jesse`
- Fix SSH: `chmod 700 ~/.ssh && chmod 600 ~/.ssh/id_*`

---

## Future: ARR Stack Setup

After dev lab is stable, the remaining ~750GB can be used for:
- Sonarr (TV management)
- Radarr (Movie management)
- Prowlarr (Indexer management)
- Bazarr (Subtitle management)
- qBittorrent or SABnzbd (Download client)
- Overseerr (Request management)

These will run as Docker containers on Unraid (separate guide).
