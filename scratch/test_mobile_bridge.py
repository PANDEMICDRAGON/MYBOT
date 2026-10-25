import httpx
import os
import time
import json
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def test_mobile_bridge():
    print("[1] Simulating mobile device queuing port scan on TV 192.168.100.10...")
    r = httpx.post(
        f"{SUPABASE_URL}/rest/v1/command_queue",
        headers=headers,
        json={
            "origin": "MOBILE",
            "mode": "PORT-SCAN",
            "directive": "/portscan 192.168.100.10 standard",
            "status": "PENDING"
        },
        timeout=10
    )
    assert r.status_code == 201, f"Failed queue: {r.status_code} {r.text}"
    queued = r.json()[0]
    cmd_id = queued["id"]
    print(f"Queued Directive ID: {cmd_id}")

    print("[2] Polling command_queue for bot daemon execution...")
    for i in range(12):
        time.sleep(1.5)
        res = httpx.get(
            f"{SUPABASE_URL}/rest/v1/command_queue?id=eq.{cmd_id}",
            headers=headers,
            timeout=10
        ).json()[0]
        status = res["status"]
        print(f"  Attempt {i+1}: status = {status}")
        if status == "COMPLETED":
            print("\n[SUCCESS] Mobile Port Scan completed by local Wi-Fi daemon!")
            print("Tactical Dossier:\n", res.get("response"))
            print("Structured Sources:\n", json.dumps(res.get("sources"), indent=2))
            return True
        elif status == "FAILED":
            print("[FAIL] Execution marked failed:", res.get("response"))
            return False

    print("[TIMEOUT] Bot daemon did not complete directive in time.")
    return False

if __name__ == "__main__":
    test_mobile_bridge()
