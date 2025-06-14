#!/usr/bin/env python3
"""
Fixed test script for Python 3.11
"""

print("🧪 Testing Fixed Shipment Tracker...")

try:
    import json
    import os
    import sys
    import smtplib
    from datetime import datetime
    from email.message import EmailMessage
    import requests
    from bs4 import BeautifulSoup
    print("✅ All required modules imported successfully")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    exit(1)

try:
    from tracker import ShipmentTracker
    print("✅ ShipmentTracker imported successfully")
except ImportError as e:
    print(f"❌ ShipmentTracker import failed: {e}")
    exit(1)

try:
    tracker = ShipmentTracker()
    print("✅ Config loaded successfully")
except Exception as e:
    print(f"❌ Config loading failed: {e}")
    print("   Make sure config.json exists with valid Gmail credentials")
    exit(1)

try:
    print("🌐 Testing website connection...")
    html_content = tracker.fetch_shipment_data()
    if html_content:
        print("✅ Data fetching successful")
    else:
        print("❌ Data fetching failed")
        exit(1)
except Exception as e:
    print(f"❌ Data fetching error: {e}")
    exit(1)

try:
    print("📄 Testing HTML parsing...")
    shipment_info = tracker.parse_shipment_data(html_content)
    if shipment_info:
        print("✅ HTML parsing successful")
        print(f"   📍 Current location: {shipment_info['location']}")
        print(f"   📋 Status: {shipment_info['status']}")
        print(f"   📅 Date/Time: {shipment_info['date']} {shipment_info['time']}")
    else:
        print("❌ HTML parsing failed")
        exit(1)
except Exception as e:
    print(f"❌ HTML parsing error: {e}")
    exit(1)

print("\n🎉 All tests passed! Tracker is ready to use.")
print("\n📧 To test email notifications, run:")
print("   source venv/bin/activate")
print("   python tracker.py")
