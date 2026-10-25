import httpx
import asyncio
import xml.etree.ElementTree as ET

FEEDS = [
    {"source": "BBC Sport", "url": "https://feeds.bbci.co.uk/sport/rss.xml"},
    {"source": "ESPN Top Headlines", "url": "https://www.espn.com/espn/rss/news"},
    {"source": "Sky Sports News", "url": "https://www.skysports.com/rss/12040"},
    {"source": "Kenya Athletics & Sports", "url": "https://news.google.com/rss/search?q=(Kenya+OR+Nairobi)+AND+(Harambee+Stars+OR+athletics+OR+marathon+OR+Kipchoge+OR+Omanyala+OR+FKF+OR+rugby)&hl=en-KE&gl=KE&ceid=KE:en"},
    {"source": "Premier League & UCL", "url": "https://news.google.com/rss/search?q=(%22Premier+League%22+OR+%22Champions+League%22)+AND+(Arsenal+OR+%22Man+City%22+OR+Liverpool+OR+%22Man+United%22+OR+Chelsea+OR+Real+Madrid)+AND+(transfer+OR+match+OR+score+OR+injury)&hl=en-US&gl=US&ceid=US:en"},
    {"source": "Formula 1 Motorsport", "url": "https://news.google.com/rss/search?q=(%22Formula+1%22+OR+F1+OR+Ferrari+OR+Mercedes+OR+%22Red+Bull+Racing%22+OR+Verstappen+OR+Hamilton)+AND+(Grand+Prix+OR+qualifying+OR+race)&hl=en-US&gl=US&ceid=US:en"}
]

async def check():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SportsWire/1.0"}
    async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
        for f in FEEDS:
            try:
                r = await client.get(f["url"], headers=headers)
                print(f"[{f['source']}]: HTTP {r.status_code}")
                if r.status_code == 200:
                    root = ET.fromstring(r.content)
                    items = root.findall(".//item")
                    print(f"  -> Found {len(items)} items. Top: {items[0].findtext('title') if items else 'None'}")
            except Exception as e:
                print(f"[{f['source']}]: Error -> {e}")

if __name__ == "__main__":
    asyncio.run(check())
