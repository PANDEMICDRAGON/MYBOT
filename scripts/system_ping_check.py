"""System Ping Diagnostic Forwarder -> system.py"""
import sys
from system import ping_host

def main():
    try:
        latency = ping_host()
        print(f"Average latency to 1.1.1.1: {latency:.2f} ms")
    except Exception as err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
