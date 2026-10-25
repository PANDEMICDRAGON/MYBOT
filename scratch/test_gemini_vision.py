import httpx
import asyncio
import base64

KEY = "AQ.Ab8RN6Lacuy1s4oc7LfDn-xlJqBdM-t92vdGCffic1Kz7hdHgQ"
URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"

# 1x1 red PNG
TINY_PNG = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x03\x01\x01\x00\x18\xdd\x8d\xb0\x00\x00\x00\x00IEND\xaeB`\x82'

async def test_vision():
    b64 = base64.b64encode(TINY_PNG).decode("utf-8")
    async with httpx.AsyncClient() as client:
        r = await client.post(
            URL,
            headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
            json={
                "model": "gemini-3.5-flash-lite",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "What color is this 1x1 image?"},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
                        ]
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 20
            },
            timeout=20
        )
        print("Vision status:", r.status_code)
        if r.status_code == 200:
            print("Vision reply:", r.json()["choices"][0]["message"]["content"])
        else:
            print("Error:", r.text[:200])

if __name__ == "__main__":
    asyncio.run(test_vision())
