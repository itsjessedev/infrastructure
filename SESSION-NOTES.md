# Session Notes - Global

This file tracks cross-project work and general development sessions.

## Current Status

**WSL removed from both machines. Network drives configured on DESKTOP and LAPTOP.**

## Pending Tasks

- [x] Set up Gemini API key
- [x] Set up Gmail OAuth credentials
- [x] Set up Firebase (FCM for push notifications)
- [x] Complete Gmail OAuth flow (token.pickle)
- [x] Set up VPS subdomain (dealscout.junipr.io)
- [x] Set up laptop WSL environment
- [x] Set up Syncthing for home folder sync
- [x] Set up Tailscale for direct P2P connection
- [x] Complete initial Syncthing sync
- [x] Switch Syncthing to two-way sync
- [x] Wait for eBay API account approval (dev@junipr.io) - APPROVED
- [x] Add eBay credentials to .env
- [x] Deploy DealScout backend to VPS
- [x] Test full DealScout flow (AI classification + eBay lookup working)
- [x] Build and test mobile app (SDK 54 running in Expo Go)
- [ ] Set up Swoopa alerts to dealscout25@gmail.com for real email testing
- [ ] Test push notifications with development build (not Expo Go)
- [ ] Complete mobile app testing (all screens functional)

## Next Steps

1. Set up Swoopa marketplace alerts to dealscout25@gmail.com
2. Test real email ingestion flow
3. Create Expo development build for push notifications
4. Polish mobile app UI and fix remaining issues

## Blockers/Dependencies

- Push notifications don't work in Expo Go for SDK 53+ (need development build)

## Session Log

### Session: 2026-01-12 (Lead Prospector)
**Accomplishments:**
- Built complete Lead Prospector tool for finding local businesses needing AI/automation
- Created GUI application with tkinter (city/county selectors, category selectors, progress bar, results table)
- Integrated Google Places API for business discovery
- Built website scraper for emails, social links, booking status, pain points
- Integrated Gemini AI (via Google AI API) for analyzing business opportunities
- Set up API rotation: OpenRouter primary, Google AI fallback
- Connected Google Sheets export with service account
- Created private repo: github.com/itsjessedev/lead-prospector
- Project location: /home/jesse/itsjesse.dev/lead-prospector/

**Commits Made:**
- Initial scaffolding with scraper modules
- Main GUI application with tkinter
- API rotation for OpenRouter/Google AI fallback
- Bug fixes for hanging and NoneType errors

**Testing:**
- Google Places API: Working (found 20 plumbers in Cookeville)
- Gemini AI analysis: Working (generating pain points and suggested approaches)
- Google Sheets: Connected and working
- GUI: Runs on Windows but had some hanging issues (fixed with timeouts)

**Pending:**
- User testing GUI on Windows with latest fixes
- Package as Windows EXE with PyInstaller

**Next Steps:**
1. User to test latest version with `git pull && python lead_prospector.py`
2. If working, build EXE: `pyinstaller --onefile --windowed --name "Lead Prospector" lead_prospector.py`
3. Start prospecting local businesses in Upper Cumberland TN

### Session: 2026-01-02 17:30
**Accomplishments:**
- Set up Claude Code on LAPTOP to match DESKTOP configuration
- Installed Node.js v24.12.0 LTS via winget on LAPTOP
- Installed Git v2.52.0 via winget on LAPTOP
- Installed Claude Code v2.0.76 via npm on LAPTOP
- Copied all 10 slash commands from DESKTOP to LAPTOP:
  - /hi, /bye, /goodnight, /check-repos, /save
  - /brand-design, /wp-install, /wp-setup, /wp-update, /wp-update-all
- Copied all 8 skills from DESKTOP to LAPTOP:
  - dealscout-debug, expo-dev, fastapi-backend
  - scaffold-component, scaffold-endpoint, scaffold-screen
  - study-buddy-content, vps-deploy
- Configured bypassPermissions mode on LAPTOP
- Set up custom status line (shows model + context %) on LAPTOP
- LAPTOP now has identical Claude Code setup as DESKTOP

**Commits Made:**
- None (no code changes, only LAPTOP configuration)

**Pending Tasks:**
- [ ] Test Claude Code on LAPTOP to verify everything works

**Next Steps:**
1. User can now run Claude Code on LAPTOP with full feature parity

