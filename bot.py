import os
import sys
import time
import asyncio
import hashlib
import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import httpx
from dotenv import load_dotenv

# Setup clean, informative logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("TelemetryBot")

# Load configuration from .env file
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

# Credentials & URLs
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
AUTHORIZED_CHAT_ID_RAW = os.getenv("TELEGRAM_CHAT_ID", "").strip()
SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_KEY", "").strip()
SYNC_INTERVAL = int(os.getenv("SYNC_INTERVAL", "900"))  # Default: 15 minutes

AUTHORIZED_CHAT_ID = int(AUTHORIZED_CHAT_ID_RAW) if AUTHORIZED_CHAT_ID_RAW.lstrip("-").isdigit() else 0

SUPABASE_HEADERS = {
    "apikey": SUPABASE_SERVICE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    "Content-Type": "application/json"
}

# Coordinate Registry for Open-Meteo Weather (Local + Global Hubs)
WEATHER_LOCATIONS = [
    {"city": "Kitengela", "scope": "LOCAL", "lat": -1.4746, "lon": 36.9614},
    {"city": "Nairobi", "scope": "LOCAL", "lat": -1.2921, "lon": 36.8219},
    {"city": "London", "scope": "GLOBAL", "lat": 51.5074, "lon": -0.1278},
    {"city": "New York", "scope": "GLOBAL", "lat": 40.7128, "lon": -74.0060},
    {"city": "Tokyo", "scope": "GLOBAL", "lat": 35.6762, "lon": 139.6503},
]

# RSS Feed Registry (Local + Global News)
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

# Cybersecurity Intelligence Feeds (Threat Intel & Local Cyber)
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

CISA_KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"

# WMO Weather Condition Mappings
WMO_CODES = {
    0: "Clear Sky", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing Rime Fog",
    51: "Light Drizzle", 53: "Moderate Drizzle", 55: "Dense Drizzle",
    61: "Slight Rain", 63: "Moderate Rain", 65: "Heavy Rain",
    71: "Slight Snow", 73: "Moderate Snow", 75: "Heavy Snow",
    80: "Rain Showers", 81: "Moderate Showers", 82: "Violent Showers",
    95: "Thunderstorm", 96: "Thunderstorm with Hail", 99: "Heavy Hail Storm"
}

BOOT_TIME = time.time()
force_sync_event = asyncio.Event()


# =====================================================================
# --- AI EXTENSION HOOK (MODULAR LLM INTEGRATION POINT) ---
# =====================================================================
async def process_text(text: str) -> str:
    """
    Pass-through hook for news, headlines, and threat descriptions.
    When ready, connect Gemini or Groq to summarize, categorize, or translate.
    """
    return text.strip()


# =====================================================================
# --- TELEGRAM MESSAGING & NOTIFICATION ENGINE ---
# =====================================================================
async def send_telegram(client: httpx.AsyncClient, text: str):
    """Pushes notification message to user's Telegram."""
    if not TELEGRAM_TOKEN or not AUTHORIZED_CHAT_ID:
        logger.warning(f"[Mock Telegram Push]:\n{text}")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": AUTHORIZED_CHAT_ID,
        "text": text[:4096],
        "disable_web_page_preview": True
    }
    try:
        resp = await client.post(url, json=payload, timeout=15)
        if resp.status_code != 200:
            logger.error(f"Telegram error {resp.status_code}: {resp.text}")
    except Exception as e:
        logger.error(f"[Telegram Send Error]: {e}")


