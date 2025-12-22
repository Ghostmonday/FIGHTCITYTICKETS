# SERVER FILE CLASSIFICATION GUIDE
# For AI Models Analyzing This Server
# ===================================

## PURPOSE
This document defines how to classify and count files on this server to avoid counting operating system files, Docker overhead, and other infrastructure files when analyzing application deployments.

## FILE CLASSIFICATION CATEGORIES

### 1. IGNORE THESE (DO NOT COUNT)
These are infrastructure/OS files that should NEVER be counted in application file totals:

#### Operating System Files
- `/bin`, `/sbin`, `/usr/bin`, `/usr/sbin` - System binaries
- `/lib`, `/lib64`, `/usr/lib`, `/usr/lib64` - System libraries
- `/etc` - System configuration (except application configs in /etc/nginx/sites-available/)
- `/proc`, `/sys` - Virtual filesystems
- `/dev` - Device files
- `/run` - Runtime files
- `/tmp` - Temporary files
- `/var/log` - System logs
- `/var/cache` - System cache
- `/var/lib/apt` - Package manager files
- `/var/lib/dpkg` - Package database

#### Docker Infrastructure
- `/var/lib/docker` - ALL Docker files (images, containers, volumes, networks)
- Docker layer files, overlay2 directories, image storage
- Container filesystems (these are NOT application files)

#### Package Files
- Installed package files (`/usr/share/*`, `/usr/lib/*`, `/usr/include/*`)
- Documentation files (`/usr/share/doc/*`, `/usr/share/man/*`)
- Locale files (`/usr/share/locale/*`)
- System headers, development files

#### Kernel & Boot Files
- `/boot` - Kernel and bootloader files
- `/lib/modules` - Kernel modules

### 2. COUNT THESE (APPLICATION FILES)
These are the ONLY files that should be counted when analyzing deployments:

#### User Application Code
- `/var/www/*` - ALL web applications
- `/home/*/projects/*` - User projects
- `/opt/*` - Optional application software
- Custom application directories

#### Application Configuration
- `/etc/nginx/sites-available/*` - Nginx site configs
- `/etc/systemd/system/*.service` - Application service files
- Application-specific configs in `/etc/`

#### Application Data
- `/var/www/*/data/*` - Application databases/uploads
- Application logs in `/var/log/` (app-specific only)
- User uploads, generated content

### 3. COUNTING RULES

#### When asked "How many files are on the server?"
ALWAYS clarify:
1. Total system files (including OS/Docker): ~250,000
2. Application files only: Count ONLY Category 2 files
3. Specific application files: Count files in that app's directory

#### Example Counts for This Server:
- **Total system files:** ~250,000 (IGNORE THIS NUMBER)
- **/var/www files:** ~200 (THIS IS THE RELEVANT COUNT)
- **FightSFTickets app:** ~100 files
- **Other apps:** Their respective counts

### 4. COMMAND EXAMPLES

#### Count Application Files Only:
```bash
# Count files in web applications directory
find /var/www -type f | wc -l

# Count files in specific application
find /var/www/fightsftickets -type f | wc -l

# Count source code files only
find /var/www/fightsftickets -type f \( -name "*.py" -o -name "*.tsx" -o -name "*.ts" -o -name "*.js" -o -name "*.jsx" -o -name "*.html" -o -name "*.css" -o -name "*.sql" \) | wc -l
```

#### What NOT to Count:
```bash
# NEVER use these for application file counts:
find / -type f | wc -l                    # WRONG - counts everything
find /var/lib/docker -type f | wc -l      # WRONG - Docker overhead
find /usr -type f | wc -l                 # WRONG - System files
```

### 5. SPECIFIC TO THIS SERVER

#### Current Application Directories:
1. `/var/www/fightsftickets` - FightSFTickets application
2. `/var/www/neuraldraft.net` - NeuralDraft application  
3. `/var/www/html` - Default web directory

#### Expected File Counts:
- FightSFTickets: ~100-150 files
- NeuralDraft: Unknown (check directory)
- Total application files: ~200-300 files

#### Docker Containers Running:
1. fightsftickets-web-1 (Frontend)
2. fightsftickets-api-1 (Backend) 
3. fightsftickets-db-1 (Database)

### 6. FOR FUTURE AI MODELS

#### When Analyzing This Server:
1. **FIRST** read this classification guide
2. **NEVER** report total system file count unless specifically asked
3. **ALWAYS** clarify what you're counting
4. **FOCUS** on `/var/www/` for application analysis
5. **IGNORE** Docker files unless analyzing container issues

#### Quick Reference:
```
System files: ~250,000 (IGNORE)
Docker files: ~50,000 (IGNORE)  
App files: ~200 (COUNT THIS)
```

### 7. UPDATING THIS GUIDE

When new applications are deployed:
1. Add their directory to "Application Directories"
2. Update expected file counts
3. Note any special counting rules

---
**Last Updated:** 2025-12-22  
**For:** All AI models analyzing this server  
**Purpose:** Prevent confusion between system files and application files