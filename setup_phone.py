"""
🛰️ Phone Neural Link Verification Utility
Tests connection between your local Cortana / J.A.R.V.I.S. daemon and your phone via Telegram.
"""

import os
import sys
import asyncio
from pathlib import Path
import httpx
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows consoles
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()

async def test_telegram():
    print("\n" + "=" * 60)
    print("🛰️ CORTANA / J.A.R.V.I.S. PHONE NEURAL LINK CHECK")
    print("=" * 60)

    if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        print("\n❌ TELEGRAM_TOKEN is missing in your .env file!")
        print("👉 How to get it in 60 seconds:")
        print("   1. Open Telegram on your phone and search for: @BotFather")
        print("   2. Send '/newbot', give your bot a name (e.g. 'Cortana Overwatch')")
        print("   3. Copy the HTTP API token BotFather gives you into .env")
        return False

    if not TELEGRAM_CHAT_ID or TELEGRAM_CHAT_ID == "YOUR_TELEGRAM_CHAT_ID":
        print("\n❌ TELEGRAM_CHAT_ID is missing in your .env file!")
        print("👉 How to get it in 30 seconds:")
        print("   1. Open Telegram on your phone and search for: @userinfobot")
        print("   2. Send '/start' - it immediately returns your numeric 'Id' (e.g. 123456789)")
        print("   3. Copy that number into .env as TELEGRAM_CHAT_ID")
        return False

    print(f"📡 Testing connection to bot token: {TELEGRAM_TOKEN[:8]}...{TELEGRAM_TOKEN[-5:]}")
    print(f"🎯 Target phone Chat ID: {TELEGRAM_CHAT_ID}")

    async with httpx.AsyncClient(timeout=15) as client:
        # 1. Test getMe
        try:
            me_resp = await client.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getMe")
            me_data = me_resp.json()
            if not me_data.get("ok"):
                print(f"❌ Telegram API rejected token: {me_data.get('description')}")
                return False
            bot_username = me_data["result"]["username"]
            print(f"✅ Bot identified: @{bot_username}")
        except Exception as e:
            print(f"❌ Network error contacting Telegram API: {e}")
            return False

        # 2. Send instant ping to user's phone
        print("📲 Dispatching verification ping to your phone...")
        dispatch_text = (
            "🛰️ *CORTANA // J.A.R.V.I.S. NEURAL LINK VERIFIED*\n\n"
            "Autonomous Overwatch construct is linked to your device.\n"
            "• Kinetic War & Maritime Chokepoint tracking: ONLINE\n"
            "• Multi-Network News (CNN, BBC, Al Jazeera, Fox, NYT, WSJ): ONLINE\n"
            "• Voice directives & Whisper audio parsing: READY\n"
            "• Receipt OCR & Vision analysis: READY\n\n"
            "Send a voice note or ask: *'What is the latest war update?'*"
        )
        try:
            send_resp = await client.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={
                    "chat_id": int(TELEGRAM_CHAT_ID),
                    "text": dispatch_text,
                    "parse_mode": "Markdown"
                }
            )
            send_data = send_resp.json()
            if send_data.get("ok"):
                print("🎉 SUCCESS! Verification ping received on your phone!")
                print(f"👉 You can now run the 24/7 daemon using: .\\.venv\\Scripts\\python bot.py")
                return True
            else:
                print(f"⚠️ Could not deliver message to Chat ID {TELEGRAM_CHAT_ID}: {send_data.get('description')}")
                print("💡 Tip: Make sure you have opened a chat with your bot on Telegram and tapped 'START' at least once!")
                return False
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return False

if __name__ == "__main__":
    success = asyncio.run(test_telegram())
    sys.exit(0 if success else 1)
