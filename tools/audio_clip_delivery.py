import os
import json
import wave
import contextlib
import subprocess
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent.parent
CLIPS_DIR = BASE_DIR / "audio_clips"
CLIPS_DIR.mkdir(exist_ok=True)

# Helper to list available clips
def list_clips():
    return [p.name for p in CLIPS_DIR.glob("*.wav")]

# Convert to mp3 using ffmpeg if available
def convert_to_mp3(wav_path: Path, mp3_path: Path):
    if not mp3_path.exists():
        subprocess.run(["ffmpeg", "-y", "-i", str(wav_path), str(mp3_path)], check=True)

# Generate a short preview (first 10 seconds)
def preview_clip(wav_path: Path, preview_path: Path):
    with contextlib.closing(wave.open(str(wav_path), 'r')) as wf:
        params = wf.getparams()
        frames = wf.readframes(min(10 * params.framerate, wf.getnframes()))
    with contextlib.closing(wave.open(str(preview_path), 'w')) as wf:
        wf.setparams(params)
        wf.writeframes(frames)

# Main API

def get_clip_metadata():
    clips = []
    for wav in CLIPS_DIR.glob("*.wav"):
        mp3 = wav.with_suffix('.mp3')
        preview = wav.with_name(wav.stem + '_preview.wav')
        convert_to_mp3(wav, mp3)
        preview_clip(wav, preview)
        clips.append({
            "name": wav.stem,
            "wav": str(wav.relative_to(BASE_DIR)),
            "mp3": str(mp3.relative_to(BASE_DIR)),
            "preview": str(preview.relative_to(BASE_DIR))
        })
    return clips

# Endpoint simulation (would be served by FastAPI in production)
if __name__ == "__main__":
    print(json.dumps(get_clip_metadata(), indent=2))
