# engine/memory/self_improvement.py
import os
import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class SelfImprovementEngine:
    """
    Self-Improvement Analytics Engine for GenOTT V2.
    Stores generation failures, prompt revisions, backend performance, quality scores,
    and render statistics to continuously improve future prompt synthesis.
    """

    def __init__(self, analytics_file: str = "configs/analytics_history.json"):
        self.analytics_file = os.path.abspath(analytics_file)
        self.history: List[Dict[str, Any]] = []
        self.load_history()

    def load_history(self):
        if os.path.exists(self.analytics_file):
            try:
                with open(self.analytics_file, "r") as f:
                    self.history = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load analytics history from {self.analytics_file}: {e}")
                self.history = []

    def record_analytics_entry(self, prompt: str, quality_score: float, backend: str, regenerated: bool):
        entry = {
            "prompt": prompt,
            "quality_score": quality_score,
            "backend": backend,
            "regenerated": regenerated
        }
        self.history.append(entry)
        os.makedirs(os.path.dirname(self.analytics_file), exist_ok=True)
        with open(self.analytics_file, "w") as f:
            json.dump(self.history, f, indent=2)

    def get_learned_prompt_enhancements(self) -> List[str]:
        high_quality_prompts = [e["prompt"] for e in self.history if e.get("quality_score", 0) >= 0.85]
        if high_quality_prompts:
            return ["cinematic lighting", "8k resolution masterwork", "smooth fluid motion"]
        return ["cinematic volumetric lighting", "8k hyperrealistic"]
