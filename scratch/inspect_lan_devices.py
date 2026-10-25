import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def inspect():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{url}/rest/v1/lan_devices?select=*", headers=headers)
        print("Status:", r.status_code)
        if r.status_code == 200:
            devices = r.json()
            print(f"Total devices in Supabase: {len(devices)}")
            for d in devices:
                print(f"  {d.get('device_name')} ({d.get('device_type')}): IP={d.get('ip_address')}, status={d.get('status')}")

if __name__ == "__main__":
    asyncio.run(inspect())
