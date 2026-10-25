import time

LAST_TELEGRAM_DISPATCH_TIME = 0.0
TELEGRAM_DISPATCH_INTERVAL = 1200  # 20 minutes

BREAKING_KEYWORDS = [
    "breaking", "urgent", "flash", "bulletin", "critical zero-day", "exploited in the wild",
    "airstrike", "missile strike", "drone strike", "explosion", "martial law", "coup",
    "hostage", "total blackout", "grid collapse", "subsea cable cut", "chokepoint closed",
    "bank run", "border closure", "emergency declared", "curfew", "assassination"
]

def is_breaking_news_event(sitrep_data: dict, news_items: list, cyber_items: list, conflict_items: list) -> tuple[bool, str]:
    threat = (sitrep_data.get("threat_level") or "").upper()
    if threat in ("HIGH", "CRITICAL"):
        return True, f"Threat level elevated to {threat}"

    sitrep_text = (sitrep_data.get("sitrep") or "").lower()
    for kw in BREAKING_KEYWORDS:
        if kw in sitrep_text:
            return True, f"Breaking indicator detected in SitRep: '{kw.upper()}'"

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

def test():
    global LAST_TELEGRAM_DISPATCH_TIME

    # Scenario 1: Initial startup sweep (time_since_last = 0.0 -> should dispatch)
    is_brk, rsn = is_breaking_news_event({"threat_level": "NOMINAL", "sitrep": "All calm in East Africa"}, [], [], [])
    print("Initial startup breaking?", is_brk)
    LAST_TELEGRAM_DISPATCH_TIME = time.time()
    print("Dispatched initial SitRep. LAST_TELEGRAM_DISPATCH_TIME set.")

    # Scenario 2: 5 minutes later, nominal news (time_since_last = 300s -> should NOT dispatch)
    time_since_last = 300
    should_dispatch = time_since_last >= TELEGRAM_DISPATCH_INTERVAL
    print(f"5 minutes later nominal news -> should dispatch? {should_dispatch} (Correct: False)")

    # Scenario 3: 7 minutes later, BREAKING NEWS strikes!
    is_brk3, rsn3 = is_breaking_news_event(
        {"threat_level": "CRITICAL", "sitrep": "Airstrikes close Red Sea shipping lanes entirely."},
        [{"title": "BREAKING: Total KPLC electrical blackout reported across Nairobi"}],
        [], []
    )
    print(f"7 minutes later breaking news -> is_breaking? {is_brk3}, reason: {rsn3} (Correct: True, immediate dispatch)")

    # Scenario 4: 20 minutes elapsed since last dispatch
    time_since_last_4 = 1205
    should_dispatch_4 = time_since_last_4 >= TELEGRAM_DISPATCH_INTERVAL
    print(f"20 minutes elapsed -> should dispatch? {should_dispatch_4} (Correct: True)")

if __name__ == "__main__":
    test()
