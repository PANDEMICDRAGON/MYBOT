import platform
import subprocess
import re
import sys

def ping_host(host: str = "1.1.1.1", count: int = 4) -> float:
    """Ping a host and return the average latency in milliseconds.

    Args:
        host: The IP address or hostname to ping.
        count: Number of echo requests to send.

    Returns:
        Average latency in ms. Raises RuntimeError on failure.
    """
    # Determine the appropriate ping command based on OS
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, str(count), host]
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception as e:
        raise RuntimeError(f"Ping command failed: {e}")

    if completed.returncode != 0:
        raise RuntimeError(f"Ping failed with return code {completed.returncode}: {completed.stderr.strip()}")

    output = completed.stdout
    # Extract latency numbers
    # Linux/macOS: "rtt min/avg/max/mdev = 12.345/13.678/15.901/0.987 ms"
    # Windows: "Average = 13ms"
    if platform.system().lower() == "windows":
        match = re.search(r"Average = (\d+)ms", output)
        if match:
            return float(match.group(1))
    else:
        match = re.search(r"=\s*([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+) ms", output)
        if match:
            # avg is the second capture group
            return float(match.group(2))
    raise RuntimeError("Could not parse ping output for latency.")

def main():
    try:
        latency = ping_host()
        print(f"Average latency to 1.1.1.1: {latency:.2f} ms")
    except RuntimeError as err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
