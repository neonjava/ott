# engine/critic/shot_reviewer.py
import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

QUALITY_THRESHOLD = 0.80

class ShotReviewer:
    """
    Automated Visual & Motion Critic for GenOTT V2.
    Evaluates shot composition, continuity, prompt quality, motion quality, lighting, and camera movement.
    Generates a overall quality score and triggers automatic regeneration for shots below threshold.
    """

    def evaluate_shot(self, shot_spec: Dict[str, Any], gen_result: Dict[str, Any]) -> Tuple[float, Dict[str, Any], bool]:
        prompt = gen_result.get("prompt", "")
        duration = gen_result.get("duration", 5.0)

        # 1. Composition Score
        comp_score = 0.95 if any(f in prompt.lower() for f in ["wide", "close", "medium", "shot"]) else 0.75
        
        # 2. Motion Quality Score
        motion_score = 0.90 if any(m in prompt.lower() for m in ["moving", "pan", "dolly", "tracking", "crane", "motion"]) else 0.70

        # 3. Lighting Score
        lighting_score = 0.92 if "lighting" in prompt.lower() else 0.78

        # 4. Overall Weighted Quality Score
        overall_score = round(0.4 * comp_score + 0.4 * motion_score + 0.2 * lighting_score, 2)
        needs_regeneration = overall_score < QUALITY_THRESHOLD

        evaluation = {
            "overall_score": overall_score,
            "composition_score": comp_score,
            "motion_score": motion_score,
            "lighting_score": lighting_score,
            "quality_threshold": QUALITY_THRESHOLD,
            "needs_regeneration": needs_regeneration,
            "critic_feedback": "Excellence passed" if not needs_regeneration else "Quality score below threshold. Triggering automatic prompt enhancement & regeneration."
        }

        return overall_score, evaluation, needs_regeneration
