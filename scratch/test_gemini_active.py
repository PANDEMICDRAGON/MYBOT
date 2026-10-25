import httpx
import asyncio

KEY = "AQ.Ab8RN6Lacuy1s4oc7LfDn-xlJqBdM-t92vdGCffic1Kz7hdHgQ"

async def test_active_models():
    async with httpx.AsyncClient() as client:
        for model in ["gemini-3.8-flash", "gemini-3.1-pro-preview", "gemini-3.5-flash-lite"]:
            print(f"Testing {model} via OpenAI-compatible endpoint...")
            try:
                r = await client.post(
                    "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
                    headers={
                        "Authorization": f"Bearer {KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": "You are J.A.R.V.I.S."},
                            {"role": "user", "content": "Brief system status check in 10 words."}
                        ],
                        "temperature": 0.2,
                        "max_tokens": 100
                    },
                    timeout=20
                )
                print(f"Status: {r.status_code}")
                if r.status_code == 200:
                    data = r.json()
                    print(f"Success! Reply: {data['choices'][0]['message']['content']}")
                else:
                    print("Error:", r.text[:300])
            except Exception as e:
                print("Exception:", e)

if __name__ == "__main__":
    asyncio.run(test_active_models())
