"""
Dynamic Token Budget Optimizer & Context Window Compressor.
Generated autonomously by Cortana Continuous Self-Evolution Core.
"""

from typing import List, Dict, Any

class TokenBudgetOptimizer:
    """Calculates token allocation bounds and intelligently truncates oldest non-essential context."""
    @staticmethod
    def estimate_tokens(text: str) -> int:
        return max(1, len(text) // 4)

    @classmethod
    def fit_to_budget(cls, messages: List[Dict[str, str]], max_tokens: int = 6000) -> List[Dict[str, str]]:
        total = sum(cls.estimate_tokens(m.get("content", "")) for m in messages)
        if total <= max_tokens:
            return messages

        # Preserve system prompt (messages[0]) and newest user message (messages[-1])
        if len(messages) <= 2:
            return messages

        preserved = [messages[0]]
        tail = messages[1:]
        while sum(cls.estimate_tokens(m.get("content", "")) for m in preserved + tail) > max_tokens and len(tail) > 1:
            tail.pop(0)

        return preserved + tail

if __name__ == "__main__":
    msgs = [{"role": "system", "content": "system prompt"}] + [{"role": "user", "content": "x" * 1000} for _ in range(10)]
    fitted = TokenBudgetOptimizer.fit_to_budget(msgs, max_tokens=1000)
    assert len(fitted) < len(msgs)
    print("TokenBudgetOptimizer verified.")
