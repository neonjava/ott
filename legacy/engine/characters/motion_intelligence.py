# ai/motion_intelligence.py
import math
from typing import Dict, Any, List

class MotionIntelligenceAgent:
    """
    Subsystem: Motion Intelligence
    Computes smooth blend durations, handles procedural IK weighting targets, and predicts locomotor pacing.
    """
    def __init__(self):
        # Default transitions list
        self.transitions = {
            ("idle", "walk"): {"blend_time": 0.3, "curve": "ease-in-out"},
            ("walk", "idle"): {"blend_time": 0.25, "curve": "ease-out"},
            ("walk", "run"): {"blend_time": 0.4, "curve": "ease-in"},
            ("run", "jump"): {"blend_time": 0.15, "curve": "linear"},
            ("jump", "land"): {"blend_time": 0.2, "curve": "ease-out"}
        }

    def compute_blend_parameters(self, from_action: str, to_action: str) -> Dict[str, Any]:
        """Calculates transition timings and blend curves for animation clips."""
        key = (from_action.lower(), to_action.lower())
        if key in self.transitions:
            return self.transitions[key]
        return {"blend_time": 0.25, "curve": "linear"}  # Standard fallback

    def get_ik_targets(self, action: str, speed: float) -> Dict[str, Any]:
        """Calculates IK weights for procedural foot and hand adjustments."""
        ik_profile = {
            "foot_ik_left_weight": 1.0,
            "foot_ik_right_weight": 1.0,
            "hand_ik_left_weight": 0.0,
            "hand_ik_right_weight": 0.0,
            "ankle_offset_z": 0.0
        }
        
        # Procedural foot adjustment logic based on velocity
        if action == "walk":
            ik_profile["ankle_offset_z"] = 0.02 * math.sin(speed * 3.14)
        elif action == "run":
            ik_profile["ankle_offset_z"] = 0.05 * math.sin(speed * 6.28)
            ik_profile["foot_ik_left_weight"] = 0.9
            ik_profile["foot_ik_right_weight"] = 0.9
        elif "attack" in action or "strike" in action:
            ik_profile["hand_ik_right_weight"] = 1.0  # Weapon strike target
            
        return ik_profile

    def predict_locomotion(self, path: List[List[float]], current_time: float) -> Dict[str, Any]:
        """Predicts position and orientation vectors based on path points."""
        if len(path) < 2:
            return {"position": [0.0, 0.0, 0.0], "heading": 0.0, "speed": 0.0}
            
        # Simple velocity extraction from path segments
        p1 = path[0]
        p2 = path[1]
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        heading = math.atan2(dy, dx)
        speed = math.sqrt(dx**2 + dy**2)
        
        # Predict ahead
        predicted_x = p2[0] + dx * current_time
        predicted_y = p2[1] + dy * current_time
        
        return {
            "position": [predicted_x, predicted_y, 0.0],
            "heading": heading,
            "speed": speed
        }
