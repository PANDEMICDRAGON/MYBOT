"""
Test Scraper Script
Run this script locally to test URL fetching and CSS selector extraction 
without needing Supabase or Telegram credentials configured yet.

Usage:
    python test_local.py
    python test_local.py https://news.ycombinator.com .titleline
"""

import sys
import hashlib
import asyncio
import httpx
from bs4 import BeautifulSoup


async def test_scrape(url: str, selector: str):
    print(f"\n[1/3] Fetching: {url}...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            resp = await client.get(url, headers=headers, timeout=20)
            print(f"[2/3] Status code: {resp.status_code} OK (length: {len(resp.text)} chars)")
            
            soup = BeautifulSoup(resp.text, "html.parser")
            elements = [el.get_text(" ", strip=True) for el in soup.select(selector)]
            
            print(f"[3/3] Extracted elements for selector '{selector}': {len(elements)} found")
            print("-" * 50)
            
            if not elements:
                print(f"Warning: No elements found matching '{selector}'.")
                print("Tip: Check the site's HTML or test with 'title' or 'h1' or 'h2'.")
                return

            # Deduplicate preserving order
            seen = set()
            unique_items = []
            for item in elements:
                if item and item not in seen:
                    seen.add(item)
                    unique_items.append(item)

            for idx, item in enumerate(unique_items[:10], 1):
                print(f" {idx}. {item}")

            if len(unique_items) > 10:
                print(f" ... and {len(unique_items) - 10} more items.")

            content_text = "\n• ".join(unique_items[:15])
            content_hash = hashlib.sha256(content_text.encode("utf-8")).hexdigest()
            print("-" * 50)
            print(f"Payload SHA-256 Hash: {content_hash}")
            print("Deduplication check: Ready!")

        except Exception as e:
            print(f"Extraction error: {e}")


if __name__ == "__main__":
    test_url = sys.argv[1] if len(sys.argv) > 1 else "https://news.ycombinator.com"
    test_selector = sys.argv[2] if len(sys.argv) > 2 else ".titleline"
    asyncio.run(test_scrape(test_url, test_selector))
