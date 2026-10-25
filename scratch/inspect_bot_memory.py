import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def check():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{url}/rest/v1/bot_memory?select=*", headers=headers)
        print("Status:", r.status_code)
        if r.status_code == 200:
            rows = r.json()
            print(f"Total memory rows: {len(rows)}")
            for row in rows:
                k = row.get("memory_key")
                d = row.get("directive", "")
                print(f"[{k}]: {d[:120]}")

if __name__ == "__main__":
    asyncio.run(check())
