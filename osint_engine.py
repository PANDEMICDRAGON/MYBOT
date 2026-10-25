import os
import re
import json
import random
import hashlib
import asyncio
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import httpx
from bs4 import BeautifulSoup

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# Optional Credentials & Proxy Pool (Comma-separated http/socks5 proxies)
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
DISCORD_CHANNEL_IDS = [c.strip() for c in os.getenv("DISCORD_CHANNEL_IDS", "").split(",") if c.strip()]
PROXY_POOL = [p.strip() for p in os.getenv("OSINT_PROXY_LIST", "").split(",") if p.strip()]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
]

BEHAVIORAL_DOCTRINE_PROMPT = """You are HALO's Tier-4 Planetary Intelligence Processing Engine.
You receive multi-platform social telemetry, video transcripts, imageboard dumps, and engagement metrics across Tier-1 APIs, Tier-2 Walled Gardens, and Tier-3 Unstructured Boards.
Filter all incoming data through our two core doctrines:
1. EVOLUTIONARY PSYCHOLOGY: Decode status hierarchy maneuvers (prestige vs. dominance), costly signaling vs. zero-cost virtue signaling, tribal coalition building, fear/greed contagion, and mimetic desire.
2. GAME THEORY & INCENTIVE MATRIX: Expose principal-agent divergences, asymmetric information advantages, attention/liquidity harvesting (who is using retail crowd sentiment as exit liquidity), and coordinated narrative operations.

Return valid JSON strictly matching this schema:
{
  "sentiment_vector": "Quantitative polarity (-1.0 to +1.0) and dominant psychological state across tiers.",
  "status_signaling": "Evolutionary psychology breakdown of status games, coalition posturing, and skin-in-the-game verification.",
  "game_theory_matrix": "Underlying payoff matrix, hidden financial/political motives, and Nash equilibrium projection.",
  "narrative_coordination": "Cross-platform propagation analysis (e.g., 4chan/Telegram origin -> X/TikTok amplification -> mainstream synthesis).",
  "operator_counterplay": "3 concrete, high-leverage actions for the operator to protect capital/infrastructure and exploit the crowd mispricing."
}"""


# =====================================================================
# TIER 1: THE API TIER (REDDIT, YOUTUBE + TRANSCRIPTS, MASTODON, TELEGRAM, DISCORD)
# =====================================================================

async def tier1_reddit(client: httpx.AsyncClient, query: str, limit: int = 6) -> list[dict]:
    url = f"https://www.reddit.com/search.json?q={urllib.parse.quote_plus(query)}&sort=relevance&t=week&limit={limit}"
    headers = {"User-Agent": f"linux:halo.recon:v5.0 (by /u/op_{random.randint(1000,9999)})"}
    out = []
    try:
        resp = await client.get(url, headers=headers, timeout=12)
        if resp.status_code == 200:
            for c in resp.json().get("data", {}).get("children", []):
                d = c.get("data", {})
                out.append({
                    "tier": "TIER_1_API",
                    "platform": "REDDIT",
                    "author": d.get("author", "anon"),
                    "title": f"[{d.get('subreddit_name_prefixed', 'r/all')}] {d.get('title', '')}",
                    "text": (d.get("selftext") or d.get("title") or "")[:500],
                    "metrics": f"Score: {d.get('score', 0)} | Ratio: {d.get('upvote_ratio', 0)} | Comments: {d.get('num_comments', 0)}",
                    "url": f"https://www.reddit.com{d.get('permalink', '')}"
                })
    except Exception as e:
        print(f"[Tier1 Reddit Error]: {e}")
    return out


