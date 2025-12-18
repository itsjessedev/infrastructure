# WordPress Setup Command

Complete WordPress configuration by installing theme, plugins, and applying all automated settings. Then display manual configuration instructions.

## Instructions

This command configures a WordPress installation after the user has completed the initial setup wizard (Site Name, Admin User, etc.).

**Prerequisites:**
- WordPress must be installed (via `/wp-install`)
- User must have completed WordPress setup wizard
- Running from project directory OR specify project name

**Steps:**

1. Detect project directory or get project name
2. Verify WordPress is installed and accessible
3. Install and activate Kadence theme
4. Install and activate all essential plugins
5. Configure WordPress core settings
6. Apply Wordfence license key
7. Configure media, permalink, and comment settings
8. Upload and set site logo (if exists in project)
9. Set proper file permissions for security
10. Display manual configuration instructions

**Project Detection:**

```bash
# Detect from current directory
PROJECT_NAME=$(basename "$PWD")
WP_PATH="/home/deploy/lab/$PROJECT_NAME"

# Verify WordPress exists
ssh junipr-vps "[ -f $WP_PATH/wp-config.php ] || echo 'WordPress not found'"
```

**Installation Commands:**

### 1. Install Kadence Theme

```bash
ssh junipr-vps "cd $WP_PATH && \
  wget -q https://downloads.wordpress.org/theme/kadence.latest-stable.zip && \
  unzip -q kadence.latest-stable.zip -d wp-content/themes/ && \
  rm kadence.latest-stable.zip && \
  wp theme activate kadence --allow-root"
```

### 2. Install Security Plugins

```bash
ssh junipr-vps "cd $WP_PATH && \
  wp plugin install wordfence wordfence-login-security limit-login-attempts-reloaded disable-xml-rpc --activate --allow-root"
```

### 3. Install Performance & SEO Plugins

```bash
ssh junipr-vps "cd $WP_PATH && \
  wp plugin install seo-by-rank-math cloudflare wp-smushit --activate --allow-root"
```

### 4. Delete Unused Plugins

```bash
ssh junipr-vps "cd $WP_PATH && \
  wp plugin delete akismet hello --allow-root 2>/dev/null || true"
```

### 5. Configure WordPress Core Settings

```bash
ssh junipr-vps "cd $WP_PATH && \
  wp option update timezone_string 'America/Chicago' --allow-root && \
  wp option update date_format 'F j, Y' --allow-root && \
  wp option update time_format 'g:i a' --allow-root && \
  wp option update start_of_week 0 --allow-root && \
  wp rewrite structure '/%postname%/' --allow-root && \
  wp rewrite flush --allow-root && \
  wp option update default_comment_status 'closed' --allow-root && \
  wp option update default_ping_status 'closed' --allow-root && \
  wp option update comments_notify 0 --allow-root && \
  wp option update uploads_use_yearmonth_folders 1 --allow-root && \
  wp option update thumbnail_size_w 300 --allow-root && \
  wp option update thumbnail_size_h 300 --allow-root && \
  wp option update medium_size_w 768 --allow-root && \
  wp option update medium_size_h 0 --allow-root && \
  wp option update large_size_w 1200 --allow-root && \
  wp option update large_size_h 0 --allow-root"
```

### 6. Apply Wordfence License

```bash
WORDFENCE_KEY='2cedc3dc5cc54762ae33c8558467a0c8e5dc59a914c462db8fa4ae56d38a678a45e96b19f5de72356e517927994697b2744fca572a7998fdeb9b3f3f8ab6effd'

ssh junipr-vps "cd $WP_PATH && \
  wp option update wordfence_api_key '$WORDFENCE_KEY' --allow-root"
```

### 7. Configure Wordfence Directories

```bash
ssh junipr-vps "cd $WP_PATH && \
  mkdir -p wp-content/wflogs && \
  sudo chown -R www-data:www-data wp-content/wflogs && \
  sudo chmod -R 755 wp-content/wflogs && \
  sudo chmod g+w . && \
  sudo chown deploy:www-data ."
```

### 8. Upload Logo (if exists)

```bash
# Check if logo exists in current project directory
if [ -f "logo.png" ] || [ -f "*/logo.png" ]; then
  LOGO_PATH=$(find . -name "*logo*.png" -type f | head -1)

  # Copy to VPS
  scp "$LOGO_PATH" junipr-vps:$WP_PATH/wp-content/uploads/

  # Import to media library and set as site logo
  ssh junipr-vps "cd $WP_PATH && \
    LOGO_ID=\$(wp media import wp-content/uploads/$(basename $LOGO_PATH) --porcelain --allow-root) && \
    wp option update custom_logo \$LOGO_ID --allow-root"
fi
```

