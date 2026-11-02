"""
Nairobi Commercial Grain Milling Roller Mill Drive Motor Harmonic Vibration Synaptic Neural Sentinel

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)

Monitors roller mill drive motor harmonic frequencies using a synaptic neural resonance model
to preemptively detect mechanical wear, bearing pitting, and shaft misalignment.
"""

import math
import time
import logging
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [HarmonicSynapseSentinel]: %(message)s')
logger = logging.getLogger(__name__)

class SynapticNeuralNode:
    """Represents an artificial synaptic node attuned to specific harmonic frequency bands."""
    def __init__(self, target_frequency_hz: float, sensitivity: float = 1.0):
        self.target_frequency_hz = target_frequency_hz
        self.sensitivity = sensitivity
        self.weight = 0.5
        self.activation_history: List[float] = []

    def process_signal(self, frequency: float, amplitude: float) -> float:
        """Evaluate incoming vibration signal against this synaptic node's tuned frequency."""
        diff = abs(frequency - self.target_frequency_hz)
        activation = max(0.0, 1.0 - (diff / max(1.0, self.target_frequency_hz))) * amplitude * self.weight * self.sensitivity
        self.activation_history.append(activation)
        if len(self.activation_history) > 100:
            self.activation_history.pop(0)
        return activation

class RollerMillDriveMotorSynapticSentinel:
    """Core sentinel engine protecting commercial grain milling drive motors in Nairobi industrial zones."""
    def __init__(self, motor_id: str, baseline_rpm: float = 1450.0):
        self.motor_id = motor_id
        self.baseline_rpm = baseline_rpm
        # Standard harmonic orders for 4-pole AC motors driving heavy roller mills (e.g., 1x, 2x, 3x line frequency & pass frequencies)
        self.nodes = [
            SynapticNeuralNode(target_frequency_hz=24.16, sensitivity=1.2),  # 1X RPM fundamental
            SynapticNeuralNode(target_frequency_hz=48.33, sensitivity=1.5),  # 2X harmonics (misalignment)
            SynapticNeuralNode(target_frequency_hz=120.0, sensitivity=2.0), # Electrical line harmonic
            SynapticNeuralNode(target_frequency_hz=342.5, sensitivity=2.5)  # Bearing ball pass frequency outer race (BPFO)
        ]
        self.anomaly_threshold = 0.75

    def analyze_vibration_spectrum(self, freq_amplitude_pairs: List[Tuple[float, float]]) -> Dict[str, any]:
        """Analyze a spectrum of frequency-amplitude tuples and compute synaptic neural stress index."""
        total_activation = 0.0
        node_activations = []

        for node in self.nodes:
            node_max_act = 0.0
            for freq, amp in freq_amplitude_pairs:
                act = node.process_signal(freq, amp)
                if act > node_max_act:
                    node_max_act = act
            node_activations.append(node_max_act)
            total_activation += node_max_act

        stress_index = total_activation / len(self.nodes)
        status = "NOMINAL"
        action_required = False

        if stress_index >= self.anomaly_threshold:
            status = "CRITICAL_RESONANCE_WARNING"
            action_required = True
            logger.warning(f"[{self.motor_id}] CRITICAL SYNAPTIC ANOMALY DETECTED! Stress Index: {stress_index:.4f}")
        elif stress_index >= (self.anomaly_threshold * 0.7):
            status = "ELEVATED_VIBRATION"
            logger.info(f"[{self.motor_id}] Elevated vibration harmonics observed. Stress Index: {stress_index:.4f}")
        else:
            logger.debug(f"[{self.motor_id}] Drive motor operating normally. Stress Index: {stress_index:.4f}")

        return {
            "motor_id": self.motor_id,
            "timestamp": time.time(),
            "stress_index": stress_index,
            "status": status,
            "action_required": action_required,
            "node_activations": node_activations
        }

if __name__ == "__main__":
    print("Initializing Nairobi Commercial Grain Milling Roller Mill Drive Motor Harmonic Vibration Synaptic Neural Sentinel...")
    sentinel = RollerMillDriveMotorSynapticSentinel(motor_id="MILL_DRIVE_ALPHA_04")
    
    # Simulate healthy spectrum reading
    healthy_spectrum = [(24.16, 0.2), (48.33, 0.1), (120.0, 0.05), (342.5, 0.02)]
    res_healthy = sentinel.analyze_vibration_spectrum(healthy_spectrum)
    print(f"Test 1 (Healthy): {res_healthy['status']} (Stress: {res_healthy['stress_index']:.2f})")

    # Simulate anomalous bearing pitting spectrum
    fault_spectrum = [(24.16, 0.8), (48.33, 0.9), (120.0, 0.4), (342.5, 1.8)]
    res_fault = sentinel.analyze_vibration_spectrum(fault_spectrum)
    print(f"Test 2 (Anomalous): {res_fault['status']} (Stress: {res_fault['stress_index']:.2f})")
    print("Sentinel verification complete.")
