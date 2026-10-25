"""
laptop_agent.py - Lightweight Remote LAN Control Agent
======================================================
Runs on any Windows, Linux, or macOS workstation or laptop.
Listens on local Wi-Fi port 8080 and executes incoming directives
from Cortana / J.A.R.V.I.S. (Web HUD or Telegram).

Zero external dependencies required (Pure Python 3 standard library).
"""

import sys
import json
import urllib.parse
import platform
import subprocess
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8080
OS_TYPE = platform.system().lower()

def adjust_volume(action: str):
    """Adjust system master volume without external dependencies."""
    if "windows" in OS_TYPE:
        # Virtual Key Codes: 175 = Volume Up, 174 = Volume Down, 173 = Mute
        key_map = {"up": 175, "down": 174, "mute": 173}
        vk = key_map.get(action, 175)
        ps_cmd = f"(New-Object -ComObject WScript.Shell).SendKeys([char]{vk})"
        subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd], capture_output=True, timeout=4)
    elif "darwin" in OS_TYPE:  # macOS
        if action == "up":
            subprocess.run(["osascript", "-e", "set volume output volume ((output volume of (get volume settings)) + 6)"], timeout=3)
        elif action == "down":
            subprocess.run(["osascript", "-e", "set volume output volume ((output volume of (get volume settings)) - 6)"], timeout=3)
        elif action == "mute":
            subprocess.run(["osascript", "-e", "set volume output muted not (output muted of (get volume settings))"], timeout=3)
    else:  # Linux
        if action == "up":
            subprocess.run(["amixer", "-q", "sset", "Master", "5%+"], shell=True, timeout=3)
        elif action == "down":
            subprocess.run(["amixer", "-q", "sset", "Master", "5%-"], shell=True, timeout=3)
        elif action == "mute":
            subprocess.run(["amixer", "-q", "sset", "Master", "toggle"], shell=True, timeout=3)

def lock_screen():
    """Lock workstation screen."""
    if "windows" in OS_TYPE:
        subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], timeout=3)
    elif "darwin" in OS_TYPE:
        subprocess.run(["pmset", "displaysleepnow"], timeout=3)
    else:
        subprocess.run(["loginctl", "lock-session"], timeout=3)

class RemoteControlHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self, status=200, content_type="text/plain; charset=utf-8"):
        self.send_response(status)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Content-Type", content_type)
        self.end_headers()

    def do_OPTIONS(self):
        self._send_cors_headers(200)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # 1. Health Status
        if path in ("/", "/status", "/api/status"):
            self._send_cors_headers(200, "application/json")
            res = {
                "status": "ONLINE",
                "agent": "Cortana-LAN-Control-Agent",
                "platform": platform.platform(),
                "port": PORT
            }
            self.wfile.write(json.dumps(res, indent=2).encode("utf-8"))
            return

        # 2. Open URL in Default Browser
        if path == "/open_url":
            url_list = query.get("url", [])
            if url_list:
                target_url = urllib.parse.unquote(url_list[0])
                if not target_url.startswith(("http://", "https://")):
                    target_url = "https://" + target_url
                print(f"[DIRECTIVE] Launching URL in browser: {target_url}")
                webbrowser.open(target_url)
                self._send_cors_headers(200)
                self.wfile.write(f"URL successfully opened: {target_url}".encode("utf-8"))
            else:
                self._send_cors_headers(400)
                self.wfile.write(b"Missing 'url' query parameter.")
            return

        # 3. Volume Up
        if path in ("/volume_up", "/vol_up"):
            print("[DIRECTIVE] Volume Up (+5%)")
            adjust_volume("up")
            self._send_cors_headers(200)
            self.wfile.write(b"Volume increased (+5%).")
            return

        # 4. Volume Down
        if path in ("/volume_down", "/vol_down"):
            print("[DIRECTIVE] Volume Down (-5%)")
            adjust_volume("down")
            self._send_cors_headers(200)
            self.wfile.write(b"Volume decreased (-5%).")
            return

        # 5. Audio Mute
        if path in ("/mute", "/toggle_mute"):
            print("[DIRECTIVE] Toggle Mute")
            adjust_volume("mute")
            self._send_cors_headers(200)
            self.wfile.write(b"Audio mute toggled.")
            return

        # 6. Lock Workstation
        if path in ("/lock", "/lock_screen"):
            print("[DIRECTIVE] Lock Workstation")
            lock_screen()
            self._send_cors_headers(200)
            self.wfile.write(b"Workstation locked.")
            return

        # Default 404
        self._send_cors_headers(404)
        self.wfile.write(b"Directive not recognized by remote agent.")

    def log_message(self, format, *args):
        # Clean logging
        print(f"[AGENT 8080] {self.address_string()} - {args[0]}")


def run():
    server = HTTPServer(("0.0.0.0", PORT), RemoteControlHandler)
    print("=" * 60)
    print(f"🛰️ CORTANA // REMOTE LAN CONTROL AGENT ACTIVE")
    print(f"Platform: {platform.system()} ({platform.release()})")
    print(f"Listening on port: {PORT} (0.0.0.0:{PORT})")
    print(f"Ready to receive directives from Cortana / J.A.R.V.I.S.")
    print("=" * 60)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nAgent standing down.")
        server.server_close()

if __name__ == "__main__":
    run()