async def fetch_youtube_transcript(client: httpx.AsyncClient, video_id: str) -> str:
    """Extracts closed-caption transcript text directly from YouTube watch page captionTracks."""
    try:
        watch_url = f"https://www.youtube.com/watch?v={video_id}"
        resp = await client.get(watch_url, headers={"User-Agent": random.choice(USER_AGENTS)}, timeout=12)
        match = re.search(r'"captionTracks":(\[.*?\])', resp.text)
        if not match:
            return ""
        tracks = json.loads(match.group(1))
        if not tracks:
            return ""
        base_url = tracks[0].get("baseUrl")
        if not base_url:
            return ""
        xml_resp = await client.get(base_url, timeout=10)
        root = ET.fromstring(xml_resp.content)
        lines = [el.text.strip() for el in root.findall(".//text") if el.text]
        return " ".join(lines)[:1500]
    except Exception:
        return ""


async def tier1_youtube(client: httpx.AsyncClient, query: str, limit: int = 3) -> list[dict]:
    """Searches YouTube via Innertube JSON API and extracts video transcripts."""
    url = "https://www.youtube.com/youtubei/v1/search"
    payload = {
        "context": {
            "client": {"clientName": "WEB", "clientVersion": "2.20260101.00.00", "hl": "en", "gl": "US"}
        },
        "query": query
    }
    out = []
    try:
        resp = await client.post(url, json=payload, headers={"User-Agent": random.choice(USER_AGENTS)}, timeout=15)
        if resp.status_code != 200:
            return out
        raw_str = resp.text
        video_ids = []
        for match in re.finditer(r'"videoRenderer":\{"videoId":"([a-zA-Z0-9_-]{11})".*?"title":\{"runs":\[\{"text":"(.*?)"\}', raw_str):
            vid, title = match.group(1), match.group(2)
            if vid not in [v[0] for v in video_ids]:
                video_ids.append((vid, title))
            if len(video_ids) >= limit:
                break

        for vid, title in video_ids:
            transcript = await fetch_youtube_transcript(client, vid)
            out.append({
                "tier": "TIER_1_API",
                "platform": "YOUTUBE",
                "author": "YouTube Creator",
                "title": title,
                "text": f"[TRANSCRIPT EXTRACT]: {transcript}" if transcript else f"Video Title: {title}",
                "metrics": "Transcript Parsed" if transcript else "Metadata Only",
                "url": f"https://www.youtube.com/watch?v={vid}"
            })
    except Exception as e:
        print(f"[Tier1 YouTube Error]: {e}")
    return out


async def tier1_mastodon(client: httpx.AsyncClient, query: str, limit: int = 5) -> list[dict]:
    """Queries public Fediverse tag/status timelines via Mastodon REST API."""
    tag = re.sub(r"[^a-zA-Z0-9]", "", query.split()[0]) if query.strip() else "news"
    if not tag:
        tag = "news"
    url = f"https://mastodon.social/api/v1/timelines/tag/{tag}?limit={limit}"
    out = []
    try:
        resp = await client.get(url, timeout=12)
        if resp.status_code == 200:
            for post in resp.json():
                clean_html = BeautifulSoup(post.get("content", ""), "html.parser").get_text(" ", strip=True)
                acct = post.get("account", {}).get("acct", "fediverse_user")
                out.append({
                    "tier": "TIER_1_API",
                    "platform": "MASTODON",
                    "author": acct,
                    "title": clean_html[:90],
                    "text": clean_html[:450],
                    "metrics": f"Boosts: {post.get('reblogs_count', 0)} | Favs: {post.get('favourites_count', 0)}",
                    "url": post.get("url", "")
                })
    except Exception as e:
        print(f"[Tier1 Mastodon Error]: {e}")
    return out


async def tier1_telegram(client: httpx.AsyncClient, channel: str, limit: int = 4) -> list[dict]:
    clean = channel.strip().lstrip("@").split("/")[-1]
    url = f"https://t.me/s/{clean}"
    out = []
    try:
        resp = await client.get(url, headers={"User-Agent": random.choice(USER_AGENTS)}, timeout=12)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            for b in soup.select(".tgme_widget_message_wrap")[-limit:]:
                t_el = b.select_one(".tgme_widget_message_text")
                v_el = b.select_one(".tgme_widget_message_views")
                l_el = b.select_one(".tgme_widget_message_date")
                if t_el:
                    txt = t_el.get_text(" ", strip=True)
                    out.append({
                        "tier": "TIER_1_API",
                        "platform": "TELEGRAM",
                        "author": f"@{clean}",
                        "title": txt[:90],
                        "text": txt[:450],
                        "metrics": f"Views: {v_el.get_text(strip=True) if v_el else 'N/A'}",
                        "url": l_el.get("href", url) if l_el else url
                    })
    except Exception as e:
        print(f"[Tier1 Telegram Error]: {e}")
    return out


