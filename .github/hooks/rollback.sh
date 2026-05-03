#!/bin/bash
# Rollback script - Reverts failed operations
# Called when an operation fails unexpectedly

set -euo pipefail

LOG_FILE=".github/logs/rollback-$(date +%Y%m%d-%H%M%S).log"
BACKUP_DIR=".github/backups"

# Create necessary directories
mkdir -p "$(dirname "$LOG_FILE")" "$BACKUP_DIR"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [ROLLBACK] $*" | tee -a "$LOG_FILE"
}

log "Rollback initiated for failed operation"

# Restore from git if available
if [[ -d ".git" ]]; then
    log "Restoring uncommitted changes..."
    git checkout -- . 2>> "$LOG_FILE" || log "Warning: Could not restore git state"
fi

# Restore credentials and tokens if they were modified
if [[ -f "$BACKUP_DIR/credentials.json.bak" ]]; then
    log "Restoring credentials.json from backup..."
    cp "$BACKUP_DIR/credentials.json.bak" credentials.json
fi

if [[ -f "$BACKUP_DIR/token.json.bak" ]]; then
    log "Restoring token.json from backup..."
    cp "$BACKUP_DIR/token.json.bak" token.json
fi

# Remove temporary files
log "Cleaning temporary files..."
find . -name "*.tmp" -delete 2>> "$LOG_FILE" || true
find . -name ".tmp-*" -type d -exec rm -rf {} + 2>> "$LOG_FILE" || true

log "Rollback completed. Review $LOG_FILE for details."
