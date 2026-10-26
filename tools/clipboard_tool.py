import sys
import threading
import time
from collections import deque
from typing import Deque

try:
    import pyperclip
except ImportError:
    print("[⚠️] pyperclip not installed. Installing now...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyperclip"])
    import pyperclip

# ---------------------------------------------------------------------------
# Clipboard Clipping Tool – Interactive CLI
# ---------------------------------------------------------------------------
# This script runs a background thread that watches the system clipboard for
# changes. Every unique entry is stored in an in‑memory history (max 100 items).
# The main thread presents a tiny REPL allowing the operator to:
#   • list   – show recent clipboard entries
#   • copy N – copy the N‑th entry back to the clipboard
#   • clear  – purge the history
#   • quit   – exit the tool gracefully
#
# It is deliberately lightweight, cross‑platform and requires only the
# `pyperclip` package (which the script will auto‑install if missing).
# ---------------------------------------------------------------------------

MAX_HISTORY = 100
history: Deque[str] = deque(maxlen=MAX_HISTORY)
_last_clip = None
_stop_event = threading.Event()


def _watch_clipboard() -> None:
    """Background thread that polls the clipboard every 0.5 s.

    When a new, non‑empty string appears it is appended to the global `history`
    deque. Duplicates are ignored to keep the history concise.
    """
    global _last_clip
    while not _stop_event.is_set():
        try:
            cur = pyperclip.paste()
        except Exception as e:
            # Some platforms raise when clipboard is inaccessible – ignore.
            cur = None
        if cur and cur != _last_clip:
            _last_clip = cur
            if cur not in history:
                history.appendleft(cur)
                print(f"[📋] New clip captured (#{len(history)}).")
        time.sleep(0.5)


def _print_help() -> None:
    help_msg = """
    📎 Clipboard Clipping Tool – Commands
    -----------------------------------
    list            – Show recent clipboard entries (most recent first)
    copy <index>    – Copy entry #<index> back to the system clipboard
    clear           – Empty the clipboard history
    help            – Show this help message
    quit / exit     – Stop the watcher and exit
    """
    print(help_msg)


def _list_history() -> None:
    if not history:
        print("[ℹ️] History is empty.")
        return
    print("--- Clipboard History (most recent first) ---")
    for i, entry in enumerate(history, start=1):
        # Truncate long entries for readability
        preview = entry.replace("\n", " ")
        if len(preview) > 80:
            preview = preview[:77] + "..."
        print(f"{i:2d}: {preview}")
    print("--- End of History ---")


def _copy_to_clipboard(index: int) -> None:
    try:
        entry = list(history)[index - 1]
    except IndexError:
        print(f"[❌] Invalid index {index}. Use 'list' to see valid numbers.")
        return
    pyperclip.copy(entry)
    print(f"[✅] Copied entry #{index} to clipboard.")


def _clear_history() -> None:
    history.clear()
    print("[🗑️] Clipboard history cleared.")


def main() -> None:
    watcher = threading.Thread(target=_watch_clipboard, daemon=True)
    watcher.start()
    _print_help()
    while True:
        try:
            cmd = input("clip> ").strip()
        except (EOFError, KeyboardInterrupt):
            cmd = "quit"
        if not cmd:
            continue
        parts = cmd.split()
        action = parts[0].lower()
        if action in ("quit", "exit"):
            print("[🔚] Shutting down clipboard watcher…")
            _stop_event.set()
            watcher.join()
            break
        elif action == "help":
            _print_help()
        elif action == "list":
            _list_history()
        elif action == "clear":
            _clear_history()
        elif action == "copy":
            if len(parts) != 2 or not parts[1].isdigit():
                print("[❗] Usage: copy <index>")
                continue
            _copy_to_clipboard(int(parts[1]))
        else:
            print(f"[❓] Unknown command: {action}. Type 'help' for options.")


if __name__ == "__main__":
    main()
