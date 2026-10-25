import re

def update_bot():
    with open("bot.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Add SPORTS_NEWS_FEEDS right after ROTATING_TOPIC_FEEDS
    old_topic_end = '''    {
        "subject": "Critical Minerals & Central Africa",
        "scope": "GLOBAL",
        "source": "Great Lakes Minerals Corridor",
        "theater": "CENTRAL-AFRICA",
        "url": "https://news.google.com/rss/search?q=(%22DRC%22+OR+%22Congo%22+OR+Rwanda)+AND+(minerals+OR+coltan+OR+cobalt+OR+mining+OR+security)&hl=en-US&gl=US&ceid=US:en"
    }
]'''

    sports_feeds_code = '''    {
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
]'''

    if old_topic_end in content:
        content = content.replace(old_topic_end, sports_feeds_code, 1)
        print("Added SPORTS_NEWS_FEEDS.")
    else:
        print("Warning: old_topic_end not found.")

    # 2. Update sync_news feed selection
    old_feed_selection = '''    # Select 2 base feeds + 3 rotating topic feeds
    active_feeds = list(BASE_NEWS_FEEDS[:2])
    num_rotating = len(ROTATING_TOPIC_FEEDS)
    if num_rotating > 0:
        for offset in range(3):
            idx = (SWEEP_CYCLE_INDEX * 3 + offset) % num_rotating
            active_feeds.append(ROTATING_TOPIC_FEEDS[idx])'''

    new_feed_selection = '''    # Select 2 base feeds + 2 rotating thematic feeds + 2 rotating sports feeds
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
            active_feeds.append(SPORTS_NEWS_FEEDS[s_idx])'''

    if old_feed_selection in content:
        content = content.replace(old_feed_selection, new_feed_selection, 1)
        print("Updated sync_news active_feeds with sports rotation.")
    else:
        print("Warning: old_feed_selection not found.")

    # 3. Update tool_triggers with sports terms
    old_triggers = '''    tool_triggers = [
        "weather", "news", "cyber", "cve", "war", "conflict", "sitrep", "sweep", "sync",'''

    new_triggers = '''    tool_triggers = [
        "weather", "news", "sports", "sport", "football", "soccer", "premier league", "champions league", "athletics", "marathon", "f1", "formula 1", "cyber", "cve", "war", "conflict", "sitrep", "sweep", "sync",'''

    if old_triggers in content:
        content = content.replace(old_triggers, new_triggers, 1)
        print("Updated tool_triggers with sports keywords.")
    else:
        print("Warning: old_triggers not found.")

    with open("bot.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("bot.py successfully updated with sports news.")

if __name__ == "__main__":
    update_bot()
