import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncio
import httpx
from bot import sync_news

async def main():
    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
        print("Running sync_news with sports rotation...")
        articles, deep_dives = await sync_news(client)
        print(f"Total articles returned: {len(articles)}")
        sports_count = sum(1 for a in articles if a.get("scope") == "SPORTS")
        print(f"Sports articles: {sports_count}")
        for a in articles:
            if a.get("scope") == "SPORTS":
                print(f"  [SPORTS - {a['source']}]: {a['title'][:90]}")

if __name__ == "__main__":
    asyncio.run(main())
