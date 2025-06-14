#!/usr/bin/env python3
"""
Test script to verify tracker setup - FIXED VERSION
File: test_tracker.py
"""

import sys
import os

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import requests
        print("✅ requests imported successfully")
    except ImportError as e:
        print(f"❌ requests import failed: {e}")
        return False
    
    try:
        from bs4 import BeautifulSoup
        print("✅ BeautifulSoup imported successfully")
    except ImportError as e:
        print(f"❌ BeautifulSoup import failed: {e}")
        return False
    
    try:
        import smtplib
        print("✅ smtplib imported successfully")
    except ImportError as e:
        print(f"❌ smtplib import failed: {e}")
        return False
    
    try:
        from email.mime.text import MimeText
        from email.mime.multipart import MimeMultipart
        print("✅ email.mime imported successfully")
    except ImportError as e:
        print(f"❌ email.mime import failed: {e}")
        try:
            from email.MIMEText import MIMEText
            from email.MIMEMultipart import MIMEMultipart
            print("✅ email.MIME (alternative) imported successfully")
        except ImportError as e2:
            print(f"❌ email.MIME alternative import failed: {e2}")
            return False
    
    return True

def test_tracker():
    """Test tracker functionality"""
    print("\n🧪 Testing Shipment Tracker...")
    
    # Test imports first
    if not test_imports():
        print("❌ Import tests failed. Installing missing packages...")
        os.system("sudo apt install -y python3-email python3-smtplib")
        os.system("pip3 install requests beautifulsoup4 lxml")
        return False
    
    try:
        from tracker import ShipmentTracker
        print("✅ ShipmentTracker imported successfully")
    except ImportError as e:
        print(f"❌ ShipmentTracker import failed: {e}")
        return False
    
    # Test config loading
    try:
        tracker = ShipmentTracker()
        print("✅ Config loaded successfully")
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        print("   Make sure config.json exists and has valid Gmail credentials")
        return False
    
    # Test data fetching (without sending email)
    try:
        print("🌐 Testing website connection...")
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
        print("📄 Testing HTML parsing...")
        shipment_info = tracker.parse_shipment_data(html_content)
        if shipment_info:
            print("✅ HTML parsing successful")
            print(f"   📍 Current location: {shipment_info['location']}")
            print(f"   📋 Status: {shipment_info['status']}")
            print(f"   📅 Date/Time: {shipment_info['date']} {shipment_info['time']}")
        else:
            print("❌ HTML parsing failed")
            return False
    except Exception as e:
        print(f"❌ HTML parsing error: {e}")
        return False
    
    print("\n🎉 All tests passed! Tracker is ready to use.")
    print("\n📧 To test email notifications, run:")
    print("   python3 tracker.py")
    
    return True

if __name__ == "__main__":
    test_tracker()
