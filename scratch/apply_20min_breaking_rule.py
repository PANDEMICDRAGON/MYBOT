import re

def apply_rule():
    with open("bot.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Add TELEGRAM_DISPATCH_INTERVAL, LAST_TELEGRAM_DISPATCH_TIME, and is_breaking_news_event
    old_sync = 'SYNC_INTERVAL = int(os.getenv("SYNC_INTERVAL", "900"))'
    new_sync = '''SYNC_INTERVAL = int(os.getenv("SYNC_INTERVAL", "300"))
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

    return False, ""'''

    if old_sync in content:
        content = content.replace(old_sync, new_sync, 1)
        print("Updated sync configuration & added is_breaking_news_event.")
    else:
        print("Warning: old_sync not found.")

    # 2. Update dispatch logic in execute_complete_sensor_sweep
    old_dispatch_pattern = re.compile(
        r'if is_proactive and \(news or cyber or conflict_macro or force_sync_event\.is_set\(\)\) and TELEGRAM_TOKEN and AUTHORIZED_CHAT_ID:[\s\S]*?'
        r'await send_telegram\(client, telegram_dispatch\)[\s\S]*?except Exception as e:[\s\S]*?logger\.error\(f"\[Synthesis Dispatch Error\]: \{e\}"\)',
        re.MULTILINE
    )

    new_dispatch = '''global LAST_TELEGRAM_DISPATCH_TIME

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
                        bullets.append(f"• *{dd.get('subject', 'THEATER')}:* {dd.get('latest_developments', '')}\\n  ↳ _Tactical Impact:_ {dd.get('why_it_matters', '')}")
                    deep_dives_summary = "\\n\\n2. *IN-DEPTH THEATER EVOLUTION (ACTIVE SUBJECTS):*\\n" + "\\n".join(bullets)

                header_prefix = "🚨 *BREAKING TACTICAL ALERT" if is_breaking else "🛡️ *OVERWATCH SITREP"
                breaking_banner = f"\\n⚠️ *FLASH TRIGGER:* _{breaking_reason}_\\n" if is_breaking else ""

                telegram_dispatch = (
                    f"{header_prefix} // [{b['threat_level']}]*\\n"
                    f"{breaking_banner}\\n"
                    f"1. *TACTICAL SITUATION & NEW DEVELOPMENTS:*\\n{b['sitrep']}"
                    f"{deep_dives_summary}\\n\\n"
                    f"3. *ACTIVE THEATERS & CHOKEPOINTS:*\\n{b['conflict_summary']}\\n\\n"
                    f"4. *SECOND-ORDER RISK FORECAST (7-30 DAYS):*\\n{b['future_risk_forecast']}\\n\\n"
                    f"5. *DEFENSIVE PROTOCOL:*\\n{b['defensive_protocol']}\\n\\n"
                    f"6. *ASYMMETRIC UPSIDE:*\\n{b['asymmetric_upside']}"
                )
                await send_telegram(client, telegram_dispatch)
                LAST_TELEGRAM_DISPATCH_TIME = now_ts
            except Exception as e:
                logger.error(f"[Synthesis Dispatch Error]: {e}")'''

    match = old_dispatch_pattern.search(content)
    if match:
        content = content[:match.start()] + new_dispatch + content[match.end():]
        print("Updated execute_complete_sensor_sweep dispatch gate.")
    else:
        print("Error: old_dispatch_pattern not matched.")

    # 3. Update collector_worker sweep sleep
    old_worker = '''async def collector_worker(client: httpx.AsyncClient):
    """Executes periodic sensor sync and generates proactive Tactical SitReps with real telemetry persistence."""
    logger.info(f"Tactical telemetry daemon active (Interval: {SYNC_INTERVAL}s)...")
    while True:
        try:
            await execute_complete_sensor_sweep(client, is_proactive=True)
        except Exception as ce:
            logger.error(f"[Collector Cycle Error]: {ce}")

        try:
            await asyncio.wait_for(force_sync_event.wait(), timeout=SYNC_INTERVAL)'''

    new_worker = '''async def collector_worker(client: httpx.AsyncClient):
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
            await asyncio.wait_for(force_sync_event.wait(), timeout=sweep_sleep)'''

    if old_worker in content:
        content = content.replace(old_worker, new_worker, 1)
        print("Updated collector_worker sleep timing.")
    else:
        print("Warning: old_worker not found.")

    with open("bot.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("bot.py successfully updated with 20-minute interval and breaking news rule.")

if __name__ == "__main__":
    apply_rule()