### 9. Security & Configuration: Add wp-config.php Settings

```bash
# Add FS_METHOD if missing (prevents FTP filesystem errors)
ssh junipr-vps "cd $WP_PATH && \
  grep -q 'FS_METHOD' wp-config.php || \
  (cat > /tmp/fs_method.txt <<'FSEOF'

/** Filesystem method - use direct file access */
define( 'FS_METHOD', 'direct' );
FSEOF
sed -i \"/define( 'DB_COLLATE', '' );/r /tmp/fs_method.txt\" wp-config.php && rm /tmp/fs_method.txt)"

# Add security settings if missing
ssh junipr-vps "cd $WP_PATH && \
  grep -q 'DISALLOW_FILE_EDIT' wp-config.php || \
  sed -i \"/stop editing/i\\\n// Security: Disable file editing from admin (prevents code injection)\\\ndefine('DISALLOW_FILE_EDIT', true);\\\n\\\n// Security: Allow auto-updates but use WP-CLI/SFTP for new plugin installs\\\ndefine('DISALLOW_FILE_MODS', false);\\\n\" wp-config.php"
```

### 10. Configure Wordfence Security

```bash
# Wordfence: Extended Protection & Firewall Settings
ssh junipr-vps "cd $WP_PATH && \
  wp option update wordfence_fw_protectionLevel 'EXTENDED' --allow-root && \
  wp option update wordfenceActivated 1 --allow-root"

# Wordfence: Login Security Settings
ssh junipr-vps "cd $WP_PATH && \
  wp option update wordfence_loginSec_blockInvalidPlugins 1 --allow-root && \
  wp option update wordfence_loginSec_enableSeparateTwoFactor 0 --allow-root && \
  wp option update wordfence_loginSec_disableAuthorScan 1 --allow-root"

# Wordfence: Scan Schedule (daily at 3 AM)
ssh junipr-vps "cd $WP_PATH && \
  wp option update wordfence_scheduleScan 1 --allow-root && \
  wp option update wordfence_schedScanHour 3 --allow-root && \
  wp option update wordfence_schedScanMeridian 'a.m.' --allow-root"

# Wordfence: Hide WordPress version
ssh junipr-vps "cd $WP_PATH && \
  wp option update wordfence_removeGeneratorMeta 1 --allow-root"
```

### 11. Configure Limit Login Attempts Reloaded

```bash
ssh junipr-vps "cd $WP_PATH && \
  wp option update limit_login_allowed_retries 4 --allow-root && \
  wp option update limit_login_lockout_duration 1200 --allow-root && \
  wp option update limit_login_allowed_lockouts 4 --allow-root && \
  wp option update limit_login_long_duration 86400 --allow-root && \
  wp option update limit_login_notify_email_after 4 --allow-root && \
  wp option update limit_login_gdpr 1 --allow-root && \
  wp option update limit_login_trust_ip_in_header 1 --allow-root"
```

### 12. Configure Rank Math SEO

```bash
# Rank Math: Enable XML Sitemap
ssh junipr-vps "cd $WP_PATH && \
  wp option update rank_math_modules '{\"sitemap\":\"on\",\"rich-snippet\":\"on\",\"local-seo\":\"on\",\"404-monitor\":\"on\",\"redirections\":\"on\"}' --format=json --allow-root"

# Rank Math: SEO Tweaks
ssh junipr-vps "cd $WP_PATH && \
  wp option update rank-math-options-titles '{\"noindex_empty_taxonomies\":\"on\",\"disable_author_archives\":\"on\",\"strip_category_base\":\"on\",\"attachment_redirect_urls\":\"on\"}' --format=json --allow-root"

# Rank Math: Enable Breadcrumbs
ssh junipr-vps "cd $WP_PATH && \
  wp option update rank-math-options-general '{\"breadcrumbs\":\"on\"}' --format=json --allow-root"

# Rank Math: Sitemap - Exclude Media
ssh junipr-vps "cd $WP_PATH && \
  wp option update rank-math-options-sitemap '{\"exclude_post_types\":[\"attachment\"]}' --format=json --allow-root"
```

### 13. Configure WP Smush

