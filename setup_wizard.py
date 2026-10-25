"""
🧙‍♂️ CORTANA / J.A.R.V.I.S. AUTOMATED CREDENTIAL ONBOARDING WIZARD
Guides the operator through setting up free accounts, validating API keys, 
and establishing the live connection to phone and database.
"""

import os
import sys
import json
import asyncio
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import httpx
from dotenv import load_dotenv

ENV_FILE = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_FILE)

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def prompt_input(prompt_text: str, default_val: str = "") -> str:
    if default_val:
        user_val = input(f"{prompt_text} [{default_val[:8]}...]: ").strip()
        return user_val if user_val else default_val
    else:
        return input(f"{prompt_text}: ").strip()

async def validate_telegram(token: str, chat_id: str):
    if not token or not chat_id:
        return False, "Token or Chat ID missing."
    async with httpx.AsyncClient(timeout=12) as client:
        try:
            r = await client.get(f"https://api.telegram.org/bot{token}/getMe")
            data = r.json()
            if not data.get("ok"):
                return False, f"Telegram rejected token: {data.get('description')}"
            bot_name = data["result"]["username"]

            # Test send message
            send_r = await client.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={
                    "chat_id": int(chat_id),
                    "text": "🛰️ *CORTANA // J.A.R.V.I.S. HANDSHAKE VERIFIED*\n\nNeural link established with your mobile construct. All defense & OSINT vectors online.",
                    "parse_mode": "Markdown"
                }
            )
            send_data = send_r.json()
            if send_data.get("ok"):
                return True, f"Connected to @{bot_name} and verified ping sent to phone!"
            else:
                return False, f"Bot @{bot_name} valid, but cannot message ID {chat_id}: {send_data.get('description')}. Did you open the bot on Telegram and tap START?"
        except Exception as e:
            return False, f"Network error: {e}"

async def validate_groq(api_key: str):
    if not api_key:
        return False, "Groq API Key missing."
    async with httpx.AsyncClient(timeout=12) as client:
        try:
            r = await client.get(
                "https://api.groq.com/openai/v1/models",
                headers={"Authorization": f"Bearer {api_key}"}
            )
            if r.status_code == 200:
                return True, "Groq LLaMA 3.3 70B & Whisper API verified successfully!"
            else:
                return False, f"Groq API error ({r.status_code}): {r.text[:120]}"
        except Exception as e:
            return False, f"Network error: {e}"

async def validate_supabase(url: str, key: str):
    if not url or not key:
        return False, "Supabase URL or Key missing."
    clean_url = url.strip().rstrip("/")
    async with httpx.AsyncClient(timeout=12) as client:
        try:
            r = await client.get(
                f"{clean_url}/rest/v1/",
                headers={"apikey": key, "Authorization": f"Bearer {key}"}
            )
            if r.status_code in [200, 404]:
                return True, "Supabase REST endpoint verified!"
            else:
                return False, f"Supabase returned HTTP {r.status_code}"
        except Exception as e:
            return False, f"Network error: {e}"

def save_env(config: dict):
    lines = [
        "# ==========================================================",
        "# 24/7 Cortana & J.A.R.V.I.S. Cognitive Command Configuration",
        "# ==========================================================",
        "",
        "# 1. Telegram Bot Credentials",
        f"TELEGRAM_TOKEN={config.get('TELEGRAM_TOKEN', '')}",
        f"TELEGRAM_CHAT_ID={config.get('TELEGRAM_CHAT_ID', '')}",
        "",
        "# 2. Supabase Database Configuration",
        f"SUPABASE_URL={config.get('SUPABASE_URL', '')}",
        f"SUPABASE_KEY={config.get('SUPABASE_KEY', '')}",
        f"SUPABASE_ANON_KEY={config.get('SUPABASE_ANON_KEY', '')}",
        "",
        "# 3. AI Cognitive Engine (Groq API)",
        f"GROQ_API_KEY={config.get('GROQ_API_KEY', '')}",
        "",
        "# 4. Telemetry Sync Schedule (seconds)",
        f"SYNC_INTERVAL={config.get('SYNC_INTERVAL', '900')}",
        ""
    ]
    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\n💾 Saved all verified credentials to {ENV_FILE}")

