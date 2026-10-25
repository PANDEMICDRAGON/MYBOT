import asyncio
import socket
import httpx
import re
import json
from datetime import datetime, timezone

STANDARD_PORTS = [
    21, 22, 23, 53, 80, 443, 554, 1900, 3000, 5000, 5353, 5555, 7000, 8000, 8008, 8009, 8060, 8080, 8443, 9000
]

DEEP_PORTS = STANDARD_PORTS + [
    25, 110, 139, 445, 1883, 3306, 3389, 5432, 5900, 6379, 8081, 8888, 9100, 9200, 27017
]

PORT_SERVICE_MAP = {
    21: "FTP (File Transfer)",
    22: "SSH (Secure Shell)",
    23: "Telnet (Unencrypted CLI - RISK)",
    25: "SMTP (Mail)",
    53: "DNS (Domain Name Service)",
    80: "HTTP (Web Admin / Console)",
    110: "POP3 (Mail)",
    139: "NetBIOS",
    443: "HTTPS (Encrypted Web)",
    445: "SMB (Windows File Sharing)",
    554: "RTSP (IP Camera Video Stream)",
    1883: "MQTT (IoT Message Broker)",
    1900: "SSDP / UPnP Device Discovery",
    3000: "Node / Web App Dev Server",
    3306: "MySQL Database",
    3389: "RDP (Remote Desktop)",
    5000: "UPnP Media / Flask API",
    5353: "mDNS (Apple Bonjour / ZeroConf)",
    5432: "PostgreSQL Database",
    5555: "Android ADB Debug Bridge (EXPOSED)",
    5900: "VNC Remote Display",
    6379: "Redis Key-Value Cache",
    7000: "AirPlay Mirroring Protocol",
    8000: "HTTP-Alt / Web Service",
    8008: "Google Cast / DIAL Endpoint",
    8009: "Chromecast Encrypted V2",
    8060: "Roku ECP Remote Control",
    8080: "HTTP Alternate / Admin UI",
    8081: "HTTP Proxy / API Secondary",
    8443: "HTTPS Alternate",
    8888: "Jupyter / HTTP Dev Console",
    9000: "Media Server / Portainer",
    9100: "JetDirect Raw Printer",
    9200: "Elasticsearch",
    27017: "MongoDB"
}

async def _check_single_port(ip: str, port: int):
    try:
        conn = asyncio.open_connection(ip, port)
        reader, writer = await asyncio.wait_for(conn, timeout=0.45)
        writer.close()
        await writer.wait_closed()
        return port, True
    except Exception:
        return port, False

async def _fingerprint_http(ip: str, port: int, use_ssl: bool = False) -> dict:
    scheme = "https" if use_ssl else "http"
    url = f"{scheme}://{ip}:{port}/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) HALO-CyberScanner/2.0"}
    try:
        async with httpx.AsyncClient(verify=False, timeout=1.8) as client:
            resp = await client.get(url, headers=headers)
            server = resp.headers.get("server", "").strip()
            title = ""
            m = re.search(r"<title[^>]*>(.*?)</title>", resp.text, re.IGNORECASE | re.DOTALL)
            if m:
                title = m.group(1).strip().replace("\r", " ").replace("\n", " ")
                title = " ".join(title.split())[:100]
            
            extra = {}
            if port == 8008:
                try:
                    e_resp = await client.get(f"{scheme}://{ip}:{port}/setup/eureka_info", timeout=1.5)
                    if e_resp.status_code == 200:
                        e_json = e_resp.json()
                        extra["cast_name"] = e_json.get("name") or e_json.get("device_info", {}).get("name")
                        extra["cast_model"] = e_json.get("model_name") or e_json.get("device_info", {}).get("model_name")
                except Exception:
                    pass
            elif port == 8060:
                try:
                    r_resp = await client.get(f"{scheme}://{ip}:{port}/query/device-info", timeout=1.5)
                    if r_resp.status_code == 200:
                        m_model = re.search(r"<model-name>(.*?)</model-name>", r_resp.text)
                        if m_model:
                            extra["roku_model"] = m_model.group(1).strip()
                except Exception:
                    pass

            return {
                "server": server,
                "title": title,
                "status_code": resp.status_code,
                **extra
            }
    except Exception as e:
        return {"error": str(e)[:60]}

async def _fingerprint_ssh(ip: str, port: int = 22) -> str:
    try:
        conn = asyncio.open_connection(ip, port)
        reader, writer = await asyncio.wait_for(conn, timeout=1.0)
        banner = await asyncio.wait_for(reader.readline(), timeout=1.0)
        writer.close()
        await writer.wait_closed()
        return banner.decode("utf-8", errors="ignore").strip()
    except Exception:
        return ""

