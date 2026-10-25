#!/usr/bin/env python3
"""
=============================================================================
TACTICAL WI-FI RECONNAISSANCE & CONNECTION ENGINE (CORTANA / WINDOWS WLAN)
=============================================================================
Provides real-time discovery of nearby 2.4 GHz, 5 GHz & 6 GHz Wi-Fi Access Points,
evaluates signal strengths, security protocols (WPA2, WPA3, Open), channels,
and automates seamless authenticated connections with passphrases.

Commands & Usage:
  1. Scan Nearby Wi-Fi Networks:
     python wifi_manager.py scan
     python wifi_manager.py --json

  2. Check Current Connection Status:
     python wifi_manager.py status

  3. Connect to a Wi-Fi Network with Password:
     python wifi_manager.py connect "Olalo-5G" "password123"

  4. Disconnect from Current Wi-Fi:
     python wifi_manager.py disconnect
=============================================================================
"""

import os
import sys
import re
import time
import json
import binascii
import argparse
import platform
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional

# Ensure UTF-8 console output for Windows CLI
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def get_current_wifi() -> Dict[str, Any]:
    """
    Queries current Wi-Fi interface status via 'netsh wlan show interfaces'.
    """
    os_sys = platform.system().lower()
    info = {
        "connected": False,
        "interface": "",
        "ssid": "",
        "bssid": "",
        "signal": 0,
        "state": "disconnected",
        "band": "",
        "channel": "",
        "auth": "",
        "rx_rate": "",
        "tx_rate": ""
    }

    if "windows" not in os_sys:
        return info

    try:
        res = subprocess.run(
            ["netsh", "wlan", "show", "interfaces"],
            capture_output=True,
            text=True,
            timeout=8
        )
        output = res.stdout

        for line in output.splitlines():
            line_s = line.strip()
            if not line_s or ":" not in line_s:
                continue
            key, val = [x.strip() for x in line_s.split(":", 1)]
            key_l = key.lower()

            if key_l == "name":
                info["interface"] = val
            elif key_l == "state":
                info["state"] = val.lower()
                info["connected"] = ("connected" in val.lower())
            elif key_l == "ssid":
                info["ssid"] = val
            elif key_l == "bssid":
                info["bssid"] = val
            elif key_l == "signal":
                m = re.search(r"(\d+)", val)
                info["signal"] = int(m.group(1)) if m else 0
            elif key_l == "band":
                info["band"] = val
            elif key_l == "channel":
                info["channel"] = val
            elif key_l == "authentication":
                info["auth"] = val
            elif "receive rate" in key_l:
                info["rx_rate"] = val
            elif "transmit rate" in key_l:
                info["tx_rate"] = val

    except Exception as e:
        info["error"] = str(e)

    return info


def scan_nearby_wifis() -> List[Dict[str, Any]]:
    """
    Performs real-time RF sweep of nearby Wi-Fi networks via 'netsh wlan show networks mode=bssid'.
    Returns structured list of Access Points with Signal, Security, Channel, Band & BSSID.
    """
    os_sys = platform.system().lower()
    networks: List[Dict[str, Any]] = []

    if "windows" not in os_sys:
        return networks

    current_conn = get_current_wifi()
    current_ssid = current_conn.get("ssid", "")
    current_bssid = current_conn.get("bssid", "").lower()

    try:
        res = subprocess.run(
            ["netsh", "wlan", "show", "networks", "mode=bssid"],
            capture_output=True,
            text=True,
            timeout=10
        )
        output = res.stdout

        # Split output into SSID blocks
        blocks = re.split(r"\n(?=SSID \d+ : )", output)
        for block in blocks:
            if not block.strip().startswith("SSID "):
                continue

            ssid_match = re.search(r"SSID \d+ : (.*)", block)
            ssid = ssid_match.group(1).strip() if ssid_match else ""
            if not ssid:
                continue

            auth_match = re.search(r"Authentication\s+: (.*)", block)
            auth = auth_match.group(1).strip() if auth_match else "Unknown"

            enc_match = re.search(r"Encryption\s+: (.*)", block)
            encryption = enc_match.group(1).strip() if enc_match else "Unknown"

            net_type_match = re.search(r"Network type\s+: (.*)", block)
            net_type = net_type_match.group(1).strip() if net_type_match else "Infrastructure"

            # Parse BSSID sections inside this block
            bssid_blocks = re.split(r"\n\s+BSSID \d+\s+: ", block)
            for idx, b_block in enumerate(bssid_blocks):
                if idx == 0:
                    continue  # Header part before first BSSID

                bssid_line = b_block.splitlines()[0].strip()
                bssid = bssid_line.split()[0] if bssid_line else ""

                signal_match = re.search(r"Signal\s+: (\d+)%", b_block)
                signal = int(signal_match.group(1)) if signal_match else 0

                band_match = re.search(r"Band\s+: (.*)", b_block)
                band = band_match.group(1).strip() if band_match else "2.4 GHz"

                chan_match = re.search(r"Channel\s+: (\d+)", b_block)
                channel = int(chan_match.group(1)) if chan_match else 0

                radio_match = re.search(r"Radio type\s+: (.*)", b_block)
                radio = radio_match.group(1).strip() if radio_match else ""

                # Signal strength bar emoji
                if signal >= 75:
                    bars = "📶 4/4 (Excellent)"
                elif signal >= 50:
                    bars = "📶 3/4 (Good)"
                elif signal >= 25:
                    bars = "📶 2/4 (Fair)"
                else:
                    bars = "📶 1/4 (Weak)"

                is_active = (ssid == current_ssid and (not bssid or bssid.lower() == current_bssid))

                networks.append({
                    "ssid": ssid,
                    "signal": signal,
                    "signal_display": f"{signal}% {bars}",
                    "auth": auth,
                    "encryption": encryption,
                    "band": band,
                    "channel": channel,
                    "radio_type": radio,
                    "bssid": bssid,
                    "network_type": net_type,
                    "is_connected": is_active,
                    "is_secured": (auth.lower() != "open")
                })

        # Sort networks by signal strength descending
        networks.sort(key=lambda x: (not x["is_connected"], -x["signal"]))

    except Exception as e:
        networks.append({"error": str(e)})

    return networks


