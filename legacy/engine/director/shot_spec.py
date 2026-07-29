# engine/director/shot_spec.py
from typing import Dict, Any, List

class ShotSpec:
    """
    Subsystem: Shot Specification Generator
    A formal model-agnostic visual data contract representing all cinematic constraints for a shot.
    """
    def __init__(self, shot_data: Dict[str, Any]):
        self.shot_id = shot_data.get("shot_id", "shot_01")
        self.scene_id = shot_data.get("scene_id", "scene_01")
        self.purpose = shot_data.get("purpose", "story introduction")
        
        # Camera & framing
        self.camera = shot_data.get("camera", {
            "type": "wide",
            "height": 1.5,
            "target": "actor"
        })
        
        self.lens = shot_data.get("lens", {
            "focal_length": 35,
            "aperture_fstop": 2.8
        })
        
        self.movement = shot_data.get("movement", {
            "camera_profile": "Steadicam",
            "movement_speed": 1.0
        })
        
        self.composition = shot_data.get("composition", "rule_of_thirds")
        
        # Character & acting
        self.characters = shot_data.get("characters", [{
            "name": "humanoid",
            "action": "idle",
            "mood": "neutral",
            "outfit": "armor",
            "weapon": "sword"
        }])
        
        # World context
        self.environment = shot_data.get("environment", {
            "location": "forest",
            "weather": "clear",
            "environment_props": []
        })
        
        self.lighting = shot_data.get("lighting", {
            "mood": "neutral",
            "intensity": 1.0
        })
        
        # Dialogue performance
        self.dialogue = shot_data.get("dialogue", {
            "speaker": None,
            "text": "",
            "voice_profile": None
        })
        
        self.emotion = shot_data.get("emotion", "neutral")
        self.references = shot_data.get("references", {})
        self.backend_requirements = shot_data.get("backend_requirements", {})
        self.continuity = shot_data.get("continuity", {
            "seed": 42,
            "environmental_seed": 100
        })

    def to_dict(self) -> Dict[str, Any]:
        """Serializes ShotSpec to a JSON-serializable dictionary."""
        return {
            "shot_id": self.shot_id,
            "scene_id": self.scene_id,
            "purpose": self.purpose,
            "camera": self.camera,
            "lens": self.lens,
            "movement": self.movement,
            "composition": self.composition,
            "characters": self.characters,
            "environment": self.environment,
            "lighting": self.lighting,
            "dialogue": self.dialogue,
            "emotion": self.emotion,
            "references": self.references,
            "backend_requirements": self.backend_requirements,
            "continuity": self.continuity
        }
