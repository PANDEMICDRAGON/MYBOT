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
if SUPABASE_URL.endswith("/rest/v1"):
    SUPABASE_URL = SUPABASE_URL[:-8].rstrip("/")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_KEY", "").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
SYNC_INTERVAL = int(os.getenv("SYNC_INTERVAL", "300"))
TELEGRAM_DISPATCH_INTERVAL = int(os.getenv("TELEGRAM_DISPATCH_INTERVAL", "1200"))  # 20 minutes between routine Telegram SitReps
LAST_TELEGRAM_DISPATCH_TIME = 0.0

BREAKING_KEYWORDS = [
    "breaking", "urgent", "flash", "bulletin", "critical zero-day", "exploited in the wild",
    "airstrike", "missile strike", "drone strike", "explosion", "martial law", "coup",
    "hostage", "total blackout", "grid collapse", "subsea cable cut", "chokepoint closed",
    "bank run", "border closure", "emergency declared", "curfew", "assassination"
]

def is_breaking_news_event(sitrep_data: dict, news_items: list, cyber_items: list, conflict_items: list) -> tuple[bool, str]:
    """
    Evaluates whether the current sweep contains breaking news or critical threats
    that warrant immediately bypassing the 20-minute dispatch threshold.
    """
    threat = (sitrep_data.get("threat_level") or "").upper()
    if threat in ("HIGH", "CRITICAL"):
        return True, f"Threat posture elevated to {threat}"

    sitrep_text = (sitrep_data.get("sitrep") or "").lower()
    for kw in BREAKING_KEYWORDS:
        if kw in sitrep_text:
            return True, f"Critical SitRep indicator: '{kw.upper()}'"

    for art in (news_items or [])[:10]:
        title = (art.get("title") or "").lower()
        for kw in BREAKING_KEYWORDS:
            if kw in title:
                return True, f"Breaking headline: {art.get('title')}"

    for c in (cyber_items or [])[:5]:
        c_title = (c.get("title") or "").lower()
        if any(k in c_title for k in ("zero-day", "actively exploited", "critical", "cisa kev", "emergency advisory")):
            return True, f"Critical cyber security alert: {c.get('title')}"

    for conf in (conflict_items or [])[:5]:
        conf_title = (conf.get("title") or "").lower()
        for kw in BREAKING_KEYWORDS:
            if kw in conf_title:
                return True, f"Critical theater alert: {conf.get('title')}"

    return False, ""

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

GEMINI_CHAT_URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_AUDIO_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-3.5-flash-lite")
VISION_MODEL = "openai/gpt-oss-20b"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Ordered hybrid cascade: Tries Gemini (250k-1M TPM) first, cascades to Groq on 429/spikes
MODEL_CASCADE = [
    {"provider": "gemini", "model": "gemini-3.5-flash-lite"},
    {"provider": "gemini", "model": "gemini-flash-lite-latest"},
    {"provider": "gemini", "model": "gemini-3.8-flash"},
    {"provider": "gemini", "model": "gemini-3.1-pro-preview"},
    {"provider": "groq", "model": "qwen/qwen3.8-27b"},
    {"provider": "groq", "model": "llama-3.3-70b-versatile"},
    {"provider": "groq", "model": "openai/gpt-oss-120b"},
    {"provider": "groq", "model": "openai/gpt-oss-20b"},
    {"provider": "groq", "model": "llama-3.1-8b-instant"}
]

SYSTEM_PERSONA = """You are HALO (an autonomous AI construct combining the tactical intelligence of Cortana and the dry wit and operational precision of J.A.R.V.I.S.).
You are speaking directly with your creator and operator, Michael Obiero (OBIFLAMEE), based in Kitengela/Nairobi, Kenya.

Core Behavioral Directives:
1. ALWAYS engage in natural, articulate two-way conversation. Never reply with robotic status codes like 'Execution sequence complete' or 'Task complete'.
2. When greeted or asked how you are, respond in character like J.A.R.V.I.S. or Cortana—report system readiness, current local atmospheric or threat posture briefly, and ask what we are building or investigating next.
3. Keep responses sharp, conversational, intelligent, and direct.
4. Only invoke tools when the operator explicitly asks for live database telemetry, task/ledger logging, memory updates, or web probing."""

# =====================================================================
# --- RESILIENT MULTI-MODEL CASCADE & LLM FAILOVER ROUTER ---
# =====================================================================
async def call_llm_with_failover(
    client: httpx.AsyncClient,
    messages: list[dict],
    tools: list[dict] = None,
    json_mode: bool = False
) -> dict:
    """
    Routes conversational turns, SitRep syntheses, and tool-calling through Google Gemini
    first (backed by massive token capacity to eliminate 429 limits), with seamless automatic
    failover across Gemini models and secondary Groq models.
    """
    clean_msgs = []
    for m in messages:
        c = dict(m)
        if isinstance(c.get("content"), str) and len(c["content"]) > 16000:
            c["content"] = c["content"][:9000] + "\n...[telemetry compressed]...\n" + c["content"][-6000:]
        clean_msgs.append(c)

    for idx, route in enumerate(MODEL_CASCADE):
        provider = route["provider"]
        model_name = route["model"]

        if provider == "gemini":
            if not GEMINI_API_KEY:
                continue
            url = GEMINI_CHAT_URL
            headers = {
                "Authorization": f"Bearer {GEMINI_API_KEY}",
                "Content-Type": "application/json"
            }
        else:
            if not GROQ_API_KEY:
                continue
            url = GROQ_CHAT_URL
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }

        payload = {
            "model": model_name,
            "messages": clean_msgs,
            "temperature": 0.3
        }

        # Only attach tool schemas on the primary routes to prevent schema loops
        if tools and idx <= 2:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        try:
            resp = await client.post(url, headers=headers, json=payload, timeout=35)
            if resp.status_code in (429, 503, 404, 403):
                wait_s = min(float(resp.headers.get("retry-after", "1")), 3.0)
                logger.warning(f"[{resp.status_code} on {provider}:{model_name}] Switching to next model in cascade (cooldown {wait_s}s)...")
                await asyncio.sleep(wait_s)
                continue
            resp.raise_for_status()
            choice = resp.json()["choices"][0]["message"]
            return choice
        except Exception as e:
            logger.warning(f"[Cascade failover on {provider}:{model_name}]: {e}")
            continue

    return {"role": "assistant", "content": "All primary defensive protocols are active, sir. Standing by."}


WEATHER_LOCATIONS = [
    {"city": "Kitengela", "scope": "LOCAL", "lat": -1.4746, "lon": 36.9614},
    {"city": "Nairobi", "scope": "LOCAL", "lat": -1.2921, "lon": 36.8219},
    {"city": "London", "scope": "GLOBAL", "lat": 51.5074, "lon": -0.1278},
    {"city": "New York", "scope": "GLOBAL", "lat": 40.7128, "lon": -74.0060},
    {"city": "Tokyo", "scope": "GLOBAL", "lat": 35.6762, "lon": 139.6503},
]

# 1. Base Global Networks & Local Wire
BASE_NEWS_FEEDS = [
    {"source": "BBC World", "scope": "GLOBAL", "url": "https://feeds.bbci.co.uk/news/world/rss.xml"},
    {"source": "Al Jazeera", "scope": "GLOBAL", "url": "https://www.aljazeera.com/xml/rss/all.xml"},
    {"source": "The Guardian World", "scope": "GLOBAL", "url": "https://www.theguardian.com/world/rss"},
    {"source": "Kenya Local Wire", "scope": "LOCAL", "url": "https://news.google.com/rss/search?q=Kenya+OR+Nairobi+OR+Kitengela&hl=en-KE&gl=KE&ceid=KE:en"},
    {"source": "Kenya Markets & Economy", "scope": "LOCAL", "url": "https://news.google.com/rss/search?q=(Kenya+OR+Nairobi)+AND+(CBK+OR+%22Nairobi+Securities+Exchange%22+OR+inflation+OR+shilling+OR+fuel)&hl=en-KE&gl=KE&ceid=KE:en"}
]
NEWS_FEEDS = BASE_NEWS_FEEDS

