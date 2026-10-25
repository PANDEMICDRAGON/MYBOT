import sys, os, httpx, asyncio, json
sys.path.insert(0, os.path.abspath('.'))
from dotenv import load_dotenv
load_dotenv()
from bot import call_llm_with_failover, SYSTEM_PERSONA

async def test_enrich():
    sample_news = [
        {"title": "China, Djibouti Express Serious Concern Over Threats to Red Sea Shipping", "source": "The Diplomat", "scope": "GLOBAL"},
        {"title": "Central Bank of Kenya Holds Key Rate as Inflation Eases", "source": "Kenya Markets", "scope": "LOCAL"},
        {"title": "CISA Adds Critical Fortinet and Palo Alto Vulnerabilities to Known Exploited Catalog", "source": "The Hacker News", "scope": "GLOBAL"},
    ]
    
    prompt = f"""You are HALO's Tactical Intelligence Analyst.
Analyze these incoming raw news dispatches collected in the latest sweep:
{json.dumps(sample_news, indent=2)}

Provide IN-DEPTH OPERATIONAL INTELLIGENCE around these subjects. For each distinct subject, extract:
- subject: The active theme (e.g., "Red Sea & Maritime Chokepoints", "Kenya Macro & Currency", "Perimeter Cyber Threats")
- latest_developments: Specific new details/developments (do not just repeat the headline)
- in_depth_context: Underlying mechanics, second-order economic/logistics/security ripples
- why_it_matters: Specific tactical consequence for our operator (based in Nairobi/Kitengela, managing tech/capital)

Output valid JSON strictly as an array of objects matching this schema:
[
  {{
    "subject": "Theme Title",
    "latest_developments": "...",
    "in_depth_context": "...",
    "why_it_matters": "..."
  }}
]"""

    async with httpx.AsyncClient() as client:
        msg = await call_llm_with_failover(
            client,
            [
                {"role": "system", "content": SYSTEM_PERSONA + " Always respond in valid JSON."},
                {"role": "user", "content": prompt}
            ],
            json_mode=True
        )
        print("Raw response:")
        print(msg.get("content", ""))
        try:
            parsed = json.loads(msg.get("content", "[]"))
            print("Parsed objects count:", len(parsed))
            for item in parsed:
                print("---", item.get("subject"), "---")
                print("Developments:", item.get("latest_developments"))
                print("Depth:", item.get("in_depth_context"))
                print("Why it matters:", item.get("why_it_matters"))
        except Exception as e:
            print("Parse error:", e)

if __name__ == "__main__":
    asyncio.run(test_enrich())
