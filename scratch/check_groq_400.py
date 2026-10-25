import sys, os, httpx, asyncio, json
sys.path.insert(0, os.path.abspath('.'))
from dotenv import load_dotenv
load_dotenv()
from bot import GROQ_CHAT_URL, GROQ_API_KEY, LLM_MODEL

async def check_400():
    # Let's inspect what was sent or test with a minimal request
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    body = {
        "model": "qwen/qwen3.8-27b",
        "messages": [
            {"role": "system", "content": "You are HALO. Always respond in valid JSON."},
            {"role": "user", "content": "Say hello in JSON"}
        ],
        "response_format": {"type": "json_object"}
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(GROQ_CHAT_URL, headers=headers, json=body)
        print("Status:", r.status_code)
        print("Response:", r.text)

if __name__ == "__main__":
    asyncio.run(check_400())
