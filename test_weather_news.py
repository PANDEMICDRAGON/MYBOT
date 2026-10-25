"""
Instant Test Utility for Weather & News Engines
Tests Open-Meteo weather API and RSS news feeds directly without needing Supabase.
"""

import sys
import asyncio
import xml.etree.ElementTree as ET
import httpx

# Ensure UTF-8 output on Windows consoles
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WEATHER_LOCATIONS = [
    {"city": "Kitengela", "scope": "LOCAL", "lat": -1.4746, "lon": 36.9614},
    {"city": "Nairobi", "scope": "LOCAL", "lat": -1.2921, "lon": 36.8219},
    {"city": "London", "scope": "GLOBAL", "lat": 51.5074, "lon": -0.1278},
    {"city": "New York", "scope": "GLOBAL", "lat": 40.7128, "lon": -74.0060},
    {"city": "Tokyo", "scope": "GLOBAL", "lat": 35.6762, "lon": 139.6503},
]

NEWS_FEEDS = [
    {"source": "CNN World", "scope": "GLOBAL", "url": "http://rss.cnn.com/rss/edition_world.rss"},
    {"source": "BBC World", "scope": "GLOBAL", "url": "https://feeds.bbci.co.uk/news/world/rss.xml"},
    {"source": "Al Jazeera", "scope": "GLOBAL", "url": "https://www.aljazeera.com/xml/rss/all.xml"},
    {"source": "Fox News World", "scope": "GLOBAL", "url": "https://moxie.foxnews.com/google-publisher/world.xml"},
    {"source": "NYT World", "scope": "GLOBAL", "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"},
    {"source": "WSJ World", "scope": "GLOBAL", "url": "https://feeds.a.dj.com/rss/RSSWorldNews.xml"},
    {"source": "The Guardian World", "scope": "GLOBAL", "url": "https://www.theguardian.com/world/rss"},
    {"source": "Kenya Local Wire", "scope": "LOCAL", "url": "https://news.google.com/rss/search?q=Kenya+OR+Nairobi+OR+Kitengela&hl=en-KE&gl=KE&ceid=KE:en"}
]

CONFLICT_AND_MACRO_FEEDS = [
    {"source": "Defense One", "domain": "WAR-KINETIC", "theater": "GLOBAL", "url": "https://www.defenseone.com/rss/all/"},
    {"source": "War on the Rocks", "domain": "WAR-KINETIC", "theater": "GLOBAL", "url": "https://warontherocks.com/feed/"},
    {"source": "Middle East & Red Sea", "domain": "WAR-KINETIC", "theater": "RED-SEA-MIDEAST", "url": "https://news.google.com/rss/search?q=(\"Red+Sea\"+OR+\"Hormuz\"+OR+Israel+OR+Iran+OR+Gaza+OR+Lebanon+OR+Houthi)+AND+(strike+OR+missile+OR+blockade+OR+shipping+OR+war)&hl=en-US&gl=US&ceid=US:en"},
    {"source": "Horn of Africa Security", "domain": "WAR-KINETIC", "theater": "EAST-AFRICA", "url": "https://news.google.com/rss/search?q=(Sudan+OR+Somalia+OR+Ethiopia+OR+DRC+OR+\"East+Africa\")+AND+(conflict+OR+military+OR+insurgency+OR+border+OR+security)&hl=en-KE&gl=KE&ceid=KE:en"},
    {"source": "Eastern Europe & NATO Flank", "domain": "WAR-KINETIC", "theater": "EASTERN-EUROPE", "url": "https://news.google.com/rss/search?q=(Ukraine+OR+Russia+OR+NATO+OR+Black+Sea)+AND+(frontline+OR+drone+OR+sanctions+OR+energy+OR+offensive)&hl=en-US&gl=US&ceid=US:en"},
    {"source": "Indo-Pacific & Taiwan Strait", "domain": "GEOPOLITICAL", "theater": "INDO-PACIFIC", "url": "https://news.google.com/rss/search?q=(\"South+China+Sea\"+OR+Taiwan+OR+semiconductors+OR+blockade)+AND+(military+OR+sanctions+OR+tariff+OR+supply+chain)&hl=en-US&gl=US&ceid=US:en"},
    {"source": "CNBC Global Macro", "domain": "MACRO-ECONOMIC", "theater": "GLOBAL", "url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664"},
    {"source": "WSJ Markets", "domain": "MACRO-ECONOMIC", "theater": "GLOBAL", "url": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml"}
]

WMO_CODES = {
    0: "Clear Sky", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
    45: "Fog", 51: "Light Drizzle", 61: "Light Rain", 63: "Moderate Rain",
    65: "Heavy Rain", 80: "Rain Showers", 95: "Thunderstorm"
}

async def run_test():
    async with httpx.AsyncClient(follow_redirects=True) as client:
        print("\n================== 🌤️ WEATHER ENGINE TEST ==================")
        for loc in WEATHER_LOCATIONS:
            url = (
                f"https://api.open-meteo.com/v1/forecast"
                f"?latitude={loc['lat']}&longitude={loc['lon']}"
                f"&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
            )
            try:
                resp = await client.get(url, timeout=10)
                current = resp.json().get("current", {})
                code = current.get("weather_code", 0)
                condition = WMO_CODES.get(code, f"Code {code}")
                temp = current.get("temperature_2m", 0.0)
                wind = current.get("wind_speed_10m", 0.0)
                humidity = current.get("relative_humidity_2m", 0)
                print(f"[{loc['scope']}] {loc['city']:10} | {temp:4.1f}°C | {condition:15} | Wind: {wind:4.1f} km/h | Hum: {humidity}%")
            except Exception as e:
                print(f"[{loc['scope']}] {loc['city']}: Error {e}")

        print("\n=================== 📰 GLOBAL NEWS NETWORKS TEST ====================")
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) TelemetryTest/1.0"}
        for feed in NEWS_FEEDS:
            try:
                resp = await client.get(feed["url"], headers=headers, timeout=12)
                root = ET.fromstring(resp.content)
                item = root.find(".//item")
                headline = (item.findtext("title") if item is not None else "Untitled").strip()
                print(f"[{feed['source']:20}] OK | {headline[:70]}...")
            except Exception as e:
                print(f"[{feed['source']:20}] ERROR: {e}")

        print("\n=================== 🛡️ WAR, CONFLICT & MACRO-ECONOMIC THREAT FEEDS ====================")
        for feed in CONFLICT_AND_MACRO_FEEDS:
            try:
                resp = await client.get(feed["url"], headers=headers, timeout=12)
                root = ET.fromstring(resp.content)
                item = root.find(".//item")
                headline = (item.findtext("title") if item is not None else "Untitled").strip()
                print(f"[{feed['theater']:16} | {feed['source']:24}] OK | {headline[:60]}...")
            except Exception as e:
                print(f"[{feed['theater']:16} | {feed['source']:24}] ERROR: {e}")

        print("\n✅ Verification complete! Multi-network global news and war/macro telemetry online.\n")

if __name__ == "__main__":
    asyncio.run(run_test())

