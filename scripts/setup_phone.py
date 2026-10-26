"""Phone Link Test Forwarder -> setup_wizard.py"""
import asyncio
from scripts.setup_wizard import test_telegram_link

if __name__ == "__main__":
    asyncio.run(test_telegram_link())
