"""Audio Clip Delivery Subsystem Forwarder -> clip_creator.py"""
import json
from tools.clip_creator import get_clip_metadata, list_clips, convert_to_mp3, preview_clip

if __name__ == "__main__":
    print(json.dumps(get_clip_metadata(), indent=2))
