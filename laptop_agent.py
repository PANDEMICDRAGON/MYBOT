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

def speak_text(text: str) -> str:
    """Speaks text aloud through workstation speakers via native TTS."""
    clean = text.replace("'", " ").replace('"', ' ').replace("\n", " ").strip()
    if not clean:
        clean = "Construct active on workstation."
    try:
        if "windows" in OS_TYPE:
            ps_cmd = f"(New-Object -ComObject SAPI.SpVoice).Speak('{clean}')"
            subprocess.Popen(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd])
            return f"Vocalized aloud on laptop: '{clean}'"
        elif "darwin" in OS_TYPE:
            subprocess.Popen(["say", clean])
            return f"Vocalized aloud on macOS: '{clean}'"
        else:
            subprocess.Popen(["espeak", clean])
            return f"Vocalized aloud on Linux: '{clean}'"
    except Exception as e:
        return f"Speech fault: {e}"

def open_chrome(url: str = "") -> str:
    """Launches Google Chrome on workstation, optionally loading a URL."""
    clean_url = (url or "").strip()
    if clean_url and not clean_url.startswith(("http://", "https://")):
        clean_url = "https://" + clean_url
    try:
        if "windows" in OS_TYPE:
            if clean_url:
                subprocess.Popen(f'start chrome "{clean_url}"', shell=True)
            else:
                subprocess.Popen("start chrome", shell=True)
            return f"Google Chrome opened on workstation{' loading: ' + clean_url if clean_url else ''}."
        elif "darwin" in OS_TYPE:
            args = ["open", "-a", "Google Chrome"] + ([clean_url] if clean_url else [])
            subprocess.Popen(args)
            return f"Google Chrome opened on macOS{' loading: ' + clean_url if clean_url else ''}."
        else:
            args = ["google-chrome"] + ([clean_url] if clean_url else [])
            subprocess.Popen(args)
            return f"Google Chrome opened on workstation{' loading: ' + clean_url if clean_url else ''}."
    except Exception as e:
        if clean_url:
            webbrowser.open(clean_url)
            return f"Opened URL in default browser: {clean_url}"
        return f"Failed to open Chrome: {e}"

def close_chrome() -> str:
    """Terminates all running Google Chrome processes."""
    try:
        if "windows" in OS_TYPE:
            res = subprocess.run(["taskkill", "/IM", "chrome.exe", "/F"], capture_output=True, text=True, timeout=5)
            if res.returncode == 0 or "SUCCESS" in (res.stdout or ""):
                return "Google Chrome was terminated and closed on workstation."
            else:
                subprocess.run(
                    ["powershell", "-NoProfile", "-Command", "Stop-Process -Name chrome -Force -ErrorAction SilentlyContinue"],
                    capture_output=True, timeout=4
                )
                return "Google Chrome close command executed on workstation."
        elif "darwin" in OS_TYPE:
            subprocess.run(["killall", "Google Chrome"], capture_output=True, timeout=5)
            return "Google Chrome closed on macOS."
        else:
            subprocess.run(["killall", "chrome"], capture_output=True, timeout=5)
            return "Google Chrome closed on workstation."
    except Exception as e:
        return f"Failed to terminate Chrome: {e}"

def open_app(name: str) -> str:
    """Launches an application by name."""
    if not name:
        return "Missing application name."
    try:
        if "windows" in OS_TYPE:
            subprocess.Popen(f"start {name}", shell=True)
            return f"Application '{name}' launched on workstation."
        return f"Application launch directive '{name}' dispatched."
    except Exception as e:
        return f"Failed to launch '{name}': {e}"

def close_app(name: str) -> str:
    """Terminates an application by process name."""
    if not name:
        return "Missing application name."
    try:
        if "windows" in OS_TYPE:
            proc_name = name if name.endswith(".exe") else f"{name}.exe"
            subprocess.run(["taskkill", "/IM", proc_name, "/F"], capture_output=True, timeout=5)
            return f"Application '{name}' terminated on workstation."
        return f"Close directive for '{name}' dispatched."
    except Exception as e:
        return f"Failed to close '{name}': {e}"

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

        # 2. Speak Aloud via TTS
        if path in ("/speak", "/say", "/talk", "/vocalize"):
            text_list = query.get("text", []) or query.get("msg", [])
            text_to_speak = urllib.parse.unquote(text_list[0]) if text_list else "Construct active on workstation."
            print(f"[DIRECTIVE] Speaking aloud: '{text_to_speak}'")
            res_msg = speak_text(text_to_speak)
            self._send_cors_headers(200)
            self.wfile.write(res_msg.encode("utf-8"))
            return

        # 3. Open Chrome
        if path in ("/open_chrome", "/chrome_open", "/launch_chrome"):
            url_list = query.get("url", [])
            target_url = urllib.parse.unquote(url_list[0]) if url_list else ""
            print(f"[DIRECTIVE] Opening Chrome{' with: ' + target_url if target_url else ''}")
            res_msg = open_chrome(target_url)
            self._send_cors_headers(200)
            self.wfile.write(res_msg.encode("utf-8"))
            return

        # 4. Close Chrome
        if path in ("/close_chrome", "/kill_chrome", "/terminate_chrome", "/exit_chrome"):
            print("[DIRECTIVE] Terminating Chrome processes")
            res_msg = close_chrome()
            self._send_cors_headers(200)
            self.wfile.write(res_msg.encode("utf-8"))
            return

        # 5. Open URL in Default Browser
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

        # 6. Launch Application
        if path in ("/open_app", "/launch_app"):
            app_list = query.get("app", []) or query.get("name", [])
            app_name = urllib.parse.unquote(app_list[0]) if app_list else ""
            print(f"[DIRECTIVE] Opening app: {app_name}")
            res_msg = open_app(app_name)
            self._send_cors_headers(200)
            self.wfile.write(res_msg.encode("utf-8"))
            return

        # 7. Close Application
        if path in ("/close_app", "/kill_app"):
            app_list = query.get("app", []) or query.get("name", [])
            app_name = urllib.parse.unquote(app_list[0]) if app_list else ""
            print(f"[DIRECTIVE] Closing app: {app_name}")
            res_msg = close_app(app_name)
            self._send_cors_headers(200)
            self.wfile.write(res_msg.encode("utf-8"))
            return

        # 8. Volume Up
        if path in ("/volume_up", "/vol_up"):
            print("[DIRECTIVE] Volume Up (+5%)")
            adjust_volume("up")
            self._send_cors_headers(200)
            self.wfile.write(b"Volume increased (+5%).")
            return

        # 9. Volume Down
        if path in ("/volume_down", "/vol_down"):
            print("[DIRECTIVE] Volume Down (-5%)")
            adjust_volume("down")
            self._send_cors_headers(200)
            self.wfile.write(b"Volume decreased (-5%).")
            return

        # 10. Audio Mute
        if path in ("/mute", "/toggle_mute"):
            print("[DIRECTIVE] Toggle Mute")
            adjust_volume("mute")
            self._send_cors_headers(200)
            self.wfile.write(b"Audio mute toggled.")
            return

        # 11. Lock Workstation
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
