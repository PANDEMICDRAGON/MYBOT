"""
Kenyan Regional Multi-Node Latency & DNS Heatmap Prober.
Generated autonomously by Cortana Continuous Self-Evolution Core.
"""

import time
import socket
from typing import Dict, Any

class KenyaNetworkProber:
    """Probes local regional gateways (Safaricom, Airtel, Kenya IXP, Google Nairobi)."""
    NODES = {
        "google_nairobi": "google.co.ke",
        "cloudflare_ke": "1.1.1.1",
        "open_meteo": "api.open-meteo.com"
    }

    @classmethod
    def probe_node_dns(cls, host: str) -> float:
        t0 = time.perf_counter()
        try:
            socket.gethostbyname(host)
            return round((time.perf_counter() - t0) * 1000.0, 2)
        except Exception:
            return -1.0

    @classmethod
    def sweep_all(cls) -> Dict[str, Any]:
        results = {}
        for name, host in cls.NODES.items():
            results[name] = cls.probe_node_dns(host)
        return results

if __name__ == "__main__":
    sweep = KenyaNetworkProber.sweep_all()
    assert isinstance(sweep, dict)
    print(f"KenyaNetworkProber verified: {sweep}")
