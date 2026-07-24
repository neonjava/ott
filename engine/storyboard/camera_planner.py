# engine/storyboard/camera_planner.py
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

CAMERA_STYLES = {
    "establishing": {"framing": "Extreme Wide", "movement": "crane up slowly", "lens": "24mm wide angle"},
    "dialogue": {"framing": "Medium Closeup", "movement": "dolly forward slowly", "lens": "50mm portrait"},
    "action": {"framing": "Wide Tracking", "movement": "pan right following action", "lens": "35mm anamorphic"},
    "dramatic": {"framing": "Macro Closeup", "movement": "static dynamic push", "lens": "85mm prime"},
    "reveal": {"framing": "Center Hero", "movement": "slow pull back orbit", "lens": "35mm prime"},
    "epic": {"framing": "Wide Establish", "movement": "drone overhead sweep", "lens": "18mm wide"}
}

class CameraPlanner:
    """
    Cinematography AI for GenOTT V2.
    Automatically assigns optimal framing, movement path, lens specification,
    and transitions based on narrative intent.
    """

    def plan_camera_for_shot(self, shot_spec: Dict[str, Any]) -> Dict[str, Any]:
        action_text = shot_spec.get("action", "").lower()
        
        selected_style = "establishing"
        if "talk" in action_text or "speak" in action_text or "stare" in action_text:
            selected_style = "dialogue"
        elif "ignit" in action_text or "core" in action_text or "close" in action_text:
            selected_style = "dramatic"
        elif "accelerat" in action_text or "fly" in action_text or "run" in action_text or "jump" in action_text:
            selected_style = "action"
        elif "emerge" in action_text or "reveal" in action_text or "title" in action_text:
            selected_style = "reveal"

        preset = CAMERA_STYLES[selected_style]

        planned_shot = {
            **shot_spec,
            "framing": shot_spec.get("framing") or preset["framing"],
            "camera_movement": shot_spec.get("camera_movement") or preset["movement"],
            "lens": shot_spec.get("lens") or preset["lens"],
            "cinematography_preset": selected_style
        }
        return planned_shot

    def plan_sequence(self, shots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [self.plan_camera_for_shot(s) for s in shots]
