import ast
import logging
import math
import random
import time
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [AERO_ACOUSTIC_SENTINEL]: %(message)s')
logger = logging.getLogger('AeroAcousticAnomalySentinel')

class RollerGapAcousticAnomalySentinel:
    """
    Monitors electro-acoustic emissions from commercial roller mill gaps using rolling-window
    spectral kurtosis and crest factor analysis to detect micro-jamming, bearing degradation, 
    or destructive roller contact before mill vibration compromises flour throughput.
    """
    def __init__(self, sample_rate_hz: int = 44100, buffer_size: int = 2048, anomaly_threshold: float = 3.8):
        self.sample_rate_hz = sample_rate_hz
        self.buffer_size = buffer_size
        self.anomaly_threshold = anomaly_threshold
        self.baseline_kurtosis: float = 3.0
        self.baseline_crest_factor: float = 4.2
        self.telemetry_history: List[Dict[str, float]] = []
        logger.info("RollerGapAcousticAnomalySentinel initialized for Nairobi Milling Plant Grid.")

    def ingest_audio_spectrum(self, frequency_bins: List[float], rms_amplitude: float) -> Dict[str, float]:
        """
        Ingests frequency bin magnitudes and RMS amplitude from acoustic transducers mounted on roller housings.
        Computes spectral kurtosis and crest factor to spot impact anomalies.
        """
        if not frequency_bins:
            return {"status": "error", "reason": "empty_frequency_bins"}

        # Compute pseudo crest factor
        peak_amplitude = max(frequency_bins)
        crest_factor = (peak_amplitude / (rms_amplitude + 1e-6))

        # Compute pseudo spectral kurtosis (fourth standardized moment)
        mean_val = sum(frequency_bins) / len(frequency_bins)
        variance = sum((x - mean_val) ** 2 for x in frequency_bins) / len(frequency_bins)
        if variance < 1e-9:
            kurtosis = 3.0
        else:
            fourth_moment = sum((x - mean_val) ** 4 for x in frequency_bins) / len(frequency_bins)
            kurtosis = fourth_moment / (variance ** 2)

        # Anomaly scoring based on deviation from baseline
        kurtosis_delta = abs(kurtosis - self.baseline_kurtosis)
        crest_delta = abs(crest_factor - self.baseline_crest_factor)
        anomaly_score = (kurtosis_delta * 0.6) + (crest_delta * 0.4)

        is_anomaly = anomaly_score > self.anomaly_threshold
        status_msg = "ANOMALY_DETECTED_GAP_RISK" if is_anomaly else "NOMINAL"

        result = {
            "timestamp": time.time(),
            "crest_factor": crest_factor,
            "spectral_kurtosis": kurtosis,
            "anomaly_score": anomaly_score,
            "is_anomaly": float(is_anomaly)
        }
        self.telemetry_history.append(result);
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        if is_anomaly:
            logger.warning(f"[ALERT] Roller gap anomaly detected! Score: {anomaly_score:.2f} (Kurtosis: {kurtosis:.2f}, Crest: {crest_factor:.2f})")

        return {
            "status": status_msg,
            "crest_factor": crest_factor,
            "spectral_kurtosis": kurtosis,
            "anomaly_score": anomaly_score,
            "action_required": is_anomaly
        }

    def calibrate_baseline(self, calibration_samples: List[List[float]], rms_values: List[float]) -> bool:
        """
        Recalibrates baseline kurtosis and crest factor during steady-state idling or optimal runs.
        """
        if not calibration_samples or len(calibration_samples) != len(rms_values):
            return False

        kurtosis_list = []
        crest_list = []
        for bins, rms in zip(calibration_samples, rms_values):
            peak = max(bins)
            cf = peak / (rms + 1e-6)
            mean_v = sum(bins) / len(bins)
            var = sum((x - mean_v) ** 2 for x in bins) / len(bins)
            if var > 1e-9:
                k = sum((x - mean_v) ** 4 for x in bins) / (var ** 2)
            else:
                k = 3.0
            kurtosis_list.append(k)
            crest_list.append(cf)

        self.baseline_kurtosis = sum(kurtosis_list) / len(kurtosis_list)
        self.baseline_crest_factor = sum(crest_list) / len(crest_list)
        logger.info(f"Baseline recalibrated successfully. New Baseline Kurtosis: {self.baseline_kurtosis:.2f}, Crest: {self.baseline_crest_factor:.2f}")
        return True

if __name__ == '__main__':
    sentinel = RollerGapAcousticAnomalySentinel()
    # Simulate calibration
    dummy_bins = [[random.gauss(10, 2) for _ in range(64)] for _ in range(10)]
    dummy_rms = [random.uniform(5, 6) for _ in range(10)]
    sentinel.calibrate_baseline(dummy_bins, dummy_rms)

    # Simulate live ingestion with normal vs anomalous data
    normal_run = [random.gauss(10, 2) for _ in range(64)]
    res_normal = sentinel.ingest_audio_spectrum(normal_run, 5.2)
    logger.info(f"Test Normal Ingestion: {res_normal['status']}")

    # Simulate metal impact spike in roller gap
    anomaly_run = [random.gauss(10, 2) if i != 32 else 250.0 for i in range(64)]
    res_anomaly = sentinel.ingest_audio_spectrum(anomaly_run, 15.0)
    logger.info(f"Test Anomaly Ingestion: {res_anomaly['status']} (Score: {res_anomaly['anomaly_score']:.2f})")
