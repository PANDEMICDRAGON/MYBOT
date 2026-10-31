"""adaptive_self_healing_topology.py
Provides AdaptiveSelfHealingTopology class for dynamic network resilience.
"""

from __future__ import annotations
from typing import Dict, Set, List, Tuple

class NodeFailureError(Exception):
    """Raised when an operation references a non‑existent node."""

class NoPathError(Exception):
    """Raised when no alternative path can be found between two nodes."""

class AdaptiveSelfHealingTopology:
    """Maintain a mutable undirected graph and automatically heal after node failures.

    The class tracks active nodes and edges. When a node is reported as failed,
    it is removed from the active set and the graph attempts to reconnect its
    neighbours using breadth‑first search to discover alternative routes.
    """

    def __init__(self) -> None:
        self._adjacency: Dict[str, Set[str]] = {}
        self._active: Set[str] = set()

    def add_node(self, node: str) -> None:
        """Add a node to the topology.

        Idempotent – adding an existing node has no effect.
        """
        self._adjacency.setdefault(node, set())
        self._active.add(node)

    def add_edge(self, a: str, b: str) -> None:
        """Create an undirected edge between *a* and *b*.

        Both nodes must exist; otherwise :class:`NodeFailureError` is raised.
        """
        if a not in self._adjacency or b not in self._adjacency:
            raise NodeFailureError(f"One or both nodes not present: {a}, {b}")
        self._adjacency[a].add(b)
        self._adjacency[b].add(a)

    def report_failure(self, node: str) -> None:
        """Mark *node* as failed and remove it from the active set.

        The node remains in the adjacency map so that its former neighbours
        can be examined for possible reconnection.
        """
        if node not in self._active:
            raise NodeFailureError(f"Node not active: {node}")
        self._active.remove(node)

    def _bfs(self, start: str, goal: str, excluded: Set[str]) -> List[str]:
        """Return a path from *start* to *goal* avoiding *excluded* nodes.

        Implements a simple breadth‑first search. Returns an empty list if no path exists.
        """
        if start == goal:
            return [start]
        visited: Set[str] = set()
        queue: List[Tuple[str, List[str]]] = [(start, [start])]
        while queue:
            current, path = queue.pop(0)
            visited.add(current)
            for neighbour in self._adjacency.get(current, []):
                if neighbour in excluded or neighbour in visited:
                    continue
                if neighbour == goal:
                    return path + [neighbour]
                queue.append((neighbour, path + [neighbour]))
        return []

    def heal(self) -> List[Tuple[str, str, List[str]]]:
        """Attempt to reconnect neighbours of failed nodes.

        Returns a list of tuples ``(failed_node, neighbour, new_path)`` describing
        each successful reconnection. If no alternative path exists, the tuple
        contains an empty list for *new_path*.
        """
        reconnections: List[Tuple[str, str, List[str]]] = []
        failed_nodes = set(self._adjacency.keys()) - self._active
        for failed in failed_nodes:
            neighbours = list(self._adjacency[failed])
            for neighbour in neighbours:
                alternatives = [
                    (other, self._bfs(neighbour, other, {failed}))
                    for other in neighbours if other != neighbour
                ]
                viable = [(other, path) for other, path in alternatives if path]
                if viable:
                    other, path = min(viable, key=lambda x: len(x[1]))
                    reconnections.append((failed, neighbour, path))
                else:
                    reconnections.append((failed, neighbour, []))
        return reconnections

    def active_nodes(self) -> Set[str]:
        """Return the set of currently active nodes."""
        return set(self._active)

if __name__ == "__main__":
    # Simple demonstration
    topology = AdaptiveSelfHealingTopology()
    for n in "ABCDE":
        topology.add_node(n)
    topology.add_edge("A", "B")
    topology.add_edge("B", "C")
    topology.add_edge("C", "D")
    topology.add_edge("D", "E")
    topology.add_edge("A", "E")  # creates a loop

    print("Active nodes before failure:", topology.active_nodes())
    topology.report_failure("C")
    print("Active nodes after failure:", topology.active_nodes())
    results = topology.heal()
    for failed, neighbour, path in results:
        if path:
            print(f"Reconnected {neighbour} around failed {failed} via path: {' -> '.join(path)}")
        else:
            print(f"No alternative path for {neighbour} after failure of {failed}")
