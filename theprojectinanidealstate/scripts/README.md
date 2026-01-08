# FightSFTickets - Deployment Scripts

This directory contains all deployment and automation scripts for FightSFTickets.

---

## 📁 Available Scripts

### 1. `deploy_hetzner.sh` ⭐ **RECOMMENDED**

#### Automated Hetzner Cloud Deployment

Fully automated deployment that provisions a server, installs all dependencies, and deploys your application in one command.

**Usage:**
```bash
export HETZNER_API_TOKEN="your-token-here"
export DOMAIN="yourdomain.com"  # Optional
./scripts/deploy_hetzner.sh
```

**What it does:**
- ✅ Creates Hetzner Cloud server (CX21)
- ✅ Configures SSH access
- ✅ Installs Docker & dependencies
- ✅ Configures firewall
- ✅ Deploys application
- ✅ Starts all services
- ✅ Runs database migrations

**Time:** ~15 minutes  
**Requirements:** Hetzner API token, API keys for services  
**Best for:** First-time deployment, starting fresh

---

### 2. `update_deployment.sh`

#### Update Existing Deployment

Updates code on an already-deployed server without reprovisioning infrastructure.

**Usage:**
```bash
SERVER_IP=xxx.xxx.xxx.xxx ./scripts/update_deployment.sh
```

**What it does:**
- ✅ Creates automatic backup
- ✅ Uploads new code
- ✅ Rebuilds Docker images
- ✅ Restarts services
- ✅ Runs migrations
- ✅ Verifies deployment

**Time:** ~5 minutes  
**Requirements:** Existing deployment, SSH access  
**Best for:** Code updates, iterative changes

---

### 3. `deploy_prod.sh`

#### Original Production Deployment

Simple production deployment script for manual server setup.

**Usage:**
```bash
# On server after manual setup
./scripts/deploy_prod.sh
```

**What it does:**
- Pulls latest code from git
- Builds frontend
- Runs migrations
- Restarts containers

**Time:** ~5 minutes  
**Requirements:** Server already configured, git repo  
**Best for:** Git-based deployments

---

### 4. `bootstrap.sh`

**Development Bootstrap**

Sets up local development environment.

**Usage:**
```bash
./scripts/bootstrap.sh
```

**What it does:**
- Installs dependencies
- Sets up database
- Configures environment

**Time:** ~3 minutes  
**Best for:** Local development setup

---

## 🚀 Quick Start Guide

### For First-Time Deployment

**Option A: Automated (Recommended)**
```bash
# 1. Set Hetzner token
export HETZNER_API_TOKEN="your-token-here"

# 2. Run deployment
cd FightSFTickets_Starter_Kit
./scripts/deploy_hetzner.sh
```

**Option B: Manual Deployment**
```bash
# 1. Set up server manually (see DEPLOYMENT_GUIDE.md)
# 2. SSH to server
ssh root@your-server

# 3. Clone repository
git clone <repo-url> /var/www/fightsftickets

# 4. Configure environment
cd /var/www/fightsftickets
cp .env.template .env
nano .env  # Add your API keys

# 5. Deploy
./scripts/deploy_prod.sh
```

---

## 🔄 Common Workflows

### Deploy New Feature
```bash
# 1. Make code changes locally
# 2. Commit changes
git commit -am "Add new feature"

# 3. Update deployment
SERVER_IP=xxx.xxx.xxx.xxx ./scripts/update_deployment.sh
```

### Rollback to Previous Version
```bash
# SSH to server
ssh root@server-ip

# Find backup
ls -lt /var/backups/fightsftickets/

# Restore database
gunzip -c /var/backups/fightsftickets/backup.sql.gz | \
  docker-compose -f docker-compose.prod.yml exec -T db psql -U postgres fightsf

# Revert code
cd /var/www/fightsftickets
git reset --hard <commit-hash>
docker-compose -f docker-compose.prod.yml up -d --build
```

### Create Manual Backup
```bash
ssh root@server-ip
cd /var/www/fightsftickets
docker-compose -f docker-compose.prod.yml exec db \
  pg_dump -U postgres fightsf > backup_$(date +%Y%m%d).sql
gzip backup_*.sql
```

