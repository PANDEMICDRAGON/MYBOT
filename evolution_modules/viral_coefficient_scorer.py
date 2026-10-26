"""
Social Media Viral Coefficient Evaluator for Obiflamee Brand.
Generated autonomously by Cortana Continuous Self-Evolution Core.
"""

import re
from typing import Dict, Any

class ViralCoefficientScorer:
    """Evaluates hook strength, hashtags, and CTA power for TikTok/Reels music marketing."""
    HOOK_TRIGGERS = ["wait for", "unreleased", "how i made", "pov", "3 am", "bass drop", "don't sleep"]
    
    @classmethod
    def score_post(cls, hook: str, caption: str, tags: str) -> Dict[str, Any]:
        combined = f"{hook} {caption} {tags}".lower()
        score = 50.0

        for trig in cls.HOOK_TRIGGERS:
            if trig in combined:
                score += 10.0

        tag_count = len(re.findall(r"#\w+", tags))
        if 3 <= tag_count <= 7:
            score += 15.0
        elif tag_count > 10:
            score -= 10.0

        if "?" in caption or "drop a" in combined or "link in bio" in combined:
            score += 15.0

        final_score = min(100.0, max(0.0, score))
        return {
            "viral_score": round(final_score, 1),
            "tier": "VIRAL_POTENTIAL" if final_score >= 80 else "STEADY",
            "tag_count": tag_count
        }

if __name__ == "__main__":
    res = ViralCoefficientScorer.score_post("Wait for the drop...", "Does Nairobi know about this? Drop a fire emoji!", "#OBIFLAMEE #AfroHouse #Kenya")
    assert res["viral_score"] >= 80
    print(f"ViralCoefficientScorer verified: {res}")
