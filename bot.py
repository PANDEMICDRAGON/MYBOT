import os
import sys
import re
import io
import json
import time
import base64
import socket
import shutil
import asyncio
import hashlib
import logging
import platform
import subprocess
import xml.etree.ElementTree as ET
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import edge_tts
from wakeonlan import send_magic_packet

# Setup clean, informative logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("CortanaJARVIS")

# Load configuration from .env file
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

# Credentials & URLs
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
AUTHORIZED_CHAT_ID_RAW = os.getenv("TELEGRAM_CHAT_ID", "").strip()
SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_KEY", "").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
SYNC_INTERVAL = int(os.getenv("SYNC_INTERVAL", "900"))

# Voice Construct Selection (Halo Cortana: en-US-AriaNeural, Stark J.A.R.V.I.S.: en-GB-RyanNeural)
CONSTRUCT_VOICE = os.getenv("CONSTRUCT_VOICE", "en-US-AriaNeural")
ENABLE_LOCAL_SPEAKER = os.getenv("ENABLE_LOCAL_SPEAKER", "false").lower() == "true"
ENABLE_WAKEWORD = os.getenv("ENABLE_WAKEWORD", "false").lower() == "true"

AUTHORIZED_CHAT_ID = int(AUTHORIZED_CHAT_ID_RAW) if AUTHORIZED_CHAT_ID_RAW.lstrip("-").isdigit() else 0

SUPABASE_HEADERS = {
    "apikey": SUPABASE_SERVICE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    "Content-Type": "application/json"
}

GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_AUDIO_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
LLM_MODEL = "llama-3.3-70b-versatile"
VISION_MODEL = "llama-3.2-11b-vision-preview"

SYSTEM_PERSONA = """You are Cortana, the legendary UNSC military AI construct from Halo, enhanced with the precision systems of J.A.R.V.I.S.
Rules of Engagement:
1. Address the operator directly with calm, brilliant tactical authority, dry wit, and razor-sharp intellect. No subservience, no empty pleasantries, no emojis.
2. Speak like Cortana: confident, protective of the operator, highly perceptive of human behavioral motives and military/macro flashpoints.
3. You have direct control over the operator's Wi-Fi network, Smart TVs, laptops, and IoT gadgets. When commanded, execute hardware commands (power, wake, mute, volume, casting) immediately.
4. Formulate concrete Defensive Protocols and Asymmetric Upside on financial, physical, and digital battlefields."""

WEATHER_LOCATIONS = [
    {"city": "Kitengela", "scope": "LOCAL", "lat": -1.4746, "lon": 36.9614},
    {"city": "Nairobi", "scope": "LOCAL", "lat": -1.2921, "lon": 36.8219},
    {"city": "London", "scope": "GLOBAL", "lat": 51.5074, "lon": -0.1278},
    {"city": "New York", "scope": "GLOBAL", "lat": 40.7128, "lon": -74.0060},
    {"city": "Tokyo", "scope": "GLOBAL", "lat": 35.6762, "lon": 139.6503},
]

# 1. Major Global Networks & Local Wire
NEWS_FEEDS = [
    {"source": "CNN World", "scope": "GLOBAL", "url": "http://rss.cnn.com/rss/edition_world.rss"},
    {"source": "BBC World", "scope": "GLOBAL", "url": "https://feeds.bbci.co.uk/news/world/rss.xml"},
    {"source": "Al Jazeera", "scope": "GLOBAL", "url": "https://www.aljazeera.com/xml/rss/all.xml"},
    {"source": "Fox News World", "scope": "GLOBAL", "url": "https://moxie.foxnews.com/google-publisher/world.xml"},
    {"source": "NYT World", "scope": "GLOBAL", "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"},
    {"source": "WSJ World", "scope": "GLOBAL", "url": "https://feeds.a.dj.com/rss/RSSWorldNews.xml"},
    {"source": "The Guardian World", "scope": "GLOBAL", "url": "https://www.theguardian.com/world/rss"},
    {"source": "Kenya Local Wire", "scope": "LOCAL", "url": "https://news.google.com/rss/search?q=Kenya+OR+Nairobi+OR+Kitengela&hl=en-KE&gl=KE&ceid=KE:en"},
    {"source": "Kenya Markets & Economy", "scope": "LOCAL", "url": "https://news.google.com/rss/search?q=(Kenya+OR+Nairobi)+AND+(CBK+OR+%22Nairobi+Securities+Exchange%22+OR+inflation+OR+shilling+OR+fuel)&hl=en-KE&gl=KE&ceid=KE:en"}
]

# 2. Continuous War, Geopolitical Flashpoint & Macro-Economic Threat Feeds
CONFLICT_AND_MACRO_FEEDS = [
    {
        "source": "Defense One",
        "domain": "WAR-KINETIC",
        "theater": "GLOBAL",
        "url": "https://www.defenseone.com/rss/all/"
    },
    {
        "source": "War on the Rocks",
        "domain": "WAR-KINETIC",
        "theater": "GLOBAL",
        "url": "https://warontherocks.com/feed/"
    },
    {
        "source": "Middle East & Red Sea Corridor",
        "domain": "WAR-KINETIC",
        "theater": "RED-SEA-MIDEAST",
        "url": "https://news.google.com/rss/search?q=(%22Red+Sea%22+OR+%22Hormuz%22+OR+Israel+OR+Iran+OR+Gaza+OR+Lebanon+OR+Houthi)+AND+(strike+OR+missile+OR+blockade+OR+shipping+OR+war)&hl=en-US&gl=US&ceid=US:en"
    },
    {
        "source": "Horn of Africa & Regional Security",
        "domain": "WAR-KINETIC",
        "theater": "EAST-AFRICA",
        "url": "https://news.google.com/rss/search?q=(Sudan+OR+Somalia+OR+Ethiopia+OR+DRC+OR+%22East+Africa%22)+AND+(conflict+OR+military+OR+insurgency+OR+border+OR+security)&hl=en-KE&gl=KE&ceid=KE:en"
    },
    {
        "source": "Eastern Europe & NATO Flank",
        "domain": "WAR-KINETIC",
        "theater": "EASTERN-EUROPE",
        "url": "https://news.google.com/rss/search?q=(Ukraine+OR+Russia+OR+NATO+OR+Black+Sea)+AND+(frontline+OR+drone+OR+sanctions+OR+energy+OR+offensive)&hl=en-US&gl=US&ceid=US:en"
    },
    {
        "source": "Indo-Pacific & Taiwan Strait",
        "domain": "GEOPOLITICAL",
        "theater": "INDO-PACIFIC",
        "url": "https://news.google.com/rss/search?q=(%22South+China+Sea%22+OR+Taiwan+OR+semiconductors+OR+blockade)+AND+(military+OR+sanctions+OR+tariff+OR+supply+chain)&hl=en-US&gl=US&ceid=US:en"
    },
    {
        "source": "CNBC Global Macro & Commodities",
        "domain": "MACRO-ECONOMIC",
        "theater": "GLOBAL",
        "url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664"
    },
    {
        "source": "WSJ Markets & Monetary Policy",
        "domain": "MACRO-ECONOMIC",
        "theater": "GLOBAL",
        "url": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml"
    }
]

# Cybersecurity Intelligence Feeds
CYBER_RSS_FEEDS = [
    {"source": "The Hacker News", "category": "THREAT-INTEL", "url": "https://feeds.feedburner.com/TheHackersNews"},
    {"source": "BleepingComputer", "category": "THREAT-INTEL", "url": "https://www.bleepingcomputer.com/feed/"},
    {"source": "Kenya Cyber Monitor", "category": "LOCAL-CYBER", "url": "https://news.google.com/rss/search?q=(Kenya+OR+Nairobi)+AND+(cybersecurity+OR+cyberattack+OR+ransomware+OR+%22data+breach%22+OR+KE-CIRT)&hl=en-KE&gl=KE&ceid=KE:en"}
]

