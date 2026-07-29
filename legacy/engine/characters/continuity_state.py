# engine/characters/continuity_state.py
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SceneContinuityState:
    """
    Manages persistent scene state and character memory across multi-shot AI movie generation sequences.
    Ensures identical character features, outfit, lighting, environment, and weather anchors across all shots.
    """

    def __init__(self):
        self.character_identity = "a futuristic cybernetic explorer woman with sharp jawline, high cheekbones, and sleek silver hair styled in a side-swept bob"
        self.outfit = "a fitted black leather tactical coat with glowing cyan fiber-optic seams and dark metallic collar"
        self.environment = "a rain-slicked neon-lit cyberpunk metropolis street at night with towering holographic billboards and glowing cyan and magenta reflections on wet dark asphalt"
        self.weather_lighting = "steady soft rain falling, dark moody atmosphere, volumetric fog, dramatic neon rim lighting, warm golden-cyan dual tone highlights"
        self.camera_style = "cinematic anamorphic lens, 35mm film grain, shallow depth of field, 8k resolution, photorealistic Hollywood film production quality"

    def get_shot_prompt(self, shot_num: int, shot_type: str, action_description: str, camera_movement: str) -> str:
        prompt = (
            f"Cinematic {shot_type} of {self.character_identity}, wearing {self.outfit}. "
            f"{action_description}. {camera_movement}. "
            f"Set in {self.environment}. {self.weather_lighting}. {self.camera_style}."
        )
        return prompt

    def get_negative_prompt(self) -> str:
        return "low quality, blurry, distorted, static, bad anatomy, deformed, glitch, cartoon, 3d render, low resolution, flickering"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "character_identity": self.character_identity,
            "outfit": self.outfit,
            "environment": self.environment,
            "weather_lighting": self.weather_lighting,
            "camera_style": self.camera_style
        }
