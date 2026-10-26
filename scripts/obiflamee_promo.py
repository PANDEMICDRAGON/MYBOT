#!/usr/bin/env python3
"""
=====================================================================
OBIFLAMEE SOCIAL MEDIA PROMOTION & MUSIC VIRALITY ENGINE
=====================================================================
A tactical, zero-budget (0 Ksh) music promotion toolkit engineered
specifically for Michael Obiero (OBIFLAMEE) in Kitengela/Nairobi, Kenya.

Capabilities:
  1. Content Calendar Generator (30-day multi-platform strategy)
  2. Viral Hook & Caption Optimizer (TikTok, Reels, Shorts, X, WhatsApp)
  3. Influencer, DJ & Playlist Curator DM Outreach Templates
  4. Release Campaign Lifecycle Framework (Pre-save -> Drop -> Post-drop)
  5. Local & Regional Hashtag Strategy (#Obiflamee, #KenyanHipHop, etc.)
  6. CSV Growth & Metrics Tracker Export
=====================================================================
"""

import os
import sys
import csv
import json
import random
import argparse
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

# --- CORE BRAND & METADATA ---
ARTIST_NAME = "OBIFLAMEE"
CREATOR = "Michael Obiero"
LOCATION = "Kitengela / Nairobi, Kenya"
GENRES = ["Afro-Fusion", "Kenyan Hip-Hop", "Drill / Street Lyricism", "FL Studio Production"]

# Platform Best Practices
PLATFORMS = {
    "TIKTOK": {
        "aspect_ratio": "9:16",
        "optimal_duration": "15-30s",
        "peak_posting_eat": ["12:00 PM", "6:30 PM", "9:00 PM"],
        "content_focus": "Relatable beat-making hooks, lyric punchlines, raw studio energy in Kitengela"
    },
    "INSTAGRAM_REELS": {
        "aspect_ratio": "9:16",
        "optimal_duration": "20-45s",
        "peak_posting_eat": ["1:00 PM", "7:00 PM", "9:30 PM"],
        "content_focus": "High aesthetic behind-the-scenes, visualizer snippet, artist lifestyle"
    },
    "YOUTUBE_SHORTS": {
        "aspect_ratio": "9:16",
        "optimal_duration": "30-60s",
        "peak_posting_eat": ["4:00 PM", "8:00 PM"],
        "content_focus": "High retention storytelling, track production breakdowns, studio sessions"
    },
    "X_TWITTER": {
        "aspect_ratio": "16:9 or Text",
        "optimal_duration": "Short audio card or teaser",
        "peak_posting_eat": ["8:00 AM", "1:00 PM", "6:00 PM"],
        "content_focus": "Hot takes on music production, Kenya entertainment banter, lyrics quote-tweets"
    },
    "WHATSAPP_STATUS": {
        "aspect_ratio": "9:16",
        "optimal_duration": "30s clips",
        "peak_posting_eat": ["7:30 AM", "12:30 PM", "8:00 PM"],
        "content_focus": "Direct circle hype, streaming links, behind-the-glass FL Studio previews"
    }
}

# High-converting viral hooks tailored for OBIFLAMEE
VIRAL_HOOKS = [
    {
        "category": "Producer / Studio Grind",
        "hook": "Made this beat at 3 AM in Kitengela and now I can't stop looping it...",
        "call_to_action": "Should I drop this on Friday or keep it locked in the vault? Drop a 🔥 in comments."
    },
    {
        "category": "Lyric Punchline",
        "hook": "When the compiler gives 20 red errors but the 808s are hitting perfectly...",
        "call_to_action": "Tag someone who codes by day and drops heat by night. Stream link in bio."
    },
    {
        "category": "Raw Energy / Relatability",
        "hook": "They said you can't build an independent music empire from Kitengela. Watch this.",
        "call_to_action": "Save this sound before it blows up. OBIFLAMEE season is officially live."
    },
    {
        "category": "Emotional Resonance",
        "hook": "I wrote this verse when everyone doubted the vision. Every line is real.",
        "call_to_action": "If you've ever had to bet on yourself when nobody was clapping, this song is for you."
    },
    {
        "category": "Audio Illusion / Bass Drop",
        "hook": "Wait until the second 808 slides in... Put your headphones on right now.",
        "call_to_action": "Rate this drop from 1 to 10 in the comments. Full track out now."
    }
]

