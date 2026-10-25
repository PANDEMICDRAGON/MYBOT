#!/usr/bin/env python3
"""
=====================================================================
4-LAYER PLANETARY OSINT & BEHAVIORAL RECONNAISSANCE ENGINE
=====================================================================
Zero-cost multi-platform reconnaissance bypassing paywalls via:
- Layer 1: Keyless direct stream gateways (Reddit JSON + Telegram Web)
- Layer 2: Stealth headless browser swarm (Playwright Chromium node with automation masking)
- Layer 3: Multi-platform search dorking (X/Twitter, LinkedIn, Instagram, Web OSINT)
- Layer 4: Behavioral & Game-Theory analytical pipeline (Evolutionary Psychology + Payoffs)
"""

import os
import sys
import json
import random
import asyncio
import urllib.parse
from datetime import datetime, timezone
import httpx
from bs4 import BeautifulSoup

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
]

BEHAVIORAL_DOCTRINE_PROMPT = """You are HALO's Planetary OSINT and Behavioral Intelligence Decoder.
Analyze the incoming social media, forum, and public footprint telemetry through two strict analytical lenses:
1. EVOLUTIONARY PSYCHOLOGY: Decode status games, prestige vs. dominance hierarchy posturing, costly signaling vs. cheap talk (virtue signaling without skin in the game), in-group coalition enforcement, and mimetic contagion.
2. GAME THEORY & INCENTIVE STRUCTURES: Identify the underlying payoff matrix, principal-agent problems, asymmetric information advantages, liquidity/attention farming (exit-liquidity traps), and coordinated narrative astroturfing.

Return valid JSON strictly matching this schema:
{
  "sentiment_vector": "Polarity label and score from -1.0 to +1.0, plus dominant crowd emotion (e.g. 'FEAR / CAPITULATION (-0.68)').",
  "status_signaling": "Analysis of status signals, coalition behavior, and whether actors have real skin in the game or are engaging in performative signaling.",
  "game_theory_matrix": "Breakdown of hidden financial/political incentives, who profits from this narrative, and the equilibrium outcome.",
  "narrative_coordination": "Assessment of organic discourse vs. coordinated PR, bot amplification, or memetic engineering.",
  "operator_counterplay": "3 concrete tactical actions for the operator to exploit the crowd mispricing, protect assets, or leverage the intelligence."
}"""


# --- LAYER 1: API GATEWAY & KEYLESS STREAM INGESTION (REDDIT JSON + TELEGRAM WEB) ---
async def ingest_reddit_stream(client: httpx.AsyncClient, query: str, limit: int = 8) -> list[dict]:
    """Pulls live threads, upvote ratios, and comment velocity directly from Reddit's JSON gateway."""
    encoded = urllib.parse.quote_plus(query)
    url = f"https://www.reddit.com/search.json?q={encoded}&sort=new&limit={limit}"
    headers = {"User-Agent": f"linux:halo.osint.engine:v4.0 (by /u/operator_{random.randint(1000,9999)})"}
    results = []
    try:
        resp = await client.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            children = resp.json().get("data", {}).get("children", [])
            for c in children:
                d = c.get("data", {})
                results.append({
                    "platform": "REDDIT",
                    "author": d.get("author", "unknown"),
                    "subreddit": d.get("subreddit_name_prefixed", ""),
                    "title": d.get("title", ""),
                    "text": (d.get("selftext") or "")[:400],
                    "metrics": f"Score: {d.get('score', 0)} | Upvote Ratio: {d.get('upvote_ratio', 0)} | Comments: {d.get('num_comments', 0)}",
                    "url": f"https://www.reddit.com{d.get('permalink', '')}"
                })
    except Exception as e:
        print(f"[OSINT Reddit Error]: {e}")
    return results