```bash
# WP Smush: Auto-optimize uploads
ssh junipr-vps "cd $WP_PATH && \
  wp option update wp-smush-auto '1' --allow-root && \
  wp option update wp-smush-lossy '1' --allow-root && \
  wp option update wp-smush-strip-exif '1' --allow-root && \
  wp option update wp-smush-original '1' --allow-root"

# WP Smush: Lazy Load
ssh junipr-vps "cd $WP_PATH && \
  wp option update wp-smush-lazy_load '1' --allow-root && \
  wp option update wp-smush-lazy-load-images '1' --allow-root && \
  wp option update wp-smush-lazy-load-iframes '1' --allow-root && \
  wp option update wp-smush-lazy-load-fadein '1' --allow-root"

# WP Smush: WebP Conversion
ssh junipr-vps "cd $WP_PATH && \
  wp option update wp-smush-webp '1' --allow-root && \
  wp option update wp-smush-webp-delete-original '1' --allow-root"

# WP Smush: Compression settings
ssh junipr-vps "cd $WP_PATH && \
  wp option update wp-smush-resize '1' --allow-root && \
  wp option update wp-smush-resize-maxwidth '2000' --allow-root && \
  wp option update wp-smush-resize-maxheight '2000' --allow-root"
```

### 14. Configure Kadence Theme Colors & Typography

```bash
# Kadence: Apply brand colors from project (if defined)
# Deep Court Green, Sandstone Gold, Coastal Mist, etc.
ssh junipr-vps "cd $WP_PATH && \
  wp option update kadence_global_palette '{\"palette\":[{\"color\":\"#0F3D2E\",\"slug\":\"deep-court-green\"},{\"color\":\"#C59D5F\",\"slug\":\"sandstone-gold\"},{\"color\":\"#87A8A4\",\"slug\":\"coastal-mist\"},{\"color\":\"#F7F5F1\",\"slug\":\"porcelain\"},{\"color\":\"#2C2A28\",\"slug\":\"graphite\"}]}' --format=json --allow-root 2>/dev/null || true"

# Kadence: Configure typography (Playfair Display for headings, Source Sans 3 for body)
ssh junipr-vps "cd $WP_PATH && \
  wp option update kadence_heading_font_family 'Playfair Display' --allow-root && \
  wp option update kadence_heading_font_weight '600' --allow-root && \
  wp option update kadence_body_font_family 'Source Sans 3' --allow-root && \
  wp option update kadence_body_font_weight '400' --allow-root && \
  wp option update kadence_body_font_size '18px' --allow-root"
```

### 15. Create Essential Pages

```bash
# Create Privacy Policy page
ssh junipr-vps "cd $WP_PATH && \
  wp post create --post_type=page --post_title='Privacy Policy' --post_status=publish --post_content='This privacy policy outlines how we collect, use, and protect your personal information. We are committed to ensuring your privacy is protected.' --allow-root"

# Create Terms of Service page
ssh junipr-vps "cd $WP_PATH && \
  wp post create --post_type=page --post_title='Terms of Service' --post_status=publish --post_content='By accessing this website, you agree to be bound by these terms of service. This blog contains affiliate links and we may earn commission from purchases made through our links.' --allow-root"

# Create About page
ssh junipr-vps "cd $WP_PATH && \
  wp post create --post_type=page --post_title='About' --post_status=publish --post_content='Welcome to our community where passion meets sophistication. We provide curated content for discerning enthusiasts.' --allow-root"

# Create Contact page
ssh junipr-vps "cd $WP_PATH && \
  wp post create --post_type=page --post_title='Contact' --post_status=publish --post_content='Get in touch with us. We love hearing from our readers.' --allow-root"
```

### 16. Create Post Categories

```bash
# Create categories matching content pillars
ssh junipr-vps "cd $WP_PATH && \
  wp term create category 'Luxury Destinations & Travel' --slug=luxury-destinations --description='Aspirational resorts, destination guides, and travel packages' --allow-root && \
  wp term create category 'Premium Gear & Style' --slug=premium-gear --description='Equipment reviews and style guides' --allow-root && \
  wp term create category 'Exclusive Clubs & Venues' --slug=exclusive-clubs --description='Private clubs and premium venues' --allow-root && \
  wp term create category 'Community & Events' --slug=community-events --description='Event coverage and member spotlights' --allow-root && \
  wp term create category 'Wellness & Longevity' --slug=wellness --description='Injury prevention, fitness, and recovery' --allow-root && \
  wp term create category 'Home Courts & Property' --slug=home-courts --description='Residential court design and installation' --allow-root && \
  wp term create category 'Strategy & Skill' --slug=strategy --description='Strategic insights for intermediate and advanced players' --allow-root"
```

### 17. Create Primary Navigation Menu

```bash
# Create menu
ssh junipr-vps "cd $WP_PATH && \
  MENU_ID=\$(wp menu create 'Main Navigation' --porcelain --allow-root) && \
  wp menu location assign \$MENU_ID primary --allow-root"

# Add pages to menu
ssh junipr-vps "cd $WP_PATH && \
  MENU_ID=\$(wp menu list --format=ids --allow-root | head -1) && \
  ABOUT_ID=\$(wp post list --post_type=page --post_title='About' --format=ids --allow-root) && \
  CONTACT_ID=\$(wp post list --post_type=page --post_title='Contact' --format=ids --allow-root) && \
  wp menu item add-post \$MENU_ID \$ABOUT_ID --allow-root && \
  wp menu item add-post \$MENU_ID \$CONTACT_ID --allow-root"
```

