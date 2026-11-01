import time
import math
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillResolverInterferometerSentinel")

class RollerMillResolverInterferometerSentinel:
    """
    Monitors high-speed roller mill drive shafts using a synthetic quadrature resolver
    interferometer model. Tracks harmonic phase quadrature anomalies, fringe shift
    deviations, and optical/magnetic encoder jitter in Nairobi grain mills.
    """
    def __init__(self, mill_id: str, nominal_rpm: float = 1500.0, tolerance_degrees: float = 0.05):
        self.mill_id = mill_id
        self.nominal_rpm = nominal_rpm
        self.tolerance_degrees = tolerance_degrees
        self.metrics_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized Resolver Interferometer Sentinel for Mill: {self.mill_id} at {nominal_rpm} RPM")

    def analyze_interference_pattern(self, raw_sine: float, raw_cosine: float, timestamp: Optional[float] = None) -> Dict[str, Any]:
        """
        Computes instantaneous phase angle via arctan2(sin, cos), extracts quadrature
        error, and detects interferometric fringe anomalies.
        """
        ts = timestamp if timestamp else time.time()
        
        # Compute electrical angle in radians and degrees
        rad = math.atan2(raw_sine, raw_cosine)
        deg = math.degrees(rad)
        if deg < 0:
            deg += 360.0
            
        # Synthetic reference calculation assuming steady nominal rotation
        # Expected angle based on nominal frequency (e.g. 25Hz for 1500 RPM 2-pole)
        frequency_hz = (self.nominal_rpm / 60.0)
        expected_deg = (ts * frequency_hz * 360.0) % 360.0
        
        # Phase deviation calculation with wrap-around consideration
        diff = abs(deg - expected_deg)
        if diff > 180.0:
            diff = 360.0 - diff
            
        status = "NOMINAL"
        if diff > self.tolerance_degrees:
            status = "INTERFEROMETRIC_DRIFT_WARNING"
        if diff > (self.tolerance_degrees * 3.0):
            status = "CRITICAL_RESOLVER_DECOUPLING"
            
        result = {
            "timestamp": ts,
            "mill_id": self.mill_id,
            "measured_angle_deg": round(deg, 4),
            "expected_angle_deg": round(expected_deg, 4),
            "phase_deviation_deg": round(diff, 4),
            "quadrature_magnitude": round(math.sqrt(raw_sine**2 + raw_cosine**2), 4),
            "status": status
        }
        
        self.metrics_history.append(result)
        if len(self.metrics_history) > 1000:
            self.metrics_history.pop(0)
            
        if status != "NOMINAL":
            logger.warning(f"[{self.mill_id}] Interferometer Alert: {status} | Deviation: {diff:.4f}°")
            
        return result

    def get_diagnostics_summary(self) -> Dict[str, Any]:
        """
        Returns summary statistics of the interferometer telemetry.
        """
        if not self.metrics_history:
            return {"status": "NO_DATA"}
            
        deviations = [m["phase_deviation_deg"] for m in self.metrics_history]
        max_dev = max(deviations)
        avg_dev = sum(deviations) / len(deviations)
        
        critical_count = sum(1 for m in self.metrics_history if m["status"] == "CRITICAL_RESOLVER_DECOUPLING")
        
        return {
            "mill_id": self.mill_id,
            "total_samples": len(self.metrics_history),
            "max_phase_deviation_deg": max_dev,
            "avg_phase_deviation_deg": round(avg_dev, 4),
            "critical_events": critical_count,
            "system_health": "DEGRADED" if critical_count > 0 else "HEALTHY"
        }

if __name__ == "__main__":
    print("Executing RollerMillResolverInterferometerSentinel self-test...")
    sentinel = RollerMillResolverInterferometerSentinel(mill_id="NAIROBI_MAIZE_MILL_04", nominal_rpm=1500.0, tolerance_degrees=0.05)
    
    # Simulate normal and aberrant readings
    for i in range(10):
        t = time.time() + (i * 0.01)
        angle = (t * 25.0 * 2.0 * math.pi) % (2.0 * math.pi)
        # Inject slight phase error on step 7
        if i == 7:
            angle += 0.2
        s = math.sin(angle)
        c = math.cos(angle)
        res = sentinel.analyze_interference_pattern(s, c, timestamp=t)
        print(f"Step {i}: angle={res['measured_angle_deg']}°, dev={res['phase_deviation_deg']}°, status={res['status']}")
        
    summary = sentinel.get_diagnostics_summary()
    print("Diagnostics Summary:", summary)
    print("Self-test completed successfully.")
