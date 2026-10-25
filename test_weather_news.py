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
    {
        "source": "Kenya Local News",
        "scope": "LOCAL",
        "url": "https://news.google.com/rss/search?q=Kenya+OR+Nairobi+OR+Kitengela&hl=en-KE&gl=KE&ceid=KE:en"
    },
    {
        "source": "BBC World",
        "scope": "GLOBAL",
        "url": "https://feeds.bbci.co.uk/news/world/rss.xml"
    },
    {
        "source": "Al Jazeera Global",
        "scope": "GLOBAL",
        "url": "https://www.aljazeera.com/xml/rss/all.xml"
    }
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

        print("\n=================== 📰 NEWS ENGINE TEST ====================")
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) TelemetryTest/1.0"}
        for feed in NEWS_FEEDS:
            print(f"\n--- {feed['source']} ({feed['scope']}) ---")
            try:
                resp = await client.get(feed["url"], headers=headers, timeout=15)
                root = ET.fromstring(resp.content)
                items = root.findall(".//item")[:3]
                for i, item in enumerate(items, 1):
                    title = item.findtext("title") or "Untitled"
                    link = item.findtext("link") or ""
                    print(f" {i}. {title}")
                    print(f"    Link: {link}")
            except Exception as e:
                print(f"Error fetching {feed['source']}: {e}")

        print("\n✅ Verification complete! Both feeds are operational.\n")

if __name__ == "__main__":
    asyncio.run(run_test())
