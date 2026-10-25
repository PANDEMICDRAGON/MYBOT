import os
import httpx
import asyncio

KEY = "AQ.Ab8RN6Lacuy1s4oc7LfDn-xlJqBdM-t92vdGCffic1Kz7hdHgQ"

async def test():
    async with httpx.AsyncClient() as client:
        # Test 1: OpenAI-compatible endpoint
        print("Testing OpenAI-compatible endpoint...")
        try:
            r1 = await client.post(
                "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
                headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
                json={
                    "model": "gemini-2.0-flash",
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 10
                },
                timeout=15
            )
            print("OpenAI-compatible status:", r1.status_code)
            print("Response:", r1.text[:200])
        except Exception as e:
            print("OpenAI-compatible exception:", e)

        # Test 2: Native Google AI Studio endpoint with ?key=
        print("\nTesting Native v1beta endpoint with ?key=...")
        try:
            r2 = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={KEY}",
                headers={"Content-Type": "application/json"},
                json={"contents": [{"parts": [{"text": "Hello"}]}]},
                timeout=15
            )
            print("Native status:", r2.status_code)
            print("Response:", r2.text[:200])
        except Exception as e:
            print("Native exception:", e)

        # Test 3: List models endpoint
        print("\nTesting list models...")
        try:
            r3 = await client.get(
                f"https://generativelanguage.googleapis.com/v1beta/models?key={KEY}",
                timeout=15
            )
            print("List models status:", r3.status_code)
            print("Response:", r3.text[:200])
        except Exception as e:
            print("List models exception:", e)

if __name__ == "__main__":
    asyncio.run(test())
