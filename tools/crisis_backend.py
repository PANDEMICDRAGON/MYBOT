#!/usr/bin/env python3
"""
Global Crisis & Nuclear Fallout Preparedness Command Center
Backend API for tracking survival resources, bunker telemetry, and emergency protocols.
"""

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

DATA_FILE = "tools/crisis_data.json"

DEFAULT_DATA = {
    "readiness_score": 88,
    "defcon_level": "DEFCON 2",
    "target_date": "2026-11-03",
    "categories": [
        {
            "name": "Water & Hydration",
            "status": "Secured",
            "items": ["300L RO Filtered Water", "Gravity Ceramic Filters", "Purification Tablets"]
        },
        {
            "name": "Energy & Power",
            "status": "Nominal",
            "items": ["Solar Generator 2kW", "LiFePO4 Backup Banks", "EMP Faraday Shielding"]
        },
        {
            "name": "Comms & Recon",
            "status": "Active",
            "items": ["Mesh Radio Nodes", "Starlink Terminal + Manual Backup", "Encrypted Offline LLMs"]
        },
        {
            "name": "Medical & NBC",
            "status": "Critical Review",
            "items": ["Potassium Iodide Stockpile", "Trauma First Aid Kits", "Hazmat / P100 Respirators"]
        }
    ]
}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    save_data(DEFAULT_DATA)
    return DEFAULT_DATA

def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

class CrisisHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/status":
            data = load_data()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/update":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            try:
                body = json.loads(post_data.decode("utf-8"))
                save_data(body)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "data": body}).encode("utf-8"))
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

def run_server(port=8092):
    server = HTTPServer(("0.0.0.0", port), CrisisHandler)
    print(f"Crisis Command Center backend running on port {port}...")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