---

## 🔧 Script Configuration

### Environment Variables

All scripts support these environment variables:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `HETZNER_API_TOKEN` | Hetzner Cloud API token | - | Yes (deploy_hetzner) |
| `DOMAIN` | Your domain name | fightsftickets.com | No |
| `SERVER_IP` | Server IP address | - | Yes (update_deployment) |
| `SERVER_TYPE` | Hetzner server type | cx21 | No |
| `SERVER_LOCATION` | Server location | ash | No |
| `SSH_KEY_PATH` | SSH key path | ~/.ssh/id_rsa | No |
| `DEPLOY_USER` | Deployment user | deploy | No |
| `DEPLOY_PATH` | Deployment path | /var/www/fightsftickets | No |

### Setting Variables

**Temporary (current session):**
```bash
export HETZNER_API_TOKEN="your-token"
export DOMAIN="yourdomain.com"
```

**Permanent (add to ~/.bashrc or ~/.zshrc):**
```bash
echo 'export HETZNER_API_TOKEN="your-token"' >> ~/.bashrc
source ~/.bashrc
```

---

## 📋 Prerequisites

### For Automated Deployment (deploy_hetzner.sh)

**Local Machine:**
- Bash shell
- curl
- jq (auto-installed if missing)
- SSH client

**Accounts & Keys:**
- Hetzner Cloud account + API token
- Stripe account + API keys
- Lob account + API key
- OpenAI account + API key
- DeepSeek account + API key

### For Manual Deployment (deploy_prod.sh)

**Server:**
- Ubuntu 22.04 LTS
- Docker & Docker Compose installed
- Git installed
- 4GB+ RAM, 2+ vCPU

**Configuration:**
- `.env` file configured
- Docker Compose setup
- Nginx configured

---

## 🐛 Troubleshooting

### "Command not found: deploy_hetzner.sh"

**Solution:**
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Or run with bash
bash scripts/deploy_hetzner.sh
```

### "HETZNER_API_TOKEN not set"

**Solution:**
```bash
export HETZNER_API_TOKEN="your-token-here"
```

### "Permission denied (publickey)"

**Solution:**
```bash
# Generate SSH key
ssh-keygen -t rsa -b 4096

# Or specify key path
SSH_KEY_PATH=/path/to/key ./scripts/deploy_hetzner.sh
```

### "Docker containers not starting"

**Solution:**
```bash
# SSH to server
ssh root@server-ip

# Check logs
cd /var/www/fightsftickets
docker-compose -f docker-compose.prod.yml logs

# Restart services
docker-compose -f docker-compose.prod.yml restart
```

### "Script hangs at 'Waiting for SSH'"

**Solution:**
- Wait longer (server may be slow to boot)
- Check Hetzner Cloud Console for server status
- Verify firewall allows SSH (port 22)
- Try manual SSH: `ssh root@server-ip`

---

## 🔒 Security Best Practices

### Protect API Keys
```bash
# Never commit tokens to git
echo "*.token" >> .gitignore
echo ".env*" >> .gitignore

# Store in password manager
# Use environment variables
# Rotate keys regularly
```

### Secure SSH Keys
```bash
# Set proper permissions
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub

# Use SSH agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_rsa

