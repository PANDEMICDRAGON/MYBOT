import os
import sys
import time
import asyncio
import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path

import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("CollectorBot")

# Load environment variables from .env if present
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

# Environment Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
AUTHORIZED_CHAT_ID_RAW = os.getenv("TELEGRAM_CHAT_ID", "").strip()
SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()
SCRAPE_INTERVAL = int(os.getenv("SCRAPE_INTERVAL", "300"))

# Validate required configuration
missing_vars = []
if not TELEGRAM_TOKEN or "YOUR_" in TELEGRAM_TOKEN:
    missing_vars.append("TELEGRAM_TOKEN")
if not AUTHORIZED_CHAT_ID_RAW or not AUTHORIZED_CHAT_ID_RAW.lstrip("-").isdigit():
    missing_vars.append("TELEGRAM_CHAT_ID")
if not SUPABASE_URL or "your-project" in SUPABASE_URL:
    missing_vars.append("SUPABASE_URL")
if not SUPABASE_KEY or "YOUR_" in SUPABASE_KEY:
    missing_vars.append("SUPABASE_KEY")

AUTHORIZED_CHAT_ID = int(AUTHORIZED_CHAT_ID_RAW) if AUTHORIZED_CHAT_ID_RAW.lstrip("-").isdigit() else 0

SUPABASE_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

BOOT_TIME = time.time()
force_scrape_event = asyncio.Event()


# ==============================================================================
# --- MODULAR PROCESSING HOOK (FUTURE AI / LLM EXTENSION POINT) ---
# ==============================================================================
async def process_extracted_data(raw_items: list[str], url: str = "") -> str:
    """
    Format raw scraped DOM texts.
    When ready to enable AI, replace or augment this function to call Gemini, Groq, etc.
    """
    cleaned = [item.strip() for item in raw_items if item.strip()]
    if not cleaned:
        return ""
    # Deduplicate while preserving order
    seen = set()
    unique_items = []
    for item in cleaned:
        if item not in seen:
            seen.add(item)
            unique_items.append(item)
            
    # Return formatted list (max 15 items per alert to avoid exceeding Telegram message limits)
    return "\n• ".join(unique_items[:15])


# ==============================================================================
# --- SUPABASE DATABASE OPERATIONS ---
# ==============================================================================
async def db_get_targets(client: httpx.AsyncClient) -> list[dict]:
    """Fetch active targets from Supabase bot_targets table."""
    url = f"{SUPABASE_URL}/rest/v1/bot_targets?active=eq.true&select=*"
    resp = await client.get(url, headers=SUPABASE_HEADERS, timeout=15)
    resp.raise_for_status()
    return resp.json()


async def db_add_target(client: httpx.AsyncClient, target_url: str, selector: str) -> dict:
    """Add a new target to bot_targets table."""
    url = f"{SUPABASE_URL}/rest/v1/bot_targets"
    payload = {"url": target_url, "selector": selector, "active": True}
    resp = await client.post(url, headers=SUPABASE_HEADERS, json=payload, timeout=15)
    resp.raise_for_status()
    rows = resp.json()
    return rows[0] if isinstance(rows, list) and rows else {"id": "unknown", "url": target_url, "selector": selector}


async def db_remove_target(client: httpx.AsyncClient, target_id: int) -> bool:
    """Delete a target from bot_targets table."""
    url = f"{SUPABASE_URL}/rest/v1/bot_targets?id=eq.{target_id}"
    resp = await client.delete(url, headers=SUPABASE_HEADERS, timeout=15)
    return resp.status_code in (200, 204)