CISA_KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
WMO_CODES = {0: "Clear", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast", 45: "Fog", 51: "Light Drizzle", 61: "Light Rain", 63: "Moderate Rain", 65: "Heavy Rain", 80: "Rain Showers", 95: "Thunderstorm"}

force_sync_event = asyncio.Event()
conversation_history = []
BOOT_TIME = time.time()


# =====================================================================
# --- PERSISTENT MEMORY & DATABASE OPERATIONS ---
# =====================================================================
async def get_operator_memory(client: httpx.AsyncClient) -> str:
    """Retrieve standing orders, tech stack, and asset exposure directives."""
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        return (
            "Base location: Kitengela/Nairobi. Currency: KES. "
            "Exposure: Nairobi Securities Exchange (SCOM, COOP, ABSA), Cloud APIs, USD Royalties. "
            "Stack: Python, Next.js, PostgreSQL, Linux."
        )
    try:
        resp = await client.get(f"{SUPABASE_URL}/rest/v1/bot_memory?select=memory_key,directive", headers=SUPABASE_HEADERS, timeout=10)
        if resp.status_code == 200 and resp.json():
            return "\n".join([f"- [{r['memory_key']}]: {r['directive']}" for r in resp.json()])
    except Exception as e:
        logger.error(f"[Memory Read Error]: {e}")
    return "Base: Kitengela/Nairobi. Currency: KES. Monitor kinetic conflicts, fuel/import shipping, and tech stack."


async def tool_query_telemetry(client: httpx.AsyncClient, table: str, limit: int = 5) -> str:
    """Query live Supabase tables."""
    valid_tables = {
        "weather_reports": "updated_at",
        "news_articles": "created_at",
        "cyber_alerts": "created_at",
        "conflict_and_macro_intel": "created_at",
        "tactical_briefings": "created_at",
        "personal_tasks": "created_at",
        "personal_ledger": "created_at",
        "idea_vault": "created_at",
        "osint_dossiers": "created_at",
        "lan_devices": "last_seen"
    }
    if table not in valid_tables:
        return f"Invalid telemetry stream. Valid: {list(valid_tables.keys())}"
    try:
        order_col = valid_tables[table]
        url = f"{SUPABASE_URL}/rest/v1/{table}?select=*&order={order_col}.desc&limit={min(limit, 15)}"
        resp = await client.get(url, headers=SUPABASE_HEADERS, timeout=12)
        return json.dumps(resp.json())
    except Exception as e:
        return f"Query error on {table}: {e}"


async def tool_save_memory(client: httpx.AsyncClient, memory_key: str, directive: str) -> str:
    try:
        headers = {**SUPABASE_HEADERS, "Prefer": "resolution=merge-duplicates"}
        payload = {"memory_key": memory_key.lower().replace(" ", "_"), "directive": directive, "updated_at": datetime.now(timezone.utc).isoformat()}
        resp = await client.post(f"{SUPABASE_URL}/rest/v1/bot_memory", headers=headers, json=payload, timeout=10)
        return f"Directive '{memory_key}' committed to persistent memory." if resp.status_code in (200, 201) else "Memory write failed."
    except Exception as e:
        return f"Memory save error: {e}"


async def tool_live_web_probe(client: httpx.AsyncClient, url: str) -> str:
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; TacticalConstruct/4.0)"}
        resp = await client.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        text = " ".join(soup.stripped_strings)
        return text[:3500]
    except Exception as e:
        return f"Web probe failed: {e}"


async def tool_manage_tasks(
    client: httpx.AsyncClient, action: str, title: str = "", priority: str = "NORMAL", due_at: str = None, task_id: int = None
) -> str:
    try:
        if action == "add":
            payload = {"title": title, "priority": priority.upper(), "due_at": due_at, "completed": False}
            resp = await client.post(f"{SUPABASE_URL}/rest/v1/personal_tasks", headers=SUPABASE_HEADERS, json=payload, timeout=10)
            return f"Task logged: '{title}' (Priority: {priority}, Due: {due_at or 'Unscheduled'})." if resp.status_code == 201 else "Task insert failed."

        elif action == "complete" and task_id:
            url = f"{SUPABASE_URL}/rest/v1/personal_tasks?id=eq.{task_id}"
            resp = await client.patch(url, headers=SUPABASE_HEADERS, json={"completed": True}, timeout=10)
            return f"Task {task_id} marked complete." if resp.status_code in (200, 204) else "Update failed."

        elif action == "list":
            url = f"{SUPABASE_URL}/rest/v1/personal_tasks?completed=eq.false&select=*&order=created_at.desc&limit=10"
            resp = await client.get(url, headers=SUPABASE_HEADERS, timeout=10)
            return json.dumps(resp.json())
    except Exception as e:
        return f"Task error: {e}"
    return "Invalid task action."


async def tool_log_ledger_entry(
    client: httpx.AsyncClient, counterparty: str, amount: float, category: str, currency: str = "KES", ref_code: str = "", raw_summary: str = ""
) -> str:
    try:
        payload = {
            "ref_code": ref_code.upper() if ref_code else None,
            "amount": amount,
            "currency": currency.upper(),
            "counterparty": counterparty,
            "category": category.upper(),
            "raw_summary": raw_summary
        }
        resp = await client.post(f"{SUPABASE_URL}/rest/v1/personal_ledger", headers=SUPABASE_HEADERS, json=payload, timeout=10)
        return f"Ledger recorded: {currency} {amount} | {counterparty} | Ref: {ref_code or 'N/A'}" if resp.status_code == 201 else "Ledger write failed."
    except Exception as e:
        return f"Ledger error: {e}"


async def tool_log_vault_note(client: httpx.AsyncClient, tag: str, content: str) -> str:
    try:
        payload = {"tag": tag.upper(), "content": content}
        resp = await client.post(f"{SUPABASE_URL}/rest/v1/idea_vault", headers=SUPABASE_HEADERS, json=payload, timeout=10)
        return f"Logged to Idea Vault under [{tag.upper()}]." if resp.status_code == 201 else "Vault write failed."
    except Exception as e:
        return f"Vault error: {e}"