async def tier1_discord(client: httpx.AsyncClient, query: str) -> list[dict]:
    """Reads recent messages from configured Discord channels if DISCORD_BOT_TOKEN is present."""
    if not DISCORD_BOT_TOKEN or not DISCORD_CHANNEL_IDS:
        return []
    headers = {"Authorization": f"Bot {DISCORD_BOT_TOKEN}"}
    out = []
    for cid in DISCORD_CHANNEL_IDS[:3]:
        try:
            resp = await client.get(f"https://discord.com/api/v10/channels/{cid}/messages?limit=15", headers=headers, timeout=10)
            if resp.status_code == 200:
                for m in resp.json():
                    content = m.get("content", "")
                    if query.lower() in content.lower() or len(out) < 3:
                        out.append({
                            "tier": "TIER_1_API",
                            "platform": "DISCORD",
                            "author": m.get("author", {}).get("username", "user"),
                            "title": content[:80],
                            "text": content[:400],
                            "metrics": f"Channel: {cid}",
                            "url": f"https://discord.com/channels/@me/{cid}/{m.get('id', '')}"
                        })
        except Exception as e:
            print(f"[Tier1 Discord Error]: {e}")
    return out


# =====================================================================
# TIER 2: HEADLESS HEAVY INFANTRY (TIKTOK, IG, FB, LINKEDIN, THREADS, PINTEREST, X)
# =====================================================================

async def simulate_human_jitter(page):
    """Generates randomized human-like cursor trajectories and scroll bursts to bypass behavioral bot checks."""
    for _ in range(random.randint(2, 4)):
        x = random.randint(100, 1100)
        y = random.randint(100, 650)
        await page.mouse.move(x, y, steps=random.randint(8, 20))
        await page.wait_for_timeout(random.randint(120, 380))
    await page.mouse.wheel(0, random.randint(250, 700))
    await page.wait_for_timeout(random.randint(300, 700))