**Notes:**
- LAPTOP Claude Code accessible via: `claude` command in PowerShell
- Config location: `C:\Users\Jesse\.claude\`

---

### Session: 2025-12-31 (New Year's Eve)
**Accomplishments:**
- Completed DESKTOP network drive setup:
  - Set network profile to Private (was Public, blocking SMB)
  - Created `map-drives.bat` script on Desktop
  - Mapped L: → `\\192.168.99.84\devlab` (full dev-lab filesystem)
  - Mapped M: → `\\192.168.99.83\media` (Unraid media share)
  - Both drives persistent with saved credentials
- Reset Samba password on dev-lab (same password, just refreshed)
- Committed savestate flipping master plan document

**Commits Made:**
- projects: "Add Facebook Marketplace flipping master plan" (448c24b)

**Repository Status:**
- All repos clean and pushed
- itsjesse.dev has WIP portfolio projects (untracked, intentional)

**Notes:**
- SSH sessions can't save Windows credentials (requires interactive session)
- Used batch script workaround for drive mapping
- GitHub repo moved notice: projects repo now at itsjessedev/projects.git

---

### Session: 2025-12-24 00:15
**Accomplishments:**
- Researched AMD motherboard + CPU combos to replace i9-9900KF under $200
  - Compared Ryzen 5 5600X, Ryzen 7 5700X, Threadripper PRO 3945WX performance
  - Found used 5700X (~$170) + B550 (~$50) = best value but slightly over budget
  - Recommended 5600X + B550 for under $200 (beats 9900KF by 21%)
- Set up 13 MCP servers for Claude Code:
  - cloudflare, playwright, postgres, sqlite, filesystem, git, github
  - memory, fetch, thinking, docker, youtube, websearch
- Created 5 custom skills in ~/.claude/skills/:
  - expo-dev: React Native/Expo development in WSL
  - fastapi-backend: FastAPI endpoint/model/migration patterns
  - vps-deploy: VPS deployment and systemd service management
  - dealscout-debug: DealScout-specific debugging
  - study-buddy-content: Question generator and explainer creation
- Explained Claude Code extension architecture (MCP servers, skills, hooks, slash commands)
- Synced global agent context files (CLAUDE.md → AGENTS.md, GEMINI.md)

**MCP Servers Installed:**
- Connected: memory, github, filesystem
- Installed (need runtime args): cloudflare, playwright, postgres, sqlite, git, fetch, thinking, docker, youtube, websearch

**Skills Created:**
- ~/.claude/skills/expo-dev/SKILL.md
- ~/.claude/skills/fastapi-backend/SKILL.md
- ~/.claude/skills/vps-deploy/SKILL.md
- ~/.claude/skills/dealscout-debug/SKILL.md
- ~/.claude/skills/study-buddy-content/SKILL.md

**Pending Tasks:**
- [ ] Restart Claude Code to load new MCP servers
- [ ] Test MCP servers with real queries
- [ ] Regenerate GitHub PAT (shared in chat)

**Next Steps:**
1. Restart Claude Code to activate MCP servers
2. Test memory MCP for cross-session persistence
3. Continue with DealScout or Study Buddy work

**Notes:**
- GitHub PAT stored in ~/.claude.json (expires Jan 23, 2026)
- Memory MCP will enable cross-session knowledge retention
- Skills auto-activate based on task context (no explicit invocation needed)

---

### Session: 2025-12-23 04:22
**Accomplishments:**
- Added distance calculation for deals (location.py service with Haversine formula)
- Integrated eBay local pickup detection for deals within 100mi of Rickman, TN
- Added distance display and "Local Pickup" badge on deal cards
- Created React web app at dealscout.junipr.io (dark theme landing page)
- Restructured API to /api path (dealscout.junipr.io/api)
- Implemented eBay OAuth-based authentication system:
  - User model with session token management
  - Auth service with token generation and validation
  - /auth endpoints (status, login, logout, me)
  - Updated eBay callback to create users and issue session tokens
  - Mobile AuthContext for app-wide auth state
- Updated mobile API service with auth methods and token injection
- Updated Caddy config for web app + API routing

**Commits Made:**
- dealscout: "Add distance calculation and eBay local pickup detection" (0865ec7)
- dealscout: "Add web app, API restructure, and eBay OAuth authentication" (a2b6c14)

**Pending Tasks:**
- [ ] Wire up AuthContext in mobile App.tsx
- [ ] Add login UI to mobile app
- [ ] Add auth callback handling in web app
- [ ] Test full eBay OAuth login flow

**Next Steps:**
1. Complete mobile app auth integration (login screen, session persistence)
2. Add auth callback route to web app
3. Test end-to-end login with real eBay account

---

### Session: 2025-12-23 01:00
**Accomplishments:**
- Configured eBay API credentials in backend/.env
- Deployed DealScout backend to VPS (dealscout.junipr.io)
- Fixed Gemini API quota issues by switching to OpenRouter API
- Rewrote gemini_classifier.py to use OpenRouter (google/gemini-2.0-flash-001)
- Successfully tested full pipeline: classification → eBay lookup → profit calculation
- Upgraded mobile app to Expo SDK 54 for Expo Go compatibility
- Fixed multiple toFixed() errors (API returns strings, not numbers)
- Added Android-compatible purchase modal (Alert.prompt is iOS-only)
- Added placeholder app icons for Expo
- Configured Cloudflare WAF exception for dealscout.junipr.io API access
- Added Cloudflare API credentials to global CLAUDE.md
- Added troubleshooting note to global CLAUDE.md about dependency issues
- Fixed backend profit_calculator.py Decimal type conversion error

**Commits Made:**
- dealscout: "Session end: Mobile app fixes, OpenRouter integration, Cloudflare config" (49d11d6)

**Pending Tasks:**
- [ ] Set up Swoopa alerts to dealscout25@gmail.com
- [ ] Test purchase flow (I Bought This button) end-to-end
- [ ] Test Mark Sold flow
- [ ] Create development build for push notifications

**Next Steps:**
1. Set up Swoopa marketplace alerts
2. Test complete user flow in mobile app
3. Create Expo development build for push notifications

**Notes:**
- Push notifications don't work in Expo Go for SDK 53+
- Cloudflare exception added to WAF rule for dealscout.junipr.io
- OpenRouter API key stored in backend/.env (sk-or-v1-...)
- Mobile app API URL: https://dealscout.junipr.io

---

### Session: 2025-12-22 20:00
**Accomplishments:**
- Documented WSL auto-start solution in SYNC-SETUP.md
  - Working method: Windows Terminal Preview "Launch on machine startup" with Ubuntu as default
- Fixed media-server agent context file sync (removed duplicate header lines)
- Noted eBay developer account is approved (will configure later)

**Commits Made:**
- infrastructure: "Update WSL auto-start solution in sync docs" (3270efc)
- media-server: "Sync agent context files (AGENTS.md, GEMINI.md)" (82efa77)

**Pending Tasks:**
- [ ] Add eBay credentials to DealScout backend/.env
- [ ] Deploy DealScout backend to VPS
- [ ] Test full DealScout flow
- [ ] Build and test mobile app

**Next Steps:**
1. GPU upgrade (user doing now)
2. When ready, configure eBay credentials and deploy DealScout

---

### Session: 2025-12-22 19:30 (Sync Setup Finalized)
**Accomplishments:**
- Abandoned Windows-native Syncthing/Tailscale approach (files in WSL require WSL running anyway)
- Reinstalled Syncthing + Tailscale in WSL on desktop
- Configured bidirectional sync between desktop and laptop
- Removed old Windows Tailscale entry, renamed WSL to jesse-desktop
- Cleaned up failed WSL auto-start attempts (Task Scheduler, VBScript)
- Created SYNC-SETUP.md documentation with full config details

**Commits Made:**
- study-buddy: "Update package-lock.json files" (06dc757)
- infrastructure: "Add desktop/laptop sync setup documentation" (9f622b3)

**Sync Config:**
- Desktop Tailscale: 100.125.236.116 (jesse-desktop)
- Laptop Tailscale: 100.78.98.78 (jesse-laptop)
- Desktop Syncthing ID: JZ33BAM-2R4H57F-NHNBK4U-NHEA4UJ-5HUXT5V-ESWXPJK-7HBKOCP-GGUCIAQ
- Laptop Syncthing ID: K42WERT-V243B4F-S47OD3C-CCUKUWG-LJZVYQR-GGHOJRE-QGVY7LA-QP727AB

**Notes:**
- WSL auto-start still not solved - user will try their own approach
- Sync works when WSL is running on both machines
- See infrastructure/SYNC-SETUP.md for full documentation

---

### Session: 2024-12-22 17:35 (WSL Auto-Start Fix v2)
**Status:** Rebooted - VBScript did NOT work

**Problem:** VBScript in Startup folder doesn't reliably start WSL

**Solution:** Use Task Scheduler with proper PowerShell command:
```powershell
# Run in PowerShell as Admin
schtasks /delete /tn "Start WSL" /f 2>$null
$action = New-ScheduledTaskAction -Execute "wsl.exe" -Argument "-d Ubuntu -- sleep infinity"
$trigger = New-ScheduledTaskTrigger -AtLogOn -User "$env:USERNAME"
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName "Start WSL" -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Keep WSL running for Syncthing"
```

**Key fixes:**
- `sleep infinity` keeps WSL alive (old task exited immediately)
- AllowStartIfOnBatteries - works on laptop
- DontStopIfGoingOnBatteries - won't kill when unplugged
- StartWhenAvailable - runs if missed

**After reboot, verify with:**
- Check if WSL is running without opening terminal
- `wsl -l -v` in PowerShell should show Ubuntu running
- Syncthing should be accessible at http://localhost:8384

**Cleanup:** Delete useless VBScript:
```powershell
Remove-Item "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\start-wsl.vbs"
```

---

### Session: 2024-12-22 17:15 (WSL Auto-Start Fix)
**Accomplishments:**
- Fixed Syncthing not auto-starting on Windows login
  - Root cause: WSL doesn't start until terminal is opened, even with systemd enabled
  - Created VBScript startup script: `start-wsl.vbs` in Windows Startup folder
  - Script silently runs `wsl.exe -d Ubuntu -- sleep infinity` to keep WSL alive
- Reviewed session status and all repository states

**Files Created:**
- `/mnt/c/Users/Jesse/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/start-wsl.vbs`

**Commits Made:**
- dealscout: "Add mobile package-lock.json" (976d1e6)

**Next Session:**
1. Verify WSL auto-start works after reboot
2. If working, verify Syncthing starts automatically
3. Continue with SaveState/DealScout work

**Context for Next Session (if auto-start fails):**
- VBScript location: `C:\Users\Jesse\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\start-wsl.vbs`
- Script content: `objShell.Run "wsl.exe -d Ubuntu -- sleep infinity", 0, False`
- The old Task Scheduler "Start WSL" task was broken because:
  - It ran `wsl -d Ubuntu` without a command, so WSL started and immediately exited
  - Had `No Start On Batteries` restriction (bad for laptop)
  - Last Result was -1 (failure)
- Task Scheduler task should be deleted (needs admin: `schtasks /delete /tn "Start WSL" /f`)
- If VBScript doesn't work, alternatives:
  1. Fix Task Scheduler: `wsl -d Ubuntu -- sleep infinity` with battery restriction removed
  2. Use native Windows Syncthing (no WSL dependency)
  3. Use both VBScript + Task Scheduler for redundancy

---

### Session: 2024-12-22 02:00 (Laptop Setup & Syncthing)
**Accomplishments:**
- Set up laptop WSL2 environment to mirror desktop:
  - Created laptop-wsl-setup.txt with full instructions
  - Cloned all git repos (dealscout, junipr, projects, infrastructure, dotfiles, media-server, study-buddy)
  - Applied dotfiles with stow
  - Installed all apt packages, nvm, node, npm global packages
  - Created verify-wsl-setup.sh verification script
- Set up Syncthing for ~/home/jesse folder sync:
  - Installed Syncthing on both machines
  - Created .stignore for machine-specific exclusions (.ssh, node_modules, venv, etc.)
  - Configured desktop as "Send Only", laptop as "Receive Only" for safe initial sync
  - Connected devices via Tailscale for direct P2P (not relay)
- Set up Tailscale on both machines:
  - Desktop: 100.120.124.100 (jesse-desktop)
  - Laptop: 100.78.98.78 (jesse-laptop)
  - Direct mesh VPN connection for fast sync anywhere
- Created transfer.zip with non-git files:
  - ~/CLAUDE.md, ~/AGENTS.md, ~/GEMINI.md
  - DealScout backend credentials (.env, credentials.json, firebase-service-account.json, token.pickle)

**Files Created:**
- /mnt/c/Users/Jesse/Desktop/laptop-wsl-setup.txt - Setup instructions
- /mnt/c/Users/Jesse/Desktop/verify-wsl-setup.sh - Verification script
- /mnt/c/Users/Jesse/Desktop/transfer.zip - Non-git files for manual transfer
- ~/.stignore - Syncthing exclusion patterns

**Commits Made:**
- media-server: "Update context files (AGENTS.md, GEMINI.md)" (ca7d6e3)

**Next Session:**
1. Verify Syncthing initial sync completed
2. Switch both machines to "Send & Receive" mode
3. Test bidirectional sync
4. Continue with DealScout/SaveState work

**Notes:**
- Syncthing uses Tailscale IPs for direct connection (not relay servers)
- Initial sync is ~11 GB, ETA 30-60 minutes
- After sync completes, run on both machines:
  - `syncthing cli config folders home type set sendreceive`
  - `systemctl --user restart syncthing`

---

### Session: 2024-12-22 04:30 (SaveState Brand Assets)
**Accomplishments:**
- Ran /brand-design workflow to create complete brand identity for SaveState:
  - Generated brand palette with 2 parallel agents, merged best elements
  - Created 10 logo prompts for DALL-E/Midjourney
  - Rewrote top 3 logo concepts for Google Nano Banana image generator
  - Generated CSS custom properties, Tailwind config, and design tokens
  - Created visual guidelines (photography, iconography, patterns)
  - Created component library specifications (buttons, cards, forms, badges)
  - Created social media kit (eBay, Instagram, Facebook complete guides)
  - Generated preview HTML files for colors and typography
- Reviewed and selected best outputs from each agent:
  - Used Gemini agent's code assets (better dark mode, plugins)
  - Used Codex agent's component library (more thorough)
  - Used Gemini agent's social media kit (more detail)
- Created project CLAUDE.md with website development guidance
- Fixed Syncthing ignore pattern (added .local/state/syncthing)
- Answered user questions about eBay business registration requirements
- Registered eBay store as SaveStateUS

**Brand Colors Finalized:**
- SaveState Navy: #1A2B4D (primary)
- Energy Orange: #FF6B35 (CTAs)
- Game Boy Green: #A4D65E (success)
- Retro Purple: #9B59B6 (premium)
- Warning Amber: #FF9D00 (caution)
- Alert Red: #E74C3C (errors only)

**Typography Stack:**
- Inter (H1-H3), Poppins (H4-H6), Roboto (body), Roboto Mono (technical)

**Commits Made:**
- projects: "Session end: Add SaveState brand assets and design system" (2b40edd)
- projects: "Sync agent context files (AGENTS.md, GEMINI.md)" (162de18)
- infrastructure: "Session end: Add requirements files for image/video utilities" (c54f704)

**Files Created:**
- savestate/brand-assets/savestate-brand-palette.txt - Master brand guide
- savestate/brand-assets/logo-prompts.txt - 10 DALL-E/Midjourney prompts
- savestate/brand-assets/logo-prompts-nano-banana.txt - 3 Nano Banana prompts
- savestate/brand-assets/visual-guidelines.md
- savestate/brand-assets/component-library.md
- savestate/brand-assets/social-media-kit.md
- savestate/brand-assets/code/ - CSS, Tailwind, design tokens
- savestate/brand-assets/preview/ - HTML preview files
- savestate/brand-assets/CLAUDE.md, AGENTS.md, GEMINI.md

**Next Session:**
1. Generate logo using Nano Banana prompts
2. Create eBay listing template using brand assets
3. Set up inventory tracking system

---

### Session: 2024-12-22 (SaveState Business Planning)
**Accomplishments:**
- Planned SaveState electronics resale business:
  - Defined product categories: retro gaming, PC parts, phones, vintage audio, test equipment
  - Researched sourcing channels: estate sales, thrift stores, liquidation pallets
  - Identified Liquidation.com and BlueLots as no-license-required bulk sources
  - Created profitability framework and pricing strategy
  - Documented phone verification process (IMEI checks, activation lock, carrier lock)
- Chose business name: SaveState
- Registered domain: savestate.shop
- Set up project folder at ~/projects/savestate/ with:
  - README.md with full business plan
  - Inventory tracking guide
  - Folder structure (inventory, finances, sourcing, listings, repairs, docs)

**Commits Made:**
- projects: "Add SaveState electronics resale business project" (4a8584a)

**Next Session:**
1. Create professional eBay HTML listing template for SaveState
2. Design branding (colors, logo placeholder)
3. Set up eBay store account
4. Create inventory spreadsheet

**Notes:**
- Reopening in ~/projects/savestate/ to build eBay listing template
- User wants "professional af" HTML template with graphics

---

### Session: 2024-12-22 00:30
**Accomplishments:**
- Set up eBay Developer account with dev@junipr.io (pending approval, old account was suspended)
- Fixed Google Workspace org policy to allow service account key creation
- Set up Firebase project (dealscout-88ed6):
  - Created project in Firebase Console
  - Downloaded google-services.json for mobile app
  - Downloaded firebase-service-account.json for backend
  - Added FIREBASE_PROJECT_ID to .env
- Configured VPS for DealScout:
  - Added dealscout.junipr.io subdomain to Cloudflare
  - Installed nginx and certbot on VPS
  - Added Caddy config for dealscout.junipr.io → port 8002
  - SSL will auto-provision on first request
- Completed Gmail OAuth flow:
  - Ran OAuth authorization for dealscout25@gmail.com
  - Generated token.pickle for email access
- Installed Google Chrome in WSL for future OAuth flows
- Added DISPLAY=:0 to .bashrc for WSLg GUI support
- Updated .gitignore to include token.pickle
- Committed and pushed all changes

**Files Modified:**
- ~/portfolio/dealscout/backend/.env - Added FIREBASE_PROJECT_ID
- ~/portfolio/dealscout/backend/firebase-service-account.json - Firebase admin credentials
- ~/portfolio/dealscout/backend/token.pickle - Gmail OAuth token
- ~/portfolio/dealscout/mobile/google-services.json - Firebase Android config
- ~/portfolio/dealscout/.gitignore - Added token.pickle
- ~/.bashrc - Added DISPLAY=:0 for WSLg

**VPS Changes:**
- Installed nginx, certbot on junipr-vps
- Added dealscout.junipr.io to /etc/caddy/Caddyfile

**Commits Made:**
- dealscout: "Add Firebase config and update gitignore" (89f1013)

**Next Session:**
1. Check if eBay account approved
2. Add eBay credentials if approved
3. Deploy backend to VPS
4. Test full flow

---

### Session: 2024-12-21 (continued)
**Accomplishments:**
- Updated DealScoutAPI.md with account strategy:
  - jesse@junipr.io for all API management
  - dealscout25@gmail.com for Swoopa alerts
- Set up Gemini API key in Google Cloud Console (DealScout project)
- Configured Gmail API OAuth:
  - Enabled Gmail API
  - Created OAuth consent screen
  - Added dealscout25@gmail.com as test user
  - Created Desktop app OAuth credentials
  - Downloaded and placed credentials.json
- Added Gemini API key to backend .env
- Added screenshot path convention to global CLAUDE.md
- Synced global context files (CLAUDE.md → AGENTS.md, GEMINI.md)

**Files Modified:**
- /mnt/c/Users/Jesse/Desktop/DealScoutAPI.md - Account strategy updates
- ~/portfolio/dealscout/backend/.env - Added Gemini API key
- ~/portfolio/dealscout/backend/credentials.json - Gmail OAuth credentials
- ~/CLAUDE.md - Added screenshot path convention
- ~/AGENTS.md, ~/GEMINI.md - Synced from CLAUDE.md

**Next Session:**
1. Set up eBay API credentials
2. Set up Firebase project and FCM
3. Test backend locally

---

### Session: 2024-12-21
**Accomplishments:**
- Built complete DealScout app from scratch (deal discovery + flip tracking)
- Conducted market research on Swoopa competitors and reseller tool market
- Designed app for ANY item type (not just PC parts)
- Created FastAPI backend with:
  - Gmail API email ingestion for Swoopa alerts
  - Gemini Flash AI classification (category, brand, model, condition)
  - eBay API price lookup (used/new sold listings)
  - Profit calculation with fee handling
  - Firebase Cloud Messaging push notifications
  - Scheduler: email checks (5min), review reminders (15min)
- Created React Native/Expo mobile app with:
  - Deals feed with "Needs Review" section for unknown conditions
  - Current Flips inventory tracker
  - Profits history with filters (date, category, platform)
  - Settings screen
- Wrote comprehensive API setup guide to Windows Desktop

**Commits Made:**
- dealscout: "Initial DealScout implementation" (31 files, 3840 lines)

**Repo Created:**
- https://github.com/junipr-dev/dealscout (public, portfolio-worthy)

**Key Design Decisions:**
- Item-agnostic: Works for any marketplace item, not just PC parts
- Condition detection: AI detects new/used, asks user if unclear (never guesses)
- 15-min review checks: Hardcoded, no settings needed
- eBay lookup matches condition: New items → new sold prices, used → used

**Files Created:**
- ~/portfolio/dealscout/ - Full project structure
- Backend: FastAPI with SQLite, services for Gmail/Gemini/eBay/FCM
- Mobile: React Native with 4 tab screens
- /mnt/c/Users/Jesse/Desktop/DealScoutAPI.md - Setup guide

**Next Steps:**
1. Set up API keys (Gemini, eBay, Gmail OAuth, Firebase)
2. Test backend locally
3. Deploy to VPS (lab.junipr.io)
4. Build and test mobile app

---

### Session: 2024-12-20 (continued)
**Accomplishments:**
- Implemented local push notifications with @notifee/react-native
- Added Google Sign-In with @react-native-google-signin
- Implemented account linking flow for Google with existing email/password accounts
- Added user settings persistence to Firestore for cross-device sync
- Created advance reminders feature (select 7, 3, 1, or day-of notifications)
- Built phone contact import with permission handling
- Integrated RevenueCat payments with PaywallModal
- Created ReminderDaysSelector and PaywallModal components
- Added updateUserTier action to Zustand store
- Updated all relevant screens and navigation

**Commits Made:**
- projects: "Add Phase 2 features: notifications, Google auth, payments, contact import"

**New Files Created:**
- src/services/notifications.ts - Local notification scheduling
- src/services/purchases.ts - RevenueCat integration
- src/screens/ImportContactsScreen.tsx - Contact import UI
- src/components/ReminderDaysSelector.tsx - Reminder checkbox UI
- src/components/PaywallModal.tsx - Subscription upgrade modal
- REVENUECAT_SETUP.md - Configuration documentation

**Technical Notes:**
- Used 3 parallel background agents for simultaneous feature development
- RevenueCat needs API key configuration before payments work
- All features tested on Android emulator

**Next Session:**
1. Update WSL .wslconfig for 32GB RAM (user installed upgrade)
2. Test all new features thoroughly
3. Configure RevenueCat dashboard

---

### Session: 2024-12-20 05:30
**Accomplishments:**
- Created complete Cakebuddy birthday reminder app from scratch
- Built comprehensive product plan with freemium tiers and monetization strategy
- Chose app name "Cakebuddy" after extensive name research
- Set up React Native 0.83 project with TypeScript
- Configured Firebase (Auth, Firestore, FCM) for backend
- Created full app UI:
  - Login/Signup screens with Firebase Auth
  - Home screen with birthday list and countdown
  - Add Contact screen
  - Contact Detail screen (zodiac, age, days until)
  - Settings screen
- Set up navigation with auth state handling
- Installed Java 17, Android SDK, NDK, CMake in WSL
- Successfully built and launched app on Android emulator
- Fixed WSL ↔ Windows Android SDK integration issues

**Files Created:**
- `/home/jesse/projects/cakebuddy/` - Full project structure
- `/home/jesse/projects/cakebuddy/docs/PRODUCT-PLAN.md`
- `/home/jesse/projects/cakebuddy/app/` - React Native app
- All screens: LoginScreen, SignupScreen, HomeScreen, AddContactScreen, ContactDetailScreen, SettingsScreen
- Firebase service, Zustand store, TypeScript types, Navigation

**Technical Setup:**
- React Native 0.83.1 with New Architecture
- Firebase: Auth, Firestore, Cloud Messaging
- Zustand for state management
- React Navigation for routing
- Build uses Windows Android SDK from WSL

**Key Commands for Next Session:**
```bash
# Start Metro
cd ~/projects/cakebuddy/app && npx react-native start --host 0.0.0.0

