#!/bin/bash
# Production Setup Script for FightCityTickets
# Run this on the server after initial deployment

set -e

echo "🚀 Setting up production environment..."
echo "============================================================"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root"
    exit 1
fi

# 1. Create backup directory
echo ""
echo "📁 Creating backup directory..."
mkdir -p /var/backups/fightcitytickets
chmod 700 /var/backups/fightcitytickets
echo "✅ Backup directory created"

# 2. Set up database backup script
echo ""
echo "💾 Setting up database backups..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_SCRIPT="$SCRIPT_DIR/backup_database.sh"

if [ -f "$BACKUP_SCRIPT" ]; then
    chmod +x "$BACKUP_SCRIPT"
    # Add to crontab (daily at 2 AM)
    (crontab -l 2>/dev/null | grep -v "backup_database.sh" || true; echo "0 2 * * * $BACKUP_SCRIPT >> /var/log/fightcitytickets_backup.log 2>&1") | crontab -
    echo "✅ Database backup scheduled (daily at 2 AM)"
else
    echo "⚠️  Backup script not found at $BACKUP_SCRIPT"
fi

# 3. Set up health monitoring
echo ""
echo "🏥 Setting up health monitoring..."
MONITOR_SCRIPT="$SCRIPT_DIR/monitor_health.sh"

if [ -f "$MONITOR_SCRIPT" ]; then
    chmod +x "$MONITOR_SCRIPT"
    # Add to crontab (every 5 minutes)
    (crontab -l 2>/dev/null | grep -v "monitor_health.sh" || true; echo "*/5 * * * * $MONITOR_SCRIPT") | crontab -
    echo "✅ Health monitoring scheduled (every 5 minutes)"
else
    echo "⚠️  Monitor script not found at $MONITOR_SCRIPT"
fi

# 4. Configure firewall
echo ""
echo "🔥 Configuring firewall..."
if command -v ufw &> /dev/null; then
    # Allow SSH
    ufw allow 22/tcp comment 'SSH'
    
    # Allow HTTP/HTTPS
    ufw allow 80/tcp comment 'HTTP'
    ufw allow 443/tcp comment 'HTTPS'
    
    # Deny database port from outside (security)
    ufw deny 5432/tcp comment 'PostgreSQL - internal only'
    
    # Enable firewall (non-interactive)
    echo "y" | ufw enable 2>/dev/null || ufw --force enable
    echo "✅ Firewall configured"
else
    echo "⚠️  UFW not installed. Install with: apt-get install ufw"
fi

# 5. Install Fail2Ban
echo ""
echo "🛡️  Setting up Fail2Ban..."
if command -v fail2ban-client &> /dev/null; then
    echo "✅ Fail2Ban already installed"
else
    apt-get update -qq
    apt-get install -y fail2ban
    systemctl enable fail2ban
    systemctl start fail2ban
    echo "✅ Fail2Ban installed and started"
fi

# 6. Set up log rotation
echo ""
echo "📋 Setting up log rotation..."
cat > /etc/logrotate.d/fightcitytickets << 'EOF'
/var/log/fightcitytickets*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
}
EOF
echo "✅ Log rotation configured"

# 7. Create log directories
echo ""
echo "📝 Creating log directories..."
mkdir -p /var/log
touch /var/log/fightcitytickets_backup.log
touch /var/log/fightcitytickets_health.log
chmod 644 /var/log/fightcitytickets*.log
echo "✅ Log files created"

# 8. Verify Docker containers are running
echo ""
echo "🐳 Checking Docker containers..."
if docker ps | grep -q fightcitytickets; then
    echo "✅ Docker containers are running"
    docker ps --filter "name=fightcitytickets" --format "table {{.Names}}\t{{.Status}}"
else
    echo "⚠️  No Docker containers found with 'fightcitytickets' in name"
fi

# 9. Summary
echo ""
echo "============================================================"
echo "✅ Production setup complete!"
echo ""
echo "📋 Summary:"
echo "  - Backup directory: /var/backups/fightcitytickets"
echo "  - Backups scheduled: Daily at 2 AM"
echo "  - Health monitoring: Every 5 minutes"
echo "  - Firewall: Configured (SSH, HTTP, HTTPS allowed)"
echo "  - Fail2Ban: Installed and running"
echo "  - Log rotation: Configured (30 days retention)"
echo ""
echo "🔍 Next steps:"
echo "  1. Review PRODUCTION_SETUP.md for additional improvements"
echo "  2. Set up external monitoring (UptimeRobot, etc.)"
echo "  3. Configure error tracking (Sentry, etc.)"
echo "  4. Test backup restoration procedure"
echo ""
echo "📊 Check status:"
echo "  - Backups: tail -f /var/log/fightcitytickets_backup.log"
echo "  - Health: tail -f /var/log/fightcitytickets_health.log"
echo "  - Cron jobs: crontab -l"
echo "============================================================"

