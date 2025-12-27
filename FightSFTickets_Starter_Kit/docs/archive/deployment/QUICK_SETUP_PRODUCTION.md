# 🚀 Quick Production Setup Guide

This guide helps you set up essential production improvements quickly.

## ⚡ Quick Start (5 minutes)

Run this on your server:

```bash
# 1. Upload scripts to server
scp scripts/setup_production.sh root@178.156.215.100:/tmp/
scp scripts/backup_database.sh root@178.156.215.100:/tmp/
scp scripts/monitor_health.sh root@178.156.215.100:/tmp/

# 2. SSH into server
ssh root@178.156.215.100

# 3. Run setup script
chmod +x /tmp/setup_production.sh /tmp/backup_database.sh /tmp/monitor_health.sh
bash /tmp/setup_production.sh

# 4. Move scripts to permanent location
mkdir -p /opt/fightcitytickets/scripts
mv /tmp/backup_database.sh /opt/fightcitytickets/scripts/
mv /tmp/monitor_health.sh /opt/fightcitytickets/scripts/
```

## ✅ What This Sets Up

1. **Automated Backups** - Daily database backups at 2 AM
2. **Health Monitoring** - Checks API health every 5 minutes
3. **Firewall** - Only allows SSH, HTTP, HTTPS (blocks database port)
4. **Fail2Ban** - Protects against brute force attacks
5. **Log Rotation** - Prevents log files from filling disk

## 🔒 Critical Security Fix

**IMPORTANT**: The database port is currently exposed. Fix it:

```bash
# On server, edit docker-compose.yml
nano /path/to/docker-compose.yml

# Comment out or remove the database ports line:
# ports:
#   - "5432:5432"

# Restart containers
docker-compose down
docker-compose up -d
```

Or use the updated `docker-compose.yml` which already has this fixed.

## 📊 Monitoring

### Check Backup Status
```bash
tail -f /var/log/fightcitytickets_backup.log
ls -lh /var/backups/fightcitytickets/
```

### Check Health Monitoring
```bash
tail -f /var/log/fightcitytickets_health.log
```

### View Scheduled Jobs
```bash
crontab -l
```

## 🚨 Manual Backup

To create a backup manually:
```bash
/opt/fightcitytickets/scripts/backup_database.sh
```

## 🔄 Restore from Backup

```bash
# Find backup file
ls -lh /var/backups/fightcitytickets/

# Restore (replace TIMESTAMP with actual backup timestamp)
gunzip < /var/backups/fightcitytickets/db_backup_TIMESTAMP.sql.gz | \
  docker exec -i fightcitytickets-db-1 psql -U postgres fightsf
```

## 📋 Additional Setup (Optional)

See `PRODUCTION_SETUP.md` for:
- Error tracking (Sentry)
- Performance monitoring
- CDN setup
- Load testing
- Disaster recovery planning

## 🆘 Troubleshooting

### Backups Not Running
```bash
# Check cron service
systemctl status cron

# Check logs
grep CRON /var/log/syslog | tail -20
```

### Health Checks Failing
```bash
# Test manually
curl https://fightcitytickets.com/api/health

# Check container status
docker ps
docker logs fightcitytickets-api-1
```

### Firewall Blocking Access
```bash
# Check firewall status
ufw status

# Temporarily disable (if needed)
ufw disable
```

---

*For detailed information, see `PRODUCTION_SETUP.md`*