async def run_wizard():
    print("=" * 65)
    print("🛰️  CORTANA // J.A.R.V.I.S. AUTOMATED ONBOARDING WIZARD")
    print("=" * 65)
    print("\nThis wizard helps you link your 3 free platform accounts in ~3 minutes:")
    print("1. Telegram  -> Gives you voice/text control on your mobile phone")
    print("2. Groq      -> Gives you ultra-fast LLaMA 3.3 70B & Whisper voice AI")
    print("3. Supabase  -> Stores conflict dossiers, OSINT profiles & financial ledger\n")

    current_config = {
        "TELEGRAM_TOKEN": os.getenv("TELEGRAM_TOKEN", ""),
        "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID", ""),
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY", ""),
        "SUPABASE_URL": os.getenv("SUPABASE_URL", ""),
        "SUPABASE_KEY": os.getenv("SUPABASE_KEY", ""),
        "SUPABASE_ANON_KEY": os.getenv("SUPABASE_ANON_KEY", ""),
        "SYNC_INTERVAL": os.getenv("SYNC_INTERVAL", "900")
    }

    # --- STEP 1: TELEGRAM ---
    print("\n" + "-" * 65)
    print("STEP 1: TELEGRAM BOT LINK (CONTROL ON YOUR PHONE)")
    print("-" * 65)
    print("How to get your Bot Token in 30 seconds:")
    print("  1. Open Telegram on your phone or web: https://t.me/BotFather")
    print("  2. Send '/newbot' and pick a name (e.g., 'My JARVIS')")
    print("  3. BotFather will give you a token like: 7123456789:AAHxyz...")
    telegram_token = prompt_input("Enter your Telegram Bot Token", current_config["TELEGRAM_TOKEN"])

    print("\nHow to get your numeric Chat ID in 15 seconds:")
    print("  1. Open Telegram and search for: https://t.me/userinfobot")
    print("  2. Send '/start' — it immediately replies with your numeric 'Id' (e.g., 987654321)")
    print("  3. IMPORTANT: Also open a chat with YOUR new bot and tap 'START' once!")
    telegram_chat_id = prompt_input("Enter your Numeric Chat ID", current_config["TELEGRAM_CHAT_ID"])

    if telegram_token and telegram_chat_id:
        print("\n⏳ Testing Telegram link and dispatching ping...")
        ok, msg = await validate_telegram(telegram_token, telegram_chat_id)
        if ok:
            print(f"✅ {msg}")
            current_config["TELEGRAM_TOKEN"] = telegram_token
            current_config["TELEGRAM_CHAT_ID"] = telegram_chat_id
        else:
            print(f"⚠️ {msg}")
            if input("Keep this value anyway? (y/n): ").lower().startswith("y"):
                current_config["TELEGRAM_TOKEN"] = telegram_token
                current_config["TELEGRAM_CHAT_ID"] = telegram_chat_id

    # --- STEP 2: GROQ AI ENGINE ---
    print("\n" + "-" * 65)
    print("STEP 2: GROQ AI INFERENCE ENGINE (FREE LLM & WHISPER)")
    print("-" * 65)
    print("How to get your Free Groq API Key in 20 seconds:")
    print("  1. Go to: https://console.groq.com/keys")
    print("  2. Sign in with Google or GitHub (100% free tier)")
    print("  3. Click 'Create API Key', name it 'JARVIS', copy the key (gsk_...)")
    groq_key = prompt_input("Enter your Groq API Key (gsk_...)", current_config["GROQ_API_KEY"])

    if groq_key:
        print("\n⏳ Validating Groq API key...")
        ok, msg = await validate_groq(groq_key)
        if ok:
            print(f"✅ {msg}")
            current_config["GROQ_API_KEY"] = groq_key
        else:
            print(f"⚠️ {msg}")
            if input("Keep this value anyway? (y/n): ").lower().startswith("y"):
                current_config["GROQ_API_KEY"] = groq_key

    # --- STEP 3: SUPABASE DATABASE ---
    print("\n" + "-" * 65)
    print("STEP 3: SUPABASE POSTGRESQL & OSINT ARCHIVE")
    print("-" * 65)
    print("How to get your Free Supabase keys in 45 seconds:")
    print("  1. Go to: https://supabase.com/dashboard")
    print("  2. Create a free project (e.g. 'Overwatch')")
    print("  3. Go to Project Settings -> API to find:")
    print("     • Project URL (https://xyz.supabase.co)")
    print("     • anon public key (eyJ...)")
    print("     • service_role secret key (eyJ...)")
    supa_url = prompt_input("Enter Supabase Project URL", current_config["SUPABASE_URL"])
    supa_anon = prompt_input("Enter Supabase anon public key", current_config["SUPABASE_ANON_KEY"])
    supa_service = prompt_input("Enter Supabase service_role key", current_config["SUPABASE_KEY"])

    if supa_url and supa_service:
        print("\n⏳ Validating Supabase credentials...")
        ok, msg = await validate_supabase(supa_url, supa_service)
        if ok:
            print(f"✅ {msg}")
            current_config["SUPABASE_URL"] = supa_url
            current_config["SUPABASE_KEY"] = supa_service
            current_config["SUPABASE_ANON_KEY"] = supa_anon
        else:
            print(f"⚠️ {msg}")
            if input("Keep this value anyway? (y/n): ").lower().startswith("y"):
                current_config["SUPABASE_URL"] = supa_url
                current_config["SUPABASE_KEY"] = supa_service
                current_config["SUPABASE_ANON_KEY"] = supa_anon

    # --- SAVE CONFIGURATION ---
    save_env(current_config)

    print("\n" + "=" * 65)
    print("🚀 SETUP COMPLETE! YOU ARE READY TO LAUNCH.")
    print("=" * 65)
    print("1. To launch the 24/7 Telegram & AI Daemon:")
    print("   .\\.venv\\Scripts\\python bot.py\n")
    print("2. Open your live Web Control HUD:")
    print("   https://telemetry-news-weather.vercel.app\n")

if __name__ == "__main__":
    asyncio.run(run_wizard())