### 18. Configure Widgets

```bash
# Add Recent Posts to sidebar
ssh junipr-vps "cd $WP_PATH && \
  wp widget add recent-posts sidebar-primary --title='Recent Articles' --number=5 --allow-root 2>/dev/null || true"

# Add Categories to sidebar
ssh junipr-vps "cd $WP_PATH && \
  wp widget add categories sidebar-primary --title='Categories' --count=1 --hierarchical=1 --allow-root 2>/dev/null || true"

# Add Search to sidebar
ssh junipr-vps "cd $WP_PATH && \
  wp widget add search sidebar-primary --allow-root 2>/dev/null || true"
```

### 19. Create .user.ini for Wordfence WAF

```bash
# Create .user.ini with auto_prepend_file for Wordfence WAF
ssh junipr-vps "cat > $WP_PATH/.user.ini << 'EOF'
; Wordfence WAF
auto_prepend_file = $WP_PATH/wordfence-waf.php
EOF"

# Reload PHP-FPM to apply .user.ini changes
ssh junipr-vps "sudo systemctl reload php8.3-fpm"
```

### 20. Set Final File Permissions

```bash
# Ensure proper ownership for security
ssh junipr-vps "sudo chown -R www-data:www-data $WP_PATH/wp-content/uploads && \
  sudo chmod -R 755 $WP_PATH/wp-content/uploads"
```

**Output Summary:**

```
✅ WordPress Setup Complete!

Theme Installed & Configured:
  ✅ Kadence (brand colors + typography applied)
  ✅ Fonts: Playfair Display (headings), Source Sans 3 (body, 18px)

Plugins Installed & Activated:
  ✅ Wordfence Security (license applied, extended protection enabled)
  ✅ Wordfence Login Security
  ✅ Limit Login Attempts Reloaded (configured)
  ✅ Disable XML-RPC
  ✅ Rank Math SEO (sitemap, breadcrumbs, SEO tweaks enabled)
  ✅ Cloudflare (ready for API connection)
  ✅ WP Smush (auto-optimize, lazy load, WebP enabled)

WordPress Settings Configured:
  ✅ Timezone: America/Chicago
  ✅ Permalinks: /%postname%/
  ✅ Comments: Disabled by default
  ✅ Media sizes: Optimized (2000px max)
  ✅ Security: wp-config.php hardened
  ✅ Logo: Uploaded and set (if found)
  ✅ Wordfence WAF: Configured via .user.ini

Security Configuration:
  ✅ Wordfence: Extended protection, daily scans at 3 AM
  ✅ Login Security: Invalid username blocking, author scan disabled
  ✅ Login Limits: 4 attempts, 20-min lockout
  ✅ XML-RPC: Disabled

SEO Configuration:
  ✅ Rank Math: Sitemap enabled (excludes media)
  ✅ SEO Tweaks: Category base stripped, attachments redirect to parent
  ✅ Breadcrumbs: Enabled
  ✅ Local SEO, 404 Monitor, Redirections: Enabled

Performance Configuration:
  ✅ WP Smush: Auto-compress new uploads
  ✅ Lazy Loading: Enabled for images and iframes
  ✅ WebP Conversion: Enabled (deletes originals to save space)
  ✅ Image Resize: Max 2000x2000px

Content Created:
  ✅ Pages: Privacy Policy, Terms of Service, About, Contact
  ✅ Categories: 7 content pillar categories with descriptions
  ✅ Menu: Primary navigation with About and Contact pages
  ✅ Widgets: Recent Posts, Categories, Search (sidebar)

================================================================================
MANUAL CONFIGURATION REQUIRED (Minimal)
================================================================================

[Display contents of /home/jesse/projects/wordpress-manual-configuration.md]

Access WordPress Admin:
https://lab.junipr.io/$PROJECT_NAME/wp-admin/

Lab Authentication:
  Username: lab
  Password: s0P98YYUSydQWgXfNY6RfWcXRriiDvaQ
```

**Important Notes:**

- All automated configuration complete
- Manual configuration required for plugin-specific settings
- Settings follow WordPress security best practices
- Timezone default: America/Chicago (can be changed later)
- File permissions: deploy:www-data for security

**Error Handling:**

- If plugin installation fails, continue with others and report failures
- If theme activation fails, report but continue
- If settings update fails, log error but continue
- If logo upload fails, skip and continue

**Validation Before Completion:**

- Verify all plugins are activated
- Verify theme is active
- Verify Wordfence license is applied
- Verify permalink structure is set
- Verify security settings in wp-config.php
