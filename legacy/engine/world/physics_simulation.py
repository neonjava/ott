# ai/physics_simulation.py
from typing import Dict, Any, List

class PhysicsSimulationAgent:
    """
    Subsystem: Physics Simulation
    Configures cloth dynamics, hair physics, wind parameters, and object rigid body collisions.
    """
    def __init__(self):
        self.default_gravity = -9.81

    def get_simulation_settings(self, environment_type: str, mood: str) -> Dict[str, Any]:
        """Returns physical simulation vectors based on environmental context and scene mood."""
        # Baseline settings
        settings = {
            "cloth_enabled": True,
            "hair_enabled": True,
            "secondary_motion_multiplier": 1.0,
            "wind_vector": [0.0, 0.0, 0.0],
            "gravity": self.default_gravity,
            "collision_margin": 0.015
        }
        
        env = environment_type.lower()
        
        # Modify physics based on environment
        if "storm" in env or "cave" in env:
            settings["wind_vector"] = [5.0, 2.0, -1.0] if "storm" in env else [0.2, 0.1, 0.0]
            settings["secondary_motion_multiplier"] = 1.3
        elif "space" in env or "moon" in env:
            settings["gravity"] = -1.62
            settings["secondary_motion_multiplier"] = 0.5
            settings["wind_vector"] = [0.0, 0.0, 0.0]
            
        # Adjust dynamics based on mood
        m = mood.lower()
        if "epic" in m or "action" in m:
            settings["secondary_motion_multiplier"] *= 1.2
            
        return settings

    def compute_collision_params(self, object_type: str) -> Dict[str, Any]:
        """Provides rigid body or soft body presets for collision detection."""
        obj = object_type.lower()
        if obj in ["sword", "shield", "axe", "mace"]:
            return {
                "body_type": "rigid",
                "mass": 3.5,
                "friction": 0.5,
                "bounciness": 0.1
            }
        elif obj in ["cape", "skirt", "banner"]:
            return {
                "body_type": "soft",
                "mass": 0.8,
                "friction": 0.8,
                "bending_stiffness": 0.5
            }
        return {
            "body_type": "rigid",
            "mass": 1.0,
            "friction": 0.5,
            "bounciness": 0.2
        }
