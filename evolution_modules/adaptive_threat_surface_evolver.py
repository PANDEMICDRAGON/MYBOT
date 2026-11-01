'''Adaptive Threat Surface Evolution Engine.

Provides dynamic modeling of an organization's threat surface,
allowing addition of assets, connections, risk scoring, and
pruning of low‑risk nodes. Designed for autonomous self‑hardening.
'''

from __future__ import annotations
from typing import Dict, Set, Tuple, List
import json
import sys

class ThreatSurfaceEvolver:
    """Manage a mutable threat‑surface graph.

    Assets are identified by a unique string. Connections are undirected.
    Each asset holds a base risk (0‑1). The overall risk of an asset is
    its base risk plus the average risk of directly connected assets.
    """

    def __init__(self) -> None:
        self._risk: Dict[str, float] = {}
        self._edges: Dict[str, Set[str]] = {}

    def add_asset(self, asset_id: str, base_risk: float) -> None:
        """Register a new asset.

        Args:
            asset_id: Unique identifier.
            base_risk: Initial risk in [0, 1].

        Raises:
            ValueError: If asset already exists or risk out of range.
        """
        if asset_id in self._risk:
            raise ValueError(f"Asset '{asset_id}' already exists.")
        if not 0.0 <= base_risk <= 1.0:
            raise ValueError("base_risk must be between 0 and 1.")
        self._risk[asset_id] = base_risk
        self._edges[asset_id] = set()

    def add_connection(self, a: str, b: str) -> None:
        """Create an undirected connection between two assets.

        Raises:
            KeyError: If either asset is unknown.
        """
        if a not in self._risk or b not in self._risk:
            raise KeyError("Both assets must be added before connecting.")
        self._edges[a].add(b)
        self._edges[b].add(a)

    def compute_risk(self, asset_id: str) -> float:
        """Calculate the propagated risk for a single asset."""
        if asset_id not in self._risk:
            raise KeyError(f"Asset '{asset_id}' not found.")
        neighbours = self._edges[asset_id]
        if not neighbours:
            return self._risk[asset_id]
        neighbour_risk = sum(self._risk[n] for n in neighbours) / len(neighbours)
        return (self._risk[asset_id] + neighbour_risk) / 2.0

    def prune_assets(self, threshold: float) -> List[str]:
        """Remove assets whose computed risk is below *threshold*.

        Returns a list of removed asset identifiers.
        """
        to_remove = [aid for aid in self._risk if self.compute_risk(aid) < threshold]
        for aid in to_remove:
            for neighbour in self._edges[aid]:
                self._edges[neighbour].discard(aid)
            del self._edges[aid]
            del self._risk[aid]
        return to_remove

    def snapshot(self) -> Dict[str, Tuple[float, List[str]]]:
        """Export a serialisable view of the current graph."""
        return {
            aid: (self._risk[aid], sorted(self._edges[aid]))
            for aid in self._risk
        }

def _demo() -> None:
    evo = ThreatSurfaceEvolver()
    evo.add_asset("web_server", 0.7)
    evo.add_asset("db_server", 0.6)
    evo.add_asset("cache", 0.3)
    evo.add_asset("internal_tool", 0.2)
    evo.add_connection("web_server", "db_server")
    evo.add_connection("web_server", "cache")
    evo.add_connection("db_server", "cache")
    evo.add_connection("internal_tool", "db_server")
    print("Initial snapshot:", json.dumps(evo.snapshot(), indent=2))
    print("Risk of web_server:", evo.compute_risk("web_server"))
    removed = evo.prune_assets(0.4)
    print("Pruned assets:", removed)
    print("Post‑prune snapshot:", json.dumps(evo.snapshot(), indent=2))

if __name__ == "__main__":
    try:
        _demo()
    except Exception as exc:
        print(f"Error during demo: {exc}", file=sys.stderr)
        sys.exit(1)
