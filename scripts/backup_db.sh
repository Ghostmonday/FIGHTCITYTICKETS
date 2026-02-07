#!/bin/bash
# =============================================
# FIGHTCITYTICKETS - Database Backup Script
# =============================================
# Creates automated backups with rotation
# =============================================

set -e

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/home/amir/Projects/FightSFTickets/backups}"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="fightcity_${DATE}.sql.gz"
MAX_BACKUPS="${MAX_BACKUPS:-14}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Create backup directory if not exists
mkdir -p "$BACKUP_DIR"

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    log_error ".env file not found!"
    exit 1
fi

# Determine backup method
if command -v docker &> /dev/null && docker ps &> /dev/null; then
    BACKUP_CMD="docker compose exec -T db pg_dump -U ${POSTGRES_USER:-postgres} ${POSTGRES_DB:-fightsf}"
    log_info "Using Docker Compose backup method"
else
    if command -v pg_dump &> /dev/null; then
        # Extract connection info from DATABASE_URL
        DB_HOST=$(echo "$DATABASE_URL" | sed -E 's|.*@([^:]+):([0-9]+).*|\1 \2|')
        BACKUP_CMD="pg_dump -h ${DB_HOST%% *} -U ${POSTGRES_USER:-postgres} ${POSTGRES_DB:-fightsf}"
        log_info "Using local pg_dump backup method"
    else
        log_error "Neither Docker nor pg_dump available!"
        exit 1
    fi
fi

# Create backup
log_info "Starting backup..."
FULL_PATH="${BACKUP_DIR}/${BACKUP_FILE}"

if $BACKUP_CMD | gzip > "$FULL_PATH"; then
    FILE_SIZE=$(du -h "$FULL_PATH" | cut -f1)
    log_info "Backup created: ${BACKUP_FILE} (${FILE_SIZE})"
else
    log_error "Backup failed!"
    rm -f "$FULL_PATH"
    exit 1
fi

# Rotation - keep only MAX_BACKUPS
log_info "Rotating backups (keeping last ${MAX_BACKUPS})..."
cd "$BACKUP_DIR"
ls -t fightcity_*.sql.gz 2>/dev/null | tail -n +$((MAX_BACKUPS + 1)) | xargs -r rm -

# List current backups
log_info "Current backups:"
ls -lh fightcity_*.sql.gz 2>/dev/null | tail -5

log_info "Backup complete!"
