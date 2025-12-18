# WordPress Update Command

Update WordPress core, all plugins, and all themes for the current project using WP-CLI.

## Instructions

This command updates all WordPress components for maximum security. Use this regularly (weekly recommended) to keep WordPress patched.

**Steps:**

1. Detect if this is a local or VPS WordPress installation
2. Run WP-CLI update commands for:
   - WordPress core
   - All plugins
   - All themes
3. Report what was updated
4. Check for any errors or warnings

**Detection:**
- Check if `wp-config.php` exists in current directory or parent directories
- If on VPS (ssh junipr-vps), use remote WP-CLI commands
- If local, use local WP-CLI (install if needed)

**Commands to run:**
```bash
# Core update
wp core update --allow-root

# Plugin updates
wp plugin update --all --allow-root

# Theme updates
wp theme update --all --allow-root

# Database update (if core was updated)
wp core update-db --allow-root
```

**Important:**
- Always use `--allow-root` flag for VPS projects (running as deploy user)
- Create backup before major version updates (WordPress core)
- Report which items were updated and to what versions
- Flag any plugins/themes that failed to update

**Error Handling:**
- If WP-CLI not found, provide installation instructions
- If wp-config.php not found, inform user this isn't a WordPress project
- If updates fail, show the error message and suggest manual investigation
