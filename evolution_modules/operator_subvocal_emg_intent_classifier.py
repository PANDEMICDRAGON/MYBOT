"""
OPERATOR SUBVOCAL ELECTROMYOGRAPHY INTENT CLASSIFIER & SILENT COMMAND SYNTHESIZER
System Upgrade Cycle #27 - Operator Amplification & Stealth Boundary

Ingests multi-channel micro-EMG surface electrode streams from operator Michael Obiero's
facial and laryngeal neuromuscular sensor array. Translates non-audible subvocalizations
into verified, cryptographically signed system intent tokens for high-noise and covert environments.
"""

from dataclasses import dataclass
import hashlib
import hmac
import math
import time
from typing import Dict, List, Optional


class EMGClassificationError(Exception):
    """Raised when sEMG signal processing or intent matching fails validation."""
    pass


@dataclass
class SubvocalSignalSample:
    """Raw micro-EMG sensor frame from neuromuscular surface array."""
    sample_id: str
    timestamp: float
    channels: List[List[float]]  # List of EMG voltage channels (microvolts)
    sampling_rate_hz: int = 1000
    sensor_impedance_kohm: float = 4.2

    def validate(self) -> bool:
        if not self.channels or any(len(ch) == 0 for ch in self.channels):
            raise EMGClassificationError("Empty channel data in sEMG sample.")
        if self.sampling_rate_hz <= 0:
            raise EMGClassificationError("Invalid sampling rate.")
        return True


@dataclass
class SubvocalFeatureVector:
    """Extracted temporal and spatial EMG features per channel."""
    rms: List[float]  # Root Mean Square
    mav: List[float]  # Mean Absolute Value
    wl: List[float]   # Waveform Length
    zc: List[int]     # Zero Crossings
    total_energy: float


@dataclass
class IntentTemplate:
    """Calibrated neuromuscular profile template for target operator subvocal commands."""
    intent_id: str
    name: str
    feature_centroid: List[float]  # Concatenated channel feature vector
    confidence_threshold: float = 0.80
    covert_priority: int = 1


@dataclass
class ClassifiedIntentResult:
    """Result of intent classification attempt."""
    intent_id: str
    command_name: str
    confidence: float
    latency_ms: float
    authenticated_token: str
    covert_priority: int


class EMGFeatureExtractor:
    """Computes temporal and spatial EMG feature vectors from microvolt streams."""

    def __init__(self, noise_threshold_uv: float = 5.0):
        self.noise_threshold_uv = noise_threshold_uv

    def extract(self, sample: SubvocalSignalSample) -> SubvocalFeatureVector:
        sample.validate()
        rms_vals: List[float] = []
        mav_vals: List[float] = []
        wl_vals: List[float] = []
        zc_vals: List[int] = []
        total_energy = 0.0

        for channel in sample.channels:
            n = len(channel)
            # RMS
            sum_sq = sum(v * v for v in channel)
            rms = math.sqrt(sum_sq / n) if n > 0 else 0.0
            rms_vals.append(rms)

            # MAV
            mav = sum(abs(v) for v in channel) / n if n > 0 else 0.0
            mav_vals.append(mav)

            # WL (Waveform Length)
            wl = sum(abs(channel[i] - channel[i - 1]) for i in range(1, n)) if n > 1 else 0.0
            wl_vals.append(wl)

            # ZC (Zero Crossings with noise filter)
            zc = 0
            for i in range(1, n):
                if ((channel[i] * channel[i - 1]) < 0) and abs(channel[i] - channel[i - 1]) > self.noise_threshold_uv:
                    zc += 1
            zc_vals.append(zc)

            total_energy += sum_sq

        return SubvocalFeatureVector(
            rms=rms_vals,
            mav=mav_vals,
            wl=wl_vals,
            zc=zc_vals,
            total_energy=total_energy
        )


