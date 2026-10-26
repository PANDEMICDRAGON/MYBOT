"""
scripts/setup_shims.py
Creates backward-compatibility shims for:
  - evolution_core.py
  - super_ai_ascension.py
  - swarm_engine.py
  - osint_engine.py
  - wifi_manager.py
  - speak.py
  - halo_agent.py
  - laptop_agent.py
"""

import os
import ast

def setup_system_entrypoints():
    with open("system.py", "r", encoding="utf-8") as f:
        content = f.read()

    if "def wifi_main():" in content:
        print("wifi_main already in system.py")
        return

    entry_points = """

# ===================================================================
# CLI ENTRYPOINTS FOR SYSTEM SUBSYSTEMS
# ===================================================================

def wifi_main():
    parser = argparse.ArgumentParser(description="Tactical Wi-Fi Reconnaissance and Connection Manager")
    parser.add_argument("action", nargs="?", default="scan", choices=["scan", "status", "connect", "disconnect", "profiles"], help="Action to execute")
    parser.add_argument("ssid", nargs="?", default="", help="SSID of target Wi-Fi network")
    parser.add_argument("password", nargs="?", default="", help="Password / WPA key for target network")
    parser.add_argument("-j", "--json", action="store_true", help="Output results in strict JSON format")
    parser.add_argument("-i", "--interface", default="", help="Specific Wi-Fi interface name")
    args = parser.parse_args()

    if args.action == "scan":
        nets = scan_nearby_wifis()
        if args.json:
            print(json.dumps(nets, indent=2))
        else:
            print(format_wifi_scan_table(nets))
    elif args.action == "status":
        cur = get_current_wifi()
        if args.json:
            print(json.dumps(cur, indent=2))
        else:
            print("[Wi-Fi Status]:", cur)
    elif args.action == "connect":
        res = connect_wifi(args.ssid, args.password)
        print(json.dumps(res, indent=2))
    elif args.action == "disconnect":
        res = disconnect_wifi(args.interface)
        print(json.dumps(res, indent=2))
    elif args.action == "profiles":
        profs = list_saved_profiles()
        print(json.dumps(profs, indent=2))

def speak_main():
    parser = argparse.ArgumentParser(description="Cortana Speech Synthesis Engine")
    parser.add_argument("text", nargs="*", help="Text to vocalize through physical audio hardware")
    parser.add_argument("--engine", choices=["auto", "edge", "sapi"], default="auto", help="Speech synthesis engine")
    parser.add_argument("--rate", default="+0%", help="Rate adjustment (e.g. +10% or -10%)")
    parser.add_argument("--volume", default="+0%", help="Volume adjustment")
    parser.add_argument("--async-mode", action="store_true", help="Speak in background without blocking")
    parser.add_argument("-i", "--interactive", action="store_true", help="Launch interactive speech REPL session")
    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
        return

    if args.text:
        text_to_speak = " ".join(args.text).strip()
        speak(text_to_speak, engine=args.engine, rate=args.rate, volume=args.volume, async_mode=args.async_mode)
        return

    if not sys.stdin.isatty():
        try:
            piped_text = sys.stdin.read().strip()
            if piped_text:
                speak(piped_text, engine=args.engine, rate=args.rate, volume=args.volume, async_mode=args.async_mode)
                return
        except Exception:
            pass

    speak("Physical audio layer connected. Audio driver bridge active, Michael.", engine=args.engine)

def laptop_main():
    run()

halo_main = main if 'main' in globals() else None
"""
    with open("system.py", "a", encoding="utf-8") as f:
        f.write(entry_points)
    print("Entry points added to system.py.")

def write_shims():
    shims = {
        "evolution_core.py": '"""Backward-compatibility shim. Use from evolution import ..."""\nfrom evolution import *\n',
        "super_ai_ascension.py": '"""Backward-compatibility shim. Use from evolution import ..."""\nfrom evolution import *\n',
        "swarm_engine.py": '"""Backward-compatibility shim. Use from intelligence import ..."""\nfrom intelligence import *\n',
        "osint_engine.py": '"""Backward-compatibility shim. Use from intelligence import ..."""\nfrom intelligence import *\n',
        "wifi_manager.py": '"""Backward-compatibility shim. Use from system import ..."""\nfrom system import *\n\nif __name__ == "__main__":\n    wifi_main()\n',
        "speak.py": '"""Backward-compatibility shim. Use from system import ..."""\nfrom system import *\n\nif __name__ == "__main__":\n    speak_main()\n',
        "halo_agent.py": '"""Backward-compatibility shim. Use from system import ..."""\nimport sys\nimport asyncio\nfrom system import *\n\nif __name__ == "__main__":\n    try:\n        if halo_main:\n            asyncio.run(halo_main())\n    except (KeyboardInterrupt, SystemExit):\n        print("\\n[HALO] Daemon standing down.")\n',
        "laptop_agent.py": '"""Backward-compatibility shim. Use from system import ..."""\nfrom system import *\n\nif __name__ == "__main__":\n    laptop_main()\n'
    }

    for fname, code in shims.items():
        ast.parse(code)
        with open(fname, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"Shim created: {fname}")

if __name__ == "__main__":
    setup_system_entrypoints()
    write_shims()
    print("All shims created and validated successfully!")
