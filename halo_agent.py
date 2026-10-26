"""Backward-compatibility shim. Use from system import ..."""
import sys
import asyncio
from system import *

if __name__ == "__main__":
    try:
        if halo_main:
            asyncio.run(halo_main())
    except (KeyboardInterrupt, SystemExit):
        print("\n[HALO] Daemon standing down.")
