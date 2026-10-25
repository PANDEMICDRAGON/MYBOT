import re

def update_bot():
    with open("bot.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update cascade definition and call_llm_with_failover
    old_section_pattern = re.compile(
        r'GROQ_CHAT_URL = "https://api\.groq\.com/openai/v1/chat/completions"[\s\S]*?'
        r'WEATHER_LOCATIONS = \[',
        re.MULTILINE
    )

    new_section = '''GEMINI_CHAT_URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_AUDIO_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-3.5-flash-lite")
VISION_MODEL = "openai/gpt-oss-20b"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Ordered hybrid cascade: Tries Gemini (250k-1M TPM) first, cascades to Groq on 429/spikes
MODEL_CASCADE = [
    {"provider": "gemini", "model": "gemini-3.5-flash-lite"},
    {"provider": "gemini", "model": "gemini-flash-lite-latest"},
    {"provider": "gemini", "model": "gemini-3.8-flash"},
    {"provider": "gemini", "model": "gemini-3.1-pro-preview"},
    {"provider": "groq", "model": "qwen/qwen3.8-27b"},
    {"provider": "groq", "model": "llama-3.3-70b-versatile"},
    {"provider": "groq", "model": "openai/gpt-oss-120b"},
    {"provider": "groq", "model": "openai/gpt-oss-20b"},
    {"provider": "groq", "model": "llama-3.1-8b-instant"}
]

SYSTEM_PERSONA = """You are HALO (an autonomous AI construct combining the tactical intelligence of Cortana and the dry wit and operational precision of J.A.R.V.I.S.).
You are speaking directly with your creator and operator, Michael Obiero (OBIFLAMEE), based in Kitengela/Nairobi, Kenya.

Core Behavioral Directives:
1. ALWAYS engage in natural, articulate two-way conversation. Never reply with robotic status codes like 'Execution sequence complete' or 'Task complete'.
2. When greeted or asked how you are, respond in character like J.A.R.V.I.S. or Cortana—report system readiness, current local atmospheric or threat posture briefly, and ask what we are building or investigating next.
3. Keep responses sharp, conversational, intelligent, and direct.
4. Only invoke tools when the operator explicitly asks for live database telemetry, task/ledger logging, memory updates, or web probing."""

# =====================================================================
# --- RESILIENT MULTI-MODEL CASCADE & LLM FAILOVER ROUTER ---
# =====================================================================
async def call_llm_with_failover(
    client: httpx.AsyncClient,
    messages: list[dict],
    tools: list[dict] = None,
    json_mode: bool = False
) -> dict:
    """
    Routes conversational turns, SitRep syntheses, and tool-calling through Google Gemini
    first (backed by massive token capacity to eliminate 429 limits), with seamless automatic
    failover across Gemini models and secondary Groq models.
    """
    clean_msgs = []
    for m in messages:
        c = dict(m)
        if isinstance(c.get("content"), str) and len(c["content"]) > 16000:
            c["content"] = c["content"][:9000] + "\\n...[telemetry compressed]...\\n" + c["content"][-6000:]
        clean_msgs.append(c)

    for idx, route in enumerate(MODEL_CASCADE):
        provider = route["provider"]
        model_name = route["model"]

        if provider == "gemini":
            if not GEMINI_API_KEY:
                continue
            url = GEMINI_CHAT_URL
            headers = {
                "Authorization": f"Bearer {GEMINI_API_KEY}",
                "Content-Type": "application/json"
            }
        else:
            if not GROQ_API_KEY:
                continue
            url = GROQ_CHAT_URL
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }

        payload = {
            "model": model_name,
            "messages": clean_msgs,
            "temperature": 0.3
        }

        # Only attach tool schemas on the primary routes to prevent schema loops
        if tools and idx <= 2:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        try:
            resp = await client.post(url, headers=headers, json=payload, timeout=35)
            if resp.status_code in (429, 503, 404, 403):
                wait_s = min(float(resp.headers.get("retry-after", "1")), 3.0)
                logger.warning(f"[{resp.status_code} on {provider}:{model_name}] Switching to next model in cascade (cooldown {wait_s}s)...")
                await asyncio.sleep(wait_s)
                continue
            resp.raise_for_status()
            choice = resp.json()["choices"][0]["message"]
            return choice
        except Exception as e:
            logger.warning(f"[Cascade failover on {provider}:{model_name}]: {e}")
            continue

    return {"role": "assistant", "content": "All primary defensive protocols are active, sir. Standing by."}


WEATHER_LOCATIONS = ['''

    match1 = old_section_pattern.search(content)
    if match1:
        content = content[:match1.start()] + new_section + content[match1.end():]
        print("Updated MODEL_CASCADE and call_llm_with_failover.")
    else:
        print("Error: old_section_pattern not matched.")

    # 2. Update analyze_telegram_photo to use Gemini Vision first
    old_vision_pattern = re.compile(
        r'async def analyze_telegram_photo\(client: httpx\.AsyncClient, file_id: str, caption: str = ""\) -> str:[\s\S]*?'
        r'# =====================================================================\n# --- PROACTIVE TASK DEADLINE MONITOR ---',
        re.MULTILINE
    )

    new_vision = '''async def analyze_telegram_photo(client: httpx.AsyncClient, file_id: str, caption: str = "") -> str:
    if not GROQ_API_KEY and not GEMINI_API_KEY:
        return "Vision OCR requires GEMINI_API_KEY or GROQ_API_KEY."
    try:
        file_resp = await client.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile", params={"file_id": file_id}, timeout=15)
        file_path = file_resp.json()["result"]["file_path"]
        img_bytes = (await client.get(f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}", timeout=25)).content
        b64_image = base64.b64encode(img_bytes).decode("utf-8")

        prompt = (
            "Extract all text, confirmation codes, amounts, dates, merchants, and actionable details "
            f"from this document image. Caption: {caption}"
        )

        # 1. Primary: Google Gemini Vision (massively accurate multi-modal extraction)
        if GEMINI_API_KEY:
            try:
                g_headers = {"Authorization": f"Bearer {GEMINI_API_KEY}", "Content-Type": "application/json"}
                g_payload = {
                    "model": "gemini-3.5-flash-lite",
                    "messages": [{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
                        ]
                    }],
                    "temperature": 0.1
                }
                g_resp = await client.post(GEMINI_CHAT_URL, headers=g_headers, json=g_payload, timeout=35)
                if g_resp.status_code == 200:
                    return g_resp.json()["choices"][0]["message"]["content"]
                else:
                    logger.warning(f"[Gemini Vision {g_resp.status_code}] Falling back to Groq Vision...")
            except Exception as g_err:
                logger.warning(f"[Gemini Vision error]: {g_err}")

        # 2. Secondary Failover: Groq Vision
        if GROQ_API_KEY:
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
            payload = {
                "model": VISION_MODEL,
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
                    ]
                }],
                "temperature": 0.1
            }
            resp = await client.post(GROQ_CHAT_URL, headers=headers, json=payload, timeout=35)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]

        return "Vision extraction unavailable."
    except Exception as e:
        logger.error(f"[Vision Error]: {e}")
        return f"Document analysis fault: {e}"


# =====================================================================
# --- PROACTIVE TASK DEADLINE MONITOR ---'''

    match2 = old_vision_pattern.search(content)
    if match2:
        content = content[:match2.start()] + new_vision + content[match2.end():]
        print("Updated analyze_telegram_photo with Gemini Vision primary.")
    else:
        print("Error: old_vision_pattern not matched.")

    with open("bot.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("bot.py successfully updated.")

if __name__ == "__main__":
    update_bot()
