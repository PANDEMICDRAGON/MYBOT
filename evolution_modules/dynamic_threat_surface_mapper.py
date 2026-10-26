"""dynamic_threat_surface_mapper.py
Provides a dynamic mapping of the system's threat surface by enumerating processes,
listening network sockets, and critical file paths. Designed to run autonomously
within Cortana's environment to continuously assess exposure and feed risk scores
to higher‑level decision modules.
"""

import os
import fnmatch
import socket
import subprocess
import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Any

@dataclass
class ThreatEntity:
    """Represents a single element of the threat surface."""
    category: str
    identifier: str
    details: Dict[str, Any]

class ThreatSurfaceMapper:
    """Collects and analyses system artefacts that may constitute attack vectors.
    """
    def __init__(self, watch_dir: str = os.getcwd()) -> None:
        self.watch_dir = watch_dir
        self.entities: List[ThreatEntity] = []

    def scan_processes(self) -> None:
        """Populate entities with running processes using the ``ps`` command."""
        try:
            result = subprocess.run(
                ["ps", "-eo", "pid,comm,args"],
                capture_output=True,
                text=True,
                check=True,
            )
            lines = result.stdout.strip().split("\n")[1:]  # skip header
            for line in lines:
                parts = line.split(None, 2)
                if len(parts) < 2:
                    continue
                pid, comm = parts[0], parts[1]
                args = parts[2] if len(parts) == 3 else ""
                entity = ThreatEntity(
                    category="process",
                    identifier=pid,
                    details={"command": comm, "args": args},
                )
                self.entities.append(entity)
        except Exception as exc:
            raise RuntimeError(f"Failed to scan processes: {exc}") from exc

    def scan_listening_ports(self) -> None:
        """Detect TCP listening sockets via ``netstat`` (fallback to ``ss``)."""
        cmd_variants = [
            ["netstat", "-tlnp"],
            ["ss", "-tlnp"],
        ]
        for cmd in cmd_variants:
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True,
                )
                self._parse_socket_output(result.stdout)
                return
            except FileNotFoundError:
                continue
            except Exception as exc:
                raise RuntimeError(f"Socket scan failed with {cmd}: {exc}") from exc
        raise RuntimeError("Neither netstat nor ss is available on this host")

    def _parse_socket_output(self, output: str) -> None:
        lines = output.strip().split("\n")
        for line in lines[2:]:  # skip header lines
            parts = line.split()
            if len(parts) < 7:
                continue
            proto, recv_q, send_q, local_addr, foreign_addr, state, pid_prog = parts[:7]
            if state != "LISTEN":
                continue
            pid, prog = pid_prog.split("/", 1) if "/" in pid_prog else ("-", pid_prog)
            entity = ThreatEntity(
                category="listening_socket",
                identifier=local_addr,
                details={"protocol": proto, "pid": pid, "program": prog},
            )
            self.entities.append(entity)

    def scan_critical_files(self, patterns: List[str] | None = None) -> None:
        """Walk ``watch_dir`` and record files matching supplied glob patterns.
        Default patterns target typical credential or config locations.
        """
        if patterns is None:
            patterns = ["*.pem", "*.key", "*.crt", "*.conf", "*.ini"]
        for root, _, files in os.walk(self.watch_dir):
            for fname in files:
                for pat in patterns:
                    if fnmatch.fnmatch(fname, pat):
                        full_path = os.path.join(root, fname)
                        try:
                            size = os.path.getsize(full_path)
                        except OSError:
                            size = -1
                        entity = ThreatEntity(
                            category="file",
                            identifier=full_path,
                            details={"size_bytes": size, "pattern": pat},
                        )
                        self.entities.append(entity)
                        break

    def generate_report(self) -> str:
        """Return a JSON string summarising the collected threat entities."""
        report = {
            "watch_dir": self.watch_dir,
            "entity_count": len(self.entities),
            "entities": [asdict(e) for e in self.entities],
        }
        return json.dumps(report, indent=2)

def _run_self_test() -> None:
    mapper = ThreatSurfaceMapper()
    mapper.scan_processes()
    mapper.scan_listening_ports()
    mapper.scan_critical_files()
    print(mapper.generate_report())

if __name__ == "__main__":
    _run_self_test()
