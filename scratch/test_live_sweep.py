import sys, os, httpx, asyncio, json
sys.path.insert(0, os.path.abspath('.'))
from dotenv import load_dotenv
load_dotenv()
from bot import execute_complete_sensor_sweep

async def main():
    async with httpx.AsyncClient() as client:
        print("Running live sensor sweep test...")
        res = await execute_complete_sensor_sweep(client, is_proactive=False)
        print("=== SWEEP RESULTS ===")
        print("Threat Level:", res["sitrep"].get("threat_level"))
        print("\n--- SITREP ---")
        print(res["sitrep"].get("sitrep"))
        print("\n--- CONFLICT / THEATERS ---")
        print(res["sitrep"].get("conflict_summary"))
        print("\n--- DEEP DIVES COUNT ---", len(res.get("deep_dives", [])))
        for dd in res.get("deep_dives", []):
            print(f"[{dd.get('subject')}]")
            print("  Dev:", dd.get("latest_developments"))
            print("  Depth:", dd.get("in_depth_context"))
            print("  Impact:", dd.get("why_it_matters"))
        print("\n--- ARTICLES COUNT ---", len(res.get("news", [])))
        for a in res.get("news", [])[:3]:
            print(f"Article: {a.get('title')} ({a.get('source')})")

if __name__ == "__main__":
    asyncio.run(main())