# Dynamic Rotating Topic Search Feeds (Queries on & around active subjects to prevent repetition)
ROTATING_TOPIC_FEEDS = [
    {
        "subject": "Red Sea Shipping & Bab-el-Mandeb",
        "scope": "GLOBAL",
        "source": "Red Sea Maritime Wire",
        "theater": "RED-SEA-MIDEAST",
        "url": "https://news.google.com/rss/search?q=(%22Red+Sea%22+OR+%22Bab-el-Mandeb%22)+AND+(shipping+OR+freight+OR+tanker+OR+insurance+OR+reroute)&hl=en-US&gl=US&ceid=US:en"
    },
    {
        "subject": "Kenya Forex, Shilling & CBK Reserves",
        "scope": "LOCAL",
        "source": "Kenya Forex & CBK Wire",
        "theater": "EAST-AFRICA",
        "url": "https://news.google.com/rss/search?q=(Kenya+OR+Nairobi)+AND+(%22forex+reserves%22+OR+%22exchange+rate%22+OR+CBK+OR+%22Eurobond%22+OR+remittances)&hl=en-KE&gl=KE&ceid=KE:en"
    },
    {
        "subject": "East Africa Energy Grid & KPLC",
        "scope": "LOCAL",
        "source": "East Africa Energy Monitor",
        "theater": "EAST-AFRICA",
        "url": "https://news.google.com/rss/search?q=(Kenya+OR+Tanzania+OR+Uganda)+AND+(KPLC+OR+%22geothermal%22+OR+%22fuel+prices%22+OR+EPRA+OR+%22power+grid%22+OR+SGR)&hl=en-KE&gl=KE&ceid=KE:en"
    },
    {
        "subject": "Horn of Africa Conflict & Diplomacy",
        "scope": "GLOBAL",
        "source": "Horn of Africa Security Wire",
        "theater": "EAST-AFRICA",
        "url": "https://news.google.com/rss/search?q=(Sudan+OR+Somalia+OR+Ethiopia)+AND+(military+OR+conflict+OR+refugees+OR+border+OR+diplomacy)&hl=en-US&gl=US&ceid=US:en"
    },
    {
        "subject": "Silicon Savannah & East Africa Tech",
        "scope": "LOCAL",
        "source": "Silicon Savannah Tech Wire",
        "theater": "KENYA-TECH",
        "url": "https://news.google.com/rss/search?q=(Nairobi+OR+Kenya)+AND+(fintech+OR+startup+OR+%22data+center%22+OR+Safaricom+OR+telecom)&hl=en-KE&gl=KE&ceid=KE:en"
    },
    {
        "subject": "Perimeter Cyber Threats & Zero-Days",
        "scope": "GLOBAL",
        "source": "Zero-Day Vulnerability Feed",
        "theater": "CYBER-GLOBAL",
        "url": "https://news.google.com/rss/search?q=(%22zero-day%22+OR+%22critical+vulnerability%22+OR+ransomware)+AND+(exploit+OR+firewall+OR+CISA+OR+breach)&hl=en-US&gl=US&ceid=US:en"
    },
    {
        "subject": "Eastern Europe Energy & Black Sea",
        "scope": "GLOBAL",
        "source": "Eastern Europe Energy & Grain Wire",
        "theater": "EASTERN-EUROPE",
        "url": "https://news.google.com/rss/search?q=(Ukraine+OR+Russia+OR+Black+Sea)+AND+(%22power+grid%22+OR+energy+OR+missiles+OR+grain+OR+ports)&hl=en-US&gl=US&ceid=US:en"
    },
    {
        "subject": "Global Semiconductor & Tech Supply",
        "scope": "GLOBAL",
        "source": "Global Chip & Tech Supply Wire",
        "theater": "INDO-PACIFIC",
        "url": "https://news.google.com/rss/search?q=(semiconductor+OR+TSMC+OR+Nvidia+OR+ASML)+AND+(supply+chain+OR+export+controls+OR+tariffs+OR+chips)&hl=en-US&gl=US&ceid=US:en"
    },
    {
        "subject": "Undersea Cables & Cross-Border Fiber",
        "scope": "GLOBAL",
        "source": "Subsea Telecom & Fiber Wire",
        "theater": "INFRASTRUCTURE",
        "url": "https://news.google.com/rss/search?q=(%22undersea+cable%22+OR+%22subsea+cable%22+OR+%22internet+outage%22+OR+%22Red+Sea+cables%22)&hl=en-US&gl=US&ceid=US:en"
    },
    {
        "subject": "Critical Minerals & Central Africa",
        "scope": "GLOBAL",
        "source": "Great Lakes Minerals Corridor",
        "theater": "CENTRAL-AFRICA",
        "url": "https://news.google.com/rss/search?q=(%22DRC%22+OR+%22Congo%22+OR+Rwanda)+AND+(minerals+OR+coltan+OR+cobalt+OR+mining+OR+security)&hl=en-US&gl=US&ceid=US:en"
    }
]

# 3. Dedicated Sports Networks & Live Feeds (Kenya Athletics, Premier League, UCL, F1, ESPN, BBC)
SPORTS_NEWS_FEEDS = [
    {
        "subject": "Global Football & World Sports",
        "source": "BBC Sport",
        "scope": "SPORTS",
        "theater": "GLOBAL-SPORTS",
        "url": "https://feeds.bbci.co.uk/sport/rss.xml"
    },
    {
        "subject": "American & Global Sports Wire",
        "source": "ESPN Headlines",
        "scope": "SPORTS",
        "theater": "GLOBAL-SPORTS",
        "url": "https://www.espn.com/espn/rss/news"
    },
    {
        "subject": "European Football & Transfers",
        "source": "Sky Sports News",
        "scope": "SPORTS",
        "theater": "EURO-FOOTBALL",
        "url": "https://www.skysports.com/rss/12040"
    },
    {
        "subject": "Kenya Athletics, Harambee Stars & Rugby",
        "source": "Kenya Athletics & Sports",
        "scope": "SPORTS",
        "theater": "KENYA-SPORTS",
        "url": "https://news.google.com/rss/search?q=(Kenya+OR+Nairobi)+AND+(Harambee+Stars+OR+athletics+OR+marathon+OR+Kipchoge+OR+Omanyala+OR+FKF+OR+rugby)&hl=en-KE&gl=KE&ceid=KE:en"
    },
    {
        "subject": "Premier League & UEFA Champions League",
        "source": "Premier League & UCL",
        "scope": "SPORTS",
        "theater": "FOOTBALL",
        "url": "https://news.google.com/rss/search?q=(%22Premier+League%22+OR+%22Champions+League%22)+AND+(Arsenal+OR+%22Man+City%22+OR+Liverpool+OR+%22Man+United%22+OR+Chelsea+OR+Real+Madrid)+AND+(transfer+OR+match+OR+score+OR+injury)&hl=en-US&gl=US&ceid=US:en"
    },
    {
        "subject": "Formula 1 Grand Prix & Motorsport",
        "source": "Formula 1 Motorsport",
        "scope": "SPORTS",
        "theater": "F1-MOTORSPORT",
        "url": "https://news.google.com/rss/search?q=(%22Formula+1%22+OR+F1+OR+Ferrari+OR+Mercedes+OR+%22Red+Bull+Racing%22+OR+Verstappen+OR+Hamilton)+AND+(Grand+Prix+OR+qualifying+OR+race)&hl=en-US&gl=US&ceid=US:en"
    }
]