# In another terminal, set up adb reverse (if needed)
/mnt/c/Users/Jesse/AppData/Local/Android/Sdk/platform-tools/adb.exe reverse tcp:8081 tcp:8081

# Launch app
/mnt/c/Users/Jesse/AppData/Local/Android/Sdk/platform-tools/adb.exe shell am start -n com.cakebuddy/.MainActivity
```

**Notes:**
- First build takes 30-45 mins (compiles C++ for 4 architectures)
- Subsequent builds are fast (2-3 mins) due to caching
- Hot reload works - code changes appear instantly
- Added cost optimization rule to global CLAUDE.md (use haiku/sonnet when possible)

---

### Session: 2024-12-18 16:45
**Accomplishments:**
- Created AGENTS.md (Codex context file) matching CLAUDE.md
- Created GEMINI.md (Gemini context file) matching CLAUDE.md
- Added synchronization rules to all three agent context files (system-wide AND project-level)
- Renamed slash commands for consistency:
  - `/session-start` → `/start-session`
  - `/wrap-session` → `/end-session`
  - `/eod` → `/end-day`
- Updated all command files with new names
- Updated `/start-session` to handle first-time use (no session notes yet)
- Updated `/end-session` and `/end-day` to automatically sync project-level context files
- Clarified that context file sync applies at BOTH system-wide and project levels
- Updated all references in CLAUDE.md, AGENTS.md, GEMINI.md, infrastructure README, SESSION-NOTES.md
- User fixed symlinks manually (bash was broken)

**Files Created:**
- `/home/jesse/AGENTS.md` - Global Codex context
- `/home/jesse/GEMINI.md` - Global Gemini context
- `/home/jesse/infrastructure/system-utilities/claude-commands/start-session.md`
- `/home/jesse/infrastructure/system-utilities/claude-commands/end-session.md`
- `/home/jesse/infrastructure/system-utilities/claude-commands/end-day.md`

**Files Modified:**
- `/home/jesse/CLAUDE.md` - Added sync rules for both global and project levels
- `/home/jesse/AGENTS.md` - Added sync rules for both global and project levels
- `/home/jesse/GEMINI.md` - Added sync rules for both global and project levels
- `/home/jesse/infrastructure/README.md` - Updated command names
- `/home/jesse/infrastructure/SESSION-NOTES.md` - Updated references
- `/home/jesse/infrastructure/system-utilities/claude-commands/start-session.md` - Added first-time disclaimer
- `/home/jesse/infrastructure/system-utilities/claude-commands/end-session.md` - Added automatic context sync
- `/home/jesse/infrastructure/system-utilities/claude-commands/end-day.md` - Added automatic context sync

**Key Insight:**
- Context files needed at BOTH levels: system-wide `/home/jesse/` AND project-level `<project-root>/`
- Allows switching between Claude/Codex/Gemini at any time in any project
- `/end-session` and `/end-day` automatically sync project-level context files

**Pending Tasks:**
- [ ] Delete old command files (session-start.md, wrap-session.md, eod.md) if they still exist
- [ ] Delete sync-context.md (not needed - sync happens in /end-session)
- [ ] Commit all changes
- [ ] Test the renamed commands

**Next:**
- Commit infrastructure repo changes
- Commit CLAUDE.md, AGENTS.md, GEMINI.md
- Verify symlinks are correct
- Create project-level context files for existing projects (Junipr, etc.)

---

### Session: 2024-12-18 15:30
**Accomplishments:**
- Created comprehensive repository management system
- Added auto-detection of all git repos (not hardcoded list)
- Created `/check-repos` command with intelligent health checks
- Created `/wrap-session` command for end-of-session cleanup
- Created `/eod` command for complete end-of-day workflow
- Created `/session-start` command for beginning new sessions
- Updated all commands to include session notes tracking
- Added session notes files to global .gitignore
- Updated CLAUDE.md with agent protocol and slash command workflow
- Updated infrastructure README.md
- Hidden all dotfiles in Windows Explorer for cleaner view

**Commands Created:**
- `/start-session` - Start new session with context from last session
- `/check-repos` - Auto-detect and check all repos for issues
- `/end-session` - Commit, push, update session notes
- `/end-day` - Complete end-of-day workflow

**Files Modified:**
- `/home/jesse/CLAUDE.md` - Added agent protocol section
- `/home/jesse/infrastructure/README.md` - Updated command list
- `/home/jesse/dotfiles/git/.gitignore_global` - Added session notes
- `/home/jesse/infrastructure/system-utilities/scripts/check-all-repos.sh` - Created
- `/home/jesse/infrastructure/system-utilities/claude-commands/check-repos.md` - Created
- `/home/jesse/infrastructure/system-utilities/claude-commands/wrap-session.md` - Created
- `/home/jesse/infrastructure/system-utilities/claude-commands/eod.md` - Created
- `/home/jesse/infrastructure/system-utilities/claude-commands/session-start.md` - Created

**Pending Tasks:**
- [ ] Recreate symlinks in `~/.claude/commands/` (bash shell broken)
- [ ] Commit changes to infrastructure repo
- [ ] Commit changes to dotfiles repo
- [ ] Commit changes to CLAUDE.md

**Next Steps:**
1. User needs to manually run these commands to fix symlinks:
   ```bash
   cd ~
   rm -rf .claude/commands/*
   ln -sf ~/infrastructure/system-utilities/claude-commands/*.md .claude/commands/
   ```
2. Test the new commands
3. Commit everything

**Notes:**
- Bash shell broke when `/home/jesse/utilities/` was deleted (was current directory)
- All commands moved to `/home/jesse/infrastructure/system-utilities/claude-commands/`
- Session notes system uses `.session-notes.md` for project-specific, `SESSION-NOTES.md` for global
- Commands auto-detect which file to use based on context

---

## Session: 2026-01-06 15:15 (Security Cleanup & Media Server)

### Accomplished
- **Removed Topaz Video AI from DESKTOP:**
  - Deleted program data folders (ProgramData, AppData/Local, AppData/Roaming)
  - Removed Start Menu shortcuts
  - Cleaned registry entries (HKCU\SOFTWARE\Topaz Labs LLC)
  - Removed file associations (.mkv, .mpg)
  - Deleted installer from Downloads

- **Discovered and removed ScreenConnect backdoor:**
  - Found malicious "Visual C++" service in C:\Program Files (x86)\Windows VC\
  - Service was connecting to 95.214.234.238 (edgeserv.ru) on port 8041
  - Came bundled with cracked Topaz Video AI from FTUApps.com
  - Stopped service, deleted files, removed registry entries
  - Router was blocking most connection attempts

- **General security audit on DESKTOP:**
  - Verified AVG Driver Updater is legitimate (user confirmed)
  - Checked hosts file - has protective FitGirl blocks
  - Verified SSH authorized keys and user accounts are clean

- **Blocked usrpubtrk.com tracking domain:**
  - Added to Unraid /etc/hosts (0.0.0.0 usrpubtrk.com)
  - Added to /boot/config/go for persistence across reboots
  - Was being triggered by ARR stack, not needed for downloads

- **Fixed stalled qBittorrent downloads:**
  - Removed 2 stalled Regular Show torrents (wrong episode numbering)
  - Found 4 missing episodes (S08E26-E29, series finale arc)
  - Sourced working magnet links with active seeds:
    - S08E26: 2 seeds
    - S08E27: 3 seeds
    - S08E28: 5 seeds
    - S08E29: 6 seeds

### Credentials Saved to Memory
- qBittorrent: admin / MediaServer2024!
- Sonarr API Key: 152f02f5f82b40c084f02a102a4041e4
- Radarr API Key: f22c6b659bdb4a0a8628f199ca5b9b4d

### Commits Made
- itsjesse.dev: "DevScout: LinkedIn comment engagement system" (8ef3382)
  - ~1500 lines added for comment queue management system

### Repository Status
- All repos clean and pushed

### Pending
- [ ] Monitor Regular Show downloads to completion

### Notes
- Router (192.168.99.1) blocked most edgeserv.ru connection attempts
- Cracked software from FTUApps bundled ScreenConnect backdoor
- Always verify cracked software or avoid entirely

---

## Session: 2025-12-31 (Evening - SSH & Machine Access Setup)

### Accomplished
- Removed `/home/jesse/dotfiles` folder (redundant - configs already in place in home dir)
- Updated global context files to remove dotfiles references
- **Set up bidirectional SSH access between dev-lab and DESKTOP:**
  - Enabled OpenSSH Server on DESKTOP (Windows 11)
  - Added dev-lab's public key to DESKTOP's authorized_keys
  - Created `ssh desktop` alias on dev-lab (192.168.99.145)
  - Can now make changes to DESKTOP remotely when user requests
- **Set up DESKTOP → VPS SSH access:**
  - Added DESKTOP's public key to VPS authorized_keys
  - Created `ssh vps` alias on DESKTOP
- **Documented machine access strategy in CLAUDE.md:**
  - Auto-detection via SSH source IP (192.168.99.145 = DESKTOP, 100.x.x.x = LAPTOP/MOBILE)
  - DESKTOP: Local ethernet, direct SSH access
  - LAPTOP: Tailscale-only (simpler, works same-LAN and remote)
  - MOBILE: Tailscale for services, no SSH back
  - App testing considerations (Expo/hot reload fine over Tailscale on same LAN)

### Public Keys Saved
- DESKTOP: `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINbhEJtF/lZpKsEeMABjtQvbfE5/2QvHrxQg3wO/I2XZ jesse@desktop`
- LAPTOP: (to be configured)

### SSH Config Updates
- dev-lab `~/.ssh/config`: Added `Host desktop` entry
- DESKTOP `~/.ssh/config`: Added `Host vps` entry (via SCP from dev-lab)

### Naming Convention Established
- Always use DESKTOP/LAPTOP/MOBILE (not "Windows 11", "Windows 10", etc.)

### Commits Made
- infrastructure: pulled updates from remote (SESSION-NOTES.md, DEV-LAB-MIGRATION.md)

### Pending
- [ ] Set up LAPTOP SSH access when ready (get Tailscale IP + public key)

### Next Session
1. Configure LAPTOP when user is ready
2. Test SSH access from different machines

---

## Session: 2025-12-31 (Late Night - Laptop Setup)

### Accomplished
- **Set up LAPTOP for full development access:**
  - Installed Tailscale and connected to network (100.68.237.46)
  - Generated SSH key (`ssh-ed25519...jesse@laptop`)
  - Created SSH config matching DESKTOP (devlab, unraid, vps hosts)
  - Added laptop key to dev-lab, Unraid, and VPS authorized_keys
  - Set up bidirectional SSH: dev-lab can now `ssh laptop`

- **Configured network drives on both LAPTOP and DESKTOP:**
  - `L:` → `\\192.168.99.84\home` (dev-lab home) - user: jesse, pass: devlab123
  - `M:` → `\\192.168.99.83\media` (Unraid media) - user: jesse, pass: media123
  - Reset Unraid Samba password (old one forgotten)

- **Renamed SSH alias:** `server` → `unraid` on all machines (dev-lab, DESKTOP, LAPTOP)

- **Removed WSL completely from both machines:**
  - Unregistered Ubuntu distros
  - Removed WSL AppX packages
  - Disabled WSL and VirtualMachinePlatform Windows features
  - Hidden Linux from File Explorer navigation pane
  - Cleaned up WSL app data and config files
  - Both machines need restart to complete feature removal

- **Updated global context files:**
  - Added LAPTOP SSH and network info to CLAUDE.md
  - Added network drive credentials (L: and M:)
  - Added LAPTOP public key
  - Synced to AGENTS.md and GEMINI.md

### Credentials Saved
- dev-lab SMB: jesse / devlab123
- Unraid SMB: jesse / media123
- LAPTOP Tailscale IP: 100.68.237.46
- LAPTOP local IP: 192.168.99.220

### SSH Config (all machines)
- `ssh devlab` → 192.168.99.84:25831 (dev-lab)
- `ssh unraid` → 192.168.99.83:22 (Unraid root)
- `ssh vps` → 204.152.223.104 (Junipr VPS)

### Pending
- [ ] Restart LAPTOP and DESKTOP to complete WSL removal

### Repository Status
- All repos clean and up to date

---

## Session: 2025-12-31 (Late Night)

### Accomplished
- Verified GPU hardware transcoding is working on Plex with P1000
  - NVDEC (decode) + NVENC (encode) confirmed active
  - nvidia-smi shows no processes inside Docker but GPU memory usage confirms activity
- Updated global context sync method to use faster cp + sed approach
- Synced all agent context files (CLAUDE.md → AGENTS.md, GEMINI.md)

### Previous Session Work (2025-12-31)
- Fixed GPU transcoding by installing nvidia-vaapi-driver
- Disabled Plex trailers (IVA bug with empty stream URLs)
- Created CAM/Telesync blocking custom format in Radarr
- Disabled 1337x (rate limiting) and RuTracker (geo-blocked)
- Documented Disk 2 health warning (8 bad sectors)

### Repository Status
- All repos clean and pushed
- homelab: up to date
- infrastructure: up to date
- projects: up to date
- junipr: up to date
- itsjesse.dev: has untracked portfolio dirs (intentional WIP)
- dotfiles: not present on dev-lab VM

### Next Session
- Consider replacing Disk 2 before failure
- Test more transcoding scenarios to ensure GPU stability
- Review untracked portfolio projects in itsjesse.dev

### Notes
- GPU transcoding only activates when video re-encoding is needed
- Audio transcoding is always CPU-based (normal)
- Direct play/stream doesn't use GPU (optimal behavior)

---

## Session: 2025-12-31 (Night - Network Drive Setup)

### Accomplished
- Rebooted DESKTOP and LAPTOP to complete WSL removal
- Fixed network drive access issues on LAPTOP:
  - Root cause: Network profile was set to "Public" (blocks SMB)
  - Changed to "Private" profile
  - Enabled SMB firewall rules and AllowInsecureGuestAuth registry key
  - Reset Samba passwords on dev-lab (jesse/devlab123) and Unraid (jesse/media123)
- Configured LAPTOP network drives:
  - L: → `\\192.168.99.84\devlab` (full dev-lab filesystem, not just /home/jesse)
  - M: → `\\192.168.99.83\media` (Unraid media share)
- Added SMB2 protocol settings to dev-lab Samba config

### Pending
- [ ] Complete DESKTOP network drive setup (same as LAPTOP)

### Notes
- User can pin /home/jesse to Quick Access for easy access
- Credentials saved with "Remember my credentials" for auto-reconnect on boot


---

### Session: 2026-01-10 (Late Night)
**Accomplishments:**
- Ran Kometa poster sweep for franchise consistency (Harry Potter, Pixar collections, etc.)
- Created Kometa config with TMDb API key and ThePosterDB integrations
- Attempted local SSL setup with mkcert + NPM (reverted - too complex for home network)
- Configured NPM as HTTP-only reverse proxy for .local domains
- Fixed Plex proxy (enabled websockets, disabled buffering)
- Cleaned up disk space issues from earlier session
- Moved Unraid HTTPS from 443 to 8443, then back to 443
- Updated Chrome bookmarks multiple times during SSL troubleshooting
- Added nested project repos (cyber-academy, income-factory, scrap-lab, tonegeist) to .gitignore

**Commits Made:**
- projects: "Add nested project repos to gitignore" (7c97555)

**Pending Tasks:**
- [ ] Verify Plex library loads correctly through plex.local proxy
- [ ] Monitor disk1 temperature (running 40°C, higher than others)
- [ ] Disk2 is nearly full (156KB free) - needs attention

**Next Steps:**
1. Test all .local domains working correctly
2. Consider moving some content off disk2 if needed
3. Re-enable downloads when ready (rdtclient disabled)

**Notes:**
- NPM running on port 80/81 for HTTP reverse proxy
- All .local domains point to 192.168.99.83 via hosts file
- Plex needs websockets enabled to work through reverse proxy
- SSL for local network deemed not worth the complexity

### Session: 2026-01-10 (Early AM)

**Accomplishments:**
- Completed PromptBase business-plan-generator with 4 full example outputs
- Deployed SnapURL API to VPS (port 8005, snapurl-api.junipr.io)
- Synced Claude configs between DESKTOP and dev-lab
- Removed 8 MCPs from dev-lab (thinking, memory, github, etc.) to match DESKTOP
- Copied codex agent to dev-lab
- Removed Mixedbread-Grep plugin from dev-lab
- Copied cyber-academy from VPS to ~/projects/cyber-academy
- Moved Tonegeist to ~/projects/tonegeist

**Commits Made:**
- income-factory: "Add 4 full example outputs to business-plan-generator"
- income-factory: "Add example inputs to PromptBase listing, deploy SnapURL API"

**Income Factory Status:**
- /create-etsy, /create-promptbase, /create-rapidapi, /variate skills complete
- PromptBase listing format finalized with:
  - 40 char title limit, 500 char description limit
  - Claude version, max tokens, temperature settings
  - Test prompt (all variables filled in)
  - 4 example inputs + 4 full example outputs
- SnapURL API deployed and accessible

**Projects Now on dev-lab:**
- ~/projects/cyber-academy (from VPS)
- ~/projects/tonegeist (moved from ~/Tonegeist)
- ~/projects/income-factory

**Claude Config Sync:**
- DESKTOP and dev-lab now match
- 14 commands, 8 skills, 1 agent (codex), 1 plugin
- No MCPs on either machine

**Pending:**
- cyber-academy: Run npm install when working on it
- SnapURL API: Test screenshot endpoint, may need Playwright deps
- Cloudflare may block some IPs accessing snapurl-api.junipr.io

**Notes:**
- VPS uses Caddy for reverse proxy (not nginx)
- API port assignments: 8001=study-buddy, 8002=dealscout, 8005=snapurl-api

---

### Session: 2026-01-11 (Late Night)

**Accomplishments:**
- Deep dive into Breath of Fire 3 ROM extraction and EMI file format reverse engineering
- Created and tested multiple extraction tools:
  - `emi_dump.py` - EMI container section extractor
  - `capcom_lzss.py` - LZSS decompression for Capcom graphics data
  - `tim_extractor.py` - TIM texture finder/extractor
- Successfully decompressed EMI graphics sections (292KB → 360KB)
- Analyzed 0x00b80380 signature - identified as PS1 VRAM coordinate encoding
- Ran jPSXdec extraction (924 items found, mostly small palettes)
- Multiple render attempts (4-bit, 8-bit, 16-bit at various widths) - format still undocumented
- Research agent found EMI is proprietary Capcom format with no public documentation

**Repository Created:**
- breath-of-fire-3: https://github.com/itsjessedev/breath-of-fire-3 (private)
  - Initial commit with all tools and documentation

**Commits Made:**
- homelab: "End of day: Updated agent documentation" (84bf811)
- breath-of-fire-3: "Initial commit: BoF3 HD Remaster project setup" (e0d866b)

**Key Findings:**
- EMI container format: MATH_TBL header, TOC at 0x10 intervals, 2048-byte aligned sections
- Graphics sections use LZSS compression (signature 0x00b80380)
- Decompressed data structure unknown - likely GPU display list format, not raw pixels
- Spriters Resource has existing character sprites that can be used as foundation

**Pending Tasks:**
- [ ] Continue EMI format reverse engineering (or use existing sprites)
- [ ] Start game engine development with available assets
- [ ] HD upscale sprites using ComfyUI/IP-Adapter workflow

**Next Steps:**
1. Decide: continue format cracking vs use Spriters Resource sprites
2. Begin Godot/Python game engine with available assets
3. Test HD generation workflow with IP-Adapter

**Notes:**
- User explicitly rejected VRAM dumping suggestion
- EMI graphics format may require significant reverse engineering effort
- Available sprites from Spriters Resource: Ryu, Nina, Rei, Teepo, Momo, Peco, Garr, Ryu Kaiser
