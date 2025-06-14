#!/usr/bin/env python3
"""
Reboot notification script - Python 3.11 compatible
File: reboot_notify.py
"""

import sys
import os
import logging
from datetime import datetime
import subprocess

# Add the tracker directory to path
sys.path.append('/home/pi/vehicle-tracker')

try:
    from tracker import ShipmentTracker
except ImportError:
    print("Error: Could not import tracker module")
    sys.exit(1)

def get_system_info():
    """Get basic system information"""
    try:
        # Get uptime
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            uptime_minutes = int(uptime_seconds / 60)
        
        # Get IP address
        try:
            ip_result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
            ip_address = ip_result.stdout.strip().split()[0] if ip_result.stdout else "Unknown"
        except:
            ip_address = "Unknown"
        
        # Get free disk space
        try:
            disk_result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
            disk_lines = disk_result.stdout.strip().split('\n')
            if len(disk_lines) > 1:
                disk_info = disk_lines[1].split()
                disk_usage = f"{disk_info[2]} used / {disk_info[1]} total ({disk_info[4]} used)"
            else:
                disk_usage = "Unknown"
        except:
            disk_usage = "Unknown"
        
        return {
            'uptime_minutes': uptime_minutes,
            'ip_address': ip_address,
            'disk_usage': disk_usage
        }
    except Exception as e:
        return {
            'uptime_minutes': 0,
            'ip_address': "Unknown",
            'disk_usage': "Unknown",
            'error': str(e)
        }

def send_reboot_notification():
    """Send reboot notification with current shipment status"""
    try:
        tracker = ShipmentTracker()
        
        # Get system info
        sys_info = get_system_info()
        
        # Try to get current shipment data
        shipment_info = None
        try:
            html_content = tracker.fetch_shipment_data()
            if html_content:
                shipment_info = tracker.parse_shipment_data(html_content)
        except Exception as e:
            print(f"Warning: Could not fetch shipment data: {e}")
        
        # Load last known status
        last_status = tracker.load_last_status()
        
        # Prepare email content
        subject = "🔄 Raspberry Pi Reboot - Shipment Tracker Online"
        
        body = f"""Raspberry Pi Shipment Tracker Status Report
==========================================

🔄 SYSTEM REBOOT DETECTED
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Uptime: {sys_info['uptime_minutes']} minutes
IP Address: {sys_info['ip_address']}
Disk Usage: {sys_info['disk_usage']}

🚚 CURRENT SHIPMENT STATUS (CH01CH7546)
"""

        if shipment_info:
            body += f"""
📍 Current Location: {shipment_info['location']}
📋 Status: {shipment_info['status']}
📅 Last Update: {shipment_info['date']} {shipment_info['time']}
🔄 Full Status: {shipment_info['full_status']}
"""
        elif last_status.get('last_location'):
            body += f"""
📍 Last Known Location: {last_status['last_location']}
📋 Last Known Status: {last_status['last_status']}
📅 Last Check: {last_status.get('last_check', 'Unknown')}
⚠️  Current data fetch failed - using last known status
"""
        else:
            body += """
⚠️  No shipment data available yet
This might be the first run after setup
"""

        body += f"""

⚙️  TRACKER SERVICE STATUS
✅ Shipment tracker is now running
✅ Email notifications enabled
✅ Automatic checks every 30 minutes
✅ Log rotation configured

📋 CRON JOBS ACTIVE:
- Shipment check: Every 30 minutes
- Log rotation: Daily at 2:00 AM
- Reboot notification: After each restart

🔍 MONITORING COMMANDS:
- Check status: ./check_status.sh
- View logs: tail -f logs/tracker.log
- Manual check: source venv/bin/activate && python tracker.py

---
Automated notification from Raspberry Pi Shipment Tracker
System is ready and monitoring your vehicle shipment.
"""

        # Send the notification
        success = tracker.send_email_notification(subject, body)
        
        if success:
            print(f"Reboot notification sent successfully at {datetime.now()}")
            
            # Log the reboot
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler('/home/pi/vehicle-tracker/logs/tracker.log', mode='a')
                ]
            )
            logging.info("System reboot detected - notification sent")
            
        else:
            print("Failed to send reboot notification")
            return False
            
        return True
        
    except Exception as e:
        print(f"Error sending reboot notification: {e}")
        return False

if __name__ == "__main__":
    send_reboot_notification()
