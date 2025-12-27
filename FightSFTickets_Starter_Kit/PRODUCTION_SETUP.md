# 🚀 Production Setup & Improvements Guide

This document outlines recommended production improvements beyond basic deployment.

## ✅ Currently Implemented

- ✅ SSL/HTTPS with Let's Encrypt
- ✅ Docker containerization
- ✅ Health checks
- ✅ Resource limits
- ✅ Auto-restart policies
- ✅ Basic logging
- ✅ CORS configuration
- ✅ Rate limiting (implemented, needs full integration)

## 🔧 Recommended Production Improvements

### 1. **Database Security** (HIGH PRIORITY)

**Issue**: PostgreSQL is exposed on port 5432, accessible from outside.

**Fix**: Remove external port exposure and use internal Docker network only.

```yaml
# docker-compose.yml
db:
  ports:
    # REMOVE THIS LINE:
    # - "5432:5432"
  # Keep only internal access
```

**Action**: Update `docker-compose.yml` to remove port mapping.

---

### 2. **Automated Backups** (HIGH PRIORITY)

**Setup**: Daily database backups with retention policy.

**Create**: `scripts/backup_database.sh`

```bash
#!/bin/bash
# Daily database backup script
BACKUP_DIR="/var/backups/fightcitytickets"
RETENTION_DAYS=30
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

# Backup database
docker exec fightcitytickets-db-1 pg_dump -U postgres fightsf | gzip > "$BACKUP_DIR/db_backup_$TIMESTAMP.sql.gz"

# Clean old backups
find "$BACKUP_DIR" -name "db_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: db_backup_$TIMESTAMP.sql.gz"
```

**Schedule**: Add to crontab:
```bash
0 2 * * * /path/to/scripts/backup_database.sh >> /var/log/backup.log 2>&1
```

---

### 3. **Monitoring & Alerting** (MEDIUM PRIORITY)

**Option A: Simple Health Monitoring**

Create `scripts/monitor_health.sh`:
```bash
#!/bin/bash
# Simple health check monitoring
ALERT_EMAIL="your-email@example.com"
API_URL="https://fightcitytickets.com/api/health"

if ! curl -f -s "$API_URL" > /dev/null; then
    echo "ALERT: API health check failed at $(date)" | mail -s "FightCityTickets Alert" "$ALERT_EMAIL"
fi
```

**Option B: Uptime Monitoring Service**

Use external services:
- **UptimeRobot** (free tier: 50 monitors)
- **Pingdom** (paid)
- **StatusCake** (free tier available)

**Setup**: Add monitors for:
- `https://fightcitytickets.com`
- `https://fightcitytickets.com/api/health`
- `https://fightcitytickets.com/api/health/db`

---

### 4. **Structured Logging** (MEDIUM PRIORITY)

**Current**: Basic Python logging to console/files.

**Improvement**: Add structured JSON logging for better parsing.

**Create**: `backend/src/logging_config.py`
```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)
```

**Benefits**:
- Easier log aggregation
- Better search/filtering
- Integration with log services (Datadog, Loggly, etc.)

---

### 5. **Rate Limiting Integration** (MEDIUM PRIORITY)

**Status**: Rate limiting code exists but needs full integration.

**Action**: Complete integration in `app.py`:
- ✅ Already initialized
- ✅ Exception handler added
- ⚠️ Need to apply to all routes

**Review**: `backend/src/routes/` - ensure all endpoints have rate limits.

---

### 6. **Environment Variable Security** (HIGH PRIORITY)

**Current**: `.env` file in repository (should be gitignored).

**Action**:
1. Ensure `.env` is in `.gitignore`
2. Use secrets management:
   - **Docker Secrets** (for Docker Swarm)
   - **HashiCorp Vault** (enterprise)
   - **Environment variables** (current, acceptable for single server)

**Check**: Verify sensitive keys are not in code:
```bash
grep -r "sk_live\|sk_test\|api_key" --exclude-dir=node_modules .
```

---

### 7. **Database Connection Pooling** (LOW PRIORITY)

**Current**: Basic database connections.

**Improvement**: Add connection pooling for better performance under load.

**Update**: `backend/src/services/database.py`
```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    database_url,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before using
)
```

---

### 8. **CDN & Static Asset Optimization** (LOW PRIORITY)

**Current**: Static assets served directly.

**Improvement**: Use CDN for static assets (images, CSS, JS).

**Options**:
- **Cloudflare** (free tier available)
- **AWS CloudFront**
- **Vercel** (if using Vercel for frontend)