async def tier2_stealth_playwright_node(target_url: str) -> dict:
    """Deploys a stealth-patched Chromium node with optional proxy rotation and human jitter."""
    if not PLAYWRIGHT_AVAILABLE:
        return {"tier": "TIER_2_HEAVY", "platform": "PLAYWRIGHT", "title": "Skipped", "text": "Playwright not installed", "metrics": "N/A", "url": target_url}

    launch_kwargs = {
        "headless": True,
        "args": [
            "--disable-blink-features=AutomationControlled",
            "--disable-features=IsolateOrigins,site-per-process",
            "--no-sandbox"
        ]
    }
    if PROXY_POOL:
        launch_kwargs["proxy"] = {"server": random.choice(PROXY_POOL)}

    async with async_playwright() as p:
        browser = await p.chromium.launch(**launch_kwargs)
        context = await browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={"width": random.choice([1366, 1440, 1920]), "height": random.choice([768, 900, 1080])},
            locale="en-US"
        )
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8});
            Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});
            window.chrome = { runtime: {} };
        """)
        page = await context.new_page()
        try:
            await page.goto(target_url, wait_until="domcontentloaded", timeout=22000)
            await simulate_human_jitter(page)
            title = await page.title()
            og_desc = await page.evaluate("() => document.querySelector('meta[property=\"og:description\"], meta[name=\"description\"]')?.content || ''")
            text_dump = await page.evaluate("() => document.body ? document.body.innerText : ''")
            await browser.close()
            return {
                "tier": "TIER_2_HEAVY",
                "platform": "STEALTH-NODE",
                "author": "DOM Extraction",
                "title": title[:120],
                "text": f"{og_desc}\n{' '.join(text_dump.split())[:1500]}",
                "metrics": "Playwright Stealth + Jitter",
                "url": target_url
            }
        except Exception as e:
            await browser.close()
            return {"tier": "TIER_2_HEAVY", "platform": "STEALTH-NODE", "author": "System", "title": "Node Blocked/Timeout", "text": str(e), "metrics": "Failed", "url": target_url}


async def tier2_walled_garden_matrix(client: httpx.AsyncClient, query: str) -> list[dict]:
    """
    Maps walled-garden platforms (TikTok, Instagram, Facebook, LinkedIn, Threads, Pinterest, X)
    simultaneously via targeted search-index dorking.
    """
    walled_gardens = [
        ("TIKTOK",    f'site:tiktok.com "{query}"'),
        ("INSTAGRAM", f'site:instagram.com "{query}"'),
        ("FACEBOOK",  f'site:facebook.com "{query}"'),
        ("LINKEDIN",  f'site:linkedin.com/posts/ OR site:linkedin.com/in/ "{query}"'),
        ("THREADS",   f'site:threads.net "{query}"'),
        ("PINTEREST", f'site:pinterest.com "{query}"'),
        ("X",         f'site:x.com OR site:twitter.com "{query}"')
    ]
    out = []
    headers = {"User-Agent": random.choice(USER_AGENTS)}

    async def probe_garden(platform_name: str, dork: str):
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote_plus(dork)}"
        try:
            resp = await client.get(url, headers=headers, timeout=14)
            soup = BeautifulSoup(resp.text, "html.parser")
            for res in soup.select(".result__body")[:3]:
                t_el = res.select_one(".result__title")
                s_el = res.select_one(".result__snippet")
                u_el = res.select_one(".result__url")
                if t_el and s_el:
                    raw_u = u_el.get_text(strip=True) if u_el else ""
                    full_u = f"https://{raw_u}" if raw_u and not raw_u.startswith("http") else raw_u
                    out.append({
                        "tier": "TIER_2_HEAVY",
                        "platform": platform_name,
                        "author": platform_name,
                        "title": t_el.get_text(" ", strip=True),
                        "text": s_el.get_text(" ", strip=True),
                        "metrics": "Walled-Garden Footprint",
                        "url": full_u
                    })
        except Exception as e:
            print(f"[Tier2 {platform_name} Error]: {e}")

    await asyncio.gather(*(probe_garden(p, d) for p, d in walled_gardens))
    return out


# =====================================================================
# TIER 3: THE UNSTRUCTURED WILD (4CHAN JSON API, HACKER NEWS, PASTES)
# =====================================================================

async def tier3_fourchan(client: httpx.AsyncClient, query: str, boards: list[str] = None) -> list[dict]:
    """Queries 4chan's official read-only JSON catalog across /biz/, /g/, and /pol/."""
    target_boards = boards or ["biz", "g", "pol"]
    q_words = [w.lower() for w in query.split() if len(w) > 2] or [w.lower() for w in query.split() if w]
    out = []

    async def scan_board(board: str):
        url = f"https://a.4cdn.org/{board}/catalog.json"
        try:
            resp = await client.get(url, timeout=12)
            if resp.status_code != 200:
                return
            for page in resp.json():
                for thread in page.get("threads", []):
                    sub = thread.get("sub", "")
                    com = BeautifulSoup(thread.get("com", ""), "html.parser").get_text(" ", strip=True)
                    combined = f"{sub} {com}".lower()
                    if any(w in combined for w in q_words):
                        no = thread.get("no")
                        out.append({
                            "tier": "TIER_3_WILD",
                            "platform": f"4CHAN (/{board}/)",
                            "author": thread.get("name", "Anonymous"),
                            "title": sub if sub else com[:80],
                            "text": com[:500],
                            "metrics": f"Replies: {thread.get('replies', 0)} | Images: {thread.get('images', 0)}",
                            "url": f"https://boards.4chan.org/{board}/thread/{no}"
                        })
                        if len(out) >= 8:
                            return
        except Exception as e:
            print(f"[Tier3 4chan /{board}/ Error]: {e}")

    await asyncio.gather(*(scan_board(b) for b in target_boards))
    return out


