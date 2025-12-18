# Shared Utilities

This folder contains tools, scripts, and utilities shared across all projects.

## Directory Structure

```
/home/jesse/utilities/
├── bin/                    - Executable scripts (in PATH)
├── scripts/                - Python/shell scripts
├── lib/                    - Shared libraries
├── config/                 - Configuration templates
├── claude-commands/        - Global Claude Code commands
└── image-downloader-env/   - Python venv for image downloader
```

## Available Tools

### Image Downloader (`download-images`)

**Purpose:** Download images from web pages using browser automation, bypassing hotlink protection.

**Technology:** Playwright (headless Chromium browser)

**Installation:** Already installed in `/home/jesse/utilities/image-downloader-env/`

**Usage:**

```bash
# Download main image from article
download-images -u "https://nytimes.com/article" -o image.jpg

# Batch download from URLs file
download-images --batch urls.txt -d ./output/

# Screenshot a specific element
download-images -u "https://site.com" -o screenshot.png --screenshot -s "#tweet-id"

# Run with visible browser (debugging)
download-images -u "https://site.com" -o image.jpg --headed
```

**How it works:**
1. Launches real Chromium browser (headless by default)
2. Navigates to the page as a normal user
3. Finds main image using og:image meta tag or common selectors
4. Downloads image or takes screenshot
5. Bypasses most hotlink protection and paywalls

**Best for:**
- News articles
- Social media posts (some sites require login)
- Any site that blocks wget/curl

**Limitations:**
- Sites requiring login (Twitter, Facebook) only show public content
- Very aggressive anti-bot sites (rare)
- For these, manual screenshot is fastest

**Files:**
- Script: `/home/jesse/utilities/scripts/download-images.py`
- Wrapper: `/home/jesse/utilities/bin/download-images`
- Venv: `/home/jesse/utilities/image-downloader-env/`

### Video Analysis Tool (`analyze-video`)

**Purpose:** AI-powered video analysis for content creation and storyboarding.

**Technology:** Three-tier approach combining Whisper (transcription) + PySceneDetect (scene detection) + Gemini 2.0 Flash (visual analysis)

**Installation:** Already installed in `/home/jesse/utilities/video-analysis-env/`

**Setup:**
```bash
# Set Gemini API key (get from https://aistudio.google.com/apikey)
export GEMINI_API_KEY="your-api-key-here"

# Add to ~/.bashrc for persistence:
echo 'export GEMINI_API_KEY="your-api-key-here"' >> ~/.bashrc
```

**Usage:**

```bash
# Analyze single video
analyze-video video.mp4 -o analysis.json

# Analyze with script matching (generates edit suggestions)
analyze-video video.mp4 -o analysis.json -s script.md

# Batch analyze all videos in folder
analyze-video videos/*.mp4 -d ./analysis/

# Use better Whisper model (more accurate, slower)
analyze-video video.mp4 -o analysis.json --whisper-model small
```

**How it works:**
1. **Whisper**: Transcribes audio with precise timestamps
2. **PySceneDetect**: Identifies visual scene changes
3. **Gemini 2.0 Flash**: Uploads video for visual analysis
4. **Output**: JSON + human-readable text with:
   - Complete transcript with timestamps
   - Scene breakdown with durations
   - Visual description of each scene
   - Edit suggestions matching footage to script

**Output formats:**
- `analysis.json` - Machine-readable full data
- `analysis.txt` - Human-readable formatted report

**Best for:**
- Matching B-roll footage to documentary scripts
- Understanding what's in your video files
- Creating edit lists and storyboards
- Finding specific moments in long videos

**Whisper models:**
- `tiny` - Fastest, lowest quality (39MB)
- `base` - Good balance (74MB) - **default**
- `small` - Better quality (244MB)
- `medium` - High quality (769MB)
- `large` - Best quality (1550MB)

**Rate limits (Gemini Free):**
- 15 requests per minute
- 1,500 requests per day
- Well within limits for typical use

**Files:**
- Script: `/home/jesse/utilities/scripts/analyze-video.py`
- Wrapper: `/home/jesse/utilities/bin/analyze-video`
- Venv: `/home/jesse/utilities/video-analysis-env/`

### Other Tools

- `rg` - ripgrep (fast code search)
- `yt-dlp` - YouTube downloader
- `build_collections.py` - Plex/Kometa collection builder
- `franchise-audit.ps1` - Media server franchise auditing

## Adding New Tools

1. **For binaries:** Place in `/home/jesse/utilities/bin/`
2. **For scripts:** Place in `/home/jesse/utilities/scripts/`
3. **Make executable:** `chmod +x /path/to/tool`
4. **Update this README:** Document the tool

## Global Claude Commands

Commands in `/home/jesse/utilities/claude-commands/` are symlinked to `~/.claude/commands/` and available in all projects:

- `/wp-install` - Install WordPress
- `/wp-setup` - Configure WordPress
- `/wp-update` - Update WordPress
- `/wp-update-all` - Update all WordPress sites
- `/brand-design` - Complete brand creation system

To add new global commands:
```bash
# Create command file
vim /home/jesse/utilities/claude-commands/new-command.md

# Symlink to global commands
ln -s /home/jesse/utilities/claude-commands/new-command.md ~/.claude/commands/new-command.md
```

## PATH Configuration

The `bin/` directory is in PATH (configured in `~/.bashrc`), so all tools are accessible system-wide.