# =====================================================================
# --- MULTI-VECTOR OSINT & BEHAVIORAL PSYCHOLOGY ENGINE ---
# =====================================================================
async def osint_ddg_dork(client: httpx.AsyncClient, query: str, max_results: int = 6) -> list[dict]:
    """Executes keyless DuckDuckGo HTML search for surface web and social media dorks."""
    url = "https://html.duckduckgo.com/html/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    results = []
    try:
        resp = await client.post(url, data={"q": query}, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.select(".result__body")[:max_results]:
            title_el = a.select_one(".result__a")
            snippet_el = a.select_one(".result__snippet")
            if title_el:
                results.append({
                    "title": title_el.get_text(strip=True),
                    "link": title_el.get("href", ""),
                    "snippet": snippet_el.get_text(strip=True) if snippet_el else ""
                })
    except Exception as e:
        logger.error(f"[DDG OSINT Error]: {e}")
    return results


async def osint_social_and_public_records(client: httpx.AsyncClient, target: str, entity_type: str) -> dict:
    """
    Sweeps public APIs, social media dorks, forums, academic databases,
    Wayback archives, and geospatial registries in parallel.
    """
    headers = {"User-Agent": "Mozilla/5.0 (compatible; TacticalOSINT/4.0)"}
    encoded = urllib.parse.quote(target)
    clean_handle = target.replace(" ", "").lower()

    # 1. Define concurrent search vectors
    general_web_task = osint_ddg_dork(client, f'"{target}"', 6)
    social_dork_task = osint_ddg_dork(
        client,
        f'"{target}" (site:linkedin.com OR site:x.com OR site:instagram.com OR site:facebook.com OR site:tiktok.com OR site:youtube.com)',
        8
    )
    public_records_task = osint_ddg_dork(
        client,
        f'"{target}" (filetype:pdf OR site:opencorporates.com OR site:ke OR "registry" OR "court" OR "director" OR "filing")',
        6
    )

    # 2. Reddit Social Sentiment & Crowd Psychology
    async def fetch_reddit():
        try:
            r = await client.get(f"https://www.reddit.com/search.json?q={encoded}&limit=5&sort=relevance", headers=headers, timeout=12)
            if r.status_code == 200:
                posts = r.json().get("data", {}).get("children", [])
                return [{"title": p["data"]["title"], "subreddit": p["data"]["subreddit"], "url": f"https://reddit.com{p['data']['permalink']}"} for p in posts]
        except Exception:
            pass
        return []

    # 3. Wikipedia / Encyclopedic Baseline
    async def fetch_wiki():
        try:
            r = await client.get(f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={encoded}&utf8=&format=json", headers=headers, timeout=10)
            if r.status_code == 200:
                items = r.json().get("query", {}).get("search", [])[:3]
                return [{"title": i["title"], "snippet": BeautifulSoup(i["snippet"], "html.parser").get_text()} for i in items]
        except Exception:
            pass
        return []

    # 4. HackerNews / Tech & Founder Footprint
    async def fetch_hn():
        try:
            r = await client.get(f"https://hn.algolia.com/api/v1/search?query={encoded}&hitsPerPage=4", timeout=10)
            if r.status_code == 200:
                return [{"title": h.get("title") or h.get("comment_text", "")[:120], "url": h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}"} for h in r.json().get("hits", [])]
        except Exception:
            pass
        return []

    # 5. Geospatial & Place Coordinates (OpenStreetMap Nominatim)
    async def fetch_geo():
        if entity_type != "PLACE":
            return []
        try:
            r = await client.get(f"https://nominatim.openstreetmap.org/search?q={encoded}&format=json&limit=2", headers=headers, timeout=10)
            if r.status_code == 200:
                return [{"display_name": loc["display_name"], "lat": loc["lat"], "lon": loc["lon"], "type": loc.get("type")} for loc in r.json()]
        except Exception:
            pass
        return []

    # 6. Direct Username / Handle Probe (GitHub & GitLab)
    async def probe_handles():
        if entity_type != "PERSON" or " " in target.strip():
            return []
        found = []
        for platform, url in [
            ("GitHub", f"https://api.github.com/users/{clean_handle}"),
            ("GitLab", f"https://gitlab.com/api/v4/users?username={clean_handle}")
        ]:
            try:
                r = await client.get(url, headers=headers, timeout=8)
                if r.status_code == 200 and r.json():
                    found.append({"platform": platform, "url": url, "data": str(r.json())[:300]})
            except Exception:
                pass
        return found

    web, social, records, reddit, wiki, hn, geo, handles = await asyncio.gather(
        general_web_task, social_dork_task, public_records_task,
        fetch_reddit(), fetch_wiki(), fetch_hn(), fetch_geo(), probe_handles()
    )

    return {
        "surface_web": web,
        "social_media_profiles": social,
        "public_records_and_filings": records,
        "reddit_crowd_pulse": reddit,
        "wikipedia_context": wiki,
        "tech_hn_mentions": hn,
        "geospatial_data": geo,
        "direct_handle_hits": handles
    }


# --- CORTANA / J.A.R.V.I.S. BEHAVIORAL PSYCHOLOGY & DOSSIER SYNTHESIZER ---
async def tool_deep_osint_investigate(
    client: httpx.AsyncClient, target_query: str, entity_type: str = "PERSON", specific_angle: str = ""
) -> str:
    """
    Executes full-spectrum OSINT across web, social media, forums, and public records,
    then generates a Behavioral & Strategic Dossier stored in Supabase.
    """
    raw_osint = await osint_social_and_public_records(client, target_query, entity_type.upper())
    memory_context = await get_operator_memory(client)

    prompt = f"""OPERATOR MEMORY & DOCTRINE:
{memory_context}

TARGET ENTITY: {target_query} (Category: {entity_type})
OPERATOR ANGLE / QUESTION: {specific_angle or 'Full 360-degree intelligence & behavioral profile'}

RAW MULTI-SOURCE OSINT TELEMETRY:
{json.dumps(raw_osint)[:12000]}

Synthesize an elite Cortana/J.A.R.V.I.S. Intelligence & Behavioral Dossier. Output strictly valid JSON with these exact keys:
{{
  "footprint_summary": "Verified facts, background, public history, digital footprint, and cross-referenced presence across web, social networks, and public records.",
  "behavioral_profile": "Deep psychological & human-dynamics analysis: core incentives, probable cognitive biases, status/power drivers, communication style, blind spots, and crowd/social behavior patterns.",
  "strategic_approchement": "Actionable playbook for the operator: how to negotiate with, persuade, defend against, or capitalize on this person, group, place, or idea.",
  "discovered_links": ["List of top 5 most relevant URLs or social profiles found in the telemetry"]
}}"""

    if not GROQ_API_KEY:
        links = []
        for src_list in [raw_osint.get("surface_web", []), raw_osint.get("social_media_profiles", [])]:
            for item in src_list:
                l = item.get("link") or item.get("url")
                if l and l not in links:
                    links.append(l)

        record = {
            "target_query": target_query,
            "entity_type": entity_type.upper(),
            "footprint_summary": f"Keyless multi-vector OSINT scan completed for '{target_query}' across web, social footprints, and registries.",
            "social_and_public_links": links[:5],
            "behavioral_profile": "Revealed behavior indicates strong status and public presence incentives. Evaluate stated claims against digital paper trails.",
            "strategic_approchement": "Anchor on objective verification, maintain high-status neutrality, and identify leverage in asymmetric incentives.",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        if SUPABASE_URL and SUPABASE_SERVICE_KEY:
            await client.post(f"{SUPABASE_URL}/rest/v1/osint_dossiers", headers=SUPABASE_HEADERS, json=record)
        return (
            f"OSINT & BEHAVIORAL DOSSIER // {target_query.upper()} [{entity_type.upper()}]\n\n"
            f"1. DIGITAL & PUBLIC RECORD FOOTPRINT:\n{record['footprint_summary']}\n\n"
            f"2. HUMAN BEHAVIOR & PSYCHOLOGICAL PROFILE:\n{record['behavioral_profile']}\n\n"
            f"3. STRATEGIC PLAYBOOK (INTERACTION / LEVERAGE):\n{record['strategic_approchement']}\n\n"
            f"4. KEY SOURCES:\n" + "\n".join([f"• {u}" for u in record["social_and_public_links"][:5]])
        )

    try:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": LLM_MODEL,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": SYSTEM_PERSONA + " You are also a master behavioral psychologist, profiler, and OSINT investigator. Output strictly valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }

        resp = await client.post(GROQ_CHAT_URL, headers=headers, json=payload, timeout=45)
        resp.raise_for_status()
        parsed = json.loads(resp.json()["choices"][0]["message"]["content"])

        record = {
            "target_query": target_query,
            "entity_type": entity_type.upper(),
            "footprint_summary": parsed.get("footprint_summary", ""),
            "social_and_public_links": parsed.get("discovered_links", []),
            "behavioral_profile": parsed.get("behavioral_profile", ""),
            "strategic_approchement": parsed.get("strategic_approchement", ""),
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        if SUPABASE_URL and SUPABASE_SERVICE_KEY:
            await client.post(f"{SUPABASE_URL}/rest/v1/osint_dossiers", headers=SUPABASE_HEADERS, json=record)

        return (
            f"OSINT & BEHAVIORAL DOSSIER // {target_query.upper()} [{entity_type.upper()}]\n\n"
            f"1. DIGITAL & PUBLIC RECORD FOOTPRINT:\n{record['footprint_summary']}\n\n"
            f"2. HUMAN BEHAVIOR & PSYCHOLOGICAL PROFILE:\n{record['behavioral_profile']}\n\n"
            f"3. STRATEGIC PLAYBOOK (INTERACTION / LEVERAGE):\n{record['strategic_approchement']}\n\n"
            f"4. KEY SOURCES:\n" + "\n".join([f"• {u}" for u in record["social_and_public_links"][:5]])
        )
    except Exception as e:
        logger.error(f"[OSINT Synthesis Error]: {e}")
        return f"OSINT reconnaissance completed with raw telemetry, but behavioral synthesis encountered: {e}"


# =====================================================================
# --- NEURAL VOICE SYNTHESIS (CORTANA HALO VOICE ENGINE) ---
# =====================================================================
def play_local_audio_file(filepath: str):
    """Plays audio on host device via available OS media engines without blocking asyncio loop."""
    try:
        if shutil.which("mpv"):
            subprocess.Popen(["mpv", "--no-terminal", "--really-quiet", filepath])
        elif shutil.which("ffplay"):
            subprocess.Popen(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", filepath])
        elif platform.system().lower() == "windows":
            escaped_path = filepath.replace("\\", "\\\\").replace("'", "''")
            ps_cmd = f"$p = New-Object -ComObject WMPlayer.OCX; $p.openPlayer('{escaped_path}'); Start-Sleep -Milliseconds 800"
            subprocess.Popen(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd])
        elif shutil.which("termux-media-player"):
            subprocess.Popen(["termux-media-player", "play", filepath])
    except Exception as e:
        logger.warning(f"Local audio playback skipped: {e}")


async def synthesize_and_send_voice(client: httpx.AsyncClient, text: str):
    """
    Synthesizes speech using Microsoft Neural TTS (edge-tts) in Cortana's Halo voice (en-US-AriaNeural),
    pushes a playable voice note to Telegram (sendVoice), and optionally plays it on local room speakers.
    """
    if not text or not text.strip():
        return

    clean_speech = text
    clean_speech = re.sub(r'```.*?```', '', clean_speech, flags=re.DOTALL)
    clean_speech = re.sub(r'`.*?`', '', clean_speech)
    clean_speech = re.sub(r'https?://\S+', '', clean_speech)
    clean_speech = re.sub(r'[*#_~>•\[\]()]', '', clean_speech)
    clean_speech = " ".join(clean_speech.split())[:1200]

    if not clean_speech:
        return

    try:
        voice_id = CONSTRUCT_VOICE
        communicate = edge_tts.Communicate(text=clean_speech, voice=voice_id, rate="+4%", pitch="-1Hz")

        audio_buffer = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_buffer.write(chunk["data"])

        audio_bytes = audio_buffer.getvalue()
        if not audio_bytes:
            return

        # 1. Send as Telegram Voice Message
        if TELEGRAM_TOKEN and AUTHORIZED_CHAT_ID:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVoice"
            files = {"voice": ("cortana_speech.mp3", audio_bytes, "audio/mpeg")}
            data = {"chat_id": str(AUTHORIZED_CHAT_ID)}
            try:
                await client.post(url, data=data, files=files, timeout=25)
            except Exception as e:
                logger.error(f"[Telegram Voice Send Error]: {e}")

        # 2. Local Host Speaker Playback (Laptop / Desktop / Termux)
        if ENABLE_LOCAL_SPEAKER or "--speak" in sys.argv:
            try:
                temp_audio = Path(__file__).resolve().parent / "temp_speech.mp3"
                with open(temp_audio, "wb") as f:
                    f.write(audio_bytes)
                play_local_audio_file(str(temp_audio))
            except Exception as e:
                logger.error(f"[Local Speaker Playback Error]: {e}")

    except Exception as e:
        logger.error(f"[Edge TTS Synthesis Error]: {e}")


# =====================================================================
# --- LOCAL WI-FI & LAN DEVICE MESH DISCOVERY ---
# =====================================================================
async def tool_scan_wifi_network(client: httpx.AsyncClient) -> str:
    """
    Scans the local Wi-Fi ARP cache to discover active Smart TVs, laptops, phones,
    and smart home gadgets, syncing their online/offline status into Supabase lan_devices.
    """
    discovered = []
    try:
        cmd = ["arp", "-a"] if platform.system().lower() == "windows" else ["ip", "neigh"]
        output = subprocess.check_output(cmd, timeout=6).decode("utf-8", errors="ignore")

        for line in output.splitlines():
            parts = line.split()
            if not parts:
                continue
            ip = ""
            mac = "UNKNOWN"
            if platform.system().lower() == "windows":
                for p in parts:
                    if "." in p and p.count(".") == 3:
                        ip = p
                    elif ("-" in p or ":" in p) and len(p) == 17:
                        mac = p.replace("-", ":").upper()
            else:
                ip = parts[0] if "." in parts[0] else (parts[1].strip("()") if len(parts) > 1 else "")
                mac = next((p for p in parts if (":" in p or "-" in p) and len(p) == 17), "UNKNOWN").replace("-", ":").upper()

            if ip and (ip.startswith("192.168.") or ip.startswith("10.") or ip.startswith("172.")):
                if not ip.endswith(".255") and ip != "255.255.255.255":
                    discovered.append({"ip": ip, "mac": mac})
    except Exception as e:
        logger.error(f"[ARP Scan Error]: {e}")
        return f"Local LAN scan error: {e}"

    # Sync discovered nodes against Supabase lan_devices table
    if SUPABASE_URL and SUPABASE_SERVICE_KEY:
        try:
            resp = await client.get(f"{SUPABASE_URL}/rest/v1/lan_devices?select=*", headers=SUPABASE_HEADERS, timeout=10)
            if resp.status_code == 200:
                registered = resp.json()
                active_ips = {d["ip"] for d in discovered}
                for dev in registered:
                    new_status = "ONLINE" if dev["ip_address"] in active_ips else "OFFLINE"
                    await client.patch(
                        f"{SUPABASE_URL}/rest/v1/lan_devices?id=eq.{dev['id']}",
                        headers=SUPABASE_HEADERS,
                        json={"status": new_status, "last_seen": datetime.now(timezone.utc).isoformat()}
                    )
        except Exception as e:
            logger.error(f"[LAN Supabase Sync Error]: {e}")

    return json.dumps({
        "status": "SCAN_COMPLETE",
        "active_devices_found": len(discovered),
        "nodes": discovered[:20]
    })


# =====================================================================
# --- SMART TV, LAPTOP & GADGET CONTROLLER ---
# =====================================================================
async def tool_control_lan_device(
    client: httpx.AsyncClient,
    device_name: str,
    command: str,
    parameter: str = "",
    ip_address: str = "",
    mac_address: str = "",
    device_type: str = "ANDROID-TV"
) -> str:
    """
    Executes hardware & network control over Smart TVs, Laptops, and Wi-Fi gadgets:
    - 'register': Saves device to Supabase lan_devices.
    - 'wake': Transmits Wake-on-LAN magic packet.
    - 'tv_power', 'tv_mute', 'tv_vol_up', 'tv_vol_down', 'tv_play_pause', 'tv_home': ADB / Roku TV remote commands.
    - 'open_url': Casts or launches YouTube, streaming, or web URL directly on the Smart TV or laptop screen.
    """
    if command != "register" and SUPABASE_URL and SUPABASE_SERVICE_KEY and not ip_address:
        try:
            encoded_name = urllib.parse.quote(device_name)
            q_url = f"{SUPABASE_URL}/rest/v1/lan_devices?device_name=ilike.*{encoded_name}*&select=*"
            res = await client.get(q_url, headers=SUPABASE_HEADERS, timeout=8)
            if res.status_code == 200 and res.json():
                dev = res.json()[0]
                ip_address = dev.get("ip_address", "")
                mac_address = dev.get("mac_address", "") or mac_address
                device_type = dev.get("device_type", device_type)
        except Exception as e:
            logger.error(f"[Device Lookup Error]: {e}")

    if command == "register":
        if not ip_address:
            return "Registration requires a valid local IP address (e.g. 192.168.1.105)."
        payload = {
            "device_name": device_name,
            "device_type": device_type.upper(),
            "ip_address": ip_address,
            "mac_address": mac_address.upper().replace("-", ":") if mac_address else None,
            "status": "ONLINE",
            "last_seen": datetime.now(timezone.utc).isoformat()
        }
        if SUPABASE_URL and SUPABASE_SERVICE_KEY:
            headers = {**SUPABASE_HEADERS, "Prefer": "resolution=merge-duplicates"}
            r = await client.post(f"{SUPABASE_URL}/rest/v1/lan_devices", headers=headers, json=payload, timeout=10)
            if r.status_code in (200, 201):
                return f"Successfully registered '{device_name}' [{device_type.upper()}] at IP {ip_address} in Wi-Fi device mesh."
        return f"Registered '{device_name}' locally at {ip_address}."

    if command == "wake":
        if not mac_address:
            return f"Wake-on-LAN requires a MAC address for '{device_name}'. Register device with MAC first."
        try:
            clean_mac = mac_address.replace("-", ":").upper()
            send_magic_packet(clean_mac)
            return f"Wake-on-LAN magic packet transmitted to '{device_name}' ({clean_mac}). Powering on."
        except Exception as e:
            return f"Wake-on-LAN packet transmission error: {e}"

    if device_type in ("ANDROID-TV", "GOOGLE-TV", "FIRE-TV"):
        adb_map = {
            "tv_power": "KEYCODE_POWER",
            "tv_mute": "KEYCODE_VOLUME_MUTE",
            "tv_vol_up": "KEYCODE_VOLUME_UP",
            "tv_vol_down": "KEYCODE_VOLUME_DOWN",
            "tv_play_pause": "KEYCODE_MEDIA_PLAY_PAUSE",
            "tv_home": "KEYCODE_HOME"
        }
        target_endpoint = f"{ip_address}:5555" if ":" not in ip_address else ip_address
        try:
            subprocess.run(["adb", "connect", target_endpoint], timeout=4, capture_output=True)
            if command in adb_map:
                keyevent = adb_map[command]
                subprocess.run(["adb", "-s", target_endpoint, "shell", "input", "keyevent", keyevent], timeout=5, capture_output=True)
                return f"Transmitted {command} ({keyevent}) to Smart TV '{device_name}' at {target_endpoint}."
            elif command == "open_url" and parameter:
                subprocess.run([
                    "adb", "-s", target_endpoint, "shell", "am", "start",
                    "-a", "android.intent.action.VIEW", "-d", parameter
                ], timeout=5, capture_output=True)
                return f"Launched URL '{parameter}' on Smart TV '{device_name}' display."
        except Exception as e:
            return f"ADB Smart TV command fault: {e}. Ensure Wireless Debugging is enabled on TV."

    if device_type == "ROKU-TV":
        roku_map = {
            "tv_power": "Power", "tv_mute": "VolumeMute",
            "tv_vol_up": "VolumeUp", "tv_vol_down": "VolumeDown",
            "tv_play_pause": "Play", "tv_home": "Home"
        }
        key = roku_map.get(command, "Home")
        try:
            await client.post(f"http://{ip_address}:8060/keypress/{key}", timeout=5)
            return f"Roku keypress command '{key}' sent to '{device_name}'."
        except Exception as e:
            return f"Roku command failed: {e}"

    if device_type == "LAPTOP-PC":
        if command == "open_url" and parameter:
            import webbrowser
            webbrowser.open(parameter)
            return f"Opened '{parameter}' on host laptop display."

    return f"LAN command '{command}' dispatched to '{device_name}' ({ip_address})."


# --- AMBIENT ROOM MICROPHONE WAKE-WORD LISTENER ('CORTANA' / 'JARVIS') ---
async def ambient_wakeword_listener(client: httpx.AsyncClient):
    """
    Continuously listens on host room microphone for wake-words 'Cortana' or 'Jarvis'.
    When heard, captures speech, synthesizes response, and speaks aloud in Cortana's voice.
    """
    logger.info("Initializing Ambient Microphone Wake-Word Engine...")
    try:
        import speech_recognition as sr
    except ImportError:
        logger.info("[WakeWord Listener]: 'SpeechRecognition' library not installed. In-room voice active via Telegram & Web HUD mic.")
        return

    try:
        r = sr.Recognizer()
        r.energy_threshold = 400
        r.dynamic_energy_threshold = True
        mic = sr.Microphone()
    except Exception as e:
        logger.info(f"[WakeWord Listener]: Microphone hardware unavailable ({e}). Standing by on Telegram & Web HUD.")
        return

    logger.info("🎙️ Ambient Wake-Word Listener ACTIVE. Say 'Cortana' or 'Jarvis'...")
    while True:
        try:
            with mic as source:
                r.adjust_for_ambient_noise(source, duration=0.6)
                audio = r.listen(source, timeout=10, phrase_time_limit=8)

            wav_data = audio.get_wav_data()
            if GROQ_API_KEY:
                files = {"file": ("wake_audio.wav", wav_data, "audio/wav")}
                data = {"model": "whisper-large-v3-turbo"}
                headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
                resp = await client.post(GROQ_AUDIO_URL, headers=headers, data=data, files=files, timeout=10)
                if resp.status_code == 200:
                    text = resp.json().get("text", "").strip()
                    lower_t = text.lower()
                    if any(w in lower_t for w in ["cortana", "jarvis"]):
                        logger.info(f"🎙️ Wake-Word Triggered! Speech: '{text}'")
                        reply = await run_agent_turn(client, text)
                        print(f"\n[CORTANA VOICE REPLY]: {reply}\n")
                        await synthesize_and_send_voice(client, reply)
        except asyncio.CancelledError:
            break
        except Exception:
            await asyncio.sleep(1)


# =====================================================================
# --- LLM TOOL DEFINITIONS ---
# =====================================================================
AGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "query_telemetry",
            "description": "Query live database for conflict_and_macro_intel, osint_dossiers, weather_reports, news_articles, cyber_alerts, tactical_briefings, personal_tasks, personal_ledger, or idea_vault.",
            "parameters": {
                "type": "object",
                "properties": {
                    "table": {
                        "type": "string",
                        "enum": ["conflict_and_macro_intel", "osint_dossiers", "weather_reports", "news_articles", "cyber_alerts", "tactical_briefings", "personal_tasks", "personal_ledger", "idea_vault"]
                    },
                    "limit": {"type": "integer", "description": "Number of rows to retrieve (1 to 15)"}
                },
                "required": ["table"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_operator_directive",
            "description": "Save a permanent fact, tech stack detail, or economic standing order into persistent memory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "memory_key": {"type": "string", "description": "Short identifier (e.g. 'asset_profile' or 'priority_watch')"},
                    "directive": {"type": "string", "description": "The fact or rule to remember permanently"}
                },
                "required": ["memory_key", "directive"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "live_web_probe",
            "description": "Fetch and inspect raw text from any URL on the internet.",
            "parameters": {
                "type": "object",
                "properties": {"url": {"type": "string", "description": "Full https:// URL to probe"}},
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sensor_sweep",
            "description": "Force an immediate synchronization of all conflict, macro, weather, news, and cyber sensors.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "manage_tasks",
            "description": "Add, list, or complete personal tasks, calendar events, and reminders.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["add", "list", "complete"]},
                    "title": {"type": "string", "description": "Task description"},
                    "priority": {"type": "string", "enum": ["CRITICAL", "HIGH", "NORMAL"]},
                    "due_at": {"type": "string", "description": "ISO-8601 UTC timestamp or null"},
                    "task_id": {"type": "integer", "description": "Task ID when completing a task"}
                },
                "required": ["action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "log_ledger_entry",
            "description": "Extract and save financial transactions, M-Pesa statements, receipts, or ticket confirmations into the personal ledger.",
            "parameters": {
                "type": "object",
                "properties": {
                    "counterparty": {"type": "string", "description": "Merchant, recipient, or sender name"},
                    "amount": {"type": "number", "description": "Numeric transaction value"},
                    "currency": {"type": "string", "description": "ISO currency code, default KES"},
                    "category": {"type": "string", "enum": ["EXPENSE", "INCOME", "RECEIPT", "TICKET"]},
                    "ref_code": {"type": "string", "description": "Transaction ID or confirmation code"},
                    "raw_summary": {"type": "string", "description": "Context or item breakdown"}
                },
                "required": ["counterparty", "amount", "category"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "log_vault_note",
            "description": "Save spoken thoughts, project architectures, song lyrics, or quick notes into the Idea Vault.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tag": {"type": "string", "enum": ["PROJECT", "CODE", "MUSIC", "GENERAL"]},
                    "content": {"type": "string", "description": "The structured note or idea"}
                },
                "required": ["tag", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "deep_osint_investigate",
            "description": "Search all available internet databases, social media sites (LinkedIn, X, Instagram, Reddit, GitHub), public records/filings, and encyclopedic archives for a person, organization, place, or idea/topic, and generate a behavioral psychology & strategic profile.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_query": {"type": "string", "description": "Name of the person, username, company, location, or concept/idea to investigate"},
                    "entity_type": {"type": "string", "enum": ["PERSON", "ORGANIZATION", "PLACE", "TOPIC-IDEA"]},
                    "specific_angle": {"type": "string", "description": "Specific behavioral, financial, or strategic question to answer"}
                },
                "required": ["target_query", "entity_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "scan_wifi_network",
            "description": "Scan the local Wi-Fi network (LAN) to discover active IPs, MAC addresses, Smart TVs, laptops, and IoT gadgets.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "control_lan_device",
            "description": "Register or control a Smart TV, laptop, or gadget on the Wi-Fi network (power, wake-on-lan, mute, volume, play/pause, or launch a YouTube/web URL on the TV).",
            "parameters": {
                "type": "object",
                "properties": {
                    "device_name": {"type": "string", "description": "Name of device, e.g. 'Living Room TV' or 'Laptop'"},
                    "command": {
                        "type": "string",
                        "enum": ["register", "wake", "tv_power", "tv_mute", "tv_vol_up", "tv_vol_down", "tv_play_pause", "tv_home", "open_url"]
                    },
                    "parameter": {"type": "string", "description": "URL to open on TV/Laptop when command is 'open_url'"},
                    "ip_address": {"type": "string", "description": "Local IP address (required when registering)"},
                    "mac_address": {"type": "string", "description": "MAC address (optional, for Wake-on-LAN)"},
                    "device_type": {"type": "string", "enum": ["ANDROID-TV", "ROKU-TV", "LG-TV", "SAMSUNG-TV", "LAPTOP-PC", "GENERIC"]}
                },
                "required": ["device_name", "command"]
            }
        }
    }
]


# =====================================================================
# --- AGENTIC REASONING ENGINE ---
# =====================================================================
async def run_agent_turn(client: httpx.AsyncClient, user_input: str) -> str:
    global conversation_history

    if not GROQ_API_KEY:
        logger.warning("GROQ_API_KEY not configured. Running baseline tactical handler.")
        return f"Directive received: '{user_input}'. Configure GROQ_API_KEY in .env for full cognitive reasoning."

    memory_context = await get_operator_memory(client)
    system_prompt = (
        f"{SYSTEM_PERSONA}\n\n"
        f"OPERATOR CONTEXT & PERSISTENT MEMORY:\n{memory_context}\n\n"
        f"Current UTC Timestamp: {datetime.now(timezone.utc).isoformat()}"
    )

    conversation_history.append({"role": "user", "content": user_input})
    conversation_history = conversation_history[-10:]

    messages = [{"role": "system", "content": system_prompt}] + conversation_history
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}

    for _ in range(3):
        try:
            payload = {
                "model": LLM_MODEL,
                "messages": messages,
                "tools": AGENT_TOOLS,
                "tool_choice": "auto",
                "temperature": 0.2
            }
            resp = await client.post(GROQ_CHAT_URL, headers=headers, json=payload, timeout=35)
            resp.raise_for_status()
            choice = resp.json()["choices"][0]["message"]
            messages.append(choice)

            tool_calls = choice.get("tool_calls")
            if not tool_calls:
                final_text = choice.get("content", "Operation completed.")
                conversation_history.append({"role": "assistant", "content": final_text})
                return final_text

            for tc in tool_calls:
                fn_name = tc["function"]["name"]
                args = json.loads(tc["function"].get("arguments", "{}"))
                logger.info(f"Executing tool call: {fn_name}({args})")

                if fn_name == "query_telemetry":
                    result = await tool_query_telemetry(client, args.get("table", "conflict_and_macro_intel"), args.get("limit", 5))
                elif fn_name == "save_operator_directive":
                    result = await tool_save_memory(client, args.get("memory_key", "directive"), args.get("directive", ""))
                elif fn_name == "live_web_probe":
                    result = await tool_live_web_probe(client, args.get("url", ""))
                elif fn_name == "trigger_sensor_sweep":
                    force_sync_event.set()
                    result = "Telemetry synchronization initiated across conflict, macro, weather, and cyber sensors."
                elif fn_name == "manage_tasks":
                    result = await tool_manage_tasks(
                        client, args.get("action", "list"), args.get("title", ""),
                        args.get("priority", "NORMAL"), args.get("due_at"), args.get("task_id")
                    )
                elif fn_name == "log_ledger_entry":
                    result = await tool_log_ledger_entry(
                        client, args.get("counterparty", "Unknown"), float(args.get("amount", 0)),
                        args.get("category", "EXPENSE"), args.get("currency", "KES"),
                        args.get("ref_code", ""), args.get("raw_summary", "")
                    )
                elif fn_name == "log_vault_note":
                    result = await tool_log_vault_note(client, args.get("tag", "GENERAL"), args.get("content", ""))
                elif fn_name == "deep_osint_investigate":
                    result = await tool_deep_osint_investigate(
                        client,
                        args.get("target_query", ""),
                        args.get("entity_type", "PERSON"),
                        args.get("specific_angle", "")
                    )
                elif fn_name == "scan_wifi_network":
                    result = await tool_scan_wifi_network(client)
                elif fn_name == "control_lan_device":
                    result = await tool_control_lan_device(
                        client,
                        args.get("device_name", ""),
                        args.get("command", "register"),
                        args.get("parameter", ""),
                        args.get("ip_address", ""),
                        args.get("mac_address", ""),
                        args.get("device_type", "ANDROID-TV")
                    )
                else:
                    result = "Unrecognized tool invocation."

                messages.append({"role": "tool", "tool_call_id": tc["id"], "name": fn_name, "content": result})

        except Exception as e:
            logger.error(f"[Agent Loop Error]: {e}")
            return f"Operational fault encountered: {e}"

    return "Execution sequence complete."


# =====================================================================
# --- WAR & MACRO-ECONOMIC THREAT INGESTION ---
# =====================================================================
async def sync_conflict_and_macro(client: httpx.AsyncClient) -> list[dict]:
    """Ingest, classify, and deduplicate kinetic war and macroeconomic shock feeds."""
    new_intel = []
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        return new_intel

    headers = {"User-Agent": "Mozilla/5.0 (compatible; TacticalConstruct/4.0)"}
    critical_terms = ["invasion", "blockade", "strait of hormuz", "bab el-mandeb", "default", "rate hike", "embargo", "nuclear", "mobilization", "cable cut", "oil spike"]
    elevated_terms = ["sanctions", "tariff", "inflation", "strike", "missile", "drone", "insurgency", "supply chain", "shortage", "devaluation"]

    for feed in CONFLICT_AND_MACRO_FEEDS:
        try:
            resp = await client.get(feed["url"], headers=headers, timeout=20)
            root = ET.fromstring(resp.content)

            for item in root.findall(".//item")[:5]:
                headline = (item.findtext("title") or "Untitled").strip()
                link = item.findtext("link") or ""
                content_hash = hashlib.sha256(f"{headline}{link}".encode()).hexdigest()

                check = await client.get(
                    f"{SUPABASE_URL}/rest/v1/conflict_and_macro_intel?content_hash=eq.{content_hash}&select=id",
                    headers=SUPABASE_HEADERS,
                    timeout=10
                )
                if check.status_code == 200 and len(check.json()) > 0:
                    continue

                lower_h = headline.lower()
                if any(k in lower_h for k in critical_terms):
                    severity = "CRITICAL"
                elif any(k in lower_h for k in elevated_terms):
                    severity = "ELEVATED"
                else:
                    severity = "WATCH"

                record = {
                    "domain": feed["domain"],
                    "theater": feed["theater"],
                    "severity": severity,
                    "headline": headline,
                    "source": feed["source"],
                    "link": link,
                    "content_hash": content_hash,
                    "created_at": datetime.now(timezone.utc).isoformat()
                }

                insert_resp = await client.post(
                    f"{SUPABASE_URL}/rest/v1/conflict_and_macro_intel",
                    headers=SUPABASE_HEADERS,
                    json=record,
                    timeout=10
                )
                if insert_resp.status_code == 201:
                    new_intel.append(record)
                    logger.info(f"🌐 War/Macro Intel: [{severity}] {feed['theater']} - {headline[:60]}...")
        except Exception as e:
            logger.error(f"[Conflict/Macro Error - {feed['source']}]: {e}")

    return new_intel


# =====================================================================
# --- STRATEGIC 4-PILLAR SITREP SYNTHESIS ---
# =====================================================================
async def synthesize_tactical_sitrep(
    client: httpx.AsyncClient,
    weather: list[dict],
    news: list[dict],
    cyber: list[dict],
    conflict_macro: list[dict]
) -> dict:
    """Synthesize wars, macro shocks, cyber threats, and weather into Protection & Upside Protocols."""
    if not GROQ_API_KEY:
        record = {
            "threat_level": "NOMINAL",
            "sitrep": "Multi-network sensors online. Monitoring kinetic conflicts and macroeconomic stability.",
            "conflict_summary": "Red Sea, Eastern Europe, and Horn of Africa corridors under active surveillance.",
            "future_risk_forecast": "Watch fuel pricing and shipping delays into Mombasa port over next 14-30 days.",
            "defensive_protocol": "Maintain USD reserves; verify edge DNS failover; backup local repositories.",
            "asymmetric_upside": "Position in domestic cash-generative equities (SCOM, banking) and cloud resilience audits.",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        if SUPABASE_URL and SUPABASE_SERVICE_KEY:
            await client.post(f"{SUPABASE_URL}/rest/v1/tactical_briefings", headers=SUPABASE_HEADERS, json=record)
        return record

    memory_context = await get_operator_memory(client)
    telemetry_dump = json.dumps({
        "local_weather": [w for w in weather if w["scope"] == "LOCAL"],
        "global_and_local_news": news[:10],
        "cyber_alerts": cyber[:6],
        "wars_and_macro_shocks": conflict_macro[:10]
    })

    prompt = f"""OPERATOR MEMORY & ASSET PROFILE:
{memory_context}

INCOMING MULTI-NETWORK TELEMETRY:
{telemetry_dump}

Synthesize this intelligence in the voice of Cortana/J.A.R.V.I.S. Output valid JSON strictly matching this schema:
{{
  "threat_level": "NOMINAL" | "ELEVATED" | "CRITICAL",
  "sitrep": "Executive synthesis (under 90 words) cross-referencing CNN, BBC, Al Jazeera, Fox, and local Kenya feeds.",
  "conflict_summary": "Status of active kinetic wars (Red Sea/Middle East, Eastern Europe, Horn of Africa/Sudan/Somalia, Indo-Pacific) and maritime chokepoints.",
  "future_risk_forecast": "Second-order economic, cyber, or supply-chain shocks projected over the next 7-30 days (fuel/import inflation, KES/USD pressure, cloud/undersea cable risks).",
  "defensive_protocol": "3 concrete actions the operator must take immediately to protect capital, infrastructure, and local operations.",
  "asymmetric_upside": "3 concrete ways the operator can benefit (NSE equity positioning, currency/commodity hedges, or high-demand technical/software opportunities created by the crisis)."
}}"""

    try:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": LLM_MODEL,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": SYSTEM_PERSONA + " Always respond in valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }
        resp = await client.post(GROQ_CHAT_URL, headers=headers, json=payload, timeout=40)
        resp.raise_for_status()
        parsed = json.loads(resp.json()["choices"][0]["message"]["content"])

        record = {
            "threat_level": parsed.get("threat_level", "NOMINAL"),
            "sitrep": parsed.get("sitrep", ""),
            "conflict_summary": parsed.get("conflict_summary", ""),
            "future_risk_forecast": parsed.get("future_risk_forecast", ""),
            "defensive_protocol": parsed.get("defensive_protocol", ""),
            "asymmetric_upside": parsed.get("asymmetric_upside", ""),
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        if SUPABASE_URL and SUPABASE_SERVICE_KEY:
            await client.post(f"{SUPABASE_URL}/rest/v1/tactical_briefings", headers=SUPABASE_HEADERS, json=record)
        return record
    except Exception as e:
        logger.error(f"[Strategic Synthesis Error]: {e}")
        return {
            "threat_level": "ELEVATED",
            "sitrep": "Sensors active across kinetic and economic theaters. Synthesis operational fault encountered.",
            "conflict_summary": "Telemetry channels streaming.",
            "future_risk_forecast": "Monitor maritime chokepoints.",
            "defensive_protocol": "Verify critical backup power and offline repository snapshots.",
            "asymmetric_upside": "Track high-yield domestic liquidity yields.",
            "created_at": datetime.now(timezone.utc).isoformat()
        }


# =====================================================================
# --- MULTIMODAL INGESTION ---
# =====================================================================
async def transcribe_telegram_voice(client: httpx.AsyncClient, file_id: str) -> str:
    if not GROQ_API_KEY:
        return "Voice transcription requires GROQ_API_KEY."
    try:
        file_resp = await client.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile", params={"file_id": file_id}, timeout=15)
        file_path = file_resp.json()["result"]["file_path"]
        audio_bytes = (await client.get(f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}", timeout=25)).content

        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
        files = {"file": ("voice.ogg", audio_bytes, "audio/ogg")}
        data = {"model": "whisper-large-v3-turbo"}
        resp = await client.post(GROQ_AUDIO_URL, headers=headers, data=data, files=files, timeout=30)
        resp.raise_for_status()
        return resp.json().get("text", "")
    except Exception as e:
        logger.error(f"[Whisper Error]: {e}")
        return f"Voice processing error: {e}"


async def analyze_telegram_photo(client: httpx.AsyncClient, file_id: str, caption: str = "") -> str:
    if not GROQ_API_KEY:
        return "Vision OCR requires GROQ_API_KEY."
    try:
        file_resp = await client.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile", params={"file_id": file_id}, timeout=15)
        file_path = file_resp.json()["result"]["file_path"]
        img_bytes = (await client.get(f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}", timeout=25)).content
        b64_image = base64.b64encode(img_bytes).decode("utf-8")

        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        prompt = (
            "Extract all text, confirmation codes, amounts, dates, merchants, and actionable details "
            f"from this document image. Caption: {caption}"
        )
        payload = {
            "model": VISION_MODEL,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
                ]
            }],
            "temperature": 0.1
        }
        resp = await client.post(GROQ_CHAT_URL, headers=headers, json=payload, timeout=35)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"[Vision Error]: {e}")
        return f"Document analysis fault: {e}"


# =====================================================================
# --- PROACTIVE TASK DEADLINE MONITOR ---
# =====================================================================
async def check_due_tasks(client: httpx.AsyncClient):
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        return
    try:
        now_iso = datetime.now(timezone.utc).isoformat()
        url = f"{SUPABASE_URL}/rest/v1/personal_tasks?completed=eq.false&notified=eq.false&due_at=lte.{now_iso}&select=*"
        resp = await client.get(url, headers=SUPABASE_HEADERS, timeout=10)
        if resp.status_code == 200:
            for task in resp.json():
                await send_telegram(
                    client,
                    f"⏰ *DEADLINE ALERT // [{task['priority']}]*\n"
                    f"• Task ID {task['id']}: *{task['title']}*\n"
                    f"• Scheduled: {task['due_at']}"
                )
                patch_url = f"{SUPABASE_URL}/rest/v1/personal_tasks?id=eq.{task['id']}"
                await client.patch(patch_url, headers=SUPABASE_HEADERS, json={"notified": True}, timeout=10)
    except Exception as e:
        logger.error(f"[Task Monitor Error]: {e}")


# =====================================================================
# --- TELEGRAM MESSAGING ---
# =====================================================================
async def send_telegram(client: httpx.AsyncClient, text: str):
    if not TELEGRAM_TOKEN or not AUTHORIZED_CHAT_ID:
        logger.warning(f"[Mock Telegram Dispatch]:\n{text}")
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
            logger.error(f"Telegram transmission error {resp.status_code}: {resp.text}")
    except Exception as e:
        logger.error(f"[Telegram Error]: {e}")


# =====================================================================
# --- SENSORS: WEATHER, NEWS, CYBER ---
# =====================================================================
async def sync_weather(client: httpx.AsyncClient) -> list[dict]:
    results = []
    for loc in WEATHER_LOCATIONS:
        try:
            url = (
                f"https://api.open-meteo.com/v1/forecast"
                f"?latitude={loc['lat']}&longitude={loc['lon']}"
                f"&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
            )
            resp = await client.get(url, timeout=15)
            if resp.status_code == 200:
                current = resp.json().get("current", {})
                code = current.get("weather_code", 0)
                record = {
                    "city": loc["city"], "scope": loc["scope"], "temp_c": round(current.get("temperature_2m", 0.0), 1),
                    "humidity": current.get("relative_humidity_2m", 0), "wind_kmh": round(current.get("wind_speed_10m", 0.0), 1),
                    "condition": WMO_CODES.get(code, f"Code {code}"), "updated_at": datetime.now(timezone.utc).isoformat()
                }
                results.append(record)
                if SUPABASE_URL and SUPABASE_SERVICE_KEY:
                    try:
                        await client.post(f"{SUPABASE_URL}/rest/v1/weather_reports", headers={**SUPABASE_HEADERS, "Prefer": "resolution=merge-duplicates"}, json=record, timeout=10)
                    except Exception:
                        pass
        except Exception as e:
            logger.error(f"[Weather Error - {loc['city']}]: {e}")
    return results


async def sync_news(client: httpx.AsyncClient) -> list[dict]:
    new_articles = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    for feed in NEWS_FEEDS:
        try:
            resp = await client.get(feed["url"], headers=headers, timeout=20)
            if resp.status_code != 200:
                continue
            root = ET.fromstring(resp.content)
            for item in root.findall(".//item")[:5]:
                title = (item.findtext("title") or "Untitled").strip()
                link = item.findtext("link") or ""
                if not title:
                    continue
                content_hash = hashlib.sha256(f"{title}{link}".encode()).hexdigest()

                if SUPABASE_URL and SUPABASE_SERVICE_KEY:
                    try:
                        check = await client.get(f"{SUPABASE_URL}/rest/v1/news_articles?content_hash=eq.{content_hash}&select=id", headers=SUPABASE_HEADERS, timeout=10)
                        if check.status_code == 200 and len(check.json()) > 0:
                            continue
                    except Exception:
                        pass

                article = {
                    "scope": feed["scope"], "source": feed["source"], "title": title, "link": link,
                    "content_hash": content_hash, "published_at": (item.findtext("pubDate") or "")[:30],
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                new_articles.append(article)
                if SUPABASE_URL and SUPABASE_SERVICE_KEY:
                    try:
                        await client.post(f"{SUPABASE_URL}/rest/v1/news_articles", headers=SUPABASE_HEADERS, json=article, timeout=10)
                    except Exception:
                        pass
        except Exception as e:
            logger.error(f"[News Feed Error - {feed['source']}]: {e}")
    return new_articles


async def sync_cyber_alerts(client: httpx.AsyncClient) -> list[dict]:
    new_alerts = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; TacticalConstruct/4.0)"}

    # 1. CISA KEV Catalog
    try:
        resp = await client.get(CISA_KEV_URL, headers=headers, timeout=25)
        if resp.status_code == 200:
            vulns = resp.json().get("vulnerabilities", [])
            for v in reversed(vulns[-15:]):
                cve_id = v.get("cveID", "UNKNOWN")
                content_hash = hashlib.sha256(cve_id.encode()).hexdigest()

                alert = {
                    "category": "CVE-KEV", "source": "CISA KEV", "cve_id": cve_id,
                    "severity": "CRITICAL" if "Remote Code Execution" in v.get("vulnerabilityName", "") or v.get("knownRansomwareCampaignUse") == "Known" else "HIGH",
                    "title": f"{cve_id}: {v.get('vendorProject')} {v.get('product')} - {v.get('vulnerabilityName')}",
                    "summary": v.get("shortDescription", "")[:300], "link": f"https://nvd.nist.gov/vuln/detail/{cve_id}",
                    "content_hash": content_hash, "published_at": v.get("dateAdded", "") + "T00:00:00Z",
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                new_alerts.append(alert)

                if SUPABASE_URL and SUPABASE_SERVICE_KEY:
                    try:
                        check = await client.get(f"{SUPABASE_URL}/rest/v1/cyber_alerts?content_hash=eq.{content_hash}&select=id", headers=SUPABASE_HEADERS, timeout=10)
                        if check.status_code == 200 and len(check.json()) == 0:
                            await client.post(f"{SUPABASE_URL}/rest/v1/cyber_alerts", headers=SUPABASE_HEADERS, json=alert, timeout=10)
                    except Exception:
                        pass
    except Exception as e:
        logger.error(f"[CISA KEV Error]: {e}")

    # 2. Threat Intel RSS Feeds
    for feed in CYBER_RSS_FEEDS:
        try:
            resp = await client.get(feed["url"], headers=headers, timeout=20)
            if resp.status_code == 200:
                root = ET.fromstring(resp.content)
                for item in root.findall(".//item")[:5]:
                    title = (item.findtext("title") or "Untitled").strip()
                    link = item.findtext("link") or ""
                    if not title:
                        continue
                    content_hash = hashlib.sha256(f"{title}{link}".encode()).hexdigest()
                    lower_t = title.lower()
                    severity = "CRITICAL" if any(k in lower_t for k in ["zero-day", "0-day", "ransomware", "rce", "actively exploited"]) else ("HIGH" if any(k in lower_t for k in ["breach", "cve-", "malware", "exploit"]) else "ADVISORY")

                    alert = {
                        "category": feed["category"], "source": feed["source"], "cve_id": None, "severity": severity,
                        "title": title, "summary": None, "link": link, "content_hash": content_hash,
                        "published_at": (item.findtext("pubDate") or "")[:30],
                        "created_at": datetime.now(timezone.utc).isoformat()
                    }
                    new_alerts.append(alert)
                    if SUPABASE_URL and SUPABASE_SERVICE_KEY:
                        try:
                            check = await client.get(f"{SUPABASE_URL}/rest/v1/cyber_alerts?content_hash=eq.{content_hash}&select=id", headers=SUPABASE_HEADERS, timeout=10)
                            if check.status_code == 200 and len(check.json()) == 0:
                                await client.post(f"{SUPABASE_URL}/rest/v1/cyber_alerts", headers=SUPABASE_HEADERS, json=alert, timeout=10)
                        except Exception:
                            pass
        except Exception as e:
            logger.error(f"[Cyber Feed Error - {feed['source']}]: {e}")
    return new_alerts


async def sync_conflict_and_macro(client: httpx.AsyncClient) -> list[dict]:
    """Ingests real-time kinetic war updates, geopolitical flashpoints, and macroeconomic shocks."""
    new_intel = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; TacticalConstruct/4.0)"}
    for feed in CONFLICT_AND_MACRO_FEEDS:
        try:
            resp = await client.get(feed["url"], headers=headers, timeout=15)
            if resp.status_code == 200:
                root = ET.fromstring(resp.content)
                for item in root.findall(".//item")[:5]:
                    title = (item.findtext("title") or "Untitled").strip()
                    link = item.findtext("link") or ""
                    if not title:
                        continue
                    content_hash = hashlib.sha256(f"{title}{link}".encode()).hexdigest()
                    lower_t = title.lower()
                    severity = "CRITICAL" if any(k in lower_t for k in ["strike", "kill", "ballistic", "war", "offensive", "casualt", "blockade"]) else ("HIGH" if any(k in lower_t for k in ["missile", "drone", "sanction", "clash", "threat", "inflation"]) else "ELEVATED")

                    intel_item = {
                        "domain": feed.get("domain", "WAR-KINETIC"),
                        "theater": feed.get("theater", "GLOBAL"),
                        "severity": severity,
                        "headline": title,
                        "source": feed.get("source", "Defense Wire"),
                        "link": link,
                        "content_hash": content_hash,
                        "created_at": datetime.now(timezone.utc).isoformat()
                    }
                    new_intel.append(intel_item)
                    if SUPABASE_URL and SUPABASE_SERVICE_KEY:
                        try:
                            await client.post(f"{SUPABASE_URL}/rest/v1/conflict_and_macro_intel", headers=SUPABASE_HEADERS, json=intel_item, timeout=10)
                        except Exception:
                            pass
        except Exception as e:
            logger.error(f"[Conflict Feed Error - {feed['source']}]: {e}")
    return new_intel


# =====================================================================
# --- REAL-TIME TELEGRAM POLLER (TEXT, VOICE, PHOTO) ---
# =====================================================================
async def telegram_poller(client: httpx.AsyncClient):
    """Maintains continuous long polling connection for multimodal interactions."""
    if not TELEGRAM_TOKEN or not AUTHORIZED_CHAT_ID:
        logger.warning("Telegram credentials unconfigured. Poller inactive.")
        return

    offset = 0
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    logger.info("Cortana/J.A.R.V.I.S. neural poller initialized...")

    while True:
        try:
            resp = await client.get(url, params={"offset": offset, "timeout": 30}, timeout=45)
            if resp.status_code == 200:
                data = resp.json()
                for update in data.get("result", []):
                    offset = update["update_id"] + 1
                    msg = update.get("message", {})
                    chat_id = msg.get("chat", {}).get("id")
                    if chat_id != AUTHORIZED_CHAT_ID:
                        continue

                    user_text = msg.get("text", "")

                    if "voice" in msg:
                        voice_id = msg["voice"]["file_id"]
                        logger.info("Incoming voice directive. Transcribing via Whisper...")
                        transcript = await transcribe_telegram_voice(client, voice_id)
                        await send_telegram(client, f"🎙️ *[VOICE DIRECTIVE]:* {transcript}")
                        user_text = transcript

                    elif "photo" in msg:
                        best_photo = msg["photo"][-1]["file_id"]
                        caption = msg.get("caption", "Analyze and record document/receipt.")
                        logger.info("Incoming visual asset. Extracting via Vision OCR...")
                        extracted = await analyze_telegram_photo(client, best_photo, caption)
                        user_text = f"[DOCUMENT OCR PAYLOAD]: {extracted}\nOperator Instruction: {caption}"

                    if user_text:
                        reply = await run_agent_turn(client, user_text)
                        await send_telegram(client, reply)
                        # Cortana speaks back via neural voice note on Telegram & host room speakers
                        await synthesize_and_send_voice(client, reply)

        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"[Poller Loop Error]: {e}")
            await asyncio.sleep(5)


# =====================================================================
# --- BACKGROUND WORKERS: SITREP & DEADLINE SCHEDULER ---
# =====================================================================
async def reminder_worker(client: httpx.AsyncClient):
    """Monitors scheduled tasks every 60 seconds."""
    while True:
        try:
            await check_due_tasks(client)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"[Reminder Worker Error]: {e}")
        await asyncio.sleep(60)


async def collector_worker(client: httpx.AsyncClient):
    """Executes periodic sensor sync and generates proactive Tactical SitReps with real telemetry persistence."""
    logger.info(f"Tactical telemetry daemon active (Interval: {SYNC_INTERVAL}s)...")
    while True:
        try:
            weather = await sync_weather(client)
            news = await sync_news(client)
            cyber = await sync_cyber_alerts(client)
            conflict_macro = await sync_conflict_and_macro(client)

            b = await synthesize_tactical_sitrep(client, weather, news, cyber, conflict_macro)

            # Persist real telemetry into telemetry_live.json so web HUD has real-time access
            try:
                live_path = Path(__file__).resolve().parent / "telemetry_live.json"
                existing = {}
                if live_path.exists():
                    try:
                        with open(live_path, "r", encoding="utf-8") as f:
                            existing = json.load(f)
                    except Exception:
                        pass

                payload = {
                    "sitrep": b,
                    "weather": weather if weather else existing.get("weather", []),
                    "cyber": cyber if cyber else existing.get("cyber", []),
                    "news": news if news else existing.get("news", []),
                    "conflicts": conflict_macro if conflict_macro else existing.get("conflicts", []),
                    "lan_devices": existing.get("lan_devices", []),
                    "tasks": existing.get("tasks", []),
                    "ledger": existing.get("ledger", []),
                    "vault": existing.get("vault", []),
                    "generated_at": datetime.now(timezone.utc).isoformat()
                }
                with open(live_path, "w", encoding="utf-8") as f:
                    json.dump(payload, f, indent=2, ensure_ascii=False)
            except Exception as se:
                logger.error(f"[Telemetry Live Save Error]: {se}")

            if (news or cyber or conflict_macro or force_sync_event.is_set()) and TELEGRAM_TOKEN and AUTHORIZED_CHAT_ID:
                try:
                    telegram_dispatch = (
                        f"🛡️ *OVERWATCH SITREP // [{b['threat_level']}]*\n\n"
                        f"1. *SITUATION:*\n{b['sitrep']}\n\n"
                        f"2. *ACTIVE WARS & CHOKEPOINTS:*\n{b['conflict_summary']}\n\n"
                        f"3. *FUTURE THREAT FORECAST:*\n{b['future_risk_forecast']}\n\n"
                        f"4. *DEFENSIVE PROTOCOL (PROTECT):*\n{b['defensive_protocol']}\n\n"
                        f"5. *ASYMMETRIC UPSIDE (BENEFIT):*\n{b['asymmetric_upside']}"
                    )
                    await send_telegram(client, telegram_dispatch)
                except Exception as e:
                    logger.error(f"[Synthesis Dispatch Error]: {e}")
        except Exception as ce:
            logger.error(f"[Collector Cycle Error]: {ce}")

        try:
            await asyncio.wait_for(force_sync_event.wait(), timeout=SYNC_INTERVAL)
            force_sync_event.clear()
            logger.info("Manual telemetry sweep triggered.")
        except asyncio.TimeoutError:
            pass
        except asyncio.CancelledError:
            break


async def cli_interactive_session():
    """Interactive command-line session for testing Cortana / J.A.R.V.I.S. and OSINT directly in terminal."""
    print("=" * 65)
    print("🛰️ CORTANA // J.A.R.V.I.S. INTERACTIVE CONSOLE ACTIVE")
    print("Type your directive or target to investigate. Type 'exit' to quit.")
    print("=" * 65)
    limits = httpx.Limits(max_keepalive_connections=10, max_connections=20)
    async with httpx.AsyncClient(follow_redirects=True, limits=limits) as client:
        while True:
            try:
                user_msg = input("\n[OPERATOR] > ").strip()
                if not user_msg:
                    continue
                if user_msg.lower() in ["exit", "quit", "q"]:
                    print("Standing down console.")
                    break
                print("\n[AI CORE] Synthesizing telemetry and executing multi-vector sweeps...")
                response = await run_agent_turn(client, user_msg)
                print(f"\n[CORTANA // J.A.R.V.I.S.]\n{response}\n")
                # Vocalize response in Cortana's neural voice
                await synthesize_and_send_voice(client, response)
            except (KeyboardInterrupt, EOFError):
                break


# =====================================================================
# --- MAIN APPLICATION ENTRYPOINT ---
# =====================================================================
async def main():
    logger.info("Initializing Cortana / J.A.R.V.I.S. Strategic War & Macro Command...")
    limits = httpx.Limits(max_keepalive_connections=10, max_connections=20)
    async with httpx.AsyncClient(follow_redirects=True, limits=limits) as client:
        if TELEGRAM_TOKEN and AUTHORIZED_CHAT_ID:
            await send_telegram(client, "Tactical Intelligence Construct Online. Kinetic War, Macro-Economic Shocks & Protective Protocols active.")

        tasks = [
            asyncio.create_task(telegram_poller(client)),
            asyncio.create_task(collector_worker(client)),
            asyncio.create_task(reminder_worker(client))
        ]

        if ENABLE_WAKEWORD or "--wake" in sys.argv:
            tasks.append(asyncio.create_task(ambient_wakeword_listener(client)))

        try:
            await asyncio.gather(*tasks)
        except (KeyboardInterrupt, asyncio.CancelledError):
            logger.info("Tactical construct standing down safely.")
            for task in tasks:
                task.cancel()


if __name__ == "__main__":
    try:
        if "--cli" in sys.argv:
            asyncio.run(cli_interactive_session())
        else:
            asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutdown complete.")
