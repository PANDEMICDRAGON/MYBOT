"""
Adaptive Zero‑Trust Policy Engine
"""

import json
import hashlib
import random
import datetime
from dataclasses import dataclass, field
from typing import Any, Dict, List, Callable, Optional

class PolicyEvaluationError(Exception):
    """Raised when policy evaluation fails due to malformed input."""

@dataclass
class AccessRequest:
    """Represents an incoming access request."""
    user_id: str
    resource: str
    action: str
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.utcnow)

@dataclass
class PolicyRule:
    """A single policy rule."""
    name: str
    condition: Callable[[AccessRequest], bool]
    effect: str  # "allow" or "deny"
    risk_weight: float = 1.0

class AdaptiveZeroTrustEngine:
    """
    Core engine that evaluates access requests against a dynamic set of
    policy rules and produces a decision based on an adaptive risk score.
    """

    def __init__(self, base_risk_threshold: float = 5.0):
        self.rules: List[PolicyRule] = []
        self.base_risk_threshold = base_risk_threshold

    def add_rule(self, rule: PolicyRule) -> None:
        """Add a new policy rule to the engine.

        Raises:
            ValueError: If a rule with the same name already exists.
        """
        if any(r.name == rule.name for r in self.rules):
            raise ValueError(f"Rule with name '{rule.name}' already exists.")
        self.rules.append(rule)

    def evaluate(self, request: AccessRequest) -> Dict[str, Any]:
        """Evaluate the request and return a decision payload.

        The payload contains:
            - decision: "allow" or "deny"
            - risk_score: cumulative risk from matched rules
            - matched_rules: list of rule names that fired
            - threshold: the adaptive risk threshold used for the decision
        """
        if not isinstance(request, AccessRequest):
            raise PolicyEvaluationError("Invalid request type.")
        matched: List[PolicyRule] = []
        risk_score = 0.0

        for rule in self.rules:
            try:
                if rule.condition(request):
                    matched.append(rule)
                    risk_score += rule.risk_weight
            except Exception:
                # Rule evaluation errors are ignored but could be logged.
                continue

        adaptive_threshold = self._adaptive_threshold()
        decision = "allow" if risk_score <= adaptive_threshold else "deny"

        return {
            "decision": decision,
            "risk_score": risk_score,
            "matched_rules": [r.name for r in matched],
            "threshold": adaptive_threshold,
        }

    def _adaptive_threshold(self) -> float:
        """Simple adaptive algorithm that adds a minute‑based jitter.

        In production this would ingest live threat intel and system load.
        """
        minute = datetime.datetime.utcnow().minute
        jitter = (minute % 5) * 0.2  # up to +/-1.0
        return self.base_risk_threshold + jitter

def _example_condition_admin(request: AccessRequest) -> bool:
    return request.context.get("role") == "admin"

def _example_condition_sensitive(request: AccessRequest) -> bool:
    return request.resource.startswith("sensitive/")

def _example_condition_off_hours(request: AccessRequest) -> bool:
    hour = request.timestamp.hour
    return hour < 6 or hour > 20

def _build_demo_engine() -> AdaptiveZeroTrustEngine:
    engine = AdaptiveZeroTrustEngine(base_risk_threshold=3.0)
    engine.add_rule(
        PolicyRule(
            name="admin_allow",
            condition=_example_condition_admin,
            effect="allow",
            risk_weight=0.5,
        )
    )
    engine.add_rule(
        PolicyRule(
            name="sensitive_deny_off_hours",
            condition=lambda r: _example_condition_sensitive(r) and _example_condition_off_hours(r),
            effect="deny",
            risk_weight=4.0,
        )
    )
    engine.add_rule(
        PolicyRule(
            name="default_deny",
            condition=lambda r: True,
            effect="deny",
            risk_weight=2.0,
        )
    )
    return engine

if __name__ == "__main__":
    demo_engine = _build_demo_engine()
    sample = AccessRequest(
        user_id="u123",
        resource="sensitive/financial_report",
        action="read",
        context={"role": "employee"},
    )
    result = demo_engine.evaluate(sample)
    print(json.dumps(result, indent=2))
