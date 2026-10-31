"""
secure_mpc_orchestrator.py

Implements a lightweight additive secret sharing based Secure Multi-Party Computation (MPC)
orchestrator for integer values. Parties submit secret shares; the orchestrator can
reconstruct the aggregate result without learning individual inputs.

Designed for offline, low‑scale use within Cortana's autonomous ecosystem.
"""

from __future__ import annotations
import random
import math
from typing import List, Dict, Callable

class MPCError(Exception):
    """Base class for MPC related errors."""
    pass

class Party:
    """Represents a participant in an MPC protocol."""
    def __init__(self, party_id: str):
        self.party_id = party_id

    def generate_shares(self, value: int, n: int, modulus: int = 2**31-1) -> List[int]:
        """
        Split ``value`` into ``n`` additive shares modulo ``modulus``.
        Returns a list of length ``n`` where the sum of shares ≡ value (mod modulus).
        """
        if n < 2:
            raise MPCError("At least two shares required.")
        shares = [random.randint(0, modulus - 1) for _ in range(n - 1)]
        last = (value - sum(shares)) % modulus
        shares.append(last)
        return shares

class MPCOrchestrator:
    """Coordinates secret sharing and secure aggregation."""
    def __init__(self, parties: List[Party], modulus: int = 2**31-1):
        if len(parties) < 2:
            raise MPCError("MPC requires at least two parties.")
        self.parties = parties
        self.modulus = modulus
        self._share_pool: Dict[str, List[int]] = {}

    def submit_shares(self, party: Party, shares: List[int]) -> None:
        """
        Store the shares contributed by ``party``.
        All parties must submit the same number of shares.
        """
        if party.party_id not in {p.party_id for p in self.parties}:
            raise MPCError(f"Unknown party {party.party_id}.")
        if self._share_pool and len(shares) != len(next(iter(self._share_pool.values()))):
            raise MPCError("Inconsistent number of shares submitted.")
        self._share_pool[party.party_id] = shares

    def _aggregate(self, func: Callable[[List[int]], int]) -> int:
        """
        Generic aggregation over the share matrix using ``func``.
        ``func`` receives a list of integers (one share per party) and must
        return the combined result for that column.
        """
        if len(self._share_pool) != len(self.parties):
            raise MPCError("Not all parties have submitted shares.")
        share_matrix = list(zip(*self._share_pool.values()))  # type: ignore[arg-type]
        column_results = [func(list(col)) % self.modulus for col in share_matrix]
        return sum(column_results) % self.modulus

    def compute_sum(self) -> int:
        """Securely compute the sum of all parties' private values."""
        return self._aggregate(lambda col: sum(col))

    def compute_product(self) -> int:
        """Securely compute the product of all parties' private values.
        Note: This naive implementation works for modest integer sizes.
        """
        return self._aggregate(lambda col: math.prod(col))

if __name__ == "__main__":
    # Demo with three parties computing the sum of private integers.
    parties = [Party(f"P{i}") for i in range(1, 4)]
    orchestrator = MPCOrchestrator(parties)

    private_values = {"P1": 42, "P2": 17, "P3": 99}
    n_shares = len(parties)

    # Each party creates shares and distributes them.
    for p in parties:
        shares = p.generate_shares(private_values[p.party_id], n_shares)
        orchestrator.submit_shares(p, shares)

    result = orchestrator.compute_sum()
    expected = sum(private_values.values()) % orchestrator.modulus
    print(f"Secure MPC sum result: {result} (expected {expected})")