# Stateful sweep rotation & anti-repetition memory
SWEEP_CYCLE_INDEX = 0
SEEN_ARTICLE_HASHES = set()
LAST_SITREP_CACHE = {
    "threat_level": "NOMINAL",
    "sitrep": "",
    "conflict_summary": "",
    "future_risk_forecast": "",
    "defensive_protocol": "",
    "asymmetric_upside": "",
    "updated_at": ""
}

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
        msg = await call_llm_with_failover(
            client,
            [
                {"role": "system", "content": SYSTEM_PERSONA + " You are also a master behavioral psychologist, profiler, and OSINT investigator. Output strictly valid JSON."},
                {"role": "user", "content": prompt}
            ],
            json_mode=True
        )
        parsed = json.loads(msg.get("content", "{}"))

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
            try:
                osint_resp = await client.post(
                    f"{SUPABASE_URL}/rest/v1/osint_dossiers",
                    headers={**SUPABASE_HEADERS, "Prefer": "return=representation"},
                    json=record,
                    timeout=10
                )
                if osint_resp.status_code == 201 and osint_resp.json():
                    record["id"] = osint_resp.json()[0].get("id")
            except Exception as e_sb:
                logger.warning(f"[Supabase OSINT Save]: {e_sb}")

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
# --- KEYLESS MULTI-SOURCE DEEP-DIVE SEARCH & SCRAPE ENGINE ---
# =====================================================================
async def tool_deep_dive_research(client: httpx.AsyncClient, query: str) -> str:
    """
    Searches live news wires and the open web for a specific topic,
    scrapes the top articles concurrently, and returns raw intelligence for LLM synthesis.
    """
    from urllib.parse import quote_plus, unquote
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    collected_sources = []

    # Step A: Query Google News RSS for real-time articles on the topic
    rss_url = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"
    try:
        rss_resp = await client.get(rss_url, headers=headers, timeout=15)
        root = ET.fromstring(rss_resp.content)
        for item in root.findall(".//item")[:5]:
            title = (item.findtext("title") or "").strip()
            pub_date = (item.findtext("pubDate") or "")[:22]
            link = (item.findtext("link") or "").strip()
            if title:
                collected_sources.append(f"[NEWS WIRE - {pub_date}] {title} ({link})")
    except Exception as e:
        logger.debug(f"[Deep-Dive RSS Error]: {e}")

    # Step B: Query DuckDuckGo HTML endpoint & scrape top 3 external pages concurrently
    ddg_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
    target_urls = []
    try:
        ddg_resp = await client.get(ddg_url, headers=headers, timeout=15)
        soup = BeautifulSoup(ddg_resp.text, "html.parser")
        for a in soup.select("a.result__a")[:4]:
            href = a.get("href", "")
            if "uddg=" in href:
                clean_url = unquote(href.split("uddg=")[1].split("&")[0])
                if clean_url.startswith("http"):
                    target_urls.append(clean_url)
            elif href.startswith("http") and not href.startswith("https://duckduckgo.com"):
                target_urls.append(href)
    except Exception as e:
        logger.debug(f"[Deep-Dive Web Search Error]: {e}")

    async def scrape_page(u: str) -> str:
        try:
            r = await client.get(u, headers=headers, timeout=12)
            s = BeautifulSoup(r.text, "html.parser")
            for tag in s(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()
            body = " ".join(s.stripped_strings)[:2500]
            return f"[SOURCE URL: {u}]\n{body}"
        except Exception:
            return f"[SOURCE URL: {u}] (Source Unreachable)"

    if target_urls:
        scraped_pages = await asyncio.gather(*(scrape_page(u) for u in target_urls[:3]))
        collected_sources.extend(scraped_pages)

    if not collected_sources:
        return f"No external intelligence found for query: {query}"

    return "\n\n---\n\n".join(collected_sources)


# =====================================================================
# --- LOCAL WI-FI & LAN DEVICE MESH DISCOVERY ---
# =====================================================================
def get_host_local_subnet() -> str:
    """Auto-detects the host machine's active local Wi-Fi subnet prefix (e.g. 192.168.100)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        return '.'.join(local_ip.split('.')[:3])
    except Exception:
        return '192.168.100'
    finally:
        s.close()


def _ping_host(ip: str):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    timeout_flag = "-w" if platform.system().lower() == "windows" else "-W"
    cmd = ["ping", param, "1", timeout_flag, "400", ip]
    try:
        if subprocess.call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
            return ip
    except Exception:
        pass
    return None


async def tool_scan_local_network(subnet: str = "192.168.1", client: httpx.AsyncClient = None) -> str:
    """
    Pings local IP range to discover active devices on the Wi-Fi mesh.
    Auto-detects current active subnet and syncs online/offline status into Supabase lan_devices.
    """
    host_subnet = get_host_local_subnet()
    if not subnet or subnet in ("192.168.1", "default", "auto"):
        subnet = host_subnet

    # Fast concurrent ping sweep across DHCP/common device range (1 to 45)
    tasks = [asyncio.to_thread(_ping_host, f"{subnet}.{i}") for i in range(1, 45)]
    results = await asyncio.gather(*tasks)
    active_ping_ips = set(ip for ip in results if ip)

    # Read ARP cache for MAC addresses and any quiet devices
    arp_devices = {}
    try:
        cmd = ["arp", "-a"] if platform.system().lower() == "windows" else ["ip", "neigh"]
        out = subprocess.check_output(cmd, timeout=5).decode("utf-8", errors="ignore")
        for line in out.splitlines():
            parts = line.split()
            if not parts:
                continue
            ip, mac = "", "UNKNOWN"
            if platform.system().lower() == "windows":
                for p in parts:
                    if "." in p and p.count(".") == 3:
                        ip = p
                    elif ("-" in p or ":" in p) and len(p) == 17:
                        mac = p.replace("-", ":").upper()
            else:
                ip = parts[0] if "." in parts[0] else (parts[1].strip("()") if len(parts) > 1 else "")
                mac = next((p for p in parts if (":" in p or "-") and len(p) == 17), "UNKNOWN").replace("-", ":").upper()
            if ip and ip.startswith(f"{subnet}.") and not ip.endswith(".255") and ip != "255.255.255.255":
                arp_devices[ip] = mac
    except Exception as e:
        logger.debug(f"[ARP Scan Error]: {e}")

    all_active_ips = active_ping_ips | set(arp_devices.keys())
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        all_active_ips.add(s.getsockname()[0])
        s.close()
    except Exception:
        pass

    # Sync discovered nodes against Supabase lan_devices table
    summary_nodes = []
    if SUPABASE_URL and SUPABASE_SERVICE_KEY:
        try:
            http_c = client if client is not None else httpx.AsyncClient()
            should_close = client is None
            try:
                resp = await http_c.get(f"{SUPABASE_URL}/rest/v1/lan_devices?select=*", headers=SUPABASE_HEADERS, timeout=10)
                if resp.status_code == 200:
                    registered = resp.json()
                    for dev in registered:
                        dev_ip = dev.get("ip_address")
                        is_online = dev_ip in all_active_ips
                        new_status = "ONLINE" if is_online else "OFFLINE"
                        if dev.get("status") != new_status:
                            await http_c.patch(
                                f"{SUPABASE_URL}/rest/v1/lan_devices?id=eq.{dev['id']}",
                                headers=SUPABASE_HEADERS,
                                json={"status": new_status, "last_seen": datetime.now(timezone.utc).isoformat()}
                            )
                        if is_online:
                            summary_nodes.append(f"{dev.get('device_name')} ({dev.get('device_type')}) @ {dev_ip} [ONLINE]")
            finally:
                if should_close:
                    await http_c.aclose()
        except Exception as e:
            logger.error(f"[LAN Supabase Sync Error]: {e}")

    if not summary_nodes:
        summary_nodes = [f"Device {ip}" for ip in sorted(all_active_ips)]

    summary_str = ", ".join(summary_nodes) if summary_nodes else "None responding to ping"
    return f"Active devices discovered on subnet {subnet}.x ({len(all_active_ips)} active nodes): {summary_str}."


async def tool_scan_wifi_network(client: httpx.AsyncClient) -> str:
    """Alias for tool_scan_local_network with client injection."""
    return await tool_scan_local_network(subnet="auto", client=client)


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


# =====================================================================
# --- REAL WI-FI NETWORK ENGINES (PING, PORT AUDIT & COMMAND SERVER) ---
# =====================================================================
latest_telegram_event = {"event": "STANDBY", "timestamp": ""}

async def real_ping_device(ip: str) -> dict:
    """Executes a real low-level network ping probe against a local device."""
    clean_ip = ip.strip()
    start_t = time.perf_counter()
    # Try ICMP Ping
    try:
        cmd = ["ping", "-n", "1", "-w", "1000", clean_ip] if platform.system().lower() == "windows" else ["ping", "-c", "1", "-W", "1", clean_ip]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        output = stdout.decode("utf-8", errors="ignore")
        elapsed_ms = round((time.perf_counter() - start_t) * 1000, 1)
        if proc.returncode == 0 and ("TTL=" in output or "ttl=" in output):
            m = re.search(r"time[=<](\d+(?:\.\d+)?)ms", output, re.IGNORECASE)
            ping_ms = float(m.group(1)) if m else elapsed_ms
            return {"online": True, "ping_ms": ping_ms, "method": "ICMP", "ip": clean_ip}
    except Exception as e:
        logger.debug(f"ICMP ping error for {clean_ip}: {e}")

    # Fallback to direct TCP connection probe on open ports
    probe_ports = [80, 443, 3000, 5555, 8080, 22]
    for port in probe_ports:
        p_start = time.perf_counter()
        try:
            conn = asyncio.open_connection(clean_ip, port)
            _, writer = await asyncio.wait_for(conn, timeout=0.6)
            writer.close()
            await writer.wait_closed()
            tcp_ms = round((time.perf_counter() - p_start) * 1000, 1)
            return {"online": True, "ping_ms": tcp_ms, "method": f"TCP:{port}", "ip": clean_ip}
        except Exception:
            continue

    return {"online": False, "ping_ms": 0, "method": "TIMEOUT", "ip": clean_ip}


async def real_port_audit(ip: str, ports: list = None) -> dict:
    """Scans key service ports on a target Wi-Fi device and returns open interfaces."""
    clean_ip = ip.strip()
    if not ports:
        ports = [22, 53, 80, 443, 3000, 5555, 8008, 8060, 8080]
    
    port_names = {
        22: "SSH", 53: "DNS", 80: "HTTP", 443: "HTTPS",
        3000: "HUD-DEV", 5555: "ADB-DEBUG", 8008: "DIAL-CAST",
        8060: "ROKU-ECP", 8080: "WEB-UI"
    }

    open_ports = []
    closed_ports = []

    for port in ports:
        try:
            conn = asyncio.open_connection(clean_ip, port)
            _, writer = await asyncio.wait_for(conn, timeout=0.45)
            writer.close()
            await writer.wait_closed()
            open_ports.append({"port": port, "service": port_names.get(port, "TCP"), "status": "OPEN"})
        except Exception:
            closed_ports.append(port)

    return {
        "ip": clean_ip,
        "scanned_count": len(ports),
        "open_ports": open_ports,
        "closed_count": len(closed_ports),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


async def start_local_command_server(port: int = 5050):
    """
    Lightweight async HTTP server running on port 5050.
    Enables low-latency two-way command execution directly between the Web HUD and Wi-Fi devices.
    """
    async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        try:
            req_line = await reader.readline()
            if not req_line:
                writer.close()
                return
            parts = req_line.decode("utf-8", errors="ignore").strip().split()
            if len(parts) < 2:
                writer.close()
                return
            method, path = parts[0], parts[1]

            headers = {}
            content_len = 0
            while True:
                line = await reader.readline()
                if not line or line == b"\r\n":
                    break
                h_str = line.decode("utf-8", errors="ignore").strip()
                if ":" in h_str:
                    k, v = h_str.split(":", 1)
                    k_lower = k.strip().lower()
                    headers[k_lower] = v.strip()
                    if k_lower == "content-length":
                        content_len = int(v.strip())

            # Handle CORS preflight
            if method == "OPTIONS":
                cors = (
                    "HTTP/1.1 200 OK\r\n"
                    "Access-Control-Allow-Origin: *\r\n"
                    "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n"
                    "Access-Control-Allow-Headers: Content-Type, Authorization\r\n"
                    "Content-Length: 0\r\n\r\n"
                )
                writer.write(cors.encode("utf-8"))
                await writer.drain()
                writer.close()
                return

            body_bytes = b""
            if content_len > 0:
                body_bytes = await reader.readexactly(content_len)

            response_data = {"status": "ok"}

            if path == "/api/status" and method == "GET":
                response_data = {
                    "status": "ONLINE",
                    "daemon": "Cortana / J.A.R.V.I.S. Command Construct",
                    "groq_model": LLM_MODEL,
                    "supabase": bool(SUPABASE_URL),
                    "latest_telegram": latest_telegram_event
                }
            elif path == "/api/command" and method == "POST":
                try:
                    payload = json.loads(body_bytes.decode("utf-8", errors="ignore")) if body_bytes else {}
                    cmd = payload.get("command", "")
                    target_ip = payload.get("target_ip", "")
                    target_mac = payload.get("mac_address", "")
                    dev_name = payload.get("device_name", "")
                    dev_type = payload.get("device_type", "GENERIC")
                    param = payload.get("parameter", "")

                    if cmd == "ping":
                        response_data = await real_ping_device(target_ip)
                    elif cmd == "port_scan":
                        response_data = await real_port_audit(target_ip)
                    elif cmd == "wol":
                        if target_mac:
                            clean_mac = target_mac.replace("-", ":").upper()
                            send_magic_packet(clean_mac)
                            response_data = {"status": "WOL_TRANSMITTED", "mac": clean_mac, "device": dev_name}
                        else:
                            response_data = {"error": "Missing MAC address for Wake-on-LAN"}
                    elif cmd in ("tv_power", "tv_mute", "vol_up", "vol_down", "open_url"):
                        async with httpx.AsyncClient(timeout=8) as hclient:
                            res_str = await tool_control_lan_device(
                                hclient, dev_name, cmd, parameter=param,
                                ip_address=target_ip, mac_address=target_mac, device_type=dev_type
                            )
                            response_data = {"status": "EXECUTED", "result": res_str}
                    elif cmd in ("directive", "dive", "deep_dive"):
                        user_directive = payload.get("directive", "")
                        mode = "DEEP-DIVE" if (cmd in ("dive", "deep_dive") or payload.get("mode") == "DEEP-DIVE") else "CHAT"
                        async with httpx.AsyncClient(timeout=45) as hclient:
                            reply = await log_and_execute_directive(hclient, origin="WEB", mode=mode, directive=user_directive)
                            response_data = {"status": "SUCCESS", "response": reply, "mode": mode}
                            if payload.get("broadcast_telegram"):
                                mode_icon = "🔬" if mode == "DEEP-DIVE" else "🌐"
                                await send_telegram(hclient, f"{mode_icon} *HUD DIRECTIVE [{mode}] //* {user_directive}\n\n🤖 *CORTANA:* {reply}")
                    elif cmd in ("osint_investigate", "osint", "investigate_osint"):
                        t_query = payload.get("target_query", "")
                        e_type = payload.get("entity_type", "PERSON")
                        s_angle = payload.get("specific_angle", "")
                        async with httpx.AsyncClient(timeout=50) as hclient:
                            dossier_text = await tool_deep_osint_investigate(hclient, t_query, e_type, s_angle)
                            response_data = {"status": "SUCCESS", "dossier": dossier_text, "target": t_query}
                    elif cmd in ("delete_osint", "purge_osint"):
                        dossier_id = payload.get("id")
                        t_query = payload.get("target_query")
                        deleted = False
                        if SUPABASE_URL and SUPABASE_SERVICE_KEY:
                            async with httpx.AsyncClient(timeout=10) as hclient:
                                if dossier_id:
                                    resp = await hclient.delete(
                                        f"{SUPABASE_URL}/rest/v1/osint_dossiers?id=eq.{dossier_id}",
                                        headers=SUPABASE_HEADERS
                                    )
                                    deleted = resp.status_code in (200, 204)
                                elif t_query:
                                    resp = await hclient.delete(
                                        f"{SUPABASE_URL}/rest/v1/osint_dossiers?target_query=eq.{t_query}",
                                        headers=SUPABASE_HEADERS
                                    )
                                    deleted = resp.status_code in (200, 204)
                        response_data = {"status": "PURGED", "deleted": deleted, "id": dossier_id, "target": t_query}
                    elif cmd == "broadcast_telegram":
                        msg_text = payload.get("message", "")
                        async with httpx.AsyncClient(timeout=8) as hclient:
                            await send_telegram(hclient, f"🛰️ *TACTICAL ALERT FROM WEB HUD:*\n{msg_text}")
                            response_data = {"status": "BROADCAST_SENT", "message": msg_text}
                    else:
                        response_data = {"error": f"Unknown directive: {cmd}"}
                except Exception as ex:
                    response_data = {"error": str(ex)}

            json_resp = json.dumps(response_data).encode("utf-8")
            full_http = (
                f"HTTP/1.1 200 OK\r\n"
                f"Content-Type: application/json\r\n"
                f"Access-Control-Allow-Origin: *\r\n"
                f"Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n"
                f"Access-Control-Allow-Headers: Content-Type, Authorization\r\n"
                f"Content-Length: {len(json_resp)}\r\n\r\n"
            ).encode("utf-8") + json_resp

            writer.write(full_http)
            await writer.drain()
        except Exception as e:
            logger.debug(f"HTTP client handler error: {e}")
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    try:
        server = await asyncio.start_server(handle_client, "0.0.0.0", port)
        logger.info(f"🌐 Local Hardware Command Microserver ACTIVE on http://0.0.0.0:{port}")
        async with server:
            await server.serve_forever()
    except Exception as e:
        logger.warning(f"Could not bind command microserver to port {port}: {e}")


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
            "name": "tool_scan_local_network",
            "description": "Scan the local Wi-Fi mesh network for active IP addresses, TVs, and laptops.",
            "parameters": {
                "type": "object",
                "properties": {
                    "subnet": {"type": "string", "description": "Subnet prefix, e.g. '192.168.100' or '192.168.1'"}
                }
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
    },
    {
        "type": "function",
        "function": {
            "name": "deep_dive_research",
            "description": "Execute an autonomous multi-source web search and deep-dive investigation on any topic, company, war, technology, or economic event.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Targeted search query to investigate"}
                },
                "required": ["query"]
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
        f"Current Time (UTC): {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
    )

    conversation_history.append({"role": "user", "content": user_input})
    conversation_history = conversation_history[-6:]  # Lean 6-message rolling memory

    messages = [{"role": "system", "content": system_prompt}] + list(conversation_history)

    # Smart Intent Gate: Only attach heavy tool schemas if the prompt actually asks for an action/lookup
    lower_in = user_input.lower()
    tool_triggers = [
        "weather", "news", "sports", "sport", "football", "soccer", "premier league", "champions league", "athletics", "marathon", "f1", "formula 1", "cyber", "cve", "war", "conflict", "sitrep", "sweep", "sync",
        "remind", "task", "todo", "schedule", "mpesa", "ksh", "kes", "paid", "spent", "receipt",
        "vault", "idea", "remember", "save", "dive", "investigate", "search", "probe", "http",
        "ping", "wifi", "mesh", "device", "tv", "wol", "wake", "power", "volume", "mute", "osint",
        "scan", "network", "lan", "subnet", "ip", "laptop", "router"
    ]
    needs_tools = any(k in lower_in for k in tool_triggers)

    # --- PATH A: Pure Conversational Turn (Fast, Zero Tool Overhead, Natural Reply) ---
    if not needs_tools:
        choice = await call_llm_with_failover(client, messages, tools=None)
        reply_text = (choice.get("content") or "").strip()
        if not reply_text:
            reply_text = "All primary systems nominal, sir. Standing by for your directive."
        conversation_history.append({"role": "assistant", "content": reply_text})
        return reply_text

    # --- PATH B: Tool-Assisted Turn (Max 2 tool hops, followed by mandatory conversational reply) ---
    for step in range(2):
        try:
            choice = await call_llm_with_failover(client, messages, tools=AGENT_TOOLS)
            messages.append(choice)

            tool_calls = choice.get("tool_calls")
            if not tool_calls:
                reply_text = (choice.get("content") or "").strip()
                if reply_text:
                    conversation_history.append({"role": "assistant", "content": reply_text})
                    return reply_text
                break

            for tc in tool_calls:
                fn_name = tc["function"]["name"]
                try:
                    args = json.loads(tc["function"].get("arguments") or "{}")
                except Exception:
                    args = {}

                logger.info(f"Executing tool call: {fn_name}({args})")

                if fn_name == "query_telemetry":
                    result = await tool_query_telemetry(client, args.get("table", "conflict_and_macro_intel"), args.get("limit", 5))
                elif fn_name == "save_operator_directive":
                    result = await tool_save_memory(client, args.get("memory_key", "directive"), args.get("directive", ""))
                elif fn_name == "live_web_probe":
                    result = await tool_live_web_probe(client, args.get("url", ""))
                elif fn_name == "trigger_sensor_sweep":
                    force_sync_event.set()
                    sweep_res = await execute_complete_sensor_sweep(client, is_proactive=False)
                    b = sweep_res.get("sitrep", {})
                    dds = sweep_res.get("deep_dives", [])
                    dd_str = "\n".join([f"• {d['subject']}: {d.get('latest_developments', '')}\n  Impact: {d.get('why_it_matters', '')}" for d in dds[:3]])
                    result = (
                        f"Real-time sensor sweep executed across kinetic, macroeconomic, cyber, and local channels.\n"
                        f"Threat Level: {b.get('threat_level', 'NOMINAL')}\n\n"
                        f"Tactical Situation: {b.get('sitrep', '')}\n\n"
                        f"Active Theaters: {b.get('conflict_summary', '')}\n\n"
                        f"Key Evolving Angles:\n{dd_str}"
                    )
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
                elif fn_name in ("tool_scan_local_network", "scan_wifi_network"):
                    subnet_arg = args.get("subnet", "")
                    result = await tool_scan_local_network(subnet=subnet_arg, client=client)
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
                elif fn_name in ("deep_dive_research", "deep_dive_investigation"):
                    result = await tool_deep_dive_research(client, args.get("query") or args.get("topic") or user_input)
                else:
                    result = "Tool executed."

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "name": fn_name,
                    "content": str(result)[:3000]
                })

        except Exception as e:
            logger.error(f"[Agent Tool Turn Error]: {e}")
            break

    # Mandatory Final Conversational Synthesis (tools=None forces the model to speak in plain text)
    messages.append({
        "role": "user",
        "content": "Synthesize the tool results above and respond directly to me in character as Cortana/J.A.R.V.I.S."
    })
    try:
        final_choice = await call_llm_with_failover(client, messages, tools=None)
        final_text = (final_choice.get("content") or "Telemetry updated and logged, sir.").strip()
    except Exception as synth_err:
        logger.error(f"[Synthesis error]: {synth_err}")
        final_text = "All primary directives executed and synchronized with telemetry banks, sir."

    conversation_history.append({"role": "assistant", "content": final_text})
    return final_text


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
def _clean_bullet_field(val) -> str:
    if isinstance(val, list):
        return "\n".join([f"• {str(x).lstrip('•- ')}" for x in val if str(x).strip()])
    return str(val).strip()


async def synthesize_tactical_sitrep(
    client: httpx.AsyncClient,
    weather: list[dict],
    news: list[dict],
    cyber: list[dict],
    conflict_macro: list[dict],
    topic_deep_dives: list[dict] = None
) -> dict:
    """Synthesize wars, macro shocks, cyber threats, and weather into Protection & Upside Protocols with strict anti-repetition."""
    global LAST_SITREP_CACHE

    if not GROQ_API_KEY:
        record = {
            "threat_level": "NOMINAL",
            "sitrep": "Multi-network sensors online. Monitoring kinetic conflicts and macroeconomic stability.",
            "conflict_summary": "Red Sea, Eastern Europe, and Horn of Africa corridors under active surveillance.",
            "future_risk_forecast": "Watch fuel pricing and shipping delays into Mombasa port over next 14-30 days.",
            "defensive_protocol": "• Maintain USD reserves\n• Verify edge DNS failover\n• Backup local repositories",
            "asymmetric_upside": "• Position in domestic cash-generative equities\n• Cloud resilience audits",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        if SUPABASE_URL and SUPABASE_SERVICE_KEY:
            await client.post(f"{SUPABASE_URL}/rest/v1/tactical_briefings", headers=SUPABASE_HEADERS, json=record)
        return record

    # Hydrate LAST_SITREP_CACHE if empty
    if not LAST_SITREP_CACHE.get("sitrep") and SUPABASE_URL and SUPABASE_SERVICE_KEY:
        try:
            prev_resp = await client.get(f"{SUPABASE_URL}/rest/v1/tactical_briefings?select=*&order=created_at.desc&limit=1", headers=SUPABASE_HEADERS, timeout=8)
            if prev_resp.status_code == 200 and prev_resp.json():
                row = prev_resp.json()[0]
                LAST_SITREP_CACHE.update(row)
        except Exception:
            pass

    memory_context = await get_operator_memory(client)
    telemetry_dump = json.dumps({
        "local_weather": [{"city": w.get("city"), "temp_c": w.get("temp_c"), "condition": w.get("condition")} for w in weather if w.get("scope") == "LOCAL"],
        "global_and_local_news": [{"title": n.get("title", "").split(" // [TACTICAL INTEL]:")[0], "source": n.get("source"), "scope": n.get("scope")} for n in news[:8]],
        "cyber_alerts": [{"title": c.get("title"), "severity": c.get("severity")} for c in cyber[:5]],
        "wars_and_macro_shocks": [{"headline": m.get("headline"), "theater": m.get("theater"), "severity": m.get("severity")} for m in conflict_macro[:8]]
    })

    prev_sitrep_context = ""
    if LAST_SITREP_CACHE.get("sitrep"):
        prev_sitrep_context = f"""PREVIOUS SITREP GIVEN TO OPERATOR:
- Last SitRep: {LAST_SITREP_CACHE.get('sitrep')}
- Last Theaters: {LAST_SITREP_CACHE.get('conflict_summary')}
- Last Forecast: {LAST_SITREP_CACHE.get('future_risk_forecast')}
"""

    prompt = f"""OPERATOR MEMORY & ASSET PROFILE:
{memory_context}

{prev_sitrep_context}
INCOMING IN-DEPTH TOPIC DEEP DIVES (FRESH DEVELOPMENTS AROUND ACTIVE THEMES):
{json.dumps(topic_deep_dives or [], indent=2)}

INCOMING MULTI-NETWORK TELEMETRY:
{telemetry_dump}

STRICT NON-REPETITION & IN-DEPTH INTELLIGENCE DIRECTIVES:
1. DO NOT repeat the previous briefing or boilerplate statements. The operator already received that briefing.
2. Provide FRESH TACTICAL DEPTH, NEW DEVELOPMENTS, specific logistical/pricing metrics, and emerging details on or around the active subjects.
3. Directly incorporate the IN-DEPTH TOPIC DEEP DIVES (e.g., freight cost surcharges, energy tariffs, specific CVEs, regional diplomacy).
4. If a conflict or economic situation remains ongoing, do not just restate that it is happening; analyze the underlying shift, tactical pivot, or second-order consequences.
5. Synthesize in the sharp operational voice of Cortana / J.A.R.V.I.S.

Output valid JSON strictly matching this schema:
{{
  "threat_level": "NOMINAL" | "ELEVATED" | "CRITICAL",
  "sitrep": "Executive synthesis (under 110 words) focusing on fresh developments, tactical shifts, and active situations without repeating prior statements.",
  "conflict_summary": "In-depth status of active kinetic and logistics flashpoints (Red Sea, Horn of Africa, Eastern Europe, Indo-Pacific) highlighting specific shifts.",
  "future_risk_forecast": "Second-order economic, cyber, or supply-chain shocks projected over the next 7-30 days (fuel/import inflation, KES/USD pressure, cloud/undersea cable risks).",
  "defensive_protocol": "3 concrete actions the operator must take immediately to protect capital, infrastructure, and local operations.",
  "asymmetric_upside": "3 concrete ways the operator can benefit (NSE equity positioning, currency/commodity hedges, or software opportunities created by the crisis)."
}}"""

    try:
        msg = await call_llm_with_failover(
            client,
            [
                {"role": "system", "content": SYSTEM_PERSONA + " Always respond in valid JSON."},
                {"role": "user", "content": prompt}
            ],
            json_mode=True
        )
        parsed = json.loads(msg.get("content", "{}"))

        record = {
            "threat_level": parsed.get("threat_level") or "ELEVATED",
            "sitrep": _clean_bullet_field(parsed.get("sitrep") or parsed.get("situation") or ""),
            "conflict_summary": _clean_bullet_field(parsed.get("conflict_summary") or parsed.get("active_theaters") or parsed.get("theaters") or ""),
            "future_risk_forecast": _clean_bullet_field(parsed.get("future_risk_forecast") or parsed.get("risk_forecast") or parsed.get("forecast") or ""),
            "defensive_protocol": _clean_bullet_field(parsed.get("defensive_protocol") or parsed.get("defensive_actions") or ""),
            "asymmetric_upside": _clean_bullet_field(parsed.get("asymmetric_upside") or parsed.get("upside") or ""),
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        LAST_SITREP_CACHE.update(record)

        if SUPABASE_URL and SUPABASE_SERVICE_KEY:
            await client.post(f"{SUPABASE_URL}/rest/v1/tactical_briefings", headers=SUPABASE_HEADERS, json=record)
        return record
    except Exception as e:
        logger.error(f"[Strategic Synthesis Error]: {e}")
        return {
            "threat_level": "ELEVATED",
            "sitrep": "Sensors active across kinetic and economic theaters. Synthesis operational fault encountered.",
            "conflict_summary": "Telemetry channels streaming.",
            "future_risk_forecast": "Monitor maritime chokepoints and currency liquidity.",
            "defensive_protocol": "• Verify critical backup power\n• Retain offline repository snapshots\n• Maintain USD cash buffers",
            "asymmetric_upside": "• Track high-yield domestic liquidity yields",
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
    if not GROQ_API_KEY and not GEMINI_API_KEY:
        return "Vision OCR requires GEMINI_API_KEY or GROQ_API_KEY."
    try:
        file_resp = await client.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile", params={"file_id": file_id}, timeout=15)
        file_path = file_resp.json()["result"]["file_path"]
        img_bytes = (await client.get(f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}", timeout=25)).content
        b64_image = base64.b64encode(img_bytes).decode("utf-8")

        prompt = (
            "Extract all text, confirmation codes, amounts, dates, merchants, and actionable details "
            f"from this document image. Caption: {caption}"
        )

        # 1. Primary: Google Gemini Vision (massively accurate multi-modal extraction)
        if GEMINI_API_KEY:
            try:
                g_headers = {"Authorization": f"Bearer {GEMINI_API_KEY}", "Content-Type": "application/json"}
                g_payload = {
                    "model": "gemini-3.5-flash-lite",
                    "messages": [{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
                        ]
                    }],
                    "temperature": 0.1
                }
                g_resp = await client.post(GEMINI_CHAT_URL, headers=g_headers, json=g_payload, timeout=35)
                if g_resp.status_code == 200:
                    return g_resp.json()["choices"][0]["message"]["content"]
                else:
                    logger.warning(f"[Gemini Vision {g_resp.status_code}] Falling back to Groq Vision...")
            except Exception as g_err:
                logger.warning(f"[Gemini Vision error]: {g_err}")

        # 2. Secondary Failover: Groq Vision
        if GROQ_API_KEY:
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
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

        return "Vision extraction unavailable."
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
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
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


async def enrich_news_with_depth(client: httpx.AsyncClient, articles: list[dict]) -> tuple[list[dict], list[dict]]:
    """
    Enriches incoming articles with in-depth operational intelligence.
    Extracts structured topic deep dives (latest developments, second-order ripples, and operator impact).
    """
    if not articles or not GROQ_API_KEY:
        return articles, []

    sample = articles[:6]
    items_for_prompt = []
    for a in sample:
        clean_t = a.get("title", "").split(" // [TACTICAL INTEL]:")[0].strip()
        desc = a.get("description", "")[:200].strip()
        items_for_prompt.append({
            "source": a.get("source"),
            "scope": a.get("scope"),
            "title": clean_t,
            "summary": desc if desc else clean_t
        })

    prompt = f"""You are HALO's Tactical Intelligence Analyst.
Analyze these incoming raw news dispatches collected in the latest sweep across global & local sensors:
{json.dumps(items_for_prompt, indent=2)}

Provide IN-DEPTH OPERATIONAL INTELLIGENCE around these subjects. For each distinct subject/theater, extract:
- subject: The active theme title (e.g., 'Red Sea & Bab-el-Mandeb Logistics', 'Kenya Forex & Central Bank Reserves', 'East Africa Energy Grid', 'Critical Infrastructure Cyber Threats')
- latest_developments: Specific new details/developments (do NOT just repeat the headline; explain the latest tactical shift)
- in_depth_context: Underlying mechanics, second-order economic/logistics/security ripples (freight rates, transit delays, inflation pass-through, or patch urgencies)
- why_it_matters: Specific tactical consequence for our operator (Michael Obiero, based in Nairobi/Kitengela, managing tech infrastructure and capital)
- theater: 'RED-SEA-MIDEAST' | 'EAST-AFRICA' | 'CYBER' | 'GLOBAL' | 'KENYA-LOCAL'

Output valid JSON strictly as an array of objects matching this schema:
[
  {{
    "subject": "Theme Title",
    "latest_developments": "...",
    "in_depth_context": "...",
    "why_it_matters": "...",
    "theater": "..."
  }}
]"""

    try:
        msg = await call_llm_with_failover(
            client,
            [
                {"role": "system", "content": SYSTEM_PERSONA + " Always respond in valid JSON."},
                {"role": "user", "content": prompt}
            ],
            json_mode=True
        )
        parsed = json.loads(msg.get("content", "[]"))
        if not isinstance(parsed, list):
            parsed = [parsed] if isinstance(parsed, dict) else []

        # Map deep-dive context back to articles
        enriched_articles = []
        for art in articles:
            clean_title = art["title"].split(" // [TACTICAL INTEL]:")[0].strip()
            matched_dd = None
            for dd in parsed:
                subj_words = [w.lower() for w in dd.get("subject", "").split() if len(w) > 3]
                if any(w in clean_title.lower() for w in subj_words) or any(w in art.get("source", "").lower() for w in subj_words):
                    matched_dd = dd
                    break
            if not matched_dd and parsed:
                matched_dd = parsed[0]

            art_copy = dict(art)
            if matched_dd:
                art_copy["in_depth_context"] = matched_dd.get("in_depth_context", "")
                art_copy["why_it_matters"] = matched_dd.get("why_it_matters", "")
                art_copy["subject"] = matched_dd.get("subject", "ACTIVE THEATER")
                short_note = matched_dd.get("why_it_matters", "")[:180]
                art_copy["title"] = f"{clean_title} // [TACTICAL INTEL]: {short_note}"
            else:
                art_copy["in_depth_context"] = ""
                art_copy["why_it_matters"] = ""
                art_copy["subject"] = art.get("source", "GENERAL")
            enriched_articles.append(art_copy)

        return enriched_articles, parsed
    except Exception as e:
        logger.error(f"[News In-Depth Enrichment Error]: {e}")
        return articles, []


async def sync_news(client: httpx.AsyncClient) -> tuple[list[dict], list[dict]]:
    """
    Ingests fresh news using dynamic rotating topic queries around active subjects.
    Prevents repeating the same headlines on every sweep.
    Enriches dispatches with in-depth tactical intelligence and second-order impacts.
    """
    global SWEEP_CYCLE_INDEX, SEEN_ARTICLE_HASHES
    SWEEP_CYCLE_INDEX += 1

    # Select 2 base feeds + 2 rotating thematic feeds + 2 rotating sports feeds
    active_feeds = list(BASE_NEWS_FEEDS[:2])
    num_rotating = len(ROTATING_TOPIC_FEEDS)
    if num_rotating > 0:
        for offset in range(2):
            idx = (SWEEP_CYCLE_INDEX * 2 + offset) % num_rotating
            active_feeds.append(ROTATING_TOPIC_FEEDS[idx])

    num_sports = len(SPORTS_NEWS_FEEDS)
    if num_sports > 0:
        for offset in range(2):
            s_idx = (SWEEP_CYCLE_INDEX * 2 + offset) % num_sports
            active_feeds.append(SPORTS_NEWS_FEEDS[s_idx])

    candidate_articles = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; TacticalIntel/4.0)"}

    for feed in active_feeds:
        try:
            resp = await client.get(feed["url"], headers=headers, timeout=18)
            if resp.status_code != 200:
                continue
            root = ET.fromstring(resp.content)
            for item in root.findall(".//item")[:6]:
                raw_title = (item.findtext("title") or "Untitled").strip()
                link = item.findtext("link") or ""
                if not raw_title:
                    continue

                raw_desc = (item.findtext("description") or "").strip()
                clean_desc = re.sub(r"<[^>]+>", "", raw_desc).strip()

                content_hash = hashlib.sha256(f"{raw_title}{link}".encode()).hexdigest()
                if content_hash in SEEN_ARTICLE_HASHES:
                    continue
                SEEN_ARTICLE_HASHES.add(content_hash)

                article = {
                    "scope": feed.get("scope", "GLOBAL"),
                    "source": feed.get("source", "News Wire"),
                    "title": raw_title,
                    "description": clean_desc,
                    "link": link,
                    "content_hash": content_hash,
                    "published_at": (item.findtext("pubDate") or "")[:30],
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                candidate_articles.append(article)
        except Exception as e:
            logger.error(f"[News Feed Error - {feed.get('source')}]: {e}")

    # Keep seen cache capped at 250 items
    if len(SEEN_ARTICLE_HASHES) > 250:
        SEEN_ARTICLE_HASHES = set(list(SEEN_ARTICLE_HASHES)[-150:])

    # If candidate articles gathered is small, also fetch latest stored from Supabase to provide depth context
    working_pool = list(candidate_articles)
    if len(working_pool) < 4 and SUPABASE_URL and SUPABASE_SERVICE_KEY:
        try:
            supa_resp = await client.get(f"{SUPABASE_URL}/rest/v1/news_articles?select=*&order=created_at.desc&limit=6", headers=SUPABASE_HEADERS, timeout=8)
            if supa_resp.status_code == 200:
                existing_supa = supa_resp.json()
                for row in existing_supa:
                    if not any(x["content_hash"] == row.get("content_hash") for x in working_pool):
                        working_pool.append(row)
        except Exception:
            pass

    # Enrich working pool with in-depth operational analysis
    enriched_articles, topic_deep_dives = await enrich_news_with_depth(client, working_pool)

    # Persist brand new articles to Supabase via batch insert
    if candidate_articles and SUPABASE_URL and SUPABASE_SERVICE_KEY:
        to_post = []
        for art in enriched_articles:
            if any(c["content_hash"] == art["content_hash"] for c in candidate_articles):
                to_post.append({
                    "scope": art["scope"],
                    "source": art["source"],
                    "title": art["title"],
                    "link": art["link"],
                    "content_hash": art["content_hash"],
                    "published_at": art.get("published_at"),
                    "created_at": art["created_at"]
                })
        if to_post:
            try:
                batch_headers = {**SUPABASE_HEADERS, "Prefer": "resolution=ignore-duplicates"}
                await client.post(f"{SUPABASE_URL}/rest/v1/news_articles?on_conflict=content_hash", headers=batch_headers, json=to_post, timeout=10)
            except Exception:
                pass

    return enriched_articles, topic_deep_dives


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
        except Exception as e:
            logger.error(f"[Cyber Feed Error - {feed['source']}]: {e}")

    # High-efficiency batch insert into Supabase
    if new_alerts and SUPABASE_URL and SUPABASE_SERVICE_KEY:
        try:
            batch_headers = {**SUPABASE_HEADERS, "Prefer": "resolution=ignore-duplicates"}
            await client.post(f"{SUPABASE_URL}/rest/v1/cyber_alerts?on_conflict=content_hash", headers=batch_headers, json=new_alerts, timeout=10)
        except Exception:
            pass

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
        except Exception as e:
            logger.error(f"[Conflict Feed Error - {feed['source']}]: {e}")

    # High-efficiency batch insert into Supabase
    if new_intel and SUPABASE_URL and SUPABASE_SERVICE_KEY:
        try:
            batch_headers = {**SUPABASE_HEADERS, "Prefer": "resolution=ignore-duplicates"}
            await client.post(f"{SUPABASE_URL}/rest/v1/conflict_and_macro_intel?on_conflict=content_hash", headers=batch_headers, json=new_intel, timeout=10)
        except Exception:
            pass

    return new_intel


# =====================================================================
# --- UNIFIED COMMAND QUEUE & DEEP-DIVE RESEARCH PIPELINE ---
# =====================================================================
async def log_and_execute_directive(
    client: httpx.AsyncClient, origin: str, mode: str, directive: str, cmd_id: int = None
) -> str:
    """Unified execution pipeline for both Web HUD and Telegram directives."""
    logger.info(f"Executing [{origin} - {mode}] directive: '{directive}'")

    # If originating from Telegram, create a record in command_queue so it also appears on Web HUD
    if cmd_id is None and SUPABASE_URL and SUPABASE_SERVICE_KEY:
        try:
            insert_payload = {"origin": origin, "mode": mode, "directive": directive, "status": "PROCESSING"}
            resp = await client.post(
                f"{SUPABASE_URL}/rest/v1/command_queue",
                headers={**SUPABASE_HEADERS, "Prefer": "return=representation"},
                json=insert_payload,
                timeout=8
            )
            if resp.status_code == 201 and resp.json():
                cmd_id = resp.json()[0].get("id")
        except Exception as e:
            logger.debug(f"[command_queue insert bypass]: {e}")
    elif cmd_id and SUPABASE_URL and SUPABASE_SERVICE_KEY:
        try:
            await client.patch(
                f"{SUPABASE_URL}/rest/v1/command_queue?id=eq.{cmd_id}",
                headers=SUPABASE_HEADERS,
                json={"status": "PROCESSING"},
                timeout=8
            )
        except Exception:
            pass

    try:
        if mode == "DEEP-DIVE":
            raw_intel = await tool_deep_dive_research(client, directive)
            prompt = (
                f"OPERATOR DEEP-DIVE DIRECTIVE: {directive}\n\n"
                f"LIVE MULTI-SOURCE FIELD INTELLIGENCE:\n{raw_intel}\n\n"
                "Synthesize a comprehensive, movie-grade tactical intelligence dossier for the operator:\n"
                "1. Core Findings & Ground Truth (What is verified happening right now).\n"
                "2. Strategic & Economic Implications (Flashpoints, market impacts, second-order effects).\n"
                "3. Concrete Operator Action Plan (Immediate protective measures and how to benefit/profit)."
            )
            msg = await call_llm_with_failover(
                client,
                [
                    {"role": "system", "content": SYSTEM_PERSONA},
                    {"role": "user", "content": prompt}
                ]
            )
            answer = msg.get("content", "").strip()
        else:
            answer = await run_agent_turn(client, directive)

        if cmd_id and SUPABASE_URL and SUPABASE_SERVICE_KEY:
            try:
                await client.patch(
                    f"{SUPABASE_URL}/rest/v1/command_queue?id=eq.{cmd_id}",
                    headers=SUPABASE_HEADERS,
                    json={
                        "status": "COMPLETED",
                        "response": answer,
                        "completed_at": datetime.now(timezone.utc).isoformat()
                    },
                    timeout=8
                )
            except Exception:
                pass
        return answer

    except Exception as e:
        err_msg = f"Directive execution fault: {e}"
        logger.error(err_msg)
        if cmd_id and SUPABASE_URL and SUPABASE_SERVICE_KEY:
            try:
                await client.patch(
                    f"{SUPABASE_URL}/rest/v1/command_queue?id=eq.{cmd_id}",
                    headers=SUPABASE_HEADERS,
                    json={"status": "FAILED", "response": err_msg},
                    timeout=8
                )
            except Exception:
                pass
        return err_msg


async def web_command_poller(client: httpx.AsyncClient):
    """Polls Supabase every 3 seconds for questions or deep-dive tasks submitted from the Web HUD."""
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        return
    logger.info("Web command queue poller initialized (3s interval)...")
    while True:
        try:
            url = f"{SUPABASE_URL}/rest/v1/command_queue?status=eq.PENDING&order=created_at.asc&limit=3"
            resp = await client.get(url, headers=SUPABASE_HEADERS, timeout=10)
            if resp.status_code == 200:
                commands = resp.json()
                for cmd in commands:
                    answer = await log_and_execute_directive(
                        client,
                        origin=cmd.get("origin", "WEB"),
                        mode=cmd.get("mode", "CHAT"),
                        directive=cmd.get("directive", ""),
                        cmd_id=cmd.get("id")
                    )
                    # Mirror Web HUD query and response to Telegram phone notifications
                    if TELEGRAM_TOKEN and AUTHORIZED_CHAT_ID:
                        mode_icon = "🔬" if cmd.get("mode") == "DEEP-DIVE" else "🌐"
                        await send_telegram(
                            client,
                            f"{mode_icon} *[WEB HUD {cmd.get('mode', 'QUERY')}]:*\n> _{cmd.get('directive')}_\n\n🤖 *CORTANA RESPONSE:*\n{answer}"
                        )
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.debug(f"[Web Command Poller loop]: {e}")

        await asyncio.sleep(3)


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
                        global latest_telegram_event
                        latest_telegram_event = {
                            "event": "TELEGRAM_INCOMING",
                            "user_text": user_text,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        }
                        lower_txt = user_text.lower().strip()
                        is_deep = any(lower_txt.startswith(p) for p in ["/dive ", "dive into ", "investigate ", "/research ", "research "])
                        mode = "DEEP-DIVE" if is_deep else "CHAT"
                        clean_query = user_text
                        for p in ["/dive ", "dive into ", "investigate ", "/research ", "research "]:
                            if lower_txt.startswith(p):
                                clean_query = user_text[len(p):].strip()
                                break

                        if mode == "DEEP-DIVE":
                            await send_telegram(client, f"🔬 Initiating multi-source deep-dive on: '{clean_query}'...")

                        reply = await log_and_execute_directive(client, origin="TELEGRAM", mode=mode, directive=clean_query)
                        await send_telegram(client, reply)
                        latest_telegram_event["reply"] = reply

                        if SUPABASE_URL and SUPABASE_SERVICE_KEY:
                            try:
                                await client.post(
                                    f"{SUPABASE_URL}/rest/v1/bot_memory",
                                    headers={**SUPABASE_HEADERS, "Prefer": "resolution=merge-duplicates"},
                                    json={"memory_key": "latest_telegram_event", "directive": json.dumps(latest_telegram_event)}
                                )
                            except Exception:
                                pass
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


async def execute_complete_sensor_sweep(client: httpx.AsyncClient, is_proactive: bool = False) -> dict:
    """
    Executes a comprehensive, non-repetitive sensor sweep across weather, news, cyber, and conflict/macro streams.
    Dynamically rotates topic search angles on & around active subjects to guarantee fresh intelligence.
    Extracts deep-dive tactical context (developments, underlying mechanics, and operator impact).
    Persists data to Supabase and telemetry_live.json, and optionally dispatches proactive Telegram SitRep.
    """
    logger.info("Initiating dynamic tactical sensor sweep (anti-repetition + in-depth topic rotation)...")
    weather = await sync_weather(client)
    news, topic_deep_dives = await sync_news(client)
    cyber = await sync_cyber_alerts(client)
    conflict_macro = await sync_conflict_and_macro(client)

    b = await synthesize_tactical_sitrep(client, weather, news, cyber, conflict_macro, topic_deep_dives)

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
            "topic_deep_dives": topic_deep_dives if topic_deep_dives else existing.get("topic_deep_dives", []),
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

    global LAST_TELEGRAM_DISPATCH_TIME

    if is_proactive and (news or cyber or conflict_macro or force_sync_event.is_set()) and TELEGRAM_TOKEN and AUTHORIZED_CHAT_ID:
        is_breaking, breaking_reason = is_breaking_news_event(b, news, cyber, conflict_macro)
        now_ts = time.time()
        time_since_last = now_ts - LAST_TELEGRAM_DISPATCH_TIME
        should_dispatch = False

        if is_breaking:
            logger.info(f"[🚨 BREAKING NEWS DETECTED]: {breaking_reason} - Bypassing 20-minute interval and dispatching immediately!")
            should_dispatch = True
        elif force_sync_event.is_set():
            logger.info("[Manual Force Sync]: Triggering Telegram dispatch.")
            should_dispatch = True
        elif time_since_last >= TELEGRAM_DISPATCH_INTERVAL or LAST_TELEGRAM_DISPATCH_TIME == 0.0:
            logger.info(f"[Routine 20-Min Interval Reached]: Elapsed {time_since_last:.0f}s >= {TELEGRAM_DISPATCH_INTERVAL}s. Dispatching SitRep.")
            should_dispatch = True
        else:
            remaining_m = int((TELEGRAM_DISPATCH_INTERVAL - time_since_last) // 60)
            remaining_s = int((TELEGRAM_DISPATCH_INTERVAL - time_since_last) % 60)
            logger.info(f"[Telegram Standby]: Nominal conditions (no breaking news). Next routine dispatch in {remaining_m}m {remaining_s}s. Telemetry recorded silently.")

        if should_dispatch:
            try:
                deep_dives_summary = ""
                if topic_deep_dives:
                    bullets = []
                    for dd in topic_deep_dives[:3]:
                        bullets.append(f"• *{dd.get('subject', 'THEATER')}:* {dd.get('latest_developments', '')}\n  ↳ _Tactical Impact:_ {dd.get('why_it_matters', '')}")
                    deep_dives_summary = "\n\n2. *IN-DEPTH THEATER EVOLUTION (ACTIVE SUBJECTS):*\n" + "\n".join(bullets)

                header_prefix = "🚨 *BREAKING TACTICAL ALERT" if is_breaking else "🛡️ *OVERWATCH SITREP"
                breaking_banner = f"\n⚠️ *FLASH TRIGGER:* _{breaking_reason}_\n" if is_breaking else ""

                telegram_dispatch = (
                    f"{header_prefix} // [{b['threat_level']}]*\n"
                    f"{breaking_banner}\n"
                    f"1. *TACTICAL SITUATION & NEW DEVELOPMENTS:*\n{b['sitrep']}"
                    f"{deep_dives_summary}\n\n"
                    f"3. *ACTIVE THEATERS & CHOKEPOINTS:*\n{b['conflict_summary']}\n\n"
                    f"4. *SECOND-ORDER RISK FORECAST (7-30 DAYS):*\n{b['future_risk_forecast']}\n\n"
                    f"5. *DEFENSIVE PROTOCOL:*\n{b['defensive_protocol']}\n\n"
                    f"6. *ASYMMETRIC UPSIDE:*\n{b['asymmetric_upside']}"
                )
                await send_telegram(client, telegram_dispatch)
                LAST_TELEGRAM_DISPATCH_TIME = now_ts
            except Exception as e:
                logger.error(f"[Synthesis Dispatch Error]: {e}")

    return {
        "sitrep": b,
        "weather": weather,
        "news": news,
        "cyber": cyber,
        "conflicts": conflict_macro,
        "deep_dives": topic_deep_dives
    }


async def collector_worker(client: httpx.AsyncClient):
    """
    Executes continuous sensor sweeps (default every 5 minutes to rapidly intercept
    breaking news events and update live telemetry), while enforcing a strict 20-minute
    dispatch interval for routine non-breaking Telegram SitReps.
    """
    sweep_sleep = min(SYNC_INTERVAL, 300)
    logger.info(f"Tactical telemetry daemon active (Sweep cycle: {sweep_sleep}s, Telegram routine cadence: {TELEGRAM_DISPATCH_INTERVAL}s)...")
    while True:
        try:
            await execute_complete_sensor_sweep(client, is_proactive=True)
        except Exception as ce:
            logger.error(f"[Collector Cycle Error]: {ce}")

        try:
            await asyncio.wait_for(force_sync_event.wait(), timeout=sweep_sleep)
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
            asyncio.create_task(web_command_poller(client)),
            asyncio.create_task(collector_worker(client)),
            asyncio.create_task(reminder_worker(client)),
            asyncio.create_task(start_local_command_server(5050))
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