# =====================================================================
# --- WEATHER ENGINE (OPEN-METEO API - ZERO KEY REQUIRED) ---
# =====================================================================
async def sync_weather(client: httpx.AsyncClient) -> list[dict]:
    """Fetches real-time weather reports for local and global cities."""
    results = []
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        logger.warning("Supabase credentials not set, skipping weather sync.")
        return results

    logger.info("Syncing weather across all monitored locations...")
    for loc in WEATHER_LOCATIONS:
        try:
            url = (
                f"https://api.open-meteo.com/v1/forecast"
                f"?latitude={loc['lat']}&longitude={loc['lon']}"
                f"&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
            )
            resp = await client.get(url, timeout=15)
            resp.raise_for_status()
            current = resp.json().get("current", {})

            code = current.get("weather_code", 0)
            record = {
                "city": loc["city"],
                "scope": loc["scope"],
                "temp_c": current.get("temperature_2m", 0.0),
                "humidity": current.get("relative_humidity_2m", 0),
                "wind_kmh": current.get("wind_speed_10m", 0.0),
                "condition": WMO_CODES.get(code, f"Code {code}"),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            results.append(record)

            # Upsert into Supabase weather_reports table
            upsert_headers = {**SUPABASE_HEADERS, "Prefer": "resolution=merge-duplicates"}
            await client.post(
                f"{SUPABASE_URL}/rest/v1/weather_reports",
                headers=upsert_headers,
                json=record,
                timeout=15
            )
        except Exception as e:
            logger.error(f"[Weather Error - {loc['city']}]: {e}")

    logger.info(f"Weather sync complete ({len(results)} cities updated).")
    return results


# =====================================================================
# --- NEWS ENGINE (STRUCTURED RSS FEEDS WITH DEDUPLICATION) ---
# =====================================================================
async def sync_news(client: httpx.AsyncClient) -> list[dict]:
    """Parses local and global RSS feeds, deduplicates by SHA-256 hash, and inserts new records."""
    new_articles = []
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        logger.warning("Supabase credentials not set, skipping news sync.")
        return new_articles

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) TelemetryCollector/2.0"}
    logger.info("Scanning RSS feeds for fresh news...")

    for feed in NEWS_FEEDS:
        try:
            resp = await client.get(feed["url"], headers=headers, timeout=20)
            resp.raise_for_status()
            root = ET.fromstring(resp.content)

            for item in root.findall(".//item")[:6]:
                raw_title = item.findtext("title") or "Untitled"
                link = item.findtext("link") or ""
                pub_date = item.findtext("pubDate") or ""

                title = await process_text(raw_title)
                content_hash = hashlib.sha256(f"{title}{link}".encode("utf-8")).hexdigest()

                # Deduplication check against Supabase
                check_url = f"{SUPABASE_URL}/rest/v1/news_articles?content_hash=eq.{content_hash}&select=id"
                check_resp = await client.get(check_url, headers=SUPABASE_HEADERS, timeout=15)
                if check_resp.status_code == 200 and len(check_resp.json()) > 0:
                    continue  # Already recorded

                article = {
                    "scope": feed["scope"],
                    "source": feed["source"],
                    "title": title,
                    "link": link,
                    "content_hash": content_hash,
                    "published_at": pub_date[:30],
                    "created_at": datetime.now(timezone.utc).isoformat()
                }

                insert_resp = await client.post(
                    f"{SUPABASE_URL}/rest/v1/news_articles",
                    headers=SUPABASE_HEADERS,
                    json=article,
                    timeout=15
                )
                if insert_resp.status_code == 201:
                    new_articles.append(article)
                    logger.info(f"✨ New article stored: [{feed['source']}] {title[:60]}...")

        except Exception as e:
            logger.error(f"[News Feed Error - {feed['source']}]: {e}")

    logger.info(f"News scan complete ({len(new_articles)} new articles discovered).")
    return new_articles


