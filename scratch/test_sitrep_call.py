import os, httpx, asyncio, json
from dotenv import load_dotenv
load_dotenv()
from bot import call_llm_with_failover, SYSTEM_PERSONA

async def test_syn():
    prompt = """OPERATOR MEMORY & ASSET PROFILE:
Base: Kitengela/Nairobi. Currency: KES. Monitor kinetic conflicts, fuel/import shipping, and tech stack.

INCOMING MULTI-NETWORK TELEMETRY:
{"local_weather": [{"city": "Nairobi", "temp": 24, "condition": "Sunny"}], "global_and_local_news": [{"title": "Red Sea attacks disrupt shipping", "source": "BBC"}], "cyber_alerts": [], "wars_and_macro_shocks": []}

Synthesize this intelligence in the voice of Cortana/J.A.R.V.I.S. Output valid JSON strictly matching this schema:
{
  "threat_level": "NOMINAL" | "ELEVATED" | "CRITICAL",
  "sitrep": "Executive synthesis (under 90 words) cross-referencing CNN, BBC, Al Jazeera, Fox, and local Kenya feeds.",
  "conflict_summary": "Status of active kinetic wars (Red Sea/Middle East, Eastern Europe, Horn of Africa/Sudan/Somalia, Indo-Pacific) and maritime chokepoints.",
  "future_risk_forecast": "Second-order economic, cyber, or supply-chain shocks projected over the next 7-30 days (fuel/import inflation, KES/USD pressure, cloud/undersea cable risks).",
  "defensive_protocol": "3 concrete actions the operator must take immediately to protect capital, infrastructure, and local operations.",
  "asymmetric_upside": "3 concrete ways the operator can benefit (NSE equity positioning, currency/commodity hedges, or high-demand technical/software opportunities created by the crisis)."
}"""
    async with httpx.AsyncClient() as client:
        msg = await call_llm_with_failover(
            client,
            [
                {"role": "system", "content": SYSTEM_PERSONA + " Always respond in valid JSON."},
                {"role": "user", "content": prompt}
            ],
            json_mode=True
        )
        print("MSG raw content:")
        print(msg.get("content", ""))
        try:
            parsed = json.loads(msg.get("content", "{}"))
            print("Parsed keys:", list(parsed.keys()))
            print("Sitrep:", parsed.get("sitrep"))
            print("Conflict:", parsed.get("conflict_summary"))
        except Exception as e:
            print("JSON parse error:", e)

if __name__ == "__main__":
    asyncio.run(test_syn())
