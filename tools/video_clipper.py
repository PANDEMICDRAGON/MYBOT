import argparse
import subprocess
import sys
import os
from pathlib import Path

def parse_time(time_str: str) -> str:
    """Validate and return time string in HH:MM:SS or seconds format for ffmpeg.
    ffmpeg accepts both, we just pass through after basic validation.
    """
    # Simple validation: allow digits, colon, dot
    if not time_str:
        raise ValueError("Time string cannot be empty")
    allowed = set("0123456789:.")
    if any(ch not in allowed for ch in time_str):
        raise ValueError(f"Invalid characters in time string: {time_str}")
    return time_str

def build_ffmpeg_cmd(input_path: Path, output_path: Path, start: str, end: str = None, duration: str = None) -> list:
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(input_path)]
    if start:
        cmd.extend(["-ss", start])
    if duration:
        cmd.extend(["-t", duration])
    elif end:
        # When end is provided, calculate duration via ffmpeg's -to
        cmd.extend(["-to", end])
    cmd.extend(["-c", "copy", str(output_path)])
    return cmd

def clip_video(input_file: str, start: str, end: str = None, duration: str = None, output_file: str = None):
    input_path = Path(input_file).resolve()
    if not input_path.is_file():
        raise FileNotFoundError(f"Input video not found: {input_path}")

    if not output_file:
        # Generate output name based on input and start time
        stem = input_path.stem
        suffix = input_path.suffix
        safe_start = start.replace(":", "-")
        output_path = input_path.parent / f"{stem}_clip_{safe_start}{suffix}"
    else:
        output_path = Path(output_file).resolve()

    start_valid = parse_time(start)
    end_valid = parse_time(end) if end else None
    duration_valid = parse_time(duration) if duration else None

    cmd = build_ffmpeg_cmd(input_path, output_path, start_valid, end_valid, duration_valid)
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Clip created: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ ffmpeg failed with error: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Clip a segment from a video using ffmpeg.")
    parser.add_argument("input", help="Path to the source video file")
    parser.add_argument("-s", "--start", required=True, help="Start time (HH:MM:SS or seconds)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-e", "--end", help="End time (HH:MM:SS or seconds)")
    group.add_argument("-d", "--duration", help="Duration of the clip (HH:MM:SS or seconds)")
    parser.add_argument("-o", "--output", help="Output file path (optional)")

    args = parser.parse_args()
    clip_video(
        input_file=args.input,
        start=args.start,
        end=args.end,
        duration=args.duration,
        output_file=args.output,
    )

if __name__ == "__main__":
    main()