async def tier3_hackernews_and_pastes(client: httpx.AsyncClient, query: str) -> list[dict]:
    """Pulls raw technical sentiment from Algolia HN API and searches public paste boards."""
    out = []
    # 1. Hacker News Algolia JSON API
    hn_url = f"https://hn.algolia.com/api/v1/search_by_date?query={urllib.parse.quote_plus(query)}&hitsPerPage=5"
    try:
        resp = await client.get(hn_url, timeout=12)
        if resp.status_code == 200:
            for hit in resp.json().get("hits", []):
                title = hit.get("title") or hit.get("story_title") or "HN Comment"
                body = BeautifulSoup(hit.get("comment_text") or hit.get("story_text") or title, "html.parser").get_text(" ", strip=True)
                out.append({
                    "tier": "TIER_3_WILD",
                    "platform": "HACKER-NEWS",
                    "author": hit.get("author", "hn_user"),
                    "title": title[:110],
                    "text": body[:450],
                    "metrics": f"Points: {hit.get('points') or 0} | Comments: {hit.get('num_comments') or 0}",
                    "url": hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
                })
    except Exception as e:
        print(f"[Tier3 HN Error]: {e}")

    # 2. Public Paste Sites (Pastebin, Rentry, GitHub Gist)
    paste_dork = f'(site:pastebin.com OR site:rentry.co OR site:gist.github.com) "{query}"'
    ddg_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote_plus(paste_dork)}"
    try:
        resp = await client.get(ddg_url, headers={"User-Agent": random.choice(USER_AGENTS)}, timeout=12)
        soup = BeautifulSoup(resp.text, "html.parser")
        for res in soup.select(".result__body")[:3]:
            t_el = res.select_one(".result__title")
            s_el = res.select_one(".result__snippet")
            u_el = res.select_one(".result__url")
            if t_el and s_el:
                raw_u = u_el.get_text(strip=True) if u_el else ""
                out.append({
                    "tier": "TIER_3_WILD",
                    "platform": "PASTE-ARCHIVE",
                    "author": "Anonymous Paste",
                    "title": t_el.get_text(" ", strip=True),
                    "text": s_el.get_text(" ", strip=True),
                    "metrics": "Raw Paste Dump",
                    "url": f"https://{raw_u}" if raw_u and not raw_u.startswith("http") else raw_u
                })
    except Exception as e:
        print(f"[Tier3 Paste Error]: {e}")

    return out


# =====================================================================
# TIER 4: THE INTELLIGENCE PROCESSING ENGINE (UNIFIED ORCHESTRATOR)
# =====================================================================

