# Session Notes - Global

This file tracks cross-project work and general development sessions.

## Current Status

**DealScout nearly ready.** All APIs configured except eBay (pending account approval). VPS subdomain configured.

## Pending Tasks

- [x] Set up Gemini API key
- [x] Set up Gmail OAuth credentials
- [x] Set up Firebase (FCM for push notifications)
- [x] Complete Gmail OAuth flow (token.pickle)
- [x] Set up VPS subdomain (dealscout.junipr.io)
- [ ] Wait for eBay API account approval (dev@junipr.io)
- [ ] Add eBay credentials to .env
- [ ] Deploy backend to VPS
- [ ] Test full flow
- [ ] Build and test mobile app

## Next Steps

1. Wait for eBay developer account approval (1+ business day)
2. Add eBay credentials to backend/.env
3. Deploy backend to dealscout.junipr.io
4. Sign up for Swoopa free trial
5. Test full deal flow

## Blockers/Dependencies

- eBay Developer account pending approval (registered with dev@junipr.io)

## Session Log

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
