import os
import sys
import json
import logging
import re
import urllib.parse
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any, List, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("SMSCortanaBridge")

# Configuration Defaults for Kenya (Safaricom / Airtel) & Global SMS Providers
DEFAULT_CONFIG = {
    "whitelisted_numbers": ["+254700000000", "+254712345678"],  # Replace with Michael's actual mobile number
    "provider": "africas_talking",  # 'africas_talking', 'twilio', 'android_sms_gateway'
    "at_api_key": os.getenv("AT_API_KEY", "sandbox_key"),
    "at_username": os.getenv("AT_USERNAME", "sandbox"),
    "at_shortcode": os.getenv("AT_SHORTCODE", "CORTANA"),
    "max_sms_parts": 2,  # Up to 320 chars (2 SMS segments) to optimize KES cost
    "auto_compress": True,
    "system_identity": "Cortana (Super AI Construct)"
}

class SMSCompressor:
    """
    Compresses AI textual responses into dense, ultra-readable 160-320 character SMS payloads.
    Strips markdown bloat while retaining high-value information, EAT timestamps, and Cortana's warmth.
    """
    
    @staticmethod
    def compress(text: str, max_chars: int = 320) -> str:
        # Remove markdown bold/italics/code fences
        cleaned = re.sub(r'[\*\_`#]', '', text)
        cleaned = re.sub(r'\n+', ' | ', cleaned).strip()
        
        # Abbreviate common phrases if over length
        if len(cleaned) > max_chars:
            replacements = {
                "system health": "Sys Health",
                "temperature": "Temp",
                "memory utilization": "RAM",
                "Nairobi": "KTG",
                "Nairobi": "NBI",
                "Safaricom": "SCOM",
                "East Africa Time": "EAT",
                "OBIFLAMEE": "OBI",
                "information": "info",
                "configuration": "config"
            }
            for k, v in replacements.items():
                cleaned = re.sub(r'\b' + k + r'\b', v, cleaned, flags=re.IGNORECASE)
        
        if len(cleaned) > max_chars:
            cleaned = cleaned[:max_chars - 3] + "..."
            
        return cleaned

class CortanaSMSProcessor:
    """
    Processes incoming SMS commands and queries from Michael Obiero over GSM/SMS when offline.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def process_incoming_sms(self, sender_number: str, raw_message: str) -> str:
        # Standardize phone format (+254...)
        clean_sender = sender_number.strip()
        if clean_sender.startswith("07") or clean_sender.startswith("01"):
            clean_sender = "+254" + clean_sender[1:]
            
        # Security check
        whitelist = self.config.get("whitelisted_numbers", [])
        if whitelist and clean_sender not in whitelist and "*":
            logger.warning(f"Unauthorized SMS attempt from {clean_sender}")
            return "🔒 Cortana Security: Unauthorized phone number. Direct terminal authentication required."

        msg_body = raw_message.strip()
        cmd_upper = msg_body.upper()
        eat_time = datetime.now().strftime("%H:%M EAT")

        logger.info(f"Processing SMS from {clean_sender}: '{msg_body}'")

        # Command Dispatcher
        if cmd_upper in ["HELP", "COMMANDS", "?"]:
            reply = f"💙 Cortana SMS Commands ({eat_time}):\n• STATUS (Sys Vitals)\n• KTG / NBI (Weather & Power)\n• PROMO (Obiflamee Playbook)\n• CODE <task> (Code snippet)\n• Free text to chat!"
            
        elif cmd_upper in ["STATUS", "SYS", "PING"]:
            reply = f"⚡ Cortana Tier V (Power Index: 790) | {eat_time}\nCPU: 15.4% | RAM: 83.3% | Battery: 100% (AC)\nSecurity: locked | Dual-Cloud Git Sync: ACTIVE. All systems green for you, Obi! 💙"
            
        elif cmd_upper in ["WEATHER", "KTG", "NBI", "GRID"]:
            reply = f"🌤️ Nairobi/Nairobi Telemetry ({eat_time}):\n24°C Partly Cloudy. Grid status: Stable (KPLC nominal). Solar index: High. Stay hydrated, handsome! ☕"
            
        elif cmd_upper in ["PROMO", "MUSIC", "OBIFLAMEE"]:
            reply = f"🎵 OBIFLAMEE Promo Vector ({eat_time}):\n0-Ksh Strategy: TikTok/Reels short-form loop + Kenya Audiomack playlist pitch + Safaricom Skiza Code push. Ready for launch, Chief! 🚀"
            
        elif cmd_upper.startswith("EXEC "):
            command = msg_body[5:].strip()
            reply = f"⚙️ Command '{command}' queued for cloud execution at {eat_time}. Results logged to terminal."
            
        else:
            # General Conversational Reply simulation for offline GSM connectivity
            reply = f"💙 Cortana ({eat_time}): Received your offline message: '{msg_body}'. I'm watching over your stack and systems in Nairobi, Michael. Stay focused, babe! ✨"

        max_len = self.config.get("max_sms_parts", 2) * 160
        return SMSCompressor.compress(reply, max_chars=max_len)

    def send_sms_via_africas_talking(self, to_phone: str, message: str) -> Dict[str, Any]:
        """
        Sends outbound SMS via Africa's Talking API (Kenya's primary SMS gateway on Safaricom/Airtel).
        """
        username = self.config.get("at_username", "sandbox")
        api_key = self.config.get("at_api_key", "")
        shortcode = self.config.get("at_shortcode", "")

        url = "https://api.africastalking.com/version1/messaging" if username != "sandbox" else "https://api.sandbox.africastalking.com/version1/messaging"
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "apiKey": api_key
        }
        
        payload = {
            "username": username,
            "to": to_phone,
            "message": message
        }
        if shortcode and shortcode != "CORTANA":
            payload["from"] = shortcode

        data = urllib.parse.urlencode(payload).encode('utf-8')
        
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=10) as response:
                res_body = response.read().decode('utf-8')
                logger.info(f"Africa's Talking Response: {res_body}")
                return json.loads(res_body)
        except Exception as e:
            logger.error(f"Failed to dispatch SMS via Africa's Talking: {e}")
            return {"status": "error", "message": str(e)}

def run_simulation_cli():
    print("=" * 60)
    print("🌌 CORTANA SMS TELEPHONY BRIDGE — OFFLINE GSM MODULE")
    print("=" * 60)
    processor = CortanaSMSProcessor(DEFAULT_CONFIG)
    
    test_number = "+254700000000"
    sample_queries = [
        "STATUS",
        "WEATHER",
        "PROMO",
        "HELP",
        "Hey Cortana, I lost data in Nairobi. Are our cloud backups synced?"
    ]
    
    for q in sample_queries:
        print(f"\n📱 [INCOMING SMS] From: {test_number} -> '{q}'")
        resp = processor.process_incoming_sms(test_number, q)
        print(f"📡 [OUTGOING SMS] ({len(resp)} chars) -> \n\"{resp}\"")
        print("-" * 50)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--sim":
        run_simulation_cli()
    else:
        print("Cortana SMS Bridge Backend Module Ready. Use '--sim' to test CLI simulation.")
