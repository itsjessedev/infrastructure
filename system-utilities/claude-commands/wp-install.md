# WordPress Installation Command

Install a fresh WordPress instance on the VPS, ready for initial setup where the user provides the Site Name.

## Instructions

This command installs WordPress up to the point where you need to configure the site name and admin credentials via the web interface.

**Steps:**

1. Detect if running in a project directory or get project name from user
2. Check if WordPress is already installed (abort if exists)
3. SSH to VPS (junipr-vps)
4. Create project directory in `/home/deploy/lab/[project-name]/`
5. Download latest WordPress
6. Create MySQL database and user
7. Configure wp-config.php with database credentials
8. Set file permissions (owner: deploy, group: www-data, secure mode)
9. Save database credentials to `DB-CREDENTIALS.txt`
10. Output the URL to access WordPress install wizard

**Project Directory Detection:**

```bash
# If in a project directory with name
PROJECT_NAME=$(basename "$PWD")

# Or ask user for project name
read -p "Enter project name (lowercase, no spaces): " PROJECT_NAME
```

**Installation Process:**

```bash
# 1. Create project directory
ssh junipr-vps "mkdir -p ~/lab/$PROJECT_NAME && cd ~/lab/$PROJECT_NAME"

# 2. Download WordPress
ssh junipr-vps "cd ~/lab/$PROJECT_NAME && wget https://wordpress.org/latest.tar.gz && tar xzf latest.tar.gz && mv wordpress/* . && rmdir wordpress && rm latest.tar.gz"

# 3. Create database
DB_NAME="${PROJECT_NAME//-/_}_wp"
DB_USER="${PROJECT_NAME:0:16}"  # MySQL username limit
DB_PASS=$(openssl rand -base64 24)  # Generate secure password

ssh junipr-vps "mysql -u root <<EOF
CREATE DATABASE IF NOT EXISTS ${DB_NAME};
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
EOF"

# 4. Configure wp-config.php
ssh junipr-vps "cd ~/lab/$PROJECT_NAME && wp config create \
  --dbname='$DB_NAME' \
  --dbuser='$DB_USER' \
  --dbpass='$DB_PASS' \
  --dbhost='localhost' \
  --allow-root"

# 4b. Add FS_METHOD to wp-config.php (prevents FTP filesystem errors)
ssh junipr-vps "cd ~/lab/$PROJECT_NAME && cat > /tmp/fs_method.txt <<'FSEOF'

/** Filesystem method - use direct file access */
define( 'FS_METHOD', 'direct' );
FSEOF
sed -i \"/define( 'DB_COLLATE', '' );/r /tmp/fs_method.txt\" wp-config.php && rm /tmp/fs_method.txt"

# 5. Set file permissions (secure: deploy owns, www-data group for web access)
ssh junipr-vps "cd ~/lab/$PROJECT_NAME && \
  sudo chown -R deploy:www-data . && \
  sudo find . -type d -exec chmod 755 {} \; && \
  sudo find . -type f -exec chmod 644 {} \; && \
  sudo chmod 640 wp-config.php"

# 6. Save credentials
ssh junipr-vps "cd ~/lab/$PROJECT_NAME && cat > DB-CREDENTIALS.txt <<EOF
Database Name: $DB_NAME
Database User: $DB_USER
Database Password: $DB_PASS
Database Host: localhost

WordPress Installation
Site URL: https://lab.junipr.io/$PROJECT_NAME/
Admin URL: https://lab.junipr.io/$PROJECT_NAME/wp-admin/

Created: $(date)
EOF"

# 7. Set permissions on credentials file
ssh junipr-vps "chmod 600 ~/lab/$PROJECT_NAME/DB-CREDENTIALS.txt"
```

**Output to User:**

```
✅ WordPress Installed Successfully!

Project: $PROJECT_NAME
Location: /home/deploy/lab/$PROJECT_NAME/

Database Details:
  Name: $DB_NAME
  User: $DB_USER
  Password: [saved to DB-CREDENTIALS.txt]

Next Steps:
1. Visit: https://lab.junipr.io/$PROJECT_NAME/
2. Complete WordPress setup wizard:
   - Site Title: [Your Site Name]
   - Username: [Your Admin Username]
   - Password: [Strong Password]
   - Email: [Your Email]
3. After setup, run: /wp-setup

Database credentials saved to: DB-CREDENTIALS.txt
```

**Error Handling:**

- If project directory already exists, ask user to confirm overwrite or abort
- If database creation fails, clean up and report error
- If WordPress download fails, clean up directory and report error
- If wp-config.php creation fails, report database credentials for manual setup

**Validation:**

Before completing, verify:
- WordPress files exist in project directory
- wp-config.php exists and has correct database settings
- Database and user were created successfully
- DB-CREDENTIALS.txt exists and has correct permissions (600)

**Important Notes:**

- Uses WP-CLI for configuration (requires WP-CLI installed on VPS)
- Database passwords are cryptographically secure (24-character random)
- File permissions follow WordPress security best practices
- All files owned by `deploy` user (not www-data) for security
- Database credentials stored securely in project directory
