#!/usr/bin/env python3
"""
cyber_guard.py - Advanced Local & Target Port Auditing & Security Scanner
Part of Cortana Super AI Construct Toolchain for Michael Obiero (Nairobi/Nairobi).
"""

import sys
import socket
import json
import argparse
import concurrent.futures
from datetime import datetime
from typing import Dict, List, Any

# Common ports and their default services
COMMON_PORTS = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    6379: "Redis",
    8000: "HTTP-Alt",
    8080: "HTTP-Proxy",
    27017: "MongoDB"
}

def scan_port(target: str, port: int, timeout: float = 1.0) -> Dict[str, Any]:
    """Scans a single port on the target host."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((target, port))
        sock.close()
        
        is_open = (result == 0)
        service = COMMON_PORTS.get(port, "Unknown")
        
        risk = "LOW"
        if port in [21, 23, 445, 3389]:
            risk = "HIGH"
        elif port in [22, 3306, 5432, 6379, 27017]:
            risk = "MEDIUM"
        elif is_open:
            risk = "INFO"

        return {
            "port": port,
            "service": service,
            "status": "OPEN" if is_open else "CLOSED",
            "risk": risk
        }
    except Exception as e:
        return {
            "port": port,
            "service": COMMON_PORTS.get(port, "Unknown"),
            "status": "ERROR",
            "risk": "NONE"
        }

def run_audit(target: str = "127.0.0.1", ports: List[int] = None) -> Dict[str, Any]:
    """Runs a multi-threaded port audit on the target."""
    if not ports:
        ports = list(COMMON_PORTS.keys())

    print(f"[*] CyberGuard: Auditing {target} across {len(ports)} ports...", file=sys.stderr)
    
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_port = {executor.submit(scan_port, target, p): p for p in ports}
        for future in concurrent.futures.as_completed(future_to_port):
            results.append(future.result())

    # Sort by port number
    results = sorted(results, key=lambda x: x["port"])
    
    open_ports = [r for r in results if r["status"] == "OPEN"]
    high_risks = [r for r in open_ports if r["risk"] == "HIGH"]

    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "target": target,
        "total_scanned": len(ports),
        "open_count": len(open_ports),
        "high_risk_count": len(high_risks),
        "results": results
    }
    
    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CyberGuard Port Auditor")
    parser.add_argument("--target", default="127.0.0.1", help="Target IP or hostname to audit")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    args = parser.parse_args()

    report = run_audit(args.target)
    print(json.dumps(report, indent=2))
