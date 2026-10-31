import logging
import time
import statistics
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillTorqueComplianceSentinel")

class RollerMillTorqueComplianceSentinel:
    """
    Monitors dynamic torsional compliance across commercial roller mill drive rolls in Nairobi.
    Detects anomalous micro-slip, twist deviations, and torsional rigidity degradation.
    """
    def __init__(self, mill_id: str, compliance_threshold_nm: float = 145.0):
        self.mill_id = mill_id
        self.compliance_threshold_nm = compliance_threshold_nm
        self.torque_readings: List[float] = []
        self.slip_events: int = 0
        logger.info(f"Initialized RollerMillTorqueComplianceSentinel for mill: {mill_id}")

    def record_torque_cycle(self, incoming_torque_nm: float, outgoing_torque_nm: float) -> Dict[str, Any]:
        """Record differential torque and evaluate torsional compliance."""
        differential = abs(incoming_torque_nm - outgoing_torque_nm)
        self.torque_readings.append(differential)
        
        if len(self.torque_readings) > 1000:
            self.torque_readings.pop(0)
            
        compliant = differential <= self.compliance_threshold_nm
        if not compliant:
            self.slip_events += int(1)
            logger.warning(f"[{self.mill_id}] Torsional compliance violation! Differential: {differential:.2f} Nm")
            
        return {
            "mill_id": self.mill_id,
            "incoming_torque_nm": incoming_torque_nm,
            "outgoing_torque_nm": outgoing_torque_nm,
            "differential_nm": differential,
            "compliant": compliant,
            "total_slip_events": self.slip_events,
            "timestamp": time.time()
        }

    def get_diagnostics(self) -> Dict[str, Any]:
        """Return aggregate torsional metrics."""
        if not self.torque_readings:
            return {"status": "no_data"}
        return {
            "mill_id": self.mill_id,
            "mean_differential_nm": statistics.mean(self.torque_readings),
            "max_differential_nm": max(self.torque_readings),
            "slip_events": self.slip_events
        }

if __name__ == "__main__":
    sentinel = RollerMillTorqueComplianceSentinel("NAI-MILL-01")
    res1 = sentinel.record_torque_cycle(1200.0, 1070.0)
    print("Test Result 1:", res1)
    res2 = sentinel.record_torque_cycle(1250.0, 1090.0)
    print("Test Result 2:", res2)
    print("Diagnostics:", sentinel.get_diagnostics())
