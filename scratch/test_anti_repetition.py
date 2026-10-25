import sys, os, httpx, asyncio, json
sys.path.insert(0, os.path.abspath('.'))
from dotenv import load_dotenv
load_dotenv()
from bot import call_llm_with_failover, SYSTEM_PERSONA

LAST_CACHE = {}

def _clean_field(val):
    if isinstance(val, list):
        return "\n".join([f"• {str(x).lstrip('•- ')}" for x in val if str(x).strip()])
    return str(val).strip()

async def run_syn(cycle_num, deep_dives, client):
    global LAST_CACHE
    prev_text = ""
    if LAST_CACHE.get("sitrep"):
        prev_text = f"""PREVIOUS SITREP GIVEN TO OPERATOR:
- Last SitRep: {LAST_CACHE.get('sitrep')}
- Last Active Theaters: {LAST_CACHE.get('conflict_summary')}
- Last Forecast: {LAST_CACHE.get('future_risk_forecast')}
"""
    prompt = f"""OPERATOR MEMORY & ASSET PROFILE:
Base: Kitengela/Nairobi. Currency: KES. Monitor kinetic conflicts, fuel/import shipping, and tech stack.

{prev_text}
INCOMING IN-DEPTH TOPIC DEEP DIVES:
{json.dumps(deep_dives, indent=2)}

STRICT NON-REPETITION & IN-DEPTH INTELLIGENCE DIRECTIVES:
1. DO NOT repeat the previous SitRep or boilerplate statements. The operator already received the prior briefing.
2. Provide FRESH TACTICAL DEPTH, NEW DEVELOPMENTS, and SPECIFIC DETAILS on or around the active subjects.
3. Directly incorporate the IN-DEPTH TOPIC DEEP DIVES.
4. If a conflict or economic situation remains ongoing, do not just restate that it is happening; analyze the underlying shift, tactical pivot, or second-order consequences.
5. Synthesize in the voice of Cortana / J.A.R.V.I.S.

Output valid JSON strictly matching this schema:
{{
  "threat_level": "NOMINAL" | "ELEVATED" | "CRITICAL",
  "sitrep": "Executive synthesis (under 110 words) focusing on fresh developments, tactical shifts, and active situations without repeating prior statements.",
  "conflict_summary": "In-depth status of active kinetic and logistics flashpoints highlighting specific shifts.",
  "future_risk_forecast": "Second-order economic, cyber, or supply-chain shocks projected over the next 7-30 days.",
  "defensive_protocol": "3 concrete actions the operator must take immediately.",
  "asymmetric_upside": "3 concrete ways the operator can benefit."
}}"""

    msg = await call_llm_with_failover(
        client,
        [
            {"role": "system", "content": SYSTEM_PERSONA + " Always respond in valid JSON."},
            {"role": "user", "content": prompt}
        ],
        json_mode=True
    )
    parsed = json.loads(msg.get("content", "{}"))
    record = {
        "threat_level": parsed.get("threat_level", "ELEVATED"),
        "sitrep": _clean_field(parsed.get("sitrep", "")),
        "conflict_summary": _clean_field(parsed.get("conflict_summary", "")),
        "future_risk_forecast": _clean_field(parsed.get("future_risk_forecast", "")),
        "defensive_protocol": _clean_field(parsed.get("defensive_protocol", "")),
        "asymmetric_upside": _clean_field(parsed.get("asymmetric_upside", "")),
    }
    LAST_CACHE.update(record)
    return record

async def main():
    async with httpx.AsyncClient() as client:
        print("=== SWEEP 1 ===")
        deep_dives_1 = [
            {"subject": "Red Sea Shipping", "latest_developments": "Houthi anti-ship missiles targeting bulk carriers", "in_depth_context": "Vessels diverting to Cape of Good Hope, insurance rate +20%", "why_it_matters": "Adds 12 days to Asia-Europe and East Africa freight."}
        ]
        res1 = await run_syn(1, deep_dives_1, client)
        print("SITREP 1:")
        print(res1["sitrep"])
        print("\nCONFLICT 1:")
        print(res1["conflict_summary"])

        print("\n=== SWEEP 2 (Same subject, evolving angle) ===")
        deep_dives_2 = [
            {"subject": "Red Sea & Djibouti Naval Base", "latest_developments": "China and Djibouti naval task forces deploy to escort commercial tankers", "in_depth_context": "Chinese PLA navy expands Bab-el-Mandeb patrols; bunker fuel costs surge in Port of Mombasa", "why_it_matters": "Higher fuel landing costs in Mombasa translate to KES fuel price pressure next week."}
        ]
        res2 = await run_syn(2, deep_dives_2, client)
        print("SITREP 2:")
        print(res2["sitrep"])
        print("\nCONFLICT 2:")
        print(res2["conflict_summary"])

if __name__ == "__main__":
    asyncio.run(main())