class SubvocalIntentClassifier:
    """Matches neuromuscular sEMG feature vectors against calibrated operator profiles."""

    def __init__(self, hmac_key: bytes):
        self._hmac_key = hmac_key
        self._extractor = EMGFeatureExtractor()
        self._templates: Dict[str, IntentTemplate] = {}
        self._initialize_default_templates()

    def _initialize_default_templates(self) -> None:
        """Populates calibrated neuromuscular templates for operator Michael Obiero."""
        self.register_template(IntentTemplate(
            intent_id="INTENT_LOCK_ENCLAVE",
            name="LOCK_SYSTEM_ENCLAVE",
            feature_centroid=[12.5, 9.8, 45.0, 12.0, 14.1, 11.2, 52.0, 15.0, 8.2, 6.1, 30.0, 8.0, 15.0, 12.0, 58.0, 18.0],
            confidence_threshold=0.80,
            covert_priority=5
        ))
        self.register_template(IntentTemplate(
            intent_id="INTENT_AUTHORIZE_TRANSACTION",
            name="AUTHORIZE_PAYMENT_STREAM",
            feature_centroid=[25.0, 20.1, 95.0, 28.0, 22.0, 18.5, 88.0, 24.0, 19.4, 15.2, 70.0, 20.0, 28.1, 23.4, 105.0, 31.0],
            confidence_threshold=0.85,
            covert_priority=4
        ))
        self.register_template(IntentTemplate(
            intent_id="INTENT_STEALTH_FALLBACK",
            name="ENGAGE_SILENT_ROUTING",
            feature_centroid=[5.2, 4.1, 18.0, 4.0, 6.0, 4.8, 22.0, 6.0, 4.8, 3.9, 16.0, 3.0, 5.9, 4.5, 20.0, 5.0],
            confidence_threshold=0.75,
            covert_priority=3
        ))

    def register_template(self, template: IntentTemplate) -> None:
        """Registers or updates a subvocal intent template."""
        self._templates[template.intent_id] = template

    def _flatten_features(self, fv: SubvocalFeatureVector) -> List[float]:
        """Flattens feature vector components into a single normalized array."""
        flat: List[float] = []
        for i in range(len(fv.rms)):
            flat.extend([fv.rms[i], fv.mav[i], fv.wl[i], float(fv.zc[i])])
        return flat

    def _cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """Computes cosine similarity between two feature vectors."""
        if len(vec_a) != len(vec_b) or not vec_a:
            return 0.0
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot / (norm_a * norm_b)

    def _generate_auth_token(self, intent_id: str, timestamp: float, confidence: float) -> str:
        """Generates cryptographically bound authentication token for matched intent."""
        message = f"{intent_id}:{timestamp:.4f}:{confidence:.4f}".encode('utf-8')
        return hmac.new(self._hmac_key, message, hashlib.sha256).hexdigest()

    def classify(self, sample: SubvocalSignalSample) -> ClassifiedIntentResult:
        """Classifies sEMG sensor sample into an authorized silent command."""
        start_time = time.perf_counter()
        fv = self._extractor.extract(sample)
        flat_vector = self._flatten_features(fv)

        best_intent: Optional[IntentTemplate] = None
        best_similarity = -1.0

        for template in self._templates.values():
            similarity = self._cosine_similarity(flat_vector, template.feature_centroid)
            if similarity > best_similarity:
                best_similarity = similarity
                best_intent = template

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        if not best_intent or best_similarity < best_intent.confidence_threshold:
            raise EMGClassificationError(
                f"Subvocal intent unrecognized or confidence below threshold. "
                f"Best fit similarity: {best_similarity:.4f}, expected > {best_intent.confidence_threshold if best_intent else 0.0}"
            )

        token = self._generate_auth_token(best_intent.intent_id, sample.timestamp, best_similarity)

        return ClassifiedIntentResult(
            intent_id=best_intent.intent_id,
            command_name=best_intent.name,
            confidence=round(best_similarity, 4),
            latency_ms=round(elapsed_ms, 3),
            authenticated_token=token,
            covert_priority=best_intent.covert_priority
        )


if __name__ == "__main__":
    # Operational Verification Harness
    key = b"Nairobi_Operator_Michael_Obiero_Subvocal_EMG_Secret_Key"
    classifier = SubvocalIntentClassifier(hmac_key=key)

    # Simulated micro-EMG sample matching INTENT_LOCK_ENCLAVE profile
    simulated_ch1 = [12.0, -12.5, 9.5, -9.8, 14.0, -13.5, 11.0, -10.0, 13.0, -12.0]
    simulated_ch2 = [14.0, -14.1, 11.0, -11.2, 15.0, -15.5, 12.0, -12.0, 14.0, -13.0]
    simulated_ch3 = [8.0, -8.2, 6.0, -6.1, 9.0, -9.5, 7.0, -7.0, 8.5, -8.0]
    simulated_ch4 = [15.0, -15.0, 12.0, -12.0, 16.0, -16.5, 13.0, -13.0, 15.5, -14.0]

    sample = SubvocalSignalSample(
        sample_id="EMG_FRAME_001092",
        timestamp=time.time(),
        channels=[simulated_ch1, simulated_ch2, simulated_ch3, simulated_ch4],
        sampling_rate_hz=1000,
        sensor_impedance_kohm=3.8
    )

    res = classifier.classify(sample)
    print("CLASSIFIED SUBVOCAL INTENT:", res)
    assert res.intent_id == "INTENT_LOCK_ENCLAVE"
    assert res.confidence >= 0.80
    assert len(res.authenticated_token) == 64
    print("sEMG Intent Classifier successfully passed self-test audit!")
