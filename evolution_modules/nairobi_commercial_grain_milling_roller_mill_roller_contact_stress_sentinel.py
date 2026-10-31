"""Nairobi Commercial Grain Milling Roller Mill Roller Contact Stress Sentinel

Computes Hertzian contact stress between grinding rolls under dynamic loads,
monitoring elastic modulus, normal force per unit length, and roller radii
to prevent surface fatigue failure, micro-pitting, and premature wear in
commercial maize and wheat flour mills across Nairobi, Kenya.
"""

import logging
import math
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RollerContactStressSentinel")


class RollerContactStressSentinel:
    """
    Monitors and evaluates Hertzian contact pressures on commercial roller mill
    cylinders to protect milling assets and ensure optimal endosperm reduction.
    """

    def __init__(self, roller_radius_m: float = 0.125, effective_length_m: float = 1.0, youngs_modulus_mpa: float = 210000.0, poisson_ratio: float = 0.3):
        self.roller_radius_m = roller_radius_m
        self.effective_length_m = effective_length_m
        self.youngs_modulus_mpa = youngs_modulus_mpa
        self.poisson_ratio = poisson_ratio
        # Equivalent elastic modulus (E_star)
        self.e_star = youngs_modulus_mpa / (2.0 * (1.0 - poisson_ratio ** 2))

    def calculate_contact_stress(self, normal_force_kn: float) -> Dict[str, float]:
        """
        Calculates maximum Hertzian contact stress (P_max) and contact half-width (b).
        Formula:
        b = sqrt( (4 * F * R_star) / (pi * E_star * L) )
        P_max = (2 * F) / (pi * b * L)
        """
        try:
            force_n = normal_force_kn * 1000.0
            # For two identical rollers of radius R, equivalent radius R_star = R / 2
            r_star = self.roller_radius_m / 2.0
            
            numerator_b = 4.0 * force_n * r_star
            denominator_b = math.pi * self.e_star * 1e6 * self.effective_length_m
            
            if denominator_b <= 0 or numerator_b < 0:
                raise ValueError("Invalid physical parameters for Hertzian calculation.")

            b = math.sqrt(numerator_b / denominator_b)
            if b == 0:
                p_max_mpa = 0.0
            else:
                p_max_mpa = (2.0 * force_n) / (math.pi * b * self.effective_length_m * 1e6)

            return {
                "contact_half_width_mm": b * 1000.0,
                "max_contact_stress_mpa": p_max_mpa,
                "equivalent_modulus_gpa": (self.e_star * 1e-3)
            }
        except Exception as e:
            logger.error(f"Error calculating contact stress: {e}")
            raise

    def evaluate_health(self, normal_force_kn: float, allowable_stress_mpa: float = 1200.0) -> Dict[str, Any]:
        metrics = self.calculate_contact_stress(normal_force_kn)
        p_max = metrics["max_contact_stress_mpa"]
        
        status = "OPTIMAL"
        if p_max > allowable_stress_mpa:
            status = "CRITICAL_OVER_STRESS"
        elif p_max > (allowable_stress_mpa * 0.85):
            status = "WARNING_ELEVATED_STRESS"

        return {
            "status": status,
            "max_contact_stress_mpa": round(p_max, 2),
            "allowable_stress_mpa": allowable_stress_mpa,
            "stress_ratio": round(p_max / allowable_stress_mpa, 3),
            "contact_half_width_mm": round(metrics["contact_half_width_mm"], 4)
        }


if __name__ == "__main__":
    sentinel = RollerContactStressSentinel()
    # Test with 15 kN normal load across 1-meter roller
    health_report = sentinel.evaluate_health(normal_force_kn=15.0)
    logger.info(f"Roller Contact Stress Sentinel Status: {health_report}")