# =====================================================================
# --- CYBERSECURITY ENGINE (CISA KEV JSON + THREAT INTEL RSS) ---
# =====================================================================
async def sync_cyber_alerts(client: httpx.AsyncClient) -> list[dict]:
    """Ingests CISA Known Exploited Vulnerabilities and threat intel feeds."""
    new_alerts = []
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        logger.warning("Supabase credentials not set, skipping cyber alerts sync.")
        return new_alerts

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CyberTelemetry/2.0"}
    logger.info("Syncing cybersecurity threat intelligence & CISA KEV...")

    # 1. Fetch CISA Known Exploited Vulnerabilities (KEV) Catalog
    try:
        resp = await client.get(CISA_KEV_URL, headers=headers, timeout=25)
        resp.raise_for_status()
        vulns = resp.json().get("vulnerabilities", [])
        # Sort by dateAdded descending and inspect top 8 entries
        vulns.sort(key=lambda x: x.get("dateAdded", ""), reverse=True)

        for v in vulns[:8]:
            cve_id = v.get("cveID", "UNKNOWN-CVE")
            vendor = v.get("vendorProject", "")
            product = v.get("product", "")
            name = v.get("vulnerabilityName", "")
            short_desc = v.get("shortDescription", "")
            ransomware = v.get("knownRansomwareCampaignUse", "Unknown")

            severity = "CRITICAL" if ransomware == "Known" else "HIGH"
            title = f"{cve_id}: {vendor} {product} - {name}"
            link = f"https://nvd.nist.gov/vuln/detail/{cve_id}"
            content_hash = hashlib.sha256(cve_id.encode("utf-8")).hexdigest()

            # Deduplication check
            check_url = f"{SUPABASE_URL}/rest/v1/cyber_alerts?content_hash=eq.{content_hash}&select=id"
            check_resp = await client.get(check_url, headers=SUPABASE_HEADERS, timeout=15)
            if check_resp.status_code == 200 and len(check_resp.json()) > 0:
                continue

            alert = {
                "category": "CVE-KEV",
                "source": "CISA KEV",
                "cve_id": cve_id,
                "severity": severity,
                "title": await process_text(title),
                "summary": short_desc[:300],
                "link": link,
                "content_hash": content_hash,
                "published_at": v.get("dateAdded", ""),
                "created_at": datetime.now(timezone.utc).isoformat()
            }

            insert_resp = await client.post(
                f"{SUPABASE_URL}/rest/v1/cyber_alerts",
                headers=SUPABASE_HEADERS,
                json=alert,
                timeout=15
            )
            if insert_resp.status_code == 201:
                new_alerts.append(alert)
                logger.info(f"🚨 New CISA CVE recorded: {cve_id} ({severity})")
    except Exception as e:
        logger.error(f"[CISA KEV Error]: {e}")

    # 2. Fetch Cybersecurity RSS Feeds (The Hacker News, BleepingComputer, Kenya Cyber)
    for feed in CYBER_RSS_FEEDS:
        try:
            resp = await client.get(feed["url"], headers=headers, timeout=20)
            resp.raise_for_status()
            root = ET.fromstring(resp.content)

            for item in root.findall(".//item")[:6]:
                raw_title = item.findtext("title") or "Untitled"
                link = item.findtext("link") or ""
                pub_date = item.findtext("pubDate") or ""

                title = await process_text(raw_title)
                content_hash = hashlib.sha256(f"{title}{link}".encode("utf-8")).hexdigest()

                check_url = f"{SUPABASE_URL}/rest/v1/cyber_alerts?content_hash=eq.{content_hash}&select=id"
                check_resp = await client.get(check_url, headers=SUPABASE_HEADERS, timeout=15)
                if check_resp.status_code == 200 and len(check_resp.json()) > 0:
                    continue

                lower_t = title.lower()
                if any(k in lower_t for k in ["zero-day", "0-day", "ransomware", "critical", "rce", "actively exploited"]):
                    severity = "CRITICAL"
                elif any(k in lower_t for k in ["breach", "vulnerability", "malware", "cve-", "backdoor", "exploit"]):
                    severity = "HIGH"
                else:
                    severity = "ADVISORY"

                alert = {
                    "category": feed["category"],
                    "source": feed["source"],
                    "cve_id": None,
                    "severity": severity,
                    "title": title,
                    "summary": None,
                    "link": link,
                    "content_hash": content_hash,
                    "published_at": pub_date[:30],
                    "created_at": datetime.now(timezone.utc).isoformat()
                }

                insert_resp = await client.post(
                    f"{SUPABASE_URL}/rest/v1/cyber_alerts",
                    headers=SUPABASE_HEADERS,
                    json=alert,
                    timeout=15
                )
                if insert_resp.status_code == 201:
                    new_alerts.append(alert)
                    logger.info(f"⚡ New Cyber alert recorded: [{severity}] {title[:60]}...")
        except Exception as e:
            logger.error(f"[Cyber RSS Error - {feed['source']}]: {e}")

    logger.info(f"Cyber telemetry scan complete ({len(new_alerts)} new alerts recorded).")
    return new_alerts