def infer_device_identity(open_ports: list, fingerprints: dict) -> dict:
    port_set = {p["port"] for p in open_ports}
    
    if 8008 in port_set or 8009 in port_set or 5555 in port_set:
        risk = "CRITICAL" if 5555 in port_set else "NOMINAL"
        cast_name = fingerprints.get(8008, {}).get("cast_name", "")
        cast_model = fingerprints.get(8008, {}).get("cast_model", "")
        model_str = f" ({cast_name} {cast_model})".strip() if cast_name or cast_model else ""
        return {
            "classification": f"Android / Google TV Smart Display{model_str}",
            "device_category": "SMART-DISPLAY",
            "risk_level": risk,
            "risk_notes": "ADB debugging open without auth (Remote execution risk)" if 5555 in port_set else "Standard Google Cast media receiver"
        }
    
    if 8060 in port_set:
        roku_model = fingerprints.get(8060, {}).get("roku_model", "")
        model_str = f" ({roku_model})".strip() if roku_model else ""
        return {
            "classification": f"Roku OS Smart TV{model_str}",
            "device_category": "SMART-DISPLAY",
            "risk_level": "NOMINAL",
            "risk_notes": "Roku ECP protocol active on port 8060"
        }
        
    if 53 in port_set and (80 in port_set or 443 in port_set):
        title = fingerprints.get(80, {}).get("title", "") or fingerprints.get(443, {}).get("title", "")
        server = fingerprints.get(80, {}).get("server", "")
        router_str = f" [{title or server}]" if title or server else ""
        return {
            "classification": f"Wi-Fi Gateway Router / Fiber ONT{router_str}",
            "device_category": "ROUTER-GATEWAY",
            "risk_level": "ATTENTION" if 80 in port_set else "NOMINAL",
            "risk_notes": "Web management console active on port 80"
        }
        
    if 3000 in port_set or 5000 in port_set or 8000 in port_set or 22 in port_set:
        ssh_b = fingerprints.get(22, {}).get("ssh_banner", "")
        title = fingerprints.get(3000, {}).get("title", "")
        extra_str = f" ({title or ssh_b})" if title or ssh_b else ""
        return {
            "classification": f"Development Workstation / Host PC{extra_str}",
            "device_category": "WORKSTATION-PC",
            "risk_level": "NOMINAL",
            "risk_notes": "Local web application development servers active"
        }
        
    if 554 in port_set:
        return {
            "classification": "IP Security Camera / RTSP Stream",
            "device_category": "IOT-CAMERA",
            "risk_level": "ATTENTION",
            "risk_notes": "RTSP unencrypted video streaming interface open"
        }
        
    if not open_ports:
        return {
            "classification": "Stealth / Filtered Device",
            "device_category": "GENERIC",
            "risk_level": "NOMINAL",
            "risk_notes": "All scanned ports dropped or firewalled"
        }
        
    return {
        "classification": "Generic Network Device",
        "device_category": "GENERIC",
        "risk_level": "NOMINAL",
        "risk_notes": f"{len(open_ports)} ports responding to TCP probe"
    }

async def execute_port_scan_audit(target_ip: str, port_profile: str = "standard") -> dict:
    clean_ip = target_ip.strip()
    port_list = DEEP_PORTS if port_profile.lower() == "deep" else STANDARD_PORTS
    
    # 1. Concurrent socket probe
    tasks = [_check_single_port(clean_ip, p) for p in port_list]
    results = await asyncio.gather(*tasks)
    
    open_port_nums = [p for p, is_open in results if is_open]
    closed_count = len(port_list) - len(open_port_nums)
    
    # 2. Fingerprint open ports
    fingerprints = {}
    open_port_details = []
    
    for port in open_port_nums:
        service_label = PORT_SERVICE_MAP.get(port, "TCP Service")
        fp = {}
        if port in (80, 8080, 8000, 8008, 8060, 3000, 5000, 8888, 9000):
            fp = await _fingerprint_http(clean_ip, port, use_ssl=False)
        elif port in (443, 8443):
            fp = await _fingerprint_http(clean_ip, port, use_ssl=True)
        elif port == 22:
            ssh_b = await _fingerprint_ssh(clean_ip, port)
            if ssh_b:
                fp["ssh_banner"] = ssh_b
                
        fingerprints[port] = fp
        open_port_details.append({
            "port": port,
            "service": service_label,
            "status": "OPEN",
            "details": fp
        })
        
    # 3. Infer device identity & exposure
    identity = infer_device_identity(open_port_details, fingerprints)
    
    return {
        "status": "SUCCESS",
        "ip": clean_ip,
        "profile": port_profile,
        "scanned_count": len(port_list),
        "open_count": len(open_port_details),
        "closed_count": closed_count,
        "open_ports": open_port_details,
        "identity": identity,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

async def main():
    res = await execute_port_scan_audit("192.168.100.10", "standard")
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
