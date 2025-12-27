#!/bin/bash
# Automated Database Backup Script for FightCityTickets
# Run daily via cron: 0 2 * * * /path/to/backup_database.sh

set -e

# Configuration
BACKUP_DIR="/var/backups/fightcitytickets"
RETENTION_DAYS=30
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="/var/log/fightcitytickets_backup.log"
# Auto-detect container name
CONTAINER_NAME=$(docker ps --format '{{.Names}}' | grep -i 'db\|postgres' | head -1)
# Try to detect database name from environment or use default
DB_NAME="${POSTGRES_DB:-fightsf}"
DB_USER="${POSTGRES_USER:-postgres}"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Log function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "Starting database backup..."

# Check if container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    # Try to find the container
    CONTAINER_NAME=$(docker ps --format '{{.Names}}' | grep -i db | head -1)
    if [ -z "$CONTAINER_NAME" ]; then
        log "ERROR: Database container not found!"
        exit 1
    fi
    log "Found container: $CONTAINER_NAME"
fi

# Perform backup
BACKUP_FILE="$BACKUP_DIR/db_backup_${TIMESTAMP}.sql.gz"
log "Backing up to: $BACKUP_FILE"

# Get database name from environment or docker-compose
if [ -f "docker-compose.yml" ]; then
    DB_NAME=$(grep -A 5 "POSTGRES_DB" docker-compose.yml | grep -oP 'POSTGRES_DB:\s*\K\w+' | head -1 || echo "$DB_NAME")
fi

if docker exec "$CONTAINER_NAME" pg_dump -U "$DB_USER" "$DB_NAME" 2>/dev/null | gzip > "$BACKUP_FILE"; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    log "✅ Backup completed successfully: $BACKUP_FILE ($BACKUP_SIZE)"
else
    log "❌ Backup failed!"
    exit 1
fi

# Clean old backups
log "Cleaning backups older than $RETENTION_DAYS days..."
DELETED=$(find "$BACKUP_DIR" -name "db_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete -print | wc -l)
if [ "$DELETED" -gt 0 ]; then
    log "Deleted $DELETED old backup(s)"
fi

# List current backups
BACKUP_COUNT=$(find "$BACKUP_DIR" -name "db_backup_*.sql.gz" | wc -l)
log "Total backups retained: $BACKUP_COUNT"

log "Backup process completed successfully"

