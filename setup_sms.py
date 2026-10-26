"""
🛰️ Cortana / J.A.R.V.I.S. Cellular SMS Gateway Configuration & Test Suite
Enables SMS control when offline or without active mobile data bundles.
"""

import os
import sys
import httpx
from dotenv import load_dotenv

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

load_dotenv()

VERCEL_SMS_URL = "https://telemetry-news-weather.vercel.app/api/sms"
AUTHORIZED_PHONE = os.getenv("AUTHORIZED_PHONE_NUMBER", "+254700000000")

def test_sms_gateway():
    print("=" * 60)
    print("🛰️ CORTANA CELLULAR SMS GATEWAY VERIFICATION")
    print("=" * 60)
    print(f"Target Gateway URL: {VERCEL_SMS_URL}")
    print(f"Authorized Phone: {AUTHORIZED_PHONE}")
    
    # 1. Test Gateway Health Check (GET)
    try:
        r = httpx.get(VERCEL_SMS_URL, timeout=10)
        print(f"\n[1/3] Gateway Ping Check: HTTP {r.status_code}")
        if r.status_code == 200:
            print("Response:", r.json())
        else:
            print("Error:", r.text)
    except Exception as e:
        print(f"Failed to ping gateway: {e}")

    # 2. Test Inbound SMS Simulation (POST - Generic Android / Africa's Talking)
    print("\n[2/3] Simulating Inbound SMS ('STATUS')...")
    payload = {
        "from": AUTHORIZED_PHONE,
        "text": "STATUS"
    }
    try:
        r = httpx.post(VERCEL_SMS_URL, json=payload, timeout=15)
        print(f"Status Code: {r.status_code}")
        print("Response:", r.text)
    except Exception as e:
        print(f"Failed to simulate SMS: {e}")

    # 3. Test Inbound SMS Twilio Format (POST - x-www-form-urlencoded)
    print("\n[3/3] Simulating Inbound Twilio SMS ('HELP')...")
    twilio_data = {
        "From": AUTHORIZED_PHONE,
        "Body": "HELP",
        "MessageSid": "SM_TEST_12345"
    }
    try:
        r = httpx.post(VERCEL_SMS_URL, data=twilio_data, timeout=15)
        print(f"Status Code: {r.status_code}")
        print("Response (TwiML):", r.text[:300])
    except Exception as e:
        print(f"Failed to simulate Twilio SMS: {e}")

    print("\n" + "=" * 60)
    print("📡 SMS INTEGRATION INSTRUCTIONS FOR YOUR PHONE:")
    print("1. Africa's Talking (Kenya/Pan-Africa):")
    print("   Set Inbound SMS Callback URL to: https://telemetry-news-weather.vercel.app/api/sms")
    print("2. Twilio:")
    print("   Set 'A Message Comes In' Webhook (HTTP POST) to: https://telemetry-news-weather.vercel.app/api/sms")
    print("3. Android Direct SMS Forwarder (No third-party fees):")
    print("   Install 'SMS Forwarder' or 'Termux' on Android.")
    print("   Configure forward rule: Forward incoming SMS from specific number or all to:")
    print("   POST https://telemetry-news-weather.vercel.app/api/sms")
    print("=" * 60)

if __name__ == "__main__":
    test_sms_gateway()
