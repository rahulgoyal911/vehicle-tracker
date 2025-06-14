#!/bin/bash
# Quick status check script

echo "🚚 Shipment Tracker Status Check"
echo "================================="

# Check if cron job is running
echo "📅 Cron job status:"
crontab -l | grep vehicle-tracker
echo ""

# Show last few log entries
echo "📋 Recent log entries:"
tail -n 10 /home/pi/vehicle-tracker/logs/tracker.log 2>/dev/null || echo "No log file found"
echo ""

# Show current status
echo "📍 Current shipment status:"
if [ -f "/home/pi/vehicle-tracker/last_status.json" ]; then
    cat /home/pi/vehicle-tracker/last_status.json | python3 -m json.tool
else
    echo "No status file found"
fi
echo ""

# Check disk space
echo "💾 Disk space:"
df -h /home/pi/vehicle-tracker/
