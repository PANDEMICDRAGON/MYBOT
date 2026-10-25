import os
import httpx
import asyncio
import socket
import subprocess
import platform
import json
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

def get_host_local_subnet() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        return '.'.join(s.getsockname()[0].split('.')[:3])
    except Exception:
        return '192.168.100'
    finally:
        s.close()

def _ping_host(ip: str):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    timeout_flag = "-w" if platform.system().lower() == "windows" else "-W"
    cmd = ["ping", param, "1", timeout_flag, "400", ip]
    try:
        if subprocess.call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
            return ip
    except Exception:
        pass
    return None

async def tool_scan_local_network(client: httpx.AsyncClient = None, subnet: str = "") -> str:
    """Pings local IP range to discover active devices on the Wi-Fi mesh."""
    host_subnet = get_host_local_subnet()
    if not subnet or subnet in ("192.168.1", "default", "auto"):
        subnet = host_subnet

    # Concurrent ping sweep of common DHCP/device range
    tasks = [asyncio.to_thread(_ping_host, f"{subnet}.{i}") for i in range(1, 45)]
    results = await asyncio.gather(*tasks)
    active_ping_ips = set(ip for ip in results if ip)

    # Read ARP cache
    arp_devices = {}
    try:
        cmd = ["arp", "-a"] if platform.system().lower() == "windows" else ["ip", "neigh"]
        out = subprocess.check_output(cmd, timeout=5).decode("utf-8", errors="ignore")
        for line in out.splitlines():
            parts = line.split()
            if not parts:
                continue
            ip, mac = "", "UNKNOWN"
            if platform.system().lower() == "windows":
                for p in parts:
                    if "." in p and p.count(".") == 3:
                        ip = p
                    elif ("-" in p or ":" in p) and len(p) == 17:
                        mac = p.replace("-", ":").upper()
            else:
                ip = parts[0] if "." in parts[0] else (parts[1].strip("()") if len(parts) > 1 else "")
                mac = next((p for p in parts if (":" in p or "-") and len(p) == 17), "UNKNOWN").replace("-", ":").upper()
            if ip and ip.startswith(f"{subnet}.") and not ip.endswith(".255") and ip != "255.255.255.255":
                arp_devices[ip] = mac
    except Exception as e:
        print("ARP error:", e)

    all_active_ips = active_ping_ips | set(arp_devices.keys())
    # Add local host IP itself
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        all_active_ips.add(s.getsockname()[0])
        s.close()
    except Exception:
        pass

    # Sync with Supabase lan_devices
    summary_nodes = []
    if client and SUPABASE_URL and SUPABASE_KEY:
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
        try:
            r = await client.get(f"{SUPABASE_URL}/rest/v1/lan_devices?select=*", headers=headers)
            if r.status_code == 200:
                registered = r.json()
                for dev in registered:
                    dev_ip = dev.get("ip_address")
                    is_online = dev_ip in all_active_ips
                    new_status = "ONLINE" if is_online else "OFFLINE"
                    if dev.get("status") != new_status:
                        await client.patch(
                            f"{SUPABASE_URL}/rest/v1/lan_devices?id=eq.{dev['id']}",
                            headers=headers,
                            json={"status": new_status, "last_seen": datetime.now(timezone.utc).isoformat()}
                        )
                    if is_online:
                        summary_nodes.append(f"{dev.get('device_name')} ({dev.get('device_type')}) @ {dev_ip} [ONLINE]")
        except Exception as e:
            print("Supabase sync err:", e)

    if not summary_nodes:
        summary_nodes = [f"Active Node: {ip}" for ip in sorted(all_active_ips)]

    summary_str = ", ".join(summary_nodes) if summary_nodes else "None responding to ping"
    return (
        f"Active devices discovered on subnet {subnet}.x ({len(all_active_ips)} active nodes): "
        f"{summary_str}."
    )

async def main():
    async with httpx.AsyncClient() as c:
        res = await tool_scan_local_network(c)
        print("Result:\n", res)

if __name__ == "__main__":
    asyncio.run(main())
