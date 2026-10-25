import httpx
import asyncio
import json

KEY = "AQ.Ab8RN6Lacuy1s4oc7LfDn-xlJqBdM-t92vdGCffic1Kz7hdHgQ"
URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"

async def test_features():
    async with httpx.AsyncClient() as client:
        # Test 1: JSON mode
        print("Testing JSON mode on gemini-3.5-flash-lite...")
        r_json = await client.post(
            URL,
            headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
            json={
                "model": "gemini-3.5-flash-lite",
                "messages": [
                    {"role": "system", "content": "Return a JSON object with 'status' and 'version'."},
                    {"role": "user", "content": "System check"}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.1
            },
            timeout=20
        )
        print("JSON mode status:", r_json.status_code)
        if r_json.status_code == 200:
            print("Parsed:", r_json.json()["choices"][0]["message"]["content"])
        else:
            print("Error:", r_json.text[:200])

        # Test 2: Tool calling
        print("\nTesting Tool calling on gemini-3.5-flash-lite...")
        tools = [{
            "type": "function",
            "function": {
                "name": "query_telemetry",
                "description": "Fetch live sensor telemetry.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category": {"type": "string", "enum": ["weather", "cyber", "news"]}
                    },
                    "required": ["category"]
                }
            }
        }]
        r_tools = await client.post(
            URL,
            headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
            json={
                "model": "gemini-3.5-flash-lite",
                "messages": [
                    {"role": "system", "content": "You are J.A.R.V.I.S. Use tools when needed."},
                    {"role": "user", "content": "Check current weather telemetry"}
                ],
                "tools": tools,
                "tool_choice": "auto",
                "temperature": 0.1
            },
            timeout=20
        )
        print("Tools status:", r_tools.status_code)
        if r_tools.status_code == 200:
            choice = r_tools.json()["choices"][0]["message"]
            print("Message choice:", choice)
        else:
            print("Error:", r_tools.text[:200])

if __name__ == "__main__":
    asyncio.run(test_features())
