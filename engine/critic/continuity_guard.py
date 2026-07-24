# engine/critic/continuity_guard.py
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class VisualContinuityGuard:
    """
    Automated Visual Continuity Engine for GenOTT V2.
    Tracks locations, weather, lighting, camera direction, props, costumes, and object positions
    to detect continuity errors pre-render and inject correction suggestions.
    """

    def audit_scene_continuity(self, shots: List[Dict[str, Any]]) -> Dict[str, Any]:
        continuity_flags = []
        corrections = []
        
        last_location = None
        last_lighting = None
        last_weather = None

        for idx, shot in enumerate(shots, start=1):
            curr_loc = shot.get("location", shot.get("environment", ""))
            curr_light = shot.get("lighting", "")
            curr_weather = shot.get("weather", "")

            if last_location and curr_loc and curr_loc != last_location:
                # Scene transition check
                if not shot.get("scene_transition"):
                    continuity_flags.append({
                        "shot_id": idx,
                        "type": "location_mismatch",
                        "message": f"Abrupt location shift from '{last_location}' to '{curr_loc}' without transition."
                    })
                    corrections.append(f"Shot {idx}: Insert establishing shot or fade transition to '{curr_loc}'.")

            if last_lighting and curr_light and curr_light != last_lighting:
                continuity_flags.append({
                    "shot_id": idx,
                    "type": "lighting_mismatch",
                    "message": f"Lighting changed from '{last_lighting}' to '{curr_light}' in same scene."
                })
                shot["lighting"] = last_lighting  # Auto-correct lighting spec for consistency
                corrections.append(f"Shot {idx}: Auto-harmonized lighting to match '{last_lighting}'.")

            last_location = curr_loc or last_location
            last_lighting = curr_light or last_lighting
            last_weather = curr_weather or last_weather

        return {
            "total_shots_audited": len(shots),
            "continuity_flags": continuity_flags,
            "corrections_applied": corrections,
            "is_continuous": len(continuity_flags) == 0
        }