def format_wifi_scan_table(networks: List[Dict[str, Any]]) -> str:
    """Formats discovered Wi-Fi access points into a high-visibility tactical table."""
    if not networks:
        return "No Wi-Fi networks discovered in current scan radius."

    if "error" in networks[0]:
        return f"Wi-Fi scan encountered error: {networks[0]['error']}"

    lines = [
        "📡 NEARBY WI-FI ACCESS POINTS // RF SPECTRUM SCAN",
        "=" * 78,
        f"{'SSID':<24} | {'SIGNAL':<16} | {'BAND':<8} | {'CH':<4} | {'SECURITY':<18}",
        "-" * 78
    ]

    for net in networks:
        ssid_display = net['ssid'][:22]
        if net.get("is_connected"):
            ssid_display = f"🟢 {ssid_display}"
        else:
            lock = "🔒" if net.get("is_secured", True) else "🔓"
            ssid_display = f"{lock} {ssid_display}"

        sig = f"{net['signal']}%"
        band = net.get("band", "2.4 GHz")[:7]
        ch = str(net.get("channel", "-"))
        auth = net.get("auth", "Unknown")[:17]

        lines.append(f"{ssid_display:<24} | {sig:<16} | {band:<8} | {ch:<4} | {auth:<18}")

    lines.append("=" * 78)
    lines.append(f"Total Networks Visible: {len(networks)}")
    return "\n".join(lines)


def generate_wlan_profile_xml(ssid: str, password: str = "") -> str:
    """Generates standard Windows WLAN XML profile for connection."""
    ssid_hex = binascii.hexlify(ssid.encode("utf-8")).decode("utf-8").upper()
    safe_ssid = ssid.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    safe_pwd = password.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    if password:
        # WPA2-Personal (PSK) Profile
        return f"""<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{safe_ssid}</name>
    <SSIDConfig>
        <SSID>
            <hex>{ssid_hex}</hex>
            <name>{safe_ssid}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>{safe_pwd}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>
"""
    else:
        # Open Network Profile
        return f"""<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{safe_ssid}</name>
    <SSIDConfig>
        <SSID>
            <hex>{ssid_hex}</hex>
            <name>{safe_ssid}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>open</authentication>
                <encryption>none</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
        </security>
    </MSM>
</WLANProfile>
"""


