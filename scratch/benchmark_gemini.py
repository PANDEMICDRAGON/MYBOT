import httpx
import asyncio

KEY = "AQ.Ab8RN6Lacuy1s4oc7LfDn-xlJqBdM-t92vdGCffic1Kz7hdHgQ"

CANDIDATES = [
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-3.7-flash",
    "gemini-3.8-flash",
    "gemini-3.1-flash-lite",
    "gemini-flash-lite-latest",
    "gemini-flash-latest",
    "gemini-pro-latest",
    "gemini-3.1-pro-preview"
]

async def benchmark():
    async with httpx.AsyncClient() as client:
        for model in CANDIDATES:
            try:
                r = await client.post(
                    "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
                    headers={
                        "Authorization": f"Bearer {KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": "Ping."}],
                        "max_tokens": 10
                    },
                    timeout=15
                )
                if r.status_code == 200:
                    reply = r.json()["choices"][0]["message"]["content"].strip()
                    print(f"[{model}]: 200 OK -> {reply}")
                else:
                    err = r.json() if "application/json" in r.headers.get("content-type","") else r.text[:100]
                    print(f"[{model}]: {r.status_code} -> {err}")
            except Exception as e:
                print(f"[{model}]: Exception -> {e}")

if __name__ == "__main__":
    asyncio.run(benchmark())