async def db_store_if_new(
    client: httpx.AsyncClient, target_id: int, source_url: str, content_hash: str, data: str
) -> bool:
    """Check if content hash exists; if not, insert and return True."""
    check_url = f"{SUPABASE_URL}/rest/v1/bot_records?content_hash=eq.{content_hash}&select=id"
    check_resp = await client.get(check_url, headers=SUPABASE_HEADERS, timeout=15)
    if check_resp.status_code == 200 and len(check_resp.json()) > 0:
        return False  # Already seen this exact content

    insert_url = f"{SUPABASE_URL}/rest/v1/bot_records"
    payload = {
        "target_id": target_id,
        "source_url": source_url,
        "content_hash": content_hash,
        "extracted_data": data,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    insert_resp = await client.post(insert_url, headers=SUPABASE_HEADERS, json=payload, timeout=15)
    return insert_resp.status_code == 201


# ==============================================================================
# --- TELEGRAM MESSAGING & COMMAND ROUTER ---
# ==============================================================================
async def send_telegram(client: httpx.AsyncClient, text: str):
    """Send text message to authorized Telegram chat (splits if > 4096 chars)."""
    if not TELEGRAM_TOKEN or not AUTHORIZED_CHAT_ID:
        logger.warning(f"[Mock Telegram Output]: {text}")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    chunk_size = 4000
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        payload = {"chat_id": AUTHORIZED_CHAT_ID, "text": chunk}
        try:
            resp = await client.post(url, json=payload, timeout=15)
            if resp.status_code != 200:
                logger.error(f"Telegram API error ({resp.status_code}): {resp.text}")
        except Exception as e:
            logger.error(f"Telegram send error: {e}")


async def handle_command(client: httpx.AsyncClient, text: str):
    """Parse and execute incoming bot commands."""
    parts = text.strip().split(maxsplit=2)
    cmd = parts[0].lower()
    logger.info(f"Received command: {cmd}")

    if cmd in ("/start", "/help"):
        msg = (
            "🤖 *24/7 Web Collector Bot Active*\n\n"
            "*Commands:*\n"
            "• `/add <url> [css_selector]` — Add target to monitor\n"
            "• `/list` — View all active targets\n"
            "• `/remove <id>` — Delete target by ID\n"
            "• `/run` — Trigger immediate scrape cycle\n"
            "• `/status` — View uptime and system metrics"
        )
        await send_telegram(client, msg)

    elif cmd == "/add":
        if len(parts) < 2:
            await send_telegram(client, "⚠️ Usage: `/add https://example.com h2` (default selector is 'title')")
            return
        target_url = parts[1]
        selector = parts[2] if len(parts) == 3 else "title"
        try:
            row = await db_add_target(client, target_url, selector)
            await send_telegram(
                client, 
                f"✅ Added Target [ID: {row.get('id')}]:\nURL: {target_url}\nSelector: `{selector}`"
            )
        except Exception as e:
            await send_telegram(client, f"❌ Failed to add target: {e}")

    elif cmd == "/list":
        try:
            targets = await db_get_targets(client)
            if not targets:
                await send_telegram(client, "ℹ️ No active targets registered in database.")
                return
            lines = [f"• ID {t['id']}: {t['url']} (Selector: `{t['selector']}`)" for t in targets]
            await send_telegram(client, "📋 *Active Targets:*\n" + "\n".join(lines))
        except Exception as e:
            await send_telegram(client, f"❌ Failed to retrieve targets: {e}")

    elif cmd == "/remove":
        if len(parts) < 2 or not parts[1].isdigit():
            await send_telegram(client, "⚠️ Usage: `/remove <id>` (e.g., `/remove 1`)")
            return
        try:
            target_id = int(parts[1])
            success = await db_remove_target(client, target_id)
            await send_telegram(client, f"🗑️ Target {target_id} removed." if success else f"❌ Target {target_id} not found.")
        except Exception as e:
            await send_telegram(client, f"❌ Error removing target: {e}")

    elif cmd == "/run":
        await send_telegram(client, "⚡ Manual scrape cycle triggered.")
        force_scrape_event.set()

    elif cmd == "/status":
        uptime_min = int((time.time() - BOOT_TIME) // 60)
        try:
            targets = await db_get_targets(client)
            active_count = len(targets)
        except Exception:
            active_count = "Unavailable (DB Error)"
        await send_telegram(
            client,
            f"📊 *System Status*\n"
            f"• State: ONLINE (24/7 Long Polling)\n"
            f"• Uptime: {uptime_min} minutes\n"
            f"• Active Targets: {active_count}\n"
            f"• Auto-Interval: {SCRAPE_INTERVAL}s"
        )


async def telegram_poller(client: httpx.AsyncClient):
    """Maintain long-polling loop with Telegram server."""
    if not TELEGRAM_TOKEN or not AUTHORIZED_CHAT_ID:
        logger.warning("Telegram credentials not configured. Poller loop disabled.")
        return

    offset = 0
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    logger.info("Telegram poller started listening for commands...")
    
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


# ==============================================================================
# --- SCRAPER & EXTRACTION ENGINE ---
# ==============================================================================
async def execute_scrape_cycle(client: httpx.AsyncClient):
    """Fetch targets, extract matching selectors, deduplicate, and push updates."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        targets = await db_get_targets(client)
    except Exception as e:
        logger.error(f"Database error fetching targets: {e}")
        return

    if not targets:
        logger.info("No active targets to scrape.")
        return

    logger.info(f"Running scrape cycle across {len(targets)} target(s)...")

    for t in targets:
        url = t["url"]
        selector = t.get("selector", "title")
        try:
            resp = await client.get(url, headers=headers, timeout=25)
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, "html.parser")
            elements = [el.get_text(" ", strip=True) for el in soup.select(selector)]

            if not elements:
                logger.info(f"No elements matched selector '{selector}' on {url}")
                continue

            formatted_output = await process_extracted_data(elements, url=url)
            if not formatted_output:
                continue

            content_hash = hashlib.sha256(formatted_output.encode("utf-8")).hexdigest()

            is_new = await db_store_if_new(client, t["id"], url, content_hash, formatted_output)
            if is_new:
                logger.info(f"🔔 NEW DATA detected on {url}")
                alert = f"🔔 *[NEW DATA]*\n🌐 `{url}`\n🎯 Selector: `{selector}`\n\n• {formatted_output}"
                await send_telegram(client, alert)
            else:
                logger.info(f"No changes detected on {url} (hash match).")

        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")


async def scraper_worker(client: httpx.AsyncClient):
    """Background loop that executes periodic scrape cycles."""
    logger.info(f"Scraper worker started (Interval: {SCRAPE_INTERVAL}s)...")
    while True:
        try:
            await execute_scrape_cycle(client)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Unexpected worker error: {e}")

        try:
            # Wait either for the scrape interval or an immediate trigger via /run
            await asyncio.wait_for(force_scrape_event.wait(), timeout=SCRAPE_INTERVAL)
            force_scrape_event.clear()
            logger.info("Triggered instant scrape cycle via manual event.")
        except asyncio.TimeoutError:
            pass
        except asyncio.CancelledError:
            break


# ==============================================================================
# --- MAIN APPLICATION ENTRY POINT ---
# ==============================================================================
async def main():
    if missing_vars:
        logger.warning(
            "⚠️ The following environment variables are missing or default in .env:\n"
            f"   {', '.join(missing_vars)}\n"
            "   Please configure .env with your credentials before running for production 24/7 operation.\n"
        )

    limits = httpx.Limits(max_keepalive_connections=10, max_connections=20)
    async with httpx.AsyncClient(follow_redirects=True, limits=limits) as client:
        if TELEGRAM_TOKEN and AUTHORIZED_CHAT_ID:
            await send_telegram(client, "🚀 Core Bot daemon initialized. Send /help for commands.")
        
        # Run poller and worker concurrently
        tasks = [
            asyncio.create_task(telegram_poller(client)),
            asyncio.create_task(scraper_worker(client))
        ]
        
        try:
            await asyncio.gather(*tasks)
        except (KeyboardInterrupt, asyncio.CancelledError):
            logger.info("Shutting down bot gracefully...")
            for task in tasks:
                task.cancel()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
