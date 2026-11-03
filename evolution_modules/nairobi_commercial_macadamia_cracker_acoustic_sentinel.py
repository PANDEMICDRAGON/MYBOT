"""Nairobi Commercial Macadamia Nut Cracker Acoustic Synapse & Kernel Integrity Sentinel V1."""

import os
import time
import math
import logging
import json
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("MacadamiaAcousticSentinel")

class MacadamiaCrackerAcousticSentinel:
    """Monitors acoustic emissions and impact force of commercial macadamia shell-cracking units."""
    
    def __init__(self, machine_id: str, target_whole_kernel_ratio: float = 0.88):
        self.machine_id = machine_id
        self.target_whole_kernel_ratio = target_whole_kernel_ratio
        self.active = False
        self.audit_log: List[Dict[str, Any]] = []
        logger.info(f"MacadamiaCrackerAcousticSentinel initialized for machine {machine_id}")

    def analyze_acoustic_waveform(self, frequency_spectrum: List[float], peak_impact_g: float) -> Dict[str, Any]:
        """Analyses real-time frequency spectrum from cracking jaws to predict kernel fragmentation."""
        if not frequency_spectrum:
            return {"status": "error", "message": "Empty frequency spectrum provided."}
        
        # Compute spectral centroid and high-frequency shatter noise ratio
        total_amplitude = sum(frequency_spectrum)
        if total_amplitude == 0:
            weighted_centroid = 0.0
        else:
            weighted_centroid = sum(i * amp for i, amp in enumerate(frequency_spectrum)) / total_amplitude

        # High frequency energy ratio (> 8kHz indicative of shell shattering vs clean fracture)
        high_freq_start = int(len(frequency_spectrum) * 0.75)
        high_freq_energy = sum(frequency_spectrum[high_freq_start:])
        shatter_ratio = high_freq_energy / (total_amplitude + 1e-9)

        # Estimate whole kernel percentage based on empirical acoustic models
        estimated_whole_ratio = max(0.0, min(1.0, 1.0 - (shatter_ratio * 1.5) - max(0.0, (peak_impact_g - 45.0) * 0.01)))
        
        status = "OPTIMAL"
        adjustment_required = 0.0
        
        if estimated_whole_ratio < self.target_whole_kernel_ratio:
            status = "SUB_OPTIMAL_FRAGMENTATION"
            # Calculate mechanical jaw gap micro-adjustment (+/- mm)
            adjustment_required = 0.25 * (self.target_whole_kernel_ratio - estimated_whole_ratio)

        audit_entry = {
            "timestamp": time.time(),
            "machine_id": self.machine_id,
            "weighted_centroid": round(weighted_centroid, 4),
            "shatter_ratio": round(shatter_ratio, 4),
            "peak_impact_g": round(peak_impact_g, 2),
            "estimated_whole_ratio": round(estimated_whole_ratio, 4),
            "status": status,
            "hydraulic_gap_adjustment_mm": round(adjustment_required, 3)
        }
        
        self.audit_log.append(audit_entry)
        return audit_entry

    def export_telemetry(self) -> str:
        """Export audit log as JSON string for cloud synchronization."""
        return json.dumps(self.audit_log, indent=2)

if __name__ == "__main__":
    logger.info("Executing self-test suite for MacadamiaCrackerAcousticSentinel...")
    sentinel = MacadamiaCrackerAcousticSentinel(machine_id="MAC-NRB-04")
    
    # Simulate mock acoustic frequency spectrum (100 bins)
    mock_spectrum = [float(100 - abs(i - 30)) for i in range(100)]
    result = sentinel.analyze_acoustic_waveform(frequency_spectrum=mock_spectrum, peak_impact_g=41.5)
    
    logger.info(f"Test Audit Result: {result}")
    logger.info("MacadamiaCrackerAcousticSentinel self-test completed successfully.")
