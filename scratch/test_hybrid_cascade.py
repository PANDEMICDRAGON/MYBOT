import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_CHAT_URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"

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

async def call_llm_with_failover(
    client: httpx.AsyncClient,
    messages: list[dict],
    tools: list[dict] = None,
    json_mode: bool = False
) -> dict:
    clean_msgs = []
    for m in messages:
        c = dict(m)
        if isinstance(c.get("content"), str) and len(c["content"]) > 16000:
            c["content"] = c["content"][:9000] + "\n...[telemetry compressed]...\n" + c["content"][-6000:]
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

        # Pass tools to primary routes
        if tools and idx <= 2:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        try:
            resp = await client.post(url, headers=headers, json=payload, timeout=35)
            if resp.status_code in (429, 503, 404, 403):
                print(f"[{resp.status_code} on {provider}:{model_name}] Failing over...")
                continue
            resp.raise_for_status()
            choice = resp.json()["choices"][0]["message"]
            print(f"[Success on {provider}:{model_name}]")
            return choice
        except Exception as e:
            print(f"[Warning on {provider}:{model_name}]: {e}")
            continue

    return {"role": "assistant", "content": "Primary and secondary neural uplinks saturated."}

async def run_tests():
    async with httpx.AsyncClient() as client:
        # 1. Chat turn
        print("--- Test 1: Chat Turn ---")
        reply = await call_llm_with_failover(
            client,
            [
                {"role": "system", "content": "You are J.A.R.V.I.S. Respond in 10 words."},
                {"role": "user", "content": "Good morning, J.A.R.V.I.S."}
            ]
        )
        print("Assistant reply:", reply.get("content"))

        # 2. JSON Mode Turn
        print("\n--- Test 2: JSON Mode ---")
        reply_json = await call_llm_with_failover(
            client,
            [
                {"role": "system", "content": "Respond strictly in JSON with fields 'status' and 'core'."},
                {"role": "user", "content": "System status check"}
            ],
            json_mode=True
        )
        print("JSON reply:", reply_json.get("content"))

if __name__ == "__main__":
    asyncio.run(run_tests())
