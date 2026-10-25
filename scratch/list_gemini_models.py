import httpx
import asyncio

KEY = "AQ.Ab8RN6Lacuy1s4oc7LfDn-xlJqBdM-t92vdGCffic1Kz7hdHgQ"

async def check():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={KEY}")
        data = r.json()
        for m in data.get("models", []):
            methods = m.get("supportedGenerationMethods", [])
            if "generateContent" in methods:
                print(m["name"])

if __name__ == "__main__":
    asyncio.run(check())
