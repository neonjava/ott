# engine/director/shot_planner.py
from typing import Dict, Any, List

class ShotPlanner:
    """
    Subsystem: Shot Planner
    Takes scene parameters and compiles sequential sub-shot items with cinematic transitions.
    """
    def __init__(self):
        pass

    def plan_shots_for_scene(self, scene: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Splits a single scene into multiple cinematic shots to add production value."""
        shots = []
        scene_num = scene.get("scene_number", 1)
        actor = scene.get("character_name", "humanoid")
        action = scene.get("action", "idle")
        duration = scene.get("duration", 4.0)
        
        # Shot 1: Establishing Shot / Wide
        shots.append({
            "shot_number": 1,
            "scene_id": f"scene_{scene_num}",
            "duration": duration * 0.4,
            "camera_objective": "Establish the character in their environment",
            "actor_objective": f"Enter the frame and perform initial {action}",
            "emotion": scene.get("mood", "neutral"),
            "transition": "Fade In" if scene_num == 1 else "Cut"
        })
        
        # Shot 2: Character Focus / Close Up or Medium Tracking
        shots.append({
            "shot_number": 2,
            "scene_id": f"scene_{scene_num}",
            "duration": duration * 0.6,
            "camera_objective": "Focus on actor emotion and interaction detail",
            "actor_objective": f"Complete the main {action} sequence",
            "emotion": scene.get("mood", "neutral"),
            "transition": "Cut"
        })
        
        return shots
