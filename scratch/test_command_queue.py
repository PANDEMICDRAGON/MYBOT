import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")

async def test():
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    async with httpx.AsyncClient() as client:
        # POST command_queue without passcode
        r_post = await client.post(
            f"{SUPABASE_URL}/rest/v1/command_queue",
            headers=headers,
            json={"origin": "WEB", "mode": "CHAT", "directive": "Ping test", "status": "PENDING"}
        )
        print("POST status (no passcode):", r_post.status_code)
        try:
            print("POST json:", r_post.json())
        except Exception:
            print("POST raw:", r_post.status_code)

if __name__ == "__main__":
    asyncio.run(test())