def connect_wifi(ssid: str, password: str = "", interface: str = "") -> Dict[str, Any]:
    """
    Connects to a Wi-Fi network using the provided SSID and password.
    Creates WLAN profile, registers it, triggers connection, and validates handshake.
    """
    clean_ssid = (ssid or "").strip()
    if not clean_ssid:
        return {"status": "FAILED", "error": "Missing SSID target"}

    clean_pwd = (password or "").strip()
    os_sys = platform.system().lower()

    if "windows" not in os_sys:
        return {"status": "FAILED", "error": f"Host OS '{os_sys}' not supported for netsh WLAN"}

    # 1. Generate XML profile and write to temp file
    profile_xml = generate_wlan_profile_xml(clean_ssid, clean_pwd)
    temp_profile = Path(__file__).resolve().parent / f"temp_wlan_{int(time.time())}.xml"

    try:
        temp_profile.write_text(profile_xml, encoding="utf-8")

        # 2. Add Profile via netsh
        add_cmd = ["netsh", "wlan", "add", "profile", f"filename={temp_profile}", "user=all"]
        if interface:
            add_cmd.append(f"interface={interface}")

        res_add = subprocess.run(add_cmd, capture_output=True, text=True, timeout=15)
        if "added" not in res_add.stdout.lower() and "success" not in res_add.stdout.lower():
            return {
                "status": "FAILED",
                "error": f"Could not register Wi-Fi profile: {res_add.stdout.strip() or res_add.stderr.strip()}"
            }

        # 3. Trigger Connection
        conn_cmd = ["netsh", "wlan", "connect", f"name={clean_ssid}", f"ssid={clean_ssid}"]
        if interface:
            conn_cmd.append(f"interface={interface}")

        res_conn = subprocess.run(conn_cmd, capture_output=True, text=True, timeout=20)
        if "successfully" not in res_conn.stdout.lower():
            return {
                "status": "FAILED",
                "error": f"Connection request rejected: {res_conn.stdout.strip()}"
            }

        # 4. Verification Loop (poll for association)
        connected = False
        time.sleep(2.0)
        for _ in range(8):
            cur = get_current_wifi()
            if cur.get("connected") and cur.get("ssid") == clean_ssid:
                connected = True
                return {
                    "status": "SUCCESS",
                    "ssid": clean_ssid,
                    "bssid": cur.get("bssid"),
                    "signal": cur.get("signal"),
                    "band": cur.get("band"),
                    "channel": cur.get("channel"),
                    "interface": cur.get("interface"),
                    "message": f"Successfully connected to Wi-Fi network '{clean_ssid}' (Signal: {cur.get('signal')}%, Band: {cur.get('band')})."
                }
            time.sleep(1.0)

        # Re-check state if still associating
        final_state = get_current_wifi()
        if final_state.get("connected") and final_state.get("ssid") == clean_ssid:
            return {
                "status": "SUCCESS",
                "ssid": clean_ssid,
                "message": f"Associated with '{clean_ssid}'."
            }
        else:
            return {
                "status": "CONNECTING_OR_INVALID_PASSWORD",
                "ssid": clean_ssid,
                "current_state": final_state.get("state", "unknown"),
                "message": f"Dispatched connection to '{clean_ssid}'. Association state: {final_state.get('state')}. If unassociated, verify Wi-Fi password."
            }

    except Exception as e:
        return {"status": "FAILED", "error": str(e)}
    finally:
        # Remove temporary profile XML securely
        try:
            if temp_profile.exists():
                temp_profile.unlink()
        except Exception:
            pass


def disconnect_wifi(interface: str = "") -> Dict[str, Any]:
    """Disconnects host from current Wi-Fi network."""
    cmd = ["netsh", "wlan", "disconnect"]
    if interface:
        cmd.append(f"interface={interface}")
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
        return {
            "status": "DISCONNECTED",
            "message": res.stdout.strip() or "Wi-Fi interface disconnected."
        }
    except Exception as e:
        return {"status": "FAILED", "error": str(e)}


def list_saved_profiles() -> List[str]:
    """Lists names of all saved Wi-Fi profiles on the workstation."""
    profiles = []
    try:
        res = subprocess.run(["netsh", "wlan", "show", "profiles"], capture_output=True, text=True, timeout=8)
        for line in res.stdout.splitlines():
            if ":" in line and "profile" in line.lower() and "user profile" in line.lower():
                p_name = line.split(":", 1)[1].strip()
                if p_name:
                    profiles.append(p_name)
    except Exception:
        pass
    return profiles


def main():
    parser = argparse.ArgumentParser(description="Tactical Wi-Fi Reconnaissance & Connection Manager")
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
        info = get_current_wifi()
        if args.json:
            print(json.dumps(info, indent=2))
        else:
            state_str = "🟢 CONNECTED" if info.get("connected") else "🔴 DISCONNECTED"
            print("==================================================")
            print(f"📡 WI-FI INTERFACE STATUS: {state_str}")
            print("==================================================")
            print(f"Interface  : {info.get('interface')}")
            print(f"SSID       : {info.get('ssid') or 'N/A'}")
            print(f"BSSID      : {info.get('bssid') or 'N/A'}")
            print(f"Signal     : {info.get('signal')}%")
            print(f"Band       : {info.get('band') or 'N/A'} (Channel {info.get('channel') or 'N/A'})")
            print(f"Security   : {info.get('auth') or 'N/A'}")
            print(f"Speed      : Rx {info.get('rx_rate')} / Tx {info.get('tx_rate')}")
            print("==================================================")

    elif args.action == "connect":
        if not args.ssid:
            print("Error: Target SSID required. Usage: python wifi_manager.py connect <SSID> [PASSWORD]")
            sys.exit(1)
        res = connect_wifi(args.ssid, args.password, interface=args.interface)
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            if res.get("status") == "SUCCESS":
                print(f"✅ {res.get('message')}")
            else:
                print(f"⚠️ [{res.get('status')}]: {res.get('message') or res.get('error')}")

    elif args.action == "disconnect":
        res = disconnect_wifi(interface=args.interface)
        print(f"🔌 {res.get('message')}")

    elif args.action == "profiles":
        profs = list_saved_profiles()
        print(f"Saved Wi-Fi Profiles ({len(profs)}):")
        for p in profs:
            print(f"  • {p}")


if __name__ == "__main__":
    main()
