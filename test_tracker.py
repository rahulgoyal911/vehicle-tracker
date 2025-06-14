#!/usr/bin/env python3
"""Test script to verify tracker setup"""

import sys
import os
sys.path.append('/home/pi/vehicle-tracker')

from tracker import ShipmentTracker
import json

def test_setup():
    print("🧪 Testing Shipment Tracker Setup...")
    
    # Test config loading
    try:
        tracker = ShipmentTracker()
        print("✅ Config loaded successfully")
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        return False
    
    # Test data fetching (without sending email)
    try:
        html_content = tracker.fetch_shipment_data()
        if html_content:
            print("✅ Data fetching successful")
        else:
            print("❌ Data fetching failed")
            return False
    except Exception as e:
        print(f"❌ Data fetching error: {e}")
        return False
    
    # Test HTML parsing
    try:
        shipment_info = tracker.parse_shipment_data(html_content)
        if shipment_info:
            print("✅ HTML parsing successful")
            print(f"   Current location: {shipment_info['location']}")
            print(f"   Status: {shipment_info['status']}")
            print(f"   Date/Time: {shipment_info['date']} {shipment_info['time']}")
        else:
            print("❌ HTML parsing failed")
            return False
    except Exception as e:
        print(f"❌ HTML parsing error: {e}")
        return False
    
    print("\n🎉 All tests passed! Tracker is ready to use.")
    print("\n📧 To test email notifications, run:")
    print("   python3 /home/pi/vehicle-tracker/tracker.py")
    
    return True

if __name__ == "__main__":
    test_setup()