# =====================================================================
# --- TELEGRAM COMMAND HANDLER ---
# =====================================================================
async def handle_command(client: httpx.AsyncClient, cmd_text: str):
    parts = cmd_text.strip().split()
    cmd = parts[0].lower() if parts else ""
    logger.info(f"Received user command: {cmd}")

    if cmd in ("/start", "/help"):
        msg = (
            "🛰️ *Telemetry Bot: News, Weather & Cyber Command*\n\n"
            "*Commands:*\n"
            "• `/cyber` — Latest CVEs & threat intelligence\n"
            "• `/weather` — Real-time weather snapshot (Local & Global)\n"
            "• `/local` — Latest Kenya news dispatches\n"
            "• `/global` — Latest world news dispatches\n"
            "• `/sync` — Trigger immediate telemetry update\n"
            "• `/status` — System health and database metrics"
        )
        await send_telegram(client, msg)

    elif cmd == "/cyber":
        try:
            url = f"{SUPABASE_URL}/rest/v1/cyber_alerts?select=*&order=created_at.desc&limit=6"
            resp = await client.get(url, headers=SUPABASE_HEADERS, timeout=15)
            rows = resp.json()
            if not rows:
                await send_telegram(client, "No cyber alerts recorded yet. Run /sync to populate.")
                return
            lines = [f"• *[{r['severity']}]* ({r['source']}) {r['title']}\n  🔗 {r['link']}" for r in rows]
            await send_telegram(client, "🛡️ *Latest Cybersecurity Intelligence:*\n\n" + "\n\n".join(lines))
        except Exception as e:
            await send_telegram(client, f"❌ Failed to fetch cyber alerts: {e}")

    elif cmd == "/weather":
        try:
            resp = await client.get(f"{SUPABASE_URL}/rest/v1/weather_reports?select=*&order=scope.desc", headers=SUPABASE_HEADERS, timeout=15)
            rows = resp.json()
            if not rows:
                await send_telegram(client, "No weather records found. Run /sync to populate.")
                return
            lines = [f"• *{r['city']}* ({r['scope']}): {r['temp_c']}°C, {r['condition']} (Wind: {r['wind_kmh']} km/h, Hum: {r['humidity']}%)" for r in rows]
            await send_telegram(client, "🌤️ *Current Weather Snapshot:*\n\n" + "\n".join(lines))
        except Exception as e:
            await send_telegram(client, f"❌ Failed to fetch weather: {e}")

    elif cmd in ("/local", "/global"):
        scope = "LOCAL" if cmd == "/local" else "GLOBAL"
        try:
            url = f"{SUPABASE_URL}/rest/v1/news_articles?scope=eq.{scope}&order=created_at.desc&limit=5"
            resp = await client.get(url, headers=SUPABASE_HEADERS, timeout=15)
            rows = resp.json()
            if not rows:
                await send_telegram(client, f"No {scope.lower()} news articles found.")
                return
            lines = [f"• *[{r['source']}]* {r['title']}\n  🔗 {r['link']}" for r in rows]
            await send_telegram(client, f"📰 *Latest {scope} Headlines:*\n\n" + "\n\n".join(lines))
        except Exception as e:
            await send_telegram(client, f"❌ Failed to fetch news: {e}")

    elif cmd == "/sync":
        await send_telegram(client, "⚡ Manual telemetry sync triggered across all streams...")
        force_sync_event.set()

    elif cmd == "/status":
        uptime_min = int((time.time() - BOOT_TIME) // 60)
        try:
            w_resp = await client.get(f"{SUPABASE_URL}/rest/v1/weather_reports?select=city", headers=SUPABASE_HEADERS, timeout=10)
            n_resp = await client.get(f"{SUPABASE_URL}/rest/v1/news_articles?select=id", headers=SUPABASE_HEADERS, timeout=10)
            c_resp = await client.get(f"{SUPABASE_URL}/rest/v1/cyber_alerts?select=id", headers=SUPABASE_HEADERS, timeout=10)
            w_count = len(w_resp.json()) if w_resp.status_code == 200 else "N/A"
            n_count = len(n_resp.json()) if n_resp.status_code == 200 else "N/A"
            c_count = len(c_resp.json()) if c_resp.status_code == 200 else "N/A"
        except Exception:
            w_count, n_count, c_count = "N/A", "N/A", "N/A"

        await send_telegram(
            client,
            f"📊 *Telemetry System Status*\n"
            f"• State: ONLINE (24/7 Long Polling)\n"
            f"• Uptime: {uptime_min} minutes\n"
            f"• Weather Stations: {w_count}\n"
            f"• Archived News: {n_count}\n"
            f"• Cyber Threat Records: {c_count}\n"
            f"• Auto-Sync Interval: {SYNC_INTERVAL}s"
        )


# =====================================================================
# --- TELEGRAM POLLER (LONG POLLING / NO DOMAIN) ---
# =====================================================================
async def telegram_poller(client: httpx.AsyncClient):
    """Long-polls Telegram for incoming commands."""
    if not TELEGRAM_TOKEN or not AUTHORIZED_CHAT_ID:
        logger.warning("Telegram credentials not configured. Poller inactive.")
        return

    offset = 0
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    logger.info("Telegram poller initialized...")

    while True:
        try:
            resp = await client.get(url, params={"offset": offset, "timeout": 30}, timeout=45)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("ok"):
                    for update in data.get("result", []):
                        offset = update["update_id"] + 1
                        msg = update.get("message", {})
                        chat_id = msg.get("chat", {}).get("id")
                        text = msg.get("text", "")
                        if chat_id == AUTHORIZED_CHAT_ID and text.startswith("/"):
                            await handle_command(client, text)
            else:
                logger.warning(f"Telegram polling status {resp.status_code}: {resp.text}")
                await asyncio.sleep(5)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"[Poller Error]: {e}")
            await asyncio.sleep(5)


