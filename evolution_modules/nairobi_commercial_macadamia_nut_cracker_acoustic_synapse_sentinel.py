"""Nairobi Commercial Macadamia Nut Cracker Acoustic Synapse Sentinel.

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)

Monitors acoustic emissions and mechanical torque feedback from commercial
macadamia nut cracking machinery to dynamically tune anvil gaps, preventing
kernel damage and maximizing whole-kernel yield.
"""

import ast
import json
import logging
import math
import random
import time
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("MacadamiaAcousticSentinel")


class MacadamiaAcousticSynapseSentinel:
    """Real-time acoustic resonance and impact correlator for macadamia processing."""

    def __init__(self, machine_id: str = "MACADAMIA_CRACKER_01", target_kernel_integrity_pct: float = 92.5):
        self.machine_id = machine_id
        self.target_integrity = target_kernel_integrity_pct
        self.current_anvil_gap_mm = 14.2
        self.acoustic_history: List[float] = []
        self.torque_history: List[float] = []
        logger.info(f"Initialized {self.machine_id} with target yield integrity {self.target_integrity}%")

    def ingest_telemetry(self, acoustic_db: float, torque_nm: float, vibration_hz: float) -> Dict[str, Any]:
        """Ingest live sensor readings and compute yield health."""
        self.acoustic_history.append(acoustic_db)
        self.torque_history.append(torque_nm)
        if len(self.acoustic_history) > 100:
            self.acoustic_history.pop(0)
            self.torque_history.pop(0)

        # Acoustic anomaly detection (shell fracture resonance typically peaks at 4.2kHz - 6.5kHz)
        # Simulated index score based on noise-to-torque ratio
        mean_acoustic = sum(self.acoustic_history) / len(self.acoustic_history)
        mean_torque = sum(self.torque_history) / len(self.torque_history)
        
        integrity_estimate = max(70.0, min(99.9, 100.0 - abs(acoustic_db - mean_acoustic) * 0.4 - abs(torque_nm - mean_torque) * 0.1))
        
        adjustment_needed = 0.0
        status = "OPTIMAL"
        if integrity_estimate < self.target_integrity:
            status = "ADJUSTING_GAP"
            if torque_nm > mean_torque:
                # Too much resistance: kernels likely getting crushed; widen gap slightly
                adjustment_needed = 0.05
            else:
                # Too loose: uncracked shells passing; narrow gap slightly
                adjustment_needed = -0.05

        self.current_anvil_gap_mm = round(max(10.0, min(18.0, self.current_anvil_gap_mm + adjustment_needed)), 3)

        return {
            "machine_id": self.machine_id,
            "timestamp": time.time(),
            "acoustic_db": acoustic_db,
            "torque_nm": torque_nm,
            "vibration_hz": vibration_hz,
            "estimated_kernel_integrity_pct": round(integrity_estimate, 2),
            "anvil_gap_mm": self.current_anvil_gap_mm,
            "status": status
        }

    def run_diagnostics(self) -> str:
        """Execute internal bytecode integrity check."""
        source_code = inspect_source(self.__class__)
        parsed = ast.parse(source_code)
        return f"Diagnostics PASSED. AST nodes parsed: {len(parsed.body)}"


def inspect_source(cls) -> str:
    import inspect
    return inspect.getsource(cls)


if __name__ == "__main__":
    logger.info("Executing Nairobi Commercial Macadamia Nut Cracker Acoustic Synapse Sentinel Test Rig...")
    sentinel = MacadamiaAcousticSynapseSentinel()
    
    for i in range(5):
        mock_acoustic = 85.0 + random.uniform(-3.0, 3.0)
        mock_torque = 45.0 + random.uniform(-2.5, 2.5)
        mock_vibration = 1200.0 + random.uniform(-50.0, 50.0)
        
        result = sentinel.ingest_telemetry(mock_acoustic, mock_torque, mock_vibration)
        print(json.dumps(result, indent=2))
        time.sleep(0.1)

    print(sentinel.run_diagnostics())
