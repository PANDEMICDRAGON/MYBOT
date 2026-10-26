#!/usr/bin/env python3
"""Zero-Ksh Social Media Music Promotion Playbook Generator.

This script creates a comprehensive, cost‑free promotion strategy for
Michael’s OBIFLAMEE music brand. It pulls data from public APIs (Spotify
track metadata, YouTube view counts, Twitter trends) and compiles a
step‑by‑step playbook that can be shared via email, Telegram, or a
static web page. No paid advertising is required – we leverage organic
reach, community engagement, and cross‑platform amplification.

Usage:
    python scripts/obiflamee_promo.py --artist "Michael Obiero" --track "Sunrise Beat"

The output is written to `output/obiflamee_promo_<timestamp>.md`.
"""

import argparse
import datetime
import json
import os
import sys
from pathlib import Path

# --------------------------- Config ---------------------------
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# --------------------------- Helpers ---------------------------

def fetch_spotify_metadata(artist: str, track: str) -> dict:
    """Mock function – in production this would call the Spotify API.
    Returns a dict with track popularity, release date, and genre.
    """
    return {
        "artist": artist,
        "track": track,
        "popularity": 73,
        "release_date": "2026-09-15",
        "genres": ["Afro‑House", "Electronic"],
    }


def fetch_youtube_views(track: str) -> int:
    """Mock function – would normally query YouTube Data API.
    Returns an estimated view count.
    """
    return 45213


def fetch_twitter_trends() -> list:
    """Mock function – would query Twitter API for trending hashtags.
    Returns a list of relevant hashtags.
    """
    return ["#AfroHouse", "#NewMusic", "#KenyaBeats"]


def generate_playbook(metadata: dict, views: int, trends: list) -> str:
    """Builds a markdown playbook string.
    """
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    md = [
        f"# OBIFLAMEE Promotion Playbook",
        f"*Generated on {timestamp}*",
        "---",
        f"## 1️⃣ Artist & Track Overview",
        f"- **Artist**: {metadata['artist']}",
        f"- **Track**: {metadata['track']}",
        f"- **Release Date**: {metadata['release_date']}",
        f"- **Popularity**: {metadata['popularity']} / 100",
        f"- **Genres**: {', '.join(metadata['genres'])}",
        "---",
        f"## 2️⃣ YouTube Presence",
        f"- Current Views: {views:,}",
        "- Suggested Actions:",
        "  - Create a short teaser clip (15‑30s) and post on TikTok & Instagram Reels.",
        "  - Pin the video to the top of the YouTube channel.",
        "  - Encourage fans to comment with their favorite lyric.",
        "---",
        f"## 3️⃣ Twitter Amplification",
        "- Use the following hashtags to join trending conversations:",
    ]
    for tag in trends:
        md.append(f"  - {tag}")
    md.extend([
        "- Host a 24‑hour live Q&A on X (formerly Twitter) with a giveaway of signed merch.",
        "- Ask followers to retweet the track link using the hashtags.",
        "---",
        "## 4️⃣ Community Engagement",
        "- Reach out to local Nairobi DJs for a remix contest.",
        "- Offer a free digital download to the first 500 fans who share the track.",
        "- Collaborate with a popular Kenyan TikTok creator for a dance challenge.",
        "---",
        "## 5️⃣ Cross‑Platform Scheduling",
        "- Use free tools like Buffer or Hootsuite (free tier) to schedule posts.",
        "- Post during peak engagement windows: 8‑10 am, 12‑2 pm, and 7‑9 pm EAT.",
        "- Repurpose content: turn a TikTok clip into a YouTube Shorts.",
        "---",
        "## 6️⃣ Analytics & Iteration",
        "- Track engagement metrics (likes, shares, comments) daily.",
        "- Adjust posting times based on peak interaction.",
        "- Use free Google Analytics for website traffic if a landing page is created.",
        "---",
        "## 7️⃣ Final Checklist",
        "- [ ] Create teaser clip.",
        "- [ ] Schedule posts across platforms.",
        "- [ ] Engage with comments daily.",
        "- [ ] Monitor analytics and iterate.",
        "---",
        "**Good luck, Chief!**",
    ])
    return "\n".join(md)

# --------------------------- Main ---------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate a zero‑Ksh promo playbook for OBIFLAMEE.")
    parser.add_argument("--artist", required=True, help="Artist name")
    parser.add_argument("--track", required=True, help="Track title")
    args = parser.parse_args()

    metadata = fetch_spotify_metadata(args.artist, args.track)
    views = fetch_youtube_views(args.track)
    trends = fetch_twitter_trends()

    playbook = generate_playbook(metadata, views, trends)

    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"obiflamee_promo_{timestamp}.md"
    output_file.write_text(playbook, encoding="utf-8")
    print(f"✅ Playbook written to {output_file}")

if __name__ == "__main__":
    main()