# =====================================================================
# --- CONTINUOUS COLLECTOR WORKER LOOP ---
# =====================================================================
async def collector_worker(client: httpx.AsyncClient):
    """24/7 Worker: updates weather, news, cyber threats, and dispatches Telegram notifications."""
    logger.info(f"Collector worker active (Cycle: {SYNC_INTERVAL}s)...")
    while True:
        weather_data = await sync_weather(client)
        new_articles = await sync_news(client)
        new_cyber = await sync_cyber_alerts(client)

        # Notify via Telegram if new articles or cyber threats discovered
        if new_articles or new_cyber:
            local_weather = [w for w in weather_data if w["scope"] == "LOCAL"]
            w_summary = " | ".join([f"{w['city']}: {w['temp_c']}°C ({w['condition']})" for w in local_weather])
            msg_parts = [f"🌤️ *LOCAL WEATHER CONDITIONS*\n{w_summary if w_summary else 'Updating...'}\n"]

            if new_cyber:
                c_items = "\n".join([f"• [{c['severity']}] {c['title']}\n  🔗 {c['link']}" for c in new_cyber[:4]])
                msg_parts.append(f"🛡️ *CYBERSECURITY THREAT ALERTS ({len(new_cyber)}):*\n{c_items}\n")

            local_new = [a for a in new_articles if a["scope"] == "LOCAL"]
            if local_new:
                items = "\n".join([f"• [{a['source']}] {a['title']}\n  🔗 {a['link']}" for a in local_new[:3]])
                msg_parts.append(f"🇰🇪 *LOCAL HEADLINES ({len(local_new)}):*\n{items}\n")

            global_new = [a for a in new_articles if a["scope"] == "GLOBAL"]
            if global_new:
                items = "\n".join([f"• [{a['source']}] {a['title']}\n  🔗 {a['link']}" for a in global_new[:3]])
                msg_parts.append(f"🌐 *GLOBAL HEADLINES ({len(global_new)}):*\n{items}\n")

            await send_telegram(client, "\n".join(msg_parts))

        try:
            await asyncio.wait_for(force_sync_event.wait(), timeout=SYNC_INTERVAL)
            force_sync_event.clear()
            logger.info("Triggered instant sync cycle via manual trigger.")
        except asyncio.TimeoutError:
            pass
        except asyncio.CancelledError:
            break


# =====================================================================
# --- MAIN APPLICATION ENTRYPOINT ---
# =====================================================================
async def main():
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        logger.warning("Supabase credentials not configured in .env. Please configure them.")
    if not TELEGRAM_TOKEN or not AUTHORIZED_CHAT_ID:
        logger.warning("Telegram credentials not configured in .env.")

    limits = httpx.Limits(max_keepalive_connections=10, max_connections=20)
    async with httpx.AsyncClient(follow_redirects=True, limits=limits) as client:
        if TELEGRAM_TOKEN and AUTHORIZED_CHAT_ID:
            await send_telegram(client, "🚀 *Telemetry Bot Online* — Monitoring Weather, News & Cyber Threats 24/7.")

        tasks = [
            asyncio.create_task(telegram_poller(client)),
            asyncio.create_task(collector_worker(client))
        ]

        try:
            await asyncio.gather(*tasks)
        except (KeyboardInterrupt, asyncio.CancelledError):
            logger.info("Shutting down bot safely...")
            for task in tasks:
                task.cancel()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot exited.")
