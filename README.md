# Infrastructure

System utilities, scripts, and configuration for development environment setup.

## Structure

```
infrastructure/
├── system-utilities/     # Shared system utilities and tools
│   ├── bin/             # Executable binaries and wrapper scripts
│   ├── scripts/         # Python/PowerShell utility scripts
│   ├── claude-commands/ # Global Claude Code slash commands
│   └── README.md        # Utilities documentation
└── install-binaries.sh  # Downloads and installs system binaries
```

## System Utilities

The `system-utilities/` folder contains tools and scripts used across all projects:

### Binaries (`bin/`)
- `rg` - ripgrep (fast code search)
- `yt-dlp` - YouTube downloader
- `analyze-video` - Video analysis wrapper script
- `download-images` - Image download wrapper script
- `grep` - ripgrep wrapper for compatibility

**Note:** Binaries are in PATH via `~/.bashrc` configuration.

### Scripts (`scripts/`)
- `analyze-video.py` - Video content analysis
- `build_collections.py` - Plex/Kometa collection builder
- `download-images.py` - Bulk image downloader
- `franchise-audit.ps1` - Media server franchise auditing

### Claude Commands (`claude-commands/`)
Global Claude Code slash commands available system-wide:
- `/brand-design` - Complete brand creation system
- `/wp-install` - Install fresh WordPress on VPS
- `/wp-setup` - Configure WordPress with theme/plugins
- `/wp-update` - Update current WordPress installation
- `/wp-update-all` - Update all WordPress installations

These are symlinked to `~/.claude/commands/` for global availability.

## Installing Binaries

The `install-binaries.sh` script downloads and installs system binaries:

```bash
cd ~/infrastructure
./install-binaries.sh
```

**What it does:**
- Downloads latest ripgrep, yt-dlp, etc. from official sources
- Installs to `system-utilities/bin/`
- Verifies checksums (where applicable)
- Makes binaries executable

**Why not commit binaries?**
- Binaries are platform-specific (CPU arch, glibc version)
- Large file sizes (not suitable for git)
- Install script ensures you get the right version for your platform

## Python Virtual Environments

Some scripts have their own virtual environments:
- `image-downloader-env/` - For download-images.py
- `video-analysis-env/` - For analyze-video.py

**These are excluded from git** (see .gitignore).

To recreate virtual environments:
```bash
# Image downloader
python3 -m venv system-utilities/image-downloader-env
source system-utilities/image-downloader-env/bin/activate
pip install -r system-utilities/image-downloader-requirements.txt

# Video analysis
python3 -m venv system-utilities/video-analysis-env
source system-utilities/video-analysis-env/bin/activate
pip install -r system-utilities/video-analysis-requirements.txt
```

## Syncing Between Machines

1. Clone this repo on new machine:
   ```bash
   git clone git@github.com:junipr-dev/infrastructure.git ~/infrastructure
   ```

2. Run install script:
   ```bash
   cd ~/infrastructure
   ./install-binaries.sh
   ```

3. Update PATH in `~/.bashrc` (if not using dotfiles repo):
   ```bash
   export PATH="$HOME/infrastructure/system-utilities/bin:$PATH"
   ```

4. Recreate Python virtual environments (see above)

## Notes

- **Scripts** (shell, python) are version-controlled
- **Binaries** (compiled executables) are downloaded via install script
- **Virtual environments** are recreated per machine (not committed)
- **Claude commands** are symlinked from `~/.claude/commands/` (global)