# Targeted regional and global hashtags
HASHTAG_POOLS = {
    "CORE": ["#OBIFLAMEE", "#KenyanMusic", "#NairobiMusic", "#KitengelaTalent", "#EastAfricanSound"],
    "HIP_HOP": ["#KenyanHipHop", "#NairobiDrill", "#AfroDrill", "#AfricanRap", "#BarsOnly"],
    "STUDIO": ["#FLStudioProducer", "#BeatMakerLife", "#StudioVibes", "#IndependentArtist", "#AudioEngineer"],
    "DISCOVERY": ["#DiscoverAfricanMusic", "#NewMusicKenya", "#ViralAudio", "#UpcomingArtist", "#MusicTikTok"]
}


@dataclass
class PromotionPost:
    day: int
    platform: str
    content_pillar: str
    hook: str
    caption: str
    hashtags: str
    time_eat: str
    status: str = "SCHEDULED"


class ObiflameePromoEngine:
    """Core autonomous marketing and campaign strategist for OBIFLAMEE."""

    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = output_dir or os.path.dirname(os.path.abspath(__file__))

    def generate_viral_caption(self, track_title: str = "Midnight in Kitengela", topic: str = "studio_grind") -> Dict[str, str]:
        """Generates a complete high-converting caption with hook and hashtags."""
        hook_obj = random.choice(VIRAL_HOOKS)
        core_tags = random.sample(HASHTAG_POOLS["CORE"], 3)
        genre_tags = random.sample(HASHTAG_POOLS["HIP_HOP"], 3)
        disc_tags = random.sample(HASHTAG_POOLS["DISCOVERY"], 2)
        all_tags = " ".join(core_tags + genre_tags + disc_tags)

        full_caption = (
            f"{hook_obj['hook']}\n\n"
            f"🎵 Track: '{track_title}' by {ARTIST_NAME}\n"
            f"📍 Engineered in {LOCATION}\n\n"
            f"{hook_obj['call_to_action']}\n\n"
            f"{all_tags}"
        )

        return {
            "hook": hook_obj["hook"],
            "track_title": track_title,
            "call_to_action": hook_obj["call_to_action"],
            "hashtags": all_tags,
            "full_caption": full_caption
        }

    def generate_30_day_calendar(self, track_title: str = "Midnight in Kitengela") -> List[PromotionPost]:
        """Builds a comprehensive 30-day multi-platform content roadmap."""
        pillars = [
            ("TIKTOK", "Studio Behind-the-Scenes (FL Studio Breakdown)", "12:00 PM"),
            ("INSTAGRAM_REELS", "Cinematic Music Snippet & Visualizer", "7:00 PM"),
            ("YOUTUBE_SHORTS", "Story Behind the Lyrics / Producer Diary", "4:00 PM"),
            ("X_TWITTER", "Lyric Punchline Quote Card & Poll", "1:00 PM"),
            ("WHATSAPP_STATUS", "Raw Track Preview & Stream Direct Link", "8:00 PM")
        ]

        calendar: List[PromotionPost] = []
        for day in range(1, 31):
            platform, pillar, time_eat = pillars[(day - 1) % len(pillars)]
            caption_data = self.generate_viral_caption(track_title=track_title)
            post = PromotionPost(
                day=day,
                platform=platform,
                content_pillar=pillar,
                hook=caption_data["hook"],
                caption=caption_data["full_caption"],
                hashtags=caption_data["hashtags"],
                time_eat=time_eat
            )
            calendar.append(post)

        return calendar

    def export_calendar_to_csv(self, calendar: List[PromotionPost], filename: str = "obiflamee_30_day_calendar.csv") -> str:
        """Exports the generated calendar to a clean CSV file."""
        out_path = os.path.join(self.output_dir, filename)
        with open(out_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Day", "Platform", "Time_EAT", "Content_Pillar", "Viral_Hook", "Caption_With_Hashtags", "Status"])
            for post in calendar:
                writer.writerow([
                    f"Day {post.day}",
                    post.platform,
                    post.time_eat,
                    post.content_pillar,
                    post.hook,
                    post.caption.replace("\n", " | "),
                    post.status
                ])
        return out_path

    def get_dm_outreach_templates(self, track_title: str, stream_link: str = "https://linktr.ee/obiflamee") -> Dict[str, str]:
        """Provides high-conversion, zero-cost DM scripts for DJs, Curators, and Creators."""
        return {
            "KENYAN_DJ_OUTREACH": (
                f"Habari Big Man / Master DJ! 🎧\n"
                f"I'm {ARTIST_NAME}, an independent music creator from Kitengela/Nairobi. "
                f"I just wrapped a high-energy banger titled '{track_title}' that would shut down dancefloors. "
                f"Got an exclusive DJ WAV/MP3 pack with intro/outro ready for your set.\n"
                f"Can I drop the Google Drive link right here for your mix?"
            ),
            "TIKTOK_CREATOR_COLLAB": (
                f"Yo! Love your energy and dance/transition content on TikTok! 🔥\n"
                f"I produced a fresh sound '{track_title}' with an insane 808 drop that matches your video style. "
                f"Sound link: {stream_link}\n"
                f"If you vibe with it and drop a clip with the sound, I'll pin your video, duet it, and push it to my audience. Let's create magic!"
            ),
            "SPOTIFY_APPLE_CURATOR": (
                f"Hello Curator team,\n\n"
                f"I hope this finds you well. I'm {ARTIST_NAME}, an independent East African artist blending hip-hop and Afro-drill. "
                f"My latest single '{track_title}' carries the distinct pulse of modern Nairobi street culture.\n\n"
                f"Stream link: {stream_link}\n"
                f"Would love your consideration for your playlist. Thank you for championing independent African sounds!"
            )
        }


def main():
    parser = argparse.ArgumentParser(description="OBIFLAMEE Social Media Promotion Engine")
    parser.add_argument("--track", type=str, default="Midnight in Kitengela", help="Title of track being promoted")
    parser.add_argument("--calendar", action="store_true", help="Generate and print 30-day content calendar")
    parser.add_argument("--export-csv", action="store_true", help="Export calendar to CSV file")
    parser.add_argument("--dms", action="store_true", help="Print influencer and DJ outreach DM scripts")
    parser.add_argument("--hook", action="store_true", help="Generate a single viral caption with hooks")
    args = parser.parse_args()

    engine = ObiflameePromoEngine()

    if args.hook or not any([args.calendar, args.export_csv, args.dms]):
        caption = engine.generate_viral_caption(track_title=args.track)
        print("\n" + "="*50)
        print(f"[OBIFLAMEE VIRAL CAPTION] - {args.track}")
        print("="*50)
        clean_cap = caption["full_caption"].encode("ascii", "replace").decode("ascii")
        print(clean_cap)
        print("="*50 + "\n")

    if args.dms:
        dms = engine.get_dm_outreach_templates(track_title=args.track)
        print("\n" + "="*50)
        print("[ZERO-BUDGET OUTREACH DM TEMPLATES]")
        print("="*50)
        for target, script in dms.items():
            clean_s = script.encode("ascii", "replace").decode("ascii")
            print(f"\n[{target}]:\n{clean_s}\n" + "-"*40)

    if args.calendar or args.export_csv:
        cal = engine.generate_30_day_calendar(track_title=args.track)
        print(f"Generated {len(cal)} days of multi-platform strategy for '{args.track}'.")
        if args.export_csv:
            csv_path = engine.export_calendar_to_csv(cal)
            print(f"[OK] Successfully exported to: {csv_path}")


if __name__ == "__main__":
    main()
