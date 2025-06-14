#!/usr/bin/env python3
"""
Vehicle Shipment Tracker - Python 3.11 Compatible
File: tracker.py
"""

import json
import os
import logging
import sys
import smtplib
import email.utils
from datetime import datetime
from email.message import EmailMessage
import requests
from bs4 import BeautifulSoup

# Setup logging
try:
    os.makedirs('/home/pi/vehicle-tracker/logs', exist_ok=True)
except:
    pass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/pi/vehicle-tracker/logs/tracker.log'),
        logging.StreamHandler()
    ]
)

class ShipmentTracker:
    def __init__(self):
        self.config_file = '/home/pi/vehicle-tracker/config.json'
        self.status_file = '/home/pi/vehicle-tracker/last_status.json'
        self.config = self.load_config()
        
    def load_config(self):
        """Load configuration from config.json"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.error(f"Config file not found: {self.config_file}")
            raise
        except json.JSONDecodeError:
            logging.error("Invalid JSON in config file")
            raise
    
    def load_last_status(self):
        """Load last known status from JSON file"""
        try:
            with open(self.status_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"last_location": "", "last_status": "", "last_check": ""}
        except json.JSONDecodeError:
            logging.warning("Corrupted status file, starting fresh")
            return {"last_location": "", "last_status": "", "last_check": ""}
    
    def save_status(self, status_data):
        """Save current status to JSON file"""
        try:
            with open(self.status_file, 'w') as f:
                json.dump(status_data, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save status: {e}")
    
    def fetch_shipment_data(self):
        """Fetch shipment data from website"""
        url = 'https://www.vehicleshift.com/track-vehicle/'
        
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.vehicleshift.com',
            'referer': 'https://www.vehicleshift.com/track-vehicle/',
            'user-agent': 'Mozilla/5.0 (X11; Linux armv7l) AppleWebKit/537.36'
        }
        
        data = {
            'track_shipment_nonce': 'c6c49001d9',
            '_wp_http_referer': '/track-vehicle/',
            'wpcargo_tracking_number': 'CH01CH7546',
            'wpcargo-submit': 'TRACK RESULT'
        }
        
        try:
            response = requests.post(url, headers=headers, data=data, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to fetch shipment data: {e}")
            return None
    
    def parse_shipment_data(self, html_content):
        """Parse HTML and extract shipment information"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract current status
            status_element = soup.find('p', id='result-status-header')
            current_status = status_element.text.strip() if status_element else "Unknown"
            
            # Extract shipment history (latest entry)
            history_table = soup.find('table', id='shipment-history')
            if not history_table:
                return None
            
            # Get the first row (most recent)
            history_rows = history_table.find('tbody').find_all('tr')
            if not history_rows:
                return None
            
            latest_row = history_rows[0]
            cells = latest_row.find_all('td')
            
            if len(cells) >= 4:
                latest_info = {
                    'date': cells[0].text.strip(),
                    'time': cells[1].text.strip(),
                    'location': cells[2].text.strip(),
                    'status': cells[3].text.strip(),
                    'full_status': current_status,
                    'timestamp': datetime.now().isoformat()
                }
                return latest_info
            
            return None
            
        except Exception as e:
            logging.error(f"Failed to parse HTML: {e}")
            return None
    
    def send_email_notification(self, subject, body):
        """Send email notification using Gmail SMTP - Python 3.11 compatible"""
        try:
            # Create EmailMessage (modern Python 3+ way)
            msg = EmailMessage()
            msg['From'] = self.config['email']['from_email']
            msg['To'] = self.config['email']['to_email']
            msg['Subject'] = subject
            msg.set_content(body)
            
            # Send email
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.config['email']['from_email'], self.config['email']['app_password'])
            server.send_message(msg)
            server.quit()
            
            logging.info(f"Email sent successfully: {subject}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to send email: {e}")
            return False
    
    def format_notification_message(self, shipment_info, is_update=True):
        """Format notification message"""
        if is_update:
            subject = f"🚚 Shipment Update - {shipment_info['location']}"
            body = f"""Vehicle Shipment Update - CH01CH7546

📍 Current Location: {shipment_info['location']}
📋 Status: {shipment_info['status']}
📅 Date: {shipment_info['date']}
🕐 Time: {shipment_info['time']}

Full Status: {shipment_info['full_status']}

Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
Automated notification from Raspberry Pi Shipment Tracker
"""
        else:
            subject = "✅ Shipment Tracker - No Changes"
            body = f"""Shipment Status Check - CH01CH7546

No changes detected since last check.

Current Location: {shipment_info['location']}
Status: {shipment_info['status']}
Last Update: {shipment_info['date']} {shipment_info['time']}

Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return subject, body
    
    def check_shipment(self):
        """Main function to check shipment and send notifications"""
        logging.info("Starting shipment check...")
        
        # Fetch current data
        html_content = self.fetch_shipment_data()
        if not html_content:
            logging.error("Failed to fetch shipment data")
            return False
        
        # Parse shipment info
        current_info = self.parse_shipment_data(html_content)
        if not current_info:
            logging.error("Failed to parse shipment data")
            return False
        
        # Load last known status
        last_status = self.load_last_status()
        
        # Check if there are changes
        location_changed = current_info['location'] != last_status.get('last_location', '')
        status_changed = current_info['status'] != last_status.get('last_status', '')
        
        if location_changed or status_changed or not last_status.get('last_check'):
            # Send update notification
            subject, body = self.format_notification_message(current_info, is_update=True)
            if self.send_email_notification(subject, body):
                logging.info(f"Status update: {current_info['location']} - {current_info['status']}")
            
            # Save new status
            new_status = {
                'last_location': current_info['location'],
                'last_status': current_info['status'],
                'last_check': current_info['timestamp'],
                'full_data': current_info
            }
            self.save_status(new_status)
            
        else:
            logging.info("No changes detected")
        
        return True

def main():
    """Main execution function"""
    try:
        tracker = ShipmentTracker()
        tracker.check_shipment()
    except Exception as e:
        logging.error(f"Script execution failed: {e}")

if __name__ == "__main__":
    main()
