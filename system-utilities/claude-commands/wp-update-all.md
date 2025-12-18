# WordPress Update All Sites Command

Update WordPress core, plugins, and themes for ALL WordPress installations on the VPS at once.

## Instructions

This command finds and updates all WordPress sites on the VPS in a single operation. Use this for regular maintenance across all sites.

**Steps:**

1. SSH to VPS (junipr-vps)
2. Find all WordPress installations by searching for wp-config.php files
3. For each WordPress installation found:
   - Update WordPress core
   - Update all plugins
   - Update all themes
   - Update database if needed
4. Report summary of all updates across all sites

**WordPress Installation Locations to Check:**
- `/srv/junipr/blog/` (production blog)
- `/home/deploy/lab/*/` (all lab projects)
- Any other locations with wp-config.php

**Commands to Run for Each Site:**

```bash
# Find all WordPress installations
find /srv/junipr /home/deploy/lab -name "wp-config.php" -type f 2>/dev/null

# For each WordPress directory found, run:
wp core update --allow-root
wp plugin update --all --allow-root
wp theme update --all --allow-root
wp core update-db --allow-root
```

**Important:**
- Always use `--allow-root` flag (running as deploy user)
- Skip directories that are backups or contain ".bak" in path
- Report which sites were updated and what changed
- If any site fails to update, continue with others and report errors at end

**Output Format:**

```
Updating WordPress Sites on VPS
================================

Found 2 WordPress installations:
1. /srv/junipr/blog
2. /home/deploy/lab/pickleballsociety

Updating /srv/junipr/blog...
  ✓ WordPress: Already up to date (6.4.2)
  ✓ Plugins: Updated wordfence (7.11.0 → 7.11.1)
  ✓ Themes: All up to date

Updating /home/deploy/lab/pickleballsociety...
  ✓ WordPress: Updated (6.4.1 → 6.4.2)
  ✓ Plugins: Updated rank-math (1.0.200 → 1.0.201)
  ✓ Themes: All up to date
  ✓ Database: Updated

Summary
=======
Sites updated: 2/2
Total plugin updates: 2
Total theme updates: 0
WordPress core updates: 1
Errors: 0
```

**Error Handling:**
- If WP-CLI fails on a site, note the error but continue with other sites
- Report all errors in final summary
- Suggest manual investigation for any failed sites
