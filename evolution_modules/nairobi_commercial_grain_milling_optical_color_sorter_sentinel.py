"""
Nairobi Commercial Grain Milling Optical Color Sorter Sentinel
=============================================================
Monitors high-speed bichromatic and NIR optical color sorters across grain milling plants
in Nairobi Industrial Area. Detects ejector solenoid valve latency, camera optical illumination
degradation, lens dust accumulation, air ejector manifold pressure drops, and erratic rejection
ratios to guarantee food safety compliance (KEBS aflatoxin/discolored grain standards) while
minimizing good-grain yield loss.
"""

import time
import math
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("OpticalColorSorterSentinel")


@dataclass
class ChuteTelemetry:
    chute_id: str
    camera_lux: float  # Expected: 800.0 - 1200.0 lux
    reference_voltage_mv: float  # Expected: 2400.0 - 2600.0 mV
    ejector_latency_ms: float  # Expected: 0.8 - 2.5 ms
    lens_dust_opacity_pct: float  # 0.0 to 100.0%
    defect_detection_rate_ppm: float  # Defect rate in PPM
    false_rejection_ratio: float  # Ratio of good grain in reject stream (0.0 to 1.0)
    air_pressure_bar: float  # Expected: 5.5 - 7.0 bar
    throughput_tph: float  # Metric tons per hour passing chute


@dataclass
class ChuteStatus:
    chute_id: str
    is_operational: bool
    health_score: float  # 0.0 to 100.0
    lens_cleaning_required: bool
    ejector_calibration_required: bool
    pressure_warning: bool
    detected_anomalies: List[str] = field(default_factory=list)


class OpticalColorSorterSentinel:
    """
    Real-time telemetry monitor and diagnostic engine for high-throughput
    commercial grain milling optical sorters.
    """

    def __init__(
        self,
        sorter_id: str = "SORTER-NRB-01",
        min_lux: float = 750.0,
        max_ejector_latency_ms: float = 3.5,
        max_lens_opacity_pct: float = 15.0,
        min_air_pressure_bar: float = 5.0,
        max_false_rejection_ratio: float = 0.08
    ):
        self.sorter_id = sorter_id
        self.min_lux = min_lux
        self.max_ejector_latency_ms = max_ejector_latency_ms
        self.max_lens_opacity_pct = max_lens_opacity_pct
        self.min_air_pressure_bar = min_air_pressure_bar
        self.max_false_rejection_ratio = max_false_rejection_ratio
        self.history: Dict[str, List[ChuteTelemetry]] = {}

    def analyze_chute(self, telemetry: ChuteTelemetry) -> ChuteStatus:
        """
        Analyzes a single optical chute telemetry sample and generates health indicators.
        """
        anomalies = []
        health_score = 100.0
        lens_clean = False
        ejector_calib = False
        pressure_warn = False

        # Illumination check
        if telemetry.camera_lux < self.min_lux:
            anomalies.append(f"Insufficient optical illumination: {telemetry.camera_lux:.1f} lux (min {self.min_lux})")
            health_score -= 20.0

        # Lens opacity check
        if telemetry.lens_dust_opacity_pct > self.max_lens_opacity_pct:
            lens_clean = True
            anomalies.append(f"High camera lens dust opacity: {telemetry.lens_dust_opacity_pct:.1f}%")
            health_score -= 25.0

        # Ejector valve latency check
        if telemetry.ejector_latency_ms > self.max_ejector_latency_ms:
            ejector_calib = True
            anomalies.append(f"Excessive ejector solenoid latency: {telemetry.ejector_latency_ms:.2f} ms")
            health_score -= 25.0

        # Air pressure check
        if telemetry.air_pressure_bar < self.min_air_pressure_bar:
            pressure_warn = True
            anomalies.append(f"Low ejector air supply pressure: {telemetry.air_pressure_bar:.2f} bar")
            health_score -= 20.0

        # False rejection ratio check
        if telemetry.false_rejection_ratio > self.max_false_rejection_ratio:
            anomalies.append(f"High false rejection ratio: {telemetry.false_rejection_ratio:.3f}")
            health_score -= 10.0

        health_score = max(0.0, health_score)
        is_operational = health_score >= 50.0

        # Record history
        if telemetry.chute_id not in self.history:
            self.history[telemetry.chute_id] = []
        self.history[telemetry.chute_id].append(telemetry)
        if len(self.history[telemetry.chute_id]) > 100:
            self.history[telemetry.chute_id].pop(0)

        return ChuteStatus(
            chute_id=telemetry.chute_id,
            is_operational=is_operational,
            health_score=health_score,
            lens_cleaning_required=lens_clean,
            ejector_calibration_required=ejector_calib,
            pressure_warning=pressure_warn,
            detected_anomalies=anomalies
        )

    def evaluate_sorter_bank(self, telemetry_batch: List[ChuteTelemetry]) -> Dict[str, object]:
        """
        Evaluates an entire bank of optical sorter chutes and returns plant-level operational metrics.
        """
        chute_statuses = [self.analyze_chute(t) for t in telemetry_batch]
        total_throughput = sum(t.throughput_tph for t in telemetry_batch)
        avg_health = sum(s.health_score for s in chute_statuses) / len(chute_statuses) if chute_statuses else 0.0

        chutes_needing_cleaning = [s.chute_id for s in chute_statuses if s.lens_cleaning_required]
        chutes_needing_calibration = [s.chute_id for s in chute_statuses if s.ejector_calibration_required]

        overall_status = "OPTIMAL"
        if avg_health < 60.0:
            overall_status = "CRITICAL"
        elif avg_health < 85.0 or len(chutes_needing_cleaning) > 0:
            overall_status = "WARNING"

        return {
            "sorter_id": self.sorter_id,
            "overall_status": overall_status,
            "average_health_score": round(avg_health, 2),
            "total_throughput_tph": round(total_throughput, 2),
            "active_chutes_count": len(telemetry_batch),
            "chutes_requiring_lens_cleaning": chutes_needing_cleaning,
            "chutes_requiring_ejector_calibration": chutes_needing_calibration,
            "chute_details": chute_statuses
        }


if __name__ == "__main__":
    sentinel = OpticalColorSorterSentinel(sorter_id="SORTER-IND-AREA-04")
    sample_data = [
        ChuteTelemetry("CHUTE-01", 950.0, 2500.0, 1.2, 5.0, 450.0, 0.02, 6.2, 12.5),
        ChuteTelemetry("CHUTE-02", 710.0, 2350.0, 4.1, 18.5, 890.0, 0.12, 4.8, 11.8),
        ChuteTelemetry("CHUTE-03", 1050.0, 2520.0, 1.5, 3.2, 310.0, 0.01, 6.4, 13.0)
    ]
    report = sentinel.evaluate_sorter_bank(sample_data)
    print(f"Sorter ID: {report['sorter_id']}")
    print(f"Status: {report['overall_status']}")
    print(f"Average Health: {report['average_health_score']}%")
    for detail in report["chute_details"]:
        print(f"  {detail.chute_id}: Health={detail.health_score}%, Anomalies={detail.detected_anomalies}")
