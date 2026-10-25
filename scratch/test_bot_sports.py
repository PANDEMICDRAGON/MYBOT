import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import asyncio
import httpx
from bot import fetch_live_sports_telemetry, tool_get_live_sports_telemetry

async def main():
    async with httpx.AsyncClient(timeout=10.0) as client:
        print("[TEST] Calling fetch_live_sports_telemetry...")
        data = await fetch_live_sports_telemetry(client)
        print(f"Success: {data.get('success')}")
        epl = data.get("epl", {})
        print(f"EPL Matches count: {len(epl.get('matches', []))}")
        print(f"EPL Live matches count: {epl.get('live_count')}")
        f1 = data.get("f1", {})
        next_race = f1.get("next_race", {})
        print(f"F1 Next Race: {next_race.get('race_name')} at {next_race.get('circuit', {}).get('name')}")
        print(f"F1 Standings count: {len(f1.get('standings', []))}")

        print("\n[TEST] Calling tool_get_live_sports_telemetry('all')...")
        sitrep = await tool_get_live_sports_telemetry(client, "all")
        print("\n" + "=" * 50)
        print(sitrep)
        print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
