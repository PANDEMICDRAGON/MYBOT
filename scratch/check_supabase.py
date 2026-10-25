import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")

async def main():
    async with httpx.AsyncClient() as client:
        # Check pg_policies or rpc
        r_pol = await client.get(
            f"{SUPABASE_URL}/rest/v1/pg_policies?tablename=eq.command_queue",
            headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
        )
        print("pg_policies status:", r_pol.status_code)
        if r_pol.status_code == 200:
            print("pg_policies:", r_pol.json())
        else:
            print("pg_policies err:", r_pol.text)


if __name__ == "__main__":
    asyncio.run(main())
