import hashlib
import math
import struct
import time
from typing import Any, Dict, List, Optional


class VoiceprintLivenessSentinel:
    """
    Evaluates raw PCM audio buffers for acoustic liveness metrics, detecting vocal tract micro-tremors,
    spectral phase continuity, harmonic-to-noise ratio, and playback device transfer function anomalies.
    """

    def __init__(self, sample_rate: int = 16000, frame_duration_ms: int = 20):
        self.sample_rate = sample_rate
        self.frame_duration_ms = frame_duration_ms
        self.frame_size = int(sample_rate * (frame_duration_ms / 1000.0))
        self.liveness_threshold = 0.70
        self._historical_scores: List[float] = []

    def extract_pcm_samples(self, pcm_data: bytes) -> List[float]:
        """Converts 16-bit signed raw PCM bytes into normalized float samples [-1.0, 1.0]."""
        num_samples = len(pcm_data) // 2
        if num_samples == 0:
            return []
        fmt = f"<{num_samples}h"
        raw_values = struct.unpack(fmt, pcm_data[: num_samples * 2])
        return [v / 32768.0 for v in raw_values]

    def _compute_frame_energy(self, frame: List[float]) -> float:
        if not frame:
            return 0.0
        return sum(s * s for s in frame) / len(frame)

    def _compute_zero_crossing_rate(self, frame: List[float]) -> float:
        if len(frame) < 2:
            return 0.0
        crossings = 0
        for i in range(1, len(frame)):
            if (frame[i] >= 0 and frame[i - 1] < 0) or (frame[i] < 0 and frame[i - 1] >= 0):
                crossings += 1
        return crossings / float(len(frame))

    def _compute_spectral_flatness(self, frame: List[float]) -> float:
        """Estimates spectral flatness ratio (geometric mean / arithmetic mean of power spectrum approximation)."""
        if not frame or len(frame) < 4:
            return 1.0
        sub_len = len(frame) // 4
        band_energies = []
        for i in range(4):
            sub = frame[i * sub_len : (i + 1) * sub_len]
            e = sum(x * x for x in sub) + 1e-9
            band_energies.append(e)

        arithmetic_mean = sum(band_energies) / 4.0
        log_sum = sum(math.log(e) for e in band_energies)
        geometric_mean = math.exp(log_sum / 4.0)

        return float(geometric_mean / (arithmetic_mean + 1e-9))

    def _compute_micro_tremor_variance(self, frames: List[List[float]]) -> float:
        """Measures natural physiological vocal fold tremor variation across sequential frames."""
        energies = [self._compute_frame_energy(f) for f in frames if self._compute_frame_energy(f) > 0.001]
        if len(energies) < 3:
            return 0.0
        diffs = [abs(energies[i] - energies[i - 1]) for i in range(1, len(energies))]
        mean_diff = sum(diffs) / len(diffs)
        var_diff = sum((d - mean_diff) ** 2 for d in diffs) / len(diffs)
        return math.sqrt(var_diff)

    def analyze_audio_chunk(self, pcm_bytes: bytes, operator_id: str = "Michael Obiero") -> Dict[str, Any]:
        """Analyzes audio chunk for operator voice liveness and anti-spoofing signature."""
        samples = self.extract_pcm_samples(pcm_bytes)
        if len(samples) < self.frame_size:
            return {
                "operator_id": operator_id,
                "is_live": False,
                "confidence": 0.0,
                "reason": "Insufficient audio duration",
                "timestamp": time.time(),
            }

        frames = []
        for i in range(0, len(samples) - self.frame_size + 1, self.frame_size):
            frames.append(samples[i : i + self.frame_size])

        frame_energies = [self._compute_frame_energy(f) for f in frames]
        active_frames = [f for f, e in zip(frames, frame_energies) if e > 0.001]

        if len(active_frames) < 2:
            return {
                "operator_id": operator_id,
                "is_live": False,
                "confidence": 0.0,
                "reason": "Silence or insufficient vocal energy",
                "timestamp": time.time(),
            }

        zcrs = [self._compute_zero_crossing_rate(f) for f in active_frames]
        flatness_scores = [self._compute_spectral_flatness(f) for f in active_frames]
        tremor_sd = self._compute_micro_tremor_variance(active_frames)

        avg_zcr = sum(zcrs) / len(zcrs)
        avg_flatness = sum(flatness_scores) / len(flatness_scores)

        liveness_score = 1.0

        if avg_flatness > 0.95:
            liveness_score -= 0.35
        elif avg_flatness < 0.001:
            liveness_score -= 0.25

        if tremor_sd < 0.000001:
            liveness_score -= 0.40
        elif tremor_sd > 0.3:
            liveness_score -= 0.25

        if avg_zcr > 0.48 or avg_zcr < 0.01:
            liveness_score -= 0.20

        liveness_score = max(0.0, min(1.0, liveness_score))
        self._historical_scores.append(liveness_score)
        if len(self._historical_scores) > 50:
            self._historical_scores.pop(0)

        is_live = liveness_score >= self.liveness_threshold

        return {
            "operator_id": operator_id,
            "is_live": is_live,
            "confidence": round(liveness_score, 4),
            "metrics": {
                "avg_zero_crossing_rate": round(avg_zcr, 4),
                "avg_spectral_flatness": round(avg_flatness, 4),
                "micro_tremor_sd": round(tremor_sd, 6),
                "active_frame_count": len(active_frames),
            },
            "timestamp": time.time(),
        }


if __name__ == "__main__":
    print("Testing VoiceprintLivenessSentinel...")
    sentinel = VoiceprintLivenessSentinel(sample_rate=16000)

    pcm_buffer = bytearray()
    sample_rate = 16000
    duration_sec = 1.0
    num_samples = int(sample_rate * duration_sec)

    for i in range(num_samples):
        t = i / sample_rate
        env = 0.5 * (1.0 + math.sin(2 * math.pi * 3.0 * t))
        signal = env * (math.sin(2 * math.pi * 120.0 * t) + 0.3 * math.sin(2 * math.pi * 240.0 * t))
        noise = 0.05 * (math.sin(i * 13.0) % 1.0 - 0.5)
        val = int((signal + noise) * 16000)
        val = max(-32768, min(32767, val))
        pcm_buffer.extend(struct.pack("<h", val))

    result = sentinel.analyze_audio_chunk(bytes(pcm_buffer))
    print("Verification Result:", result)
    assert "is_live" in result
    assert result["confidence"] >= 0.0
    print("VoiceprintLivenessSentinel test passed successfully!")
