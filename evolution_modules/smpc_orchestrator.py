"""
Secure Multi-Party Computation (SMPC) Orchestrator.

Provides a lightweight additive secret sharing orchestrator to compute
aggregated results without revealing individual inputs. Designed for
privacy‑preserving analytics across distributed operator devices.
"""

from __future__ import annotations
import random
from typing import List, Dict

class Party:
    """Represents a participant in an SMPC protocol."""
    def __init__(self, identifier: str, value: int):
        self.id = identifier
        self._value = value
        self._shares: List[int] = []

    @property
    def value(self) -> int:
        """The private value held by the party."""
        return self._value

    def generate_shares(self, n: int, modulus: int = 2**31 - 1) -> List[int]:
        """
        Split the private value into `n` additive shares modulo `modulus`.
        The last share is computed to satisfy the reconstruction equation.
        """
        if n < 2:
            raise ValueError("At least two shares are required.")
        shares = [random.randrange(modulus) for _ in range(n - 1)]
        last_share = (self._value - sum(shares)) % modulus
        shares.append(last_share)
        self._shares = shares
        return shares

    def receive_shares(self, shares: List[int]) -> None:
        """Store shares received from other parties."""
        if len(shares) != len(self._shares):
            raise ValueError("Mismatched number of shares.")
        self._shares = shares

    def get_share_for(self, recipient_id: str) -> int:
        """Return the share intended for a specific recipient.
        In this simple implementation the order of shares matches the order of parties.
        The orchestrator will map indices to identifiers.
        """
        raise NotImplementedError("Direct share extraction is managed by the orchestrator.")

class SMPCOrchestrator:
    """Coordinates additive secret sharing among a set of parties."""
    def __init__(self, parties: List[Party], modulus: int = 2**31 - 1):
        if len(parties) < 2:
            raise ValueError("SMPC requires at least two parties.")
        self.parties = parties
        self.modulus = modulus

    def distribute_shares(self) -> None:
        """Each party creates shares and distributes them to every other party."""
        n = len(self.parties)
        # Generate shares for each party
        all_shares: Dict[str, List[int]] = {}
        for party in self.parties:
            all_shares[party.id] = party.generate_shares(n, self.modulus)

        # Deliver the i‑th share of each party to the i‑th recipient
        for idx, recipient in enumerate(self.parties):
            received = [all_shares[p.id][idx] for p in self.parties]
            recipient.receive_shares(received)

    def compute_aggregate(self) -> int:
        """
        After share distribution, each party sums the shares it holds.
        The orchestrator then aggregates those partial sums to reconstruct
        the global result.
        """
        partial_sums = [sum(p._shares) % self.modulus for p in self.parties]
        total = sum(partial_sums) % self.modulus
        return total

def _demo() -> None:
    """Simple demonstration with three parties."""
    parties = [
        Party("alice", 42),
        Party("bob", 17),
        Party("carol", 31),
    ]
    orchestrator = SMPCOrchestrator(parties)
    orchestrator.distribute_shares()
    result = orchestrator.compute_aggregate()
    expected = sum(p.value for p in parties) % orchestrator.modulus
    assert result == expected, f"SMPC result {result} differs from expected {expected}"
    print(f"SMPC aggregate computed successfully: {result}")

if __name__ == "__main__":
    _demo()
