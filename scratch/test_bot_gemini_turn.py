import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncio
import httpx
from bot import run_agent_turn

async def main():
    async with httpx.AsyncClient() as client:
        print("--- Test A: Conversational Greeting ---")
        reply1 = await run_agent_turn(client, "Hello, how are you doing today?")
        print("Reply 1:", reply1)

        print("\n--- Test B: Telemetry Query ---")
        reply2 = await run_agent_turn(client, "Check our current weather in Kitengela.")
        print("Reply 2:", reply2)

if __name__ == "__main__":
    asyncio.run(main())