# Disable password auth on server
echo "PasswordAuthentication no" >> /etc/ssh/sshd_config
```

### Rotate Credentials
```bash
# Rotate every 90 days:
# - Hetzner API tokens
# - Database passwords
# - API keys
# - SSH keys
```

---

## 📊 Script Comparison

| Feature | deploy_hetzner.sh | update_deployment.sh | deploy_prod.sh |
|---------|------------------|----------------------|----------------|
| Creates server | ✅ | ❌ | ❌ |
| Installs dependencies | ✅ | ❌ | ❌ |
| Deploys application | ✅ | ✅ | ✅ |
| Creates backups | ❌ | ✅ | ❌ |
| Runs migrations | ✅ | ✅ | ✅ |
| Verifies deployment | ✅ | ✅ | ❌ |
| Time required | ~15 min | ~5 min | ~5 min |
| Use case | New deployment | Updates | Git-based |

---

## 📚 Additional Documentation

- **Complete Guide:** `../docs/DEPLOYMENT_GUIDE.md`
- **Operations:** `../docs/RUNBOOK.md`
- **Documentation Index:** `../docs/README.md`

---

## 🆘 Getting Help

### Check These First
1. Read script output carefully
2. Check logs: `docker-compose logs`
3. Verify environment variables
4. Review error messages

### Common Issues
- **Server creation fails:** Check Hetzner API token
- **SSH connection fails:** Wait longer or check firewall
- **Services won't start:** Check `.env` configuration
- **Database errors:** Verify DATABASE_URL

### Support Resources
- Hetzner Docs: https://docs.hetzner.com/cloud
- Docker Docs: https://docs.docker.com
- Project Issues: Check repository issues page

---

## 🔄 Script Updates

These scripts are actively maintained. When updating:

```bash
# Pull latest scripts
git pull origin main

# Make executable
chmod +x scripts/*.sh

# Review changelog
git log scripts/
```

---

## 📝 Script Examples

### Example 1: Complete Fresh Deployment
```bash
#!/bin/bash
# Deploy to Hetzner with all services

export HETZNER_API_TOKEN="YOUR_HETZNER_API_TOKEN"
export DOMAIN="fightsftickets.com"
export SERVER_TYPE="cx21"
export SERVER_LOCATION="ash"

cd FightSFTickets_Starter_Kit
./scripts/deploy_hetzner.sh

# Script will prompt for API keys:
# - Stripe Secret Key
# - Stripe Webhook Secret  
# - Lob API Key
# - OpenAI API Key
# - DeepSeek API Key
```

### Example 2: Update Production
```bash
#!/bin/bash
# Update existing production deployment

SERVER_IP="123.456.789.012"
SSH_KEY_PATH="~/.ssh/production_key"

export SERVER_IP
export SSH_KEY_PATH

./scripts/update_deployment.sh

# Verify deployment
curl https://fightsftickets.com/health
```

### Example 3: Emergency Rollback
```bash
#!/bin/bash
# Rollback to previous working state

SERVER_IP="123.456.789.012"

# SSH to server
ssh root@$SERVER_IP << 'EOF'
cd /var/www/fightsftickets

# Stop services
docker-compose -f docker-compose.prod.yml down

# Restore latest backup
LATEST_BACKUP=$(ls -t /var/backups/fightsftickets/*.sql.gz | head -1)
gunzip -c $LATEST_BACKUP | docker-compose -f docker-compose.prod.yml exec -T db psql -U postgres fightsf

# Revert code
git reset --hard HEAD~1

# Restart services
docker-compose -f docker-compose.prod.yml up -d --build
EOF
```

---

## ✅ Testing Scripts

### Test Deployment Script (Dry Run)
```bash
# Set test mode
export DRY_RUN=true

# Run script
./scripts/deploy_hetzner.sh

# Script will show what it would do without making changes
```

### Validate Environment
```bash
# Check all required variables
./scripts/validate_env.sh

# Or manually
echo "Hetzner Token: ${HETZNER_API_TOKEN:+SET}"
echo "Domain: ${DOMAIN:-NOT SET}"
```

---

## 🎯 Success Indicators

Successful deployment shows:

```
========================================
Deployment Complete!
========================================

Server Details:
  IP Address: xxx.xxx.xxx.xxx
  Domain: fightsftickets.com
  Deploy Path: /var/www/fightsftickets

Services:
  ✅ Frontend: Running
  ✅ Backend API: Running  
  ✅ Database: Running
  ✅ Nginx: Running

Health Check: http://xxx.xxx.xxx.xxx/health
Status: {"status":"healthy"}

Next Steps:
  1. Configure DNS
  2. Set up SSL
  3. Configure Stripe webhook
  4. Test complete flow
```

---

**Need help? Check the full deployment guide in `docs/DEPLOYMENT_GUIDE.md`**

**Ready to deploy? Start with `DEPLOY_NOW.md`**

---

*Scripts Version: 1.0.0*  
*Last Updated: 2025-01-09*  
*Maintained by: DevOps Team*