async def run_planetary_recon(
    client: httpx.AsyncClient,
    target_query: str,
    llm_caller,
    supabase_url: str = "",
    supabase_headers: dict = None,
    telegram_channels: list[str] = None
) -> dict:
    """
    Executes all 4 tiers concurrently, decodes the corpus via Evolutionary Psychology
    and Game Theory, and stores the report and raw stream telemetry in Supabase.
    """
    tg_list = telegram_channels or ["disclosetv", "unusual_whales"]

    # Execute Tiers 1, 2, and 3 concurrently across all global networks
    results = await asyncio.gather(
        tier1_reddit(client, target_query),
        tier1_youtube(client, target_query),
        tier1_mastodon(client, target_query),
        tier1_discord(client, target_query),
        *(tier1_telegram(client, ch) for ch in tg_list),
        tier2_walled_garden_matrix(client, target_query),
        tier3_fourchan(client, target_query),
        tier3_hackernews_and_pastes(client, target_query)
    )

    all_footprints = [item for sublist in results for item in sublist]

    # Deploy Playwright Stealth Heavy Infantry if an explicit URL is included in target_query
    urls_in_query = [w for w in target_query.split() if w.startswith("http")]
    if urls_in_query:
        stealth_hit = await tier2_stealth_playwright_node(urls_in_query[0])
        all_footprints.insert(0, stealth_hit)

    platforms_scanned = sorted(list({f["platform"] for f in all_footprints}))
    corpus_blocks = [
        f"[{f['tier']} // {f['platform']}] Title: {f['title']}\nContent: {f['text']}\nMetrics: {f['metrics']}"
        for f in all_footprints[:35]
    ]

    synthesis_prompt = (
        f"TARGET DIRECTIVE: {target_query}\n"
        f"ACTIVE PLATFORMS INTERCEPTED ({len(platforms_scanned)}): {', '.join(platforms_scanned)}\n\n"
        f"--- MULTI-TIER GLOBAL TELEMETRY & VIDEO TRANSCRIPTS ---\n"
        f"{chr(10).join(corpus_blocks) if corpus_blocks else 'No public footprints returned; analyze structural incentives directly.'}"
    )

    raw_llm = await llm_caller(
        client,
        [
            {"role": "system", "content": BEHAVIORAL_DOCTRINE_PROMPT},
            {"role": "user", "content": synthesis_prompt}
        ],
        json_mode=True
    )
    if isinstance(raw_llm, dict):
        raw_llm = raw_llm.get("content", "{}")

    # Clean markdown fences if model outputs ```json ... ```
    clean_llm = (raw_llm or "{}").strip()
    if clean_llm.startswith("```"):
        clean_llm = re.sub(r"^```(?:json)?\s*", "", clean_llm)
        clean_llm = re.sub(r"\s*```$", "", clean_llm)

    try:
        parsed = json.loads(clean_llm)
    except Exception:
        parsed = {
            "sentiment_vector": "NEUTRAL (0.0)",
            "status_signaling": clean_llm[:300],
            "game_theory_matrix": "Payload parsed.",
            "narrative_coordination": "Discourse mapped across available tiers.",
            "operator_counterplay": "Monitor tier footprints."
        }

    report = {
        "target_query": target_query,
        "platforms_scanned": platforms_scanned,
        "sentiment_vector": parsed.get("sentiment_vector", "NEUTRAL (0.0)"),
        "status_signaling": parsed.get("status_signaling", ""),
        "game_theory_matrix": parsed.get("game_theory_matrix", ""),
        "narrative_coordination": parsed.get("narrative_coordination", ""),
        "operator_counterplay": parsed.get("operator_counterplay", ""),
        "raw_footprints": all_footprints[:25],
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    # Persist to Supabase (osint_recon_reports + osint_raw_stream)
    if supabase_url and supabase_headers:
        try:
            rep_resp = await client.post(
                f"{supabase_url}/rest/v1/osint_recon_reports",
                headers={**supabase_headers, "Prefer": "return=representation"},
                json=report
            )
            if rep_resp.status_code in (200, 201):
                recon_id = rep_resp.json()[0]["id"]
                raw_rows = []
                for f in all_footprints[:25]:
                    h = hashlib.sha256(f"{f['platform']}{f['title']}{f.get('url', '')}".encode()).hexdigest()
                    raw_rows.append({
                        "recon_id": recon_id,
                        "resistance_tier": f["tier"],
                        "platform": f["platform"],
                        "author": f.get("author", ""),
                        "title": f["title"][:200],
                        "content_or_transcript": f["text"],
                        "engagement_metrics": f.get("metrics", ""),
                        "source_url": f.get("url", ""),
                        "content_hash": h
                    })
                if raw_rows:
                    await client.post(
                        f"{supabase_url}/rest/v1/osint_raw_stream",
                        headers={**supabase_headers, "Prefer": "resolution=ignore-duplicates"},
                        json=raw_rows
                    )
        except Exception as e:
            print(f"[Tier4 Supabase Persistence Error]: {e}")

    return report
