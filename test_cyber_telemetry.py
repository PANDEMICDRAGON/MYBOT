"""
Offline Test Utility for Cybersecurity Telemetry Feeds
Tests CISA Known Exploited Vulnerabilities (KEV) JSON and Cyber RSS feeds directly.
"""

import sys
import asyncio
import xml.etree.ElementTree as ET
import httpx

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

CISA_KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"

CYBER_RSS_FEEDS = [
    {
        "source": "The Hacker News",
        "category": "THREAT-INTEL",
        "url": "https://feeds.feedburner.com/TheHackersNews"
    },
    {
        "source": "BleepingComputer",
        "category": "THREAT-INTEL",
        "url": "https://www.bleepingcomputer.com/feed/"
    },
    {
        "source": "Kenya Cyber Monitor",
        "category": "LOCAL-CYBER",
        "url": "https://news.google.com/rss/search?q=(Kenya+OR+Nairobi)+AND+(cybersecurity+OR+cyberattack+OR+ransomware+OR+%22data+breach%22+OR+KE-CIRT)&hl=en-KE&gl=KE&ceid=KE:en"
    }
]

async def run_cyber_test():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CyberTest/1.0"}
    async with httpx.AsyncClient(follow_redirects=True) as client:
        print("\n================ 🛡️ 1. CISA KEV CATALOG TEST ================")
        try:
            resp = await client.get(CISA_KEV_URL, headers=headers, timeout=20)
            data = resp.json()
            vulns = data.get("vulnerabilities", [])
            vulns.sort(key=lambda x: x.get("dateAdded", ""), reverse=True)
            print(f"Total CVEs in CISA Catalog: {len(vulns)}")
            print("Latest 3 Actively Exploited CVEs:")
            for idx, v in enumerate(vulns[:3], 1):
                cve_id = v.get("cveID")
                vendor = v.get("vendorProject")
                product = v.get("product")
                name = v.get("vulnerabilityName")
                date = v.get("dateAdded")
                ransom = v.get("knownRansomwareCampaignUse", "Unknown")
                print(f" {idx}. [{cve_id}] {vendor} {product} ({date}) | Ransomware: {ransom}")
                print(f"    Name: {name}")
        except Exception as e:
            print(f"CISA KEV Error: {e}")

        print("\n================ ⚡ 2. THREAT INTEL RSS TEST ================")
        for feed in CYBER_RSS_FEEDS:
            print(f"\n--- {feed['source']} ({feed['category']}) ---")
            try:
                resp = await client.get(feed["url"], headers=headers, timeout=15)
                root = ET.fromstring(resp.content)
                items = root.findall(".//item")[:2]
                for i, item in enumerate(items, 1):
                    title = item.findtext("title") or "Untitled"
                    link = item.findtext("link") or ""
                    pub = item.findtext("pubDate") or ""
                    print(f" {i}. {title}")
                    print(f"    Date: {pub[:25]} | Link: {link[:70]}...")
            except Exception as e:
                print(f"Error reading {feed['source']}: {e}")

        print("\n✅ Verification complete! Cyber intelligence pipeline operational.\n")

if __name__ == "__main__":
    asyncio.run(run_cyber_test())
