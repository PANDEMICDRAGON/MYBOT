import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncio
import httpx
from bot import run_agent_turn

async def main():
    async with httpx.AsyncClient() as client:
        reply = await run_agent_turn(client, "What's the latest in sports right now?")
        print("Bot sports reply:\n", reply)

if __name__ == "__main__":
    asyncio.run(main())
