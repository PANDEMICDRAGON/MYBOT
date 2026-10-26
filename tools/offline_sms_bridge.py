import serial
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OfflineSMSBridge")

class GSMModem:
    def __init__(self, port: str, baudrate: int = 115200, timeout: int = 5):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = serial.Serial(port, baudrate, timeout=timeout)

    def send_at(self, cmd: str, expected: str = None, timeout: int = 2):
        self.ser.write((cmd + "\r").encode())
        time.sleep(timeout)
        resp = self.ser.read_all().decode(errors='ignore')
        logger.debug(f"AT Response: {resp.strip()}")
        if expected and expected not in resp:
            raise ValueError(f"Expected '{expected}' not in response: {resp}")
        return resp

    def send_sms(self, number: str, message: str):
        self.send_at("AT+CMGF=1")  # Text mode
        self.send_at(f"AT+CMGS=\"{number}\"", "+CMGS")
        self.ser.write((message + "\x1A").encode())
        time.sleep(3)
        resp = self.ser.read_all().decode(errors='ignore')
        logger.info(f"SMS send response: {resp.strip()}")
        return resp

    def read_inbox(self):
        self.send_at("AT+CMGF=1")
        raw = self.send_at("AT+CMGL=ALL", "+CMGL")
        msgs = []
        for line in raw.splitlines():
            if line.startswith('+CMGL:'):
                parts = line.split(',')
                idx = parts[0].split(':')[1].strip()
                sender = parts[2].strip('"')
                msgs.append((idx, sender))
        return msgs

    def delete_message(self, idx: str):
        self.send_at(f"AT+CMGD={idx}")

if __name__ == "__main__":
    modem = GSMModem(port="/dev/ttyUSB0")
    # Example: send test
    modem.send_sms("+254700000000", "Hello from offline bridge")
