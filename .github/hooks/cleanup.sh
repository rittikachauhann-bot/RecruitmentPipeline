#!/bin/bash
# Cleanup script - Removes temporary files and resources on failure
# Called after operations complete (successfully or not)

set -euo pipefail

LOG_FILE=".github/logs/cleanup-$(date +%Y%m%d-%H%M%S).log"

# Create log directory if needed
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [CLEANUP] $*" | tee -a "$LOG_FILE"
}

log "Cleanup started"

# Remove temporary files
log "Removing temporary files..."
find . -maxdepth 2 -name "*.tmp" -delete 2>> "$LOG_FILE" || true
find . -maxdepth 2 -name ".tmp-*" -type d -exec rm -rf {} + 2>> "$LOG_FILE" || true
find . -maxdepth 2 -name "*~" -delete 2>> "$LOG_FILE" || true

# Clean Python cache
log "Cleaning Python cache..."
find . -maxdepth 2 -type d -name "__pycache__" -exec rm -rf {} + 2>> "$LOG_FILE" || true
find . -maxdepth 2 -name "*.pyc" -delete 2>> "$LOG_FILE" || true

# Clean test artifacts
log "Cleaning test artifacts..."
find . -maxdepth 2 -name ".pytest_cache" -exec rm -rf {} + 2>> "$LOG_FILE" || true
find . -maxdepth 2 -name "*.coverage" -delete 2>> "$LOG_FILE" || true

# Close hanging processes (if applicable)
log "Checking for orphaned processes..."
if command -v lsof &> /dev/null; then
    lsof -ti :8000 | xargs kill -9 2>> "$LOG_FILE" || true
fi

# Archive old logs (keep only 30 days)
log "Archiving old logs..."
find .github/logs -type f -mtime +30 -exec gzip {} \; 2>> "$LOG_FILE" || true

log "Cleanup completed. Detailed log: $LOG_FILE"
