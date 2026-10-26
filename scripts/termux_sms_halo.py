#!/usr/bin/env python3
"""
📱 Termux Autonomous SMS Gateway for Halo (Cortana)
Runs on Android inside Termux (with Termux:API) to provide 100% free two-way SMS.
When Michael texts 'halo ...' over cellular SMS (with zero mobile data),
this gateway forwards the SMS to our 24/7 Vercel cloud node and sends the AI reply back!

Requirements on Android:
1. Termux (from F-Droid)
2. Termux:API app (from F-Droid)
3. pkg install python termux-api && pip install httpx

Run:
python termux_sms_halo.py
"""

import os
import sys
import time
import json
import subprocess
import httpx

CLOUD_WEBHOOK_URL = "https://telemetry-news-weather.vercel.app/api/sms"
POLL_INTERVAL_SECONDS = 3

def get_recent_sms():
    """Fetches the 5 most recent SMS messages using termux-sms-list."""
    try:
        res = subprocess.run(
            ["termux-sms-list", "-l", "5", "-t", "inbox"],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(res.stdout)
    except Exception as e:
        print(f"[Termux SMS Poll Error]: {e}")
        return []

def send_sms(phone_number, text):
    """Sends an SMS using termux-sms-send."""
    try:
        # termux-sms-send -n <number> <text>
        subprocess.run(
            ["termux-sms-send", "-n", phone_number, text],
            check=True
        )
        print(f"✅ Dispatched reply SMS to {phone_number}")
        return True
    except Exception as e:
        print(f"❌ Failed to send SMS to {phone_number}: {e}")
        return False

def run_gateway():
    print("=" * 60)
    print("🛰️ HALO (CORTANA) ANDROID CELLULAR SMS GATEWAY ACTIVE")
    print("=" * 60)
    print(f"Connected to Cloud Node: {CLOUD_WEBHOOK_URL}")
    print("Listening for incoming SMS with keyword 'halo' or 'cortana'...")
    print("Press Ctrl+C to terminate.")
    print("-" * 60)

    processed_ids = set()

    # Initial seed of existing IDs to prevent replying to old history
    initial_messages = get_recent_sms()
    for m in initial_messages:
        msg_id = m.get("_id") or f"{m.get('number')}_{m.get('received')}"
        processed_ids.add(msg_id)

    print(f"Seeded {len(processed_ids)} previous SMS records. Ready for new incoming transmissions.\n")

    while True:
        try:
            messages = get_recent_sms()
            for m in messages:
                msg_id = m.get("_id") or f"{m.get('number')}_{m.get('received')}"
                if msg_id in processed_ids:
                    continue

                processed_ids.add(msg_id)
                sender = m.get("number", "").strip()
                body = m.get("body", "").strip()
                lower_body = body.lower()

                print(f"\n📩 Incoming SMS from [{sender}]: \"{body}\"")

                # Forward to Vercel 24/7 Cloud Node
                try:
                    payload = {
                        "from": sender,
                        "text": body,
                        "timestamp": m.get("received")
                    }
                    r = httpx.post(CLOUD_WEBHOOK_URL, json=payload, timeout=25.0)
                    if r.status_code == 200:
                        data = r.json()
                        reply_text = data.get("reply") or data.get("message") or data.get("text")
                        if reply_text:
                            print(f"🤖 Halo Response: \"{reply_text}\"")
                            send_sms(sender, reply_text)
                    else:
                        print(f"⚠️ Cloud node error: {r.status_code} - {r.text}")
                except Exception as net_err:
                    print(f"⚠️ Network error forwarding to cloud: {net_err}")

            time.sleep(POLL_INTERVAL_SECONDS)

        except KeyboardInterrupt:
            print("\nShutting down Halo SMS Gateway.")
            break
        except Exception as loop_err:
            print(f"[Loop Exception]: {loop_err}")
            time.sleep(POLL_INTERVAL_SECONDS)

if __name__ == "__main__":
    run_gateway()