async def ingest_telegram_public_channel(client: httpx.AsyncClient, channel_handle: str, limit: int = 6) -> list[dict]:
    """Scrapes public Telegram channel web previews (https://t.me/s/<channel>) without API keys."""
    clean_handle = channel_handle.strip().lstrip("@").split("/")[-1]
    url = f"https://t.me/s/{clean_handle}"
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    results = []
    try:
        resp = await client.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            bubbles = soup.select(".tgme_widget_message_wrap")[-limit:]
            for b in bubbles:
                text_el = b.select_one(".tgme_widget_message_text")
                views_el = b.select_one(".tgme_widget_message_views")
                date_el = b.select_one("time")
                link_el = b.select_one(".tgme_widget_message_date")
                if text_el:
                    results.append({
                        "platform": f"TELEGRAM (@{clean_handle})",
                        "title": text_el.get_text(" ", strip=True)[:120],
                        "text": text_el.get_text(" ", strip=True)[:500],
                        "metrics": f"Views: {views_el.get_text(strip=True) if views_el else 'N/A'} | Time: {date_el.get('datetime', '') if date_el else ''}",
                        "url": link_el.get("href", url) if link_el else url
                    })
    except Exception as e:
        print(f"[OSINT Telegram Error]: {e}")
    return results


# --- LAYER 2: STEALTH HEADLESS BROWSER SWARM (PLAYWRIGHT ANTI-DETECT NODE) ---
async def stealth_browser_harvest(target_url: str) -> dict:
    """
    Launches a headless Chromium instance with masked automation flags to extract
    rendered DOM text and metadata from JS-protected social/web targets.
    """
    if not PLAYWRIGHT_AVAILABLE:
        return {"platform": "STEALTH-BROWSER", "title": "Bypassed", "text": "Playwright not installed in environment.", "metrics": "N/A", "url": target_url}

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
            )
            context = await browser.new_context(
                user_agent=random.choice(USER_AGENTS),
                viewport={"width": 1366, "height": 768},
                locale="en-US"
            )
            # Mask navigator.webdriver and automation fingerprints
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                window.chrome = { runtime: {} };
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            """)

            page = await context.new_page()
            try:
                await page.goto(target_url, wait_until="domcontentloaded", timeout=20000)
                await page.wait_for_timeout(2000)
                title = await page.title()
                meta_desc = await page.evaluate(
                    "() => document.querySelector('meta[name=\"description\"], meta[property=\"og:description\"]')?.content || ''"
                )
                body_text = await page.evaluate("() => document.body ? document.body.innerText : ''")
                await browser.close()
                return {
                    "platform": "STEALTH-BROWSER",
                    "title": title[:150],
                    "text": f"Meta: {meta_desc}\nBody: {' '.join(body_text.split())[:1800]}",
                    "metrics": "Direct DOM Render",
                    "url": target_url
                }
            except Exception as e:
                await browser.close()
                return {"platform": "STEALTH-BROWSER", "title": "Harvest Failed", "text": str(e), "metrics": "Error", "url": target_url}
    except Exception as launch_err:
        return {"platform": "STEALTH-BROWSER", "title": "Browser Launch Error", "text": str(launch_err), "metrics": "Error", "url": target_url}


# --- LAYER 3: OSINT AGGREGATORS & MULTI-PLATFORM SEARCH DORKING ---
async def execute_platform_dorks(client: httpx.AsyncClient, query: str) -> list[dict]:
    """
    Uses search engine dorking to extract public footprints across X/Twitter, LinkedIn,
    and Instagram without triggering platform login walls.
    """
    dork_targets = [
        ("X / TWITTER", f'site:x.com OR site:twitter.com "{query}"'),
        ("LINKEDIN", f'site:linkedin.com/in/ OR site:linkedin.com/posts/ "{query}"'),
        ("INSTAGRAM", f'site:instagram.com "{query}"'),
        ("WEB OSINT", f'"{query}" (sentiment OR controversy OR announcement OR leak OR analysis)')
    ]

    headers = {"User-Agent": random.choice(USER_AGENTS)}
    footprints = []

    async def run_single_dork(platform_label: str, dork_query: str):
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote_plus(dork_query)}"
        try:
            resp = await client.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(resp.text, "html.parser")
            for res in soup.select(".result__body")[:4]:
                t_el = res.select_one(".result__title")
                s_el = res.select_one(".result__snippet")
                u_el = res.select_one(".result__url")
                if t_el and s_el:
                    raw_link = u_el.get_text(strip=True) if u_el else ""
                    clean_url = f"https://{raw_link}" if raw_link and not raw_link.startswith("http") else raw_link
                    footprints.append({
                        "platform": platform_label,
                        "title": t_el.get_text(" ", strip=True),
                        "text": s_el.get_text(" ", strip=True),
                        "metrics": "Indexed OSINT Footprint",
                        "url": clean_url
                    })
        except Exception as e:
            print(f"[Dork Error - {platform_label}]: {e}")

    await asyncio.gather(*(run_single_dork(label, dq) for label, dq in dork_targets))
    return footprints


# --- LAYER 4: FULL RECONNAISSANCE & BEHAVIORAL DECODER PIPELINE ---
async def run_planetary_recon(
    client: httpx.AsyncClient,
    target_query: str,
    llm_caller=None,
    supabase_url: str = "",
    supabase_headers: dict = None,
    telegram_channels: list[str] = None
) -> dict:
    """
    Orchestrates all 4 layers concurrently, decodes the corpus via Evolutionary Psychology
    and Game Theory, and stores the report in Supabase.
    """
    # If llm_caller not supplied, use halo_agent's call_llm
    if llm_caller is None:
        try:
            from halo_agent import call_llm
            llm_caller = call_llm
        except Exception:
            raise RuntimeError("llm_caller must be provided or halo_agent.call_llm must be importable.")

    tg_list = telegram_channels or ["disclosetv", "unusual_whales"]

    # Run Layer 1 (Reddit + Telegram) and Layer 3 (X, LinkedIn, Instagram Dorks) concurrently
    reddit_task = ingest_reddit_stream(client, target_query, limit=8)
    dork_task = execute_platform_dorks(client, target_query)
    tg_tasks = [ingest_telegram_public_channel(client, ch, limit=4) for ch in tg_list]

    gathered = await asyncio.gather(reddit_task, dork_task, *tg_tasks)
    reddit_data = gathered[0]
    dork_data = gathered[1]
    tg_data = [item for sublist in gathered[2:] for item in sublist]

    all_footprints = reddit_data + dork_data + tg_data

    # Optional Layer 2: If target_query contains an explicit URL, deploy Stealth Playwright Node
    if "http://" in target_query or "https://" in target_query:
        urls = [w for w in target_query.split() if w.startswith("http")]
        if urls:
            browser_hit = await stealth_browser_harvest(urls[0])
            all_footprints.insert(0, browser_hit)

    platforms_found = sorted(list({f["platform"] for f in all_footprints}))
    corpus_text = "\n\n".join([
        f"[{f['platform']}] {f['title']}\nSnippet: {f['text']}\nMetrics: {f.get('metrics', '')}\nURL: {f.get('url', '')}"
        for f in all_footprints[:28]
    ])

    user_prompt = (
        f"RECONNAISSANCE TARGET: {target_query}\n"
        f"PLATFORMS INTERCEPTED: {', '.join(platforms_found)}\n\n"
        f"--- RAW MULTI-PLATFORM SOCIAL & OSINT TELEMETRY ---\n"
        f"{corpus_text if corpus_text else 'Minimal public surface area detected; infer from target domain context.'}"
    )

    raw_json = await llm_caller(
        client,
        [
            {"role": "system", "content": BEHAVIORAL_DOCTRINE_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        json_mode=True
    )

    # Support both string content return (halo_agent.py) and dict message return (bot.py)
    if isinstance(raw_json, dict):
        raw_json = raw_json.get("content", "{}")

    try:
        parsed = json.loads(raw_json)
    except Exception:
        parsed = {}

    report = {
        "target_query": target_query,
        "platforms_scanned": platforms_found,
        "sentiment_vector": parsed.get("sentiment_vector", "NEUTRAL (0.0)"),
        "status_signaling": parsed.get("status_signaling", ""),
        "game_theory_matrix": parsed.get("game_theory_matrix", ""),
        "narrative_coordination": parsed.get("narrative_coordination", ""),
        "operator_counterplay": parsed.get("operator_counterplay", ""),
        "raw_footprints": all_footprints[:15],
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    if supabase_url and supabase_headers:
        try:
            await client.post(
                f"{supabase_url}/rest/v1/osint_recon_reports",
                headers=supabase_headers,
                json=report,
                timeout=10
            )
        except Exception as e:
            print(f"[Supabase OSINT Log Error]: {e}")

    return report
