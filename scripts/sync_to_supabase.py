import os
import json
import httpx
from dotenv import load_dotenv

load_dotenv(".env")

raw_url = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
if raw_url.endswith("/rest/v1"):
    clean_url = raw_url[:-8].rstrip("/")
else:
    clean_url = raw_url

service_key = os.getenv("SUPABASE_KEY", "").strip()

print(f"Connecting to Supabase: {clean_url}")

headers = {
    "apikey": service_key,
    "Authorization": f"Bearer {service_key}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

with open("telemetry_live.json", "r", encoding="utf-8") as f:
    live_data = json.load(f)

with httpx.Client(timeout=15) as client:
    # 1. Tactical Briefings
    if "sitrep" in live_data:
        s = live_data["sitrep"]
        briefing = {
            "sitrep": s.get("sitrep", ""),
            "threat_level": s.get("threat_level", "NOMINAL"),
            "conflict_summary": s.get("conflict_summary", ""),
            "future_risk_forecast": s.get("future_risk_forecast", ""),
            "defensive_protocol": s.get("defensive_protocol", ""),
            "asymmetric_upside": s.get("asymmetric_upside", "")
        }
        r = client.post(f"{clean_url}/rest/v1/tactical_briefings", headers=headers, json=briefing)
        print("Tactical briefing seeded:", r.status_code)

    # 2. Weather Reports
    if "weather" in live_data:
        for w in live_data["weather"]:
            w_rec = {
                "city": w.get("city"),
                "scope": w.get("scope"),
                "temp_c": w.get("temp_c"),
                "humidity": w.get("humidity"),
                "wind_kmh": w.get("wind_kmh"),
                "condition": w.get("condition")
            }
            r = client.post(f"{clean_url}/rest/v1/weather_reports", headers=headers, json=w_rec)
        print("Weather reports seeded.")

    # 3. LAN Devices (Real Discovered Devices)
    if "lan_devices" in live_data:
        for d in live_data["lan_devices"]:
            d_rec = {
                "device_name": d.get("device_name"),
                "device_type": d.get("device_type"),
                "ip_address": d.get("ip_address"),
                "mac_address": d.get("mac_address"),
                "control_port": d.get("control_port", 80),
                "status": d.get("status", "ONLINE")
            }
            r = client.post(f"{clean_url}/rest/v1/lan_devices", headers=headers, json=d_rec)
        print("LAN devices seeded.")

    # 4. Personal Tasks
    if "tasks" in live_data:
        for t in live_data["tasks"]:
            t_rec = {
                "title": t.get("title"),
                "priority": t.get("priority", "NORMAL"),
                "due_at": t.get("due_at"),
                "completed": False
            }
            client.post(f"{clean_url}/rest/v1/personal_tasks", headers=headers, json=t_rec)
        print("Tasks seeded.")

    # 5. Personal Ledger
    if "ledger" in live_data:
        for l in live_data["ledger"]:
            l_rec = {
                "counterparty": l.get("counterparty"),
                "category": l.get("category"),
                "amount": l.get("amount"),
                "currency": l.get("currency", "KES"),
                "ref_code": l.get("ref_code")
            }
            client.post(f"{clean_url}/rest/v1/personal_ledger", headers=headers, json=l_rec)
        print("Ledger seeded.")

    # 6. Idea Vault
    if "vault" in live_data:
        for v in live_data["vault"]:
            v_rec = {
                "tag": v.get("tag", "NOTE"),
                "content": v.get("content")
            }
            client.post(f"{clean_url}/rest/v1/idea_vault", headers=headers, json=v_rec)
        print("Vault seeded.")

    # 7. Conflicts
    if "conflicts" in live_data:
        for c in live_data["conflicts"][:15]:
            c_rec = {
                "headline": c.get("headline"),
                "theater": c.get("theater"),
                "domain": c.get("domain"),
                "severity": c.get("severity", "ELEVATED"),
                "summary": c.get("summary", ""),
                "source": c.get("source"),
                "link": c.get("link"),
                "content_hash": c.get("content_hash")
            }
            client.post(f"{clean_url}/rest/v1/conflict_and_macro_intel", headers=headers, json=c_rec)
        print("Conflicts seeded.")

    # 8. Cyber Alerts
    if "cyber" in live_data:
        for cy in live_data["cyber"][:20]:
            cy_rec = {
                "category": cy.get("category", "CVE-KEV"),
                "source": cy.get("source"),
                "cve_id": cy.get("cve_id"),
                "severity": cy.get("severity", "HIGH"),
                "title": cy.get("title"),
                "summary": cy.get("summary"),
                "link": cy.get("link"),
                "content_hash": cy.get("content_hash")
            }
            client.post(f"{clean_url}/rest/v1/cyber_alerts", headers=headers, json=cy_rec)
        print("Cyber alerts seeded.")

    # 9. News Articles
    if "news" in live_data:
        for n in live_data["news"][:15]:
            n_rec = {
                "scope": n.get("scope", "GLOBAL"),
                "source": n.get("source"),
                "title": n.get("title"),
                "link": n.get("link"),
                "content_hash": n.get("content_hash")
            }
            client.post(f"{clean_url}/rest/v1/news_articles", headers=headers, json=n_rec)
        print("News articles seeded.")

print("All live data synced to Supabase successfully!")
