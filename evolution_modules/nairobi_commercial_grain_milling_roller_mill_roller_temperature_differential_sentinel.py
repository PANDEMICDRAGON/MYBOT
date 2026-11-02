"""Nairobi Commercial Grain Milling Roller Mill Roller Temperature Differential Sentinel.

Monitors thermal gradients across high-speed commercial roller mill journals to prevent
bearing failure, friction lockups, and un-calibrated thermal expansion drift during
continuous industrial grain milling operations in Nairobi, Kenya.
"""

import ast
import logging
import random
import time
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger('RollerTempDifferentialSentinel')


class RollerTemperatureDifferentialSentinel:
    """Real-time thermal differential monitoring sentinel for commercial roller mills."""

    def __init__(self, max_allowable_differential_celsius: float = 12.5, max_absolute_temp_celsius: float = 85.0):
        self.max_diff = max_allowable_differential_celsius
        self.max_temp = max_absolute_temp_celsius
        self.active_mills: Dict[str, Dict[str, float]] = {}
        logger.info("Initialized RollerTemperatureDifferentialSentinel (Max Diff: %.1fC, Max Temp: %.1fC)",
                    self.max_diff, self.max_temp)

    def register_mill(self, mill_id: str) -> None:
        """Registers a roller mill unit for thermal telemetry tracking."""
        self.active_mills[mill_id] = {
            "drive_side_temp": 45.0,
            "non_drive_side_temp": 45.0,
            "differential": 0.0,
            "status": "NORMAL"
        }
        logger.info("Registered roller mill unit: %s", mill_id)

    def ingest_telemetry(self, mill_id: str, drive_temp: float, non_drive_temp: float) -> Tuple[bool, str]:
        """Ingests raw thermal telemetry from drive and non-drive journals."""
        if mill_id not in self.active_mills:
            self.register_mill(mill_id)

        diff = abs(drive_temp - non_drive_temp)
        max_observed = max(drive_temp, non_drive_temp)
        status = "NORMAL"

        if max_observed > self.max_temp:
            status = "CRITICAL_OVERHEAT"
            logger.error("CRITICAL: Mill %s exceeded max absolute temp (%.1fC > %.1fC)", mill_id, max_observed, self.max_temp)
        elif diff > self.max_diff:
            status = "WARNING_THERMAL_ASYMMETRY"
            logger.warning("WARNING: Mill %s exhibits high thermal differential (%.1fC > %.1fC)", mill_id, diff, self.max_diff)

        self.active_mills[mill_id] = {
            "drive_side_temp": drive_temp,
            "non_drive_side_temp": non_drive_temp,
            "differential": diff,
            "status": status
        }

        return (status == "NORMAL", status)

    def audit_fleet(self) -> Dict[str, str]:
        """Audits all registered roller mills and returns their operational status."""
        return {mid: data["status"] for mid, data in self.active_mills.items()}


if __name__ == "__main__":
    logger.info("Executing self-test suite for RollerTemperatureDifferentialSentinel...")
    sentinel = RollerTemperatureDifferentialSentinel()
    mill_name = "UGALI_MILL_LINE_04"
    sentinel.register_mill(mill_name)

    # Simulate normal operation
    is_ok, status = sentinel.ingest_telemetry(mill_name, 52.3, 53.1)
    assert is_ok, f"Expected normal operation, got {status}"

    # Simulate thermal asymmetry (bearing friction anomaly)
    is_ok, status = sentinel.ingest_telemetry(mill_name, 68.5, 53.0)
    assert not is_ok and status == "WARNING_THERMAL_ASYMMETRY", f"Expected thermal warning, got {status}"

    # Simulate critical overheat
    is_ok, status = sentinel.ingest_telemetry(mill_name, 91.0, 89.5)
    assert not is_ok and status == "CRITICAL_OVERHEAT", f"Expected critical overheat, got {status}"

    # Validate syntax integrity
    with open(__file__, "r", encoding="utf-8") as f:
        source_code = f.read()
    parsed_ast = ast.parse(source_code)
    assert parsed_ast, "Module AST compilation failed."
    logger.info("RollerTemperatureDifferentialSentinel successfully verified and compiled.")
