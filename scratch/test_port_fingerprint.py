import asyncio
import socket
import httpx
import re
import json

TARGET_PORTS = [
    21, 22, 23, 53, 80, 443, 554, 1900, 3000, 5000, 5353, 5555, 7000, 8000, 8008, 8009, 8060, 8080, 8443, 9000
]

PORT_SERVICES = {
    21: "FTP", 22: "SSH", 23: "Telnet", 53: "DNS", 80: "HTTP", 443: "HTTPS",
    554: "RTSP (Camera)", 1900: "SSDP/UPnP", 3000: "Dev Server / Node",
    5000: "UPnP / Flask", 5353: "mDNS", 5555: "Android ADB Debug",
    7000: "AirPlay", 8000: "HTTP-Alt", 8008: "Google Cast / DIAL",
    8009: "Chromecast TLS", 8060: "Roku ECP", 8080: "Web Proxy / Admin",
    8443: "HTTPS-Alt", 9000: "Sonar / Portainer"
}

async def check_port(ip: str, port: int):
    try:
        conn = asyncio.open_connection(ip, port)
        reader, writer = await asyncio.wait_for(conn, timeout=0.5)
        writer.close()
        await writer.wait_closed()
        return port, True
    except Exception:
        return port, False

async def grab_http_banner(ip: str, port: int, use_ssl: bool = False):
    scheme = "https" if use_ssl else "http"
    url = f"{scheme}://{ip}:{port}/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) HALO-CyberScanner/2.0"}
    try:
        async with httpx.AsyncClient(verify=False, timeout=1.5) as client:
            resp = await client.get(url, headers=headers)
            server = resp.headers.get("server", "")
            title = ""
            m = re.search(r"<title[^>]*>(.*?)</title>", resp.text, re.IGNORECASE | re.DOTALL)
            if m:
                title = m.group(1).strip()
            return {"server": server, "title": title, "status_code": resp.status_code}
    except Exception as e:
        return {"error": str(e)[:60]}

async def grab_ssh_banner(ip: str, port: int = 22):
    try:
        conn = asyncio.open_connection(ip, port)
        reader, writer = await asyncio.wait_for(conn, timeout=1.0)
        banner = await asyncio.wait_for(reader.readline(), timeout=1.0)
        writer.close()
        await writer.wait_closed()
        return banner.decode("utf-8", errors="ignore").strip()
    except Exception:
        return ""

async def scan_and_fingerprint(ip: str):
    print(f"\nScanning {ip}...")
    tasks = [check_port(ip, p) for p in TARGET_PORTS]
    results = await asyncio.gather(*tasks)
    open_ports = [p for p, is_open in results if is_open]
    print(f"Open ports on {ip}: {open_ports}")

    findings = []
    for p in open_ports:
        service = PORT_SERVICES.get(p, "TCP")
        fp = {}
        if p in (80, 8080, 8000, 8008, 8060, 3000, 5000):
            fp = await grab_http_banner(ip, p, use_ssl=False)
        elif p in (443, 8443):
            fp = await grab_http_banner(ip, p, use_ssl=True)
        elif p == 22:
            ssh_banner = await grab_ssh_banner(ip, p)
            if ssh_banner:
                fp["ssh_banner"] = ssh_banner

        findings.append({
            "port": p,
            "service": service,
            "fingerprint": fp
        })
    print("Fingerprint findings:", json.dumps(findings, indent=2))
    return findings

async def main():
    # Scan router and workstation
    for target in ["192.168.100.1", "192.168.100.8", "192.168.100.10", "192.168.100.40"]:
        await scan_and_fingerprint(target)

if __name__ == "__main__":
    asyncio.run(main())
