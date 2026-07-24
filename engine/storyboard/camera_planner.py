# engine/storyboard/camera_planner.py
import random
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class CameraPlanner:
    """
    Cinematic Camera AI for GenOTT V2.
    Plans diverse, dynamic cinematography setups across shot sequences avoiding repetitive movement:
    - establishing shots
    - close ups
    - over-the-shoulder
    - POV
    - tracking
    - drone / aerial
    - dolly zoom / tracking
    - crane shot
    - handheld / shoulder-rig
    - 360 orbit
    """

    CAMERA_PRESETS = [
        {"shot_type": "Wide Establishing", "movement": "Slow Overhead Drone Glide", "focal_length": "24mm prime lens"},
        {"shot_type": "Medium Over-the-Shoulder", "movement": "Gentle Dolly Tracking Right", "focal_length": "50mm anamorphic lens"},
        {"shot_type": "Extreme Close-Up", "movement": "Subtle Handheld Micro-Shake", "focal_length": "85mm macro lens"},
        {"shot_type": "First-Person POV", "movement": "Dynamic Forward Tracking Shot", "focal_length": "35mm wide lens"},
        {"shot_type": "High Angle Crane", "movement": "Sweeping Vertical Descending Tilt", "focal_length": "28mm prime lens"},
        {"shot_type": "360 Degree Orbit", "movement": "Smooth Rotational Parallax Arc", "focal_length": "35mm anamorphic lens"},
        {"shot_type": "Low Angle Hero Shot", "movement": "Slow Forward Push-In", "focal_length": "40mm cine lens"}
    ]

    def plan_camera_for_shot(self, shot_spec: Dict[str, Any]) -> Dict[str, Any]:
        preset = self.CAMERA_PRESETS[0]
        shot_copy = dict(shot_spec)
        shot_copy["cinematography_preset"] = "dramatic"
        shot_copy["framing"] = "Macro Close-Up"
        shot_copy["camera_movement"] = preset["movement"]
        shot_copy["camera_lens"] = preset["focal_length"]
        return shot_copy

    def plan_sequence(self, shots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        planned_shots = []
        last_preset_idx = -1

        for idx, shot in enumerate(shots):
            preset_idx = (idx % len(self.CAMERA_PRESETS))
            if preset_idx == last_preset_idx:
                preset_idx = (preset_idx + 1) % len(self.CAMERA_PRESETS)
            last_preset_idx = preset_idx

            preset = self.CAMERA_PRESETS[preset_idx]
            shot_copy = dict(shot)
            shot_copy["camera_shot_type"] = preset["shot_type"]
            shot_copy["camera_movement"] = preset["movement"]
            shot_copy["camera_lens"] = preset["focal_length"]

            cinematic_prompt_addition = f"{preset['shot_type']}, {preset['movement']}, shot on {preset['focal_length']}, 24fps motion blur, cinematic lighting."
            shot_copy["cinematic_camera_spec"] = cinematic_prompt_addition
            planned_shots.append(shot_copy)

        logger.info(f"[CameraPlanner] Planned dynamic cinematography for {len(planned_shots)} shots.")
        return planned_shots
