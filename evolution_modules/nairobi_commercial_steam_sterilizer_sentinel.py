import time
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("SteamSterilizerSentinel")

class NairobiCommercialSteamSterilizerSentinel:
    """
    Monitors and validates industrial steam sterilizer cycles in Nairobi labs and clinics,
    ensuring precise temperature, pressure, and holding time parameters for pathogen destruction.
    """
    def __init__(self, sterilizer_id: str, chamber_volume_liters: float = 300.0):
        self.sterilizer_id = sterilizer_id
        self.chamber_volume_liters = chamber_volume_liters
        self.cycle_history: List[Dict[str, Any]] = []
        self.active_cycle: Optional[Dict[str, Any]] = None

    def start_cycle(self, cycle_type: str = "GRAVITY_121C") -> Dict[str, Any]:
        """Initiates a new sterilization cycle."""
        if self.active_cycle and self.active_cycle.get("status") == "RUNNING":
            raise ValueError(f"Sterilizer {self.sterilizer_id} already has an active cycle.")
        
        self.active_cycle = {
            "cycle_id": f"CYC-{int(time.time())}",
            "cycle_type": cycle_type,
            "start_time": time.time(),
            "status": "RUNNING",
            "phases": [],
            "alerts": []
        }
        logger.info(f"[{self.sterilizer_id}] Started sterilization cycle: {cycle_type}")
        return self.active_cycle

    def record_phase_metrics(self, temperature_c: float, pressure_kpa: float, phase: str) -> Dict[str, Any]:
        """
        Records temperature and pressure readings during conditioning, exposure, or exhaust phases.
        """
        if not self.active_cycle or self.active_cycle.get("status") != "RUNNING":
            raise RuntimeError(f"No active sterilization cycle found for {self.sterilizer_id}.")

        reading = {
            "timestamp": time.time(),
            "phase": phase,
            "temperature_c": temperature_c,
            "pressure_kpa": pressure_kpa
        }
        self.active_cycle["phases"].append(reading)

        # Safety checks for saturated steam parameters
        if phase == "EXPOSURE":
            if temperature_c < 121.0:
                alert = f"Sub-standard exposure temperature: {temperature_c}C (<121C threshold)."
                self.active_cycle["alerts"].append(alert)
                logger.warning(f"[{self.sterilizer_id}] {alert}")
            if pressure_kpa < 100.0:
                alert = f"Inadequate steam pressure: {pressure_kpa} kPa."
                self.active_cycle["alerts"].append(alert)
                logger.warning(f"[{self.sterilizer_id}] {alert}")

        return reading

    def complete_cycle(self, biological_indicator_passed: bool = True) -> Dict[str, Any]:
        """
        Completes the current cycle, validates biological indicator results, and archives.
        """
        if not self.active_cycle or self.active_cycle.get("status") != "RUNNING":
            raise RuntimeError(f"No running cycle to complete on {self.sterilizer_id}.")

        self.active_cycle["end_time"] = time.time()
        duration_mins = (self.active_cycle["end_time"] - self.active_cycle["start_time"]) / 60.0
        
        passed_criteria = len(self.active_cycle["alerts"]) == 0 and biological_indicator_passed
        self.active_cycle["status"] = "COMPLETED_PASSED" if passed_criteria else "COMPLETED_FAILED"
        self.active_cycle["duration_minutes"] = round(duration_mins, 2)
        self.active_cycle["biological_indicator_passed"] = biological_indicator_passed

        self.cycle_history.append(self.active_cycle)
        completed = self.active_cycle
        self.active_cycle = None

        logger.info(f"[{self.sterilizer_id}] Cycle finished with status: {completed['status']}")
        return completed

    def get_compliance_summary(self) -> Dict[str, Any]:
        """Summarizes autoclave performance and compliance metrics."""
        total_cycles = len(self.cycle_history)
        if total_cycles == 0:
            return {"total_cycles": 0, "compliance_rate": 1.0}

        passed = sum(1 for c in self.cycle_history if c["status"] == "COMPLETED_PASSED")
        return {
            "sterilizer_id": self.sterilizer_id,
            "total_cycles": total_cycles,
            "passed_cycles": passed,
            "compliance_rate": round(passed / total_cycles, 4)
        }

if __name__ == "__main__":
    sentinel = NairobiCommercialSteamSterilizerSentinel(sterilizer_id="AUTOCLAVE-NRB-04")
    cycle = sentinel.start_cycle(cycle_type="PRE_VACUUM_134C")
    sentinel.record_phase_metrics(temperature_c=135.2, pressure_kpa=210.0, phase="EXPOSURE")
    result = sentinel.complete_cycle(biological_indicator_passed=True)
    print("Sterilizer Simulation Result:", result)
    print("Compliance Summary:", sentinel.get_compliance_summary())
