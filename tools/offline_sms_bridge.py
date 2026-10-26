"""Offline SMS Modem Forwarder -> sms_cortana_bridge.py"""
from tools.sms_cortana_bridge import GSMModem

if __name__ == "__main__":
    import sys
    port = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyUSB0"
    modem = GSMModem(port=port)
    print(f"[GSM Modem] Initialized on {port}")
