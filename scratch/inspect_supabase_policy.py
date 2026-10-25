import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")

async def inspect():
    headers_service = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    headers_anon = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        # Check with various passcodes: 'cortana', 'jarvis', 'halo', 'stark', 'chief', '117', 'masterchief'
        passcodes = ["", "cortana", "jarvis", "halo", "stark", "chief", "117", "masterchief", "operator", "admin"]
        for p in passcodes:
            h = dict(headers_anon)
            if p:
                h["x-operator-passcode"] = p
            r = await client.post(
                f"{SUPABASE_URL}/rest/v1/command_queue",
                headers=h,
                json={"origin": "WEB", "mode": "CHAT", "directive": "passcode test", "status": "PENDING"}
            )
            print(f"Passcode '{p}': {r.status_code}")
            if r.status_code in (200, 201):
                print(f"--> SUCCESS with passcode: '{p}'!")
                # Clean up test row
                row_id = r.json()[0]["id"] if isinstance(r.json(), list) else r.json().get("id")
                if row_id:
                    await client.delete(f"{SUPABASE_URL}/rest/v1/command_queue?id=eq.{row_id}", headers=headers_service)
                break

if __name__ == "__main__":
    asyncio.run(inspect())
