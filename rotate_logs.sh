#!/bin/bash
# Rotate logs to prevent disk space issues

LOG_DIR="/home/pi/vehicle-tracker/logs"
MAX_SIZE="10M"

# Rotate tracker.log if it gets too big
if [ -f "$LOG_DIR/tracker.log" ]; then
    if [ $(stat -f%z "$LOG_DIR/tracker.log" 2>/dev/null || stat -c%s "$LOG_DIR/tracker.log") -gt 10485760 ]; then
        mv "$LOG_DIR/tracker.log" "$LOG_DIR/tracker.log.old"
        touch "$LOG_DIR/tracker.log"
        echo "$(date): Rotated tracker.log" >> "$LOG_DIR/maintenance.log"
    fi
fi

# Rotate cron.log if it gets too big
if [ -f "$LOG_DIR/cron.log" ]; then
    if [ $(stat -f%z "$LOG_DIR/cron.log" 2>/dev/null || stat -c%s "$LOG_DIR/cron.log") -gt 10485760 ]; then
        mv "$LOG_DIR/cron.log" "$LOG_DIR/cron.log.old"
        touch "$LOG_DIR/cron.log"
        echo "$(date): Rotated cron.log" >> "$LOG_DIR/maintenance.log"
    fi
fi

# Remove logs older than 30 days
find "$LOG_DIR" -name "*.old" -mtime +30 -delete