**Benefits**:
- Faster load times globally
- Reduced server load
- Better caching

---

### 9. **Error Tracking** (MEDIUM PRIORITY)

**Current**: Basic error logging.

**Improvement**: Add error tracking service.

**Options**:
- **Sentry** (free tier: 5K events/month)
- **Rollbar** (free tier available)
- **Honeybadger** (paid)

**Setup**: Add to `backend/src/app.py`:
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
)
```

---

### 10. **Performance Monitoring** (LOW PRIORITY)

**Options**:
- **New Relic** (paid, 14-day trial)
- **Datadog** (paid, 14-day trial)
- **Prometheus + Grafana** (self-hosted, free)

**Basic Setup**: Add Prometheus metrics endpoint:
```python
from prometheus_client import Counter, Histogram, generate_latest

request_count = Counter('http_requests_total', 'Total HTTP requests')
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

---

### 11. **Firewall Configuration** (HIGH PRIORITY)

**Current**: Server may be exposed to all ports.

**Action**: Configure UFW (Ubuntu Firewall):
```bash
# Allow SSH
ufw allow 22/tcp

# Allow HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Deny database port from outside
ufw deny 5432/tcp

# Enable firewall
ufw enable
```

---

### 12. **Fail2Ban** (MEDIUM PRIORITY)

**Purpose**: Protect against brute force attacks.

**Install**:
```bash
apt-get install fail2ban
systemctl enable fail2ban
systemctl start fail2ban
```

**Configure**: `/etc/fail2ban/jail.local`
```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
```

---

### 13. **Automated Updates** (LOW PRIORITY)

**Setup**: Automated security updates (be careful in production).

```bash
apt-get install unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades
```

**Note**: Test updates in staging first!

---

### 14. **Load Testing** (BEFORE SCALING)

**Tools**:
- **Apache Bench (ab)**: `ab -n 1000 -c 10 https://fightcitytickets.com`
- **wrk**: `wrk -t4 -c100 -d30s https://fightcitytickets.com`
- **Locust** (Python-based, more advanced)

**Goal**: Understand system limits before traffic spikes.

---

### 15. **Disaster Recovery Plan** (HIGH PRIORITY)

**Document**:
1. **Backup locations**: Where are backups stored?
2. **Recovery procedure**: How to restore from backup?
3. **RTO (Recovery Time Objective)**: How fast must system recover?
4. **RPO (Recovery Point Objective)**: How much data loss is acceptable?

**Create**: `DISASTER_RECOVERY.md` with:
- Backup restoration steps
- Server rebuild procedure
- DNS failover plan (if applicable)
- Contact information for critical services

---

## 📋 Priority Checklist

### Immediate (This Week)
- [ ] Remove database port exposure
- [ ] Set up automated backups
- [ ] Configure firewall (UFW)
- [ ] Verify `.env` is gitignored
- [ ] Complete rate limiting integration

### Short Term (This Month)
- [ ] Set up monitoring/alerting
- [ ] Add error tracking (Sentry)
- [ ] Configure Fail2Ban
- [ ] Document disaster recovery plan
- [ ] Set up structured logging

### Long Term (Next Quarter)
- [ ] Add CDN for static assets
- [ ] Implement performance monitoring
- [ ] Load testing and optimization
- [ ] Consider multi-server setup (if traffic grows)

---

## 🛠️ Quick Setup Scripts

See `scripts/` directory for:
- `setup_ssl.sh` - SSL certificate setup
- `backup_database.sh` - Database backups (to be created)
- `monitor_health.sh` - Health monitoring (to be created)
- `deploy_manual.sh` - Deployment automation

---

## 📞 Support & Resources

- **Server IP**: 178.156.215.100
- **Domain**: fightcitytickets.com
- **SSL**: Let's Encrypt (auto-renewal configured)
- **Monitoring**: To be set up
- **Backups**: To be configured

---

## 🔍 Regular Maintenance Tasks

**Daily**:
- Check application logs for errors
- Verify backups completed successfully

**Weekly**:
- Review security logs
- Check disk space usage
- Review error tracking alerts

**Monthly**:
- Review and update dependencies
- Check SSL certificate expiration (auto-renewal should handle this)
- Review performance metrics
- Test backup restoration

---

## 🚨 Emergency Contacts

Document key contacts:
- Hosting provider support
- Domain registrar support
- Payment processor (Stripe) support
- Team members with server access

---

*Last Updated: $(date)*

