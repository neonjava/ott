# ai/environment_interaction.py
"""
Environment Interaction Engine — Decides interaction parameters, trajectories, and constraints
to allow characters to dynamically interact with props, furniture, and surroundings.

Computes:
  - Approach positions and paths (avoiding obstacles/furniture)
  - Reach targets, hand IK positions, grasp/release timing
  - Stance changes (sitting, leaning, pushing, pulling)
  - Body balance and weight-lean compensation based on object mass
  - Gaze and look-at targets (speaking characters, focus props)
"""
import math
from typing import Dict, Any, List, Optional, Tuple

class EnvironmentInteractionEngine:
    """
    Computes look-at vectors, path correction coordinates, grasp/IK targets,
    and weight-shifting variables for environment interactions.
    """
    def __init__(self):
        pass

    def compute_interaction(
        self,
        interaction_type: str,
        char_pos: Tuple[float, float, float],
        object_pos: Tuple[float, float, float],
        object_mass: float = 1.0,
        shot_duration: float = 4.0
    ) -> Dict[str, Any]:
        """
        Computes spatial adjustments and timing offsets for character interactions.
        """
        state = str(interaction_type).lower().strip()
        cx, cy, cz = char_pos
        ox, oy, oz = object_pos
        
        # Calculate distance and direction
        dx = ox - cx
        dy = oy - cy
        dz = oz - cz
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        # Default results
        res = {
            "approach_position": (cx, cy, cz),
            "reach_target": object_pos,
            "hand_ik_target": object_pos,
            "grasp_time": 0.0,
            "release_time": 0.0,
            "balance_adjustment": (0.0, 0.0, 0.0),
            "eye_focus": object_pos,
            "hand_rotation": (0.0, 0.0, 0.0),
            "stance": "relaxed"
        }

        # Stride/approach calculation (ideal distance to interact is ~0.8 meters)
        ideal_dist = 0.8
        if state == "sit":
            ideal_dist = 0.1  # sit right on the chair center
        elif state == "open_door":
            ideal_dist = 0.9
            
        if dist > 0.001:
            ratio = ideal_dist / dist
            # Approach position is a point along the line toward the object
            res["approach_position"] = (
                ox - dx * ratio,
                oy - dy * ratio,
                cz
            )

        # Type-specific configurations
        if "pick_up" in state or "grab" in state:
            res["grasp_time"] = shot_duration * 0.5
            res["stance"] = "leaning"
            # Lean forward based on object weight (weight awareness)
            lean_pitch = min(0.4, 0.05 * object_mass)
            res["balance_adjustment"] = (lean_pitch, 0.0, 0.0)
            res["eye_focus"] = object_pos
            
        elif "place" in state:
            res["grasp_time"] = 0.0
            res["release_time"] = shot_duration * 0.75
            res["stance"] = "leaning"
            lean_pitch = min(0.3, 0.04 * object_mass)
            res["balance_adjustment"] = (lean_pitch, 0.0, 0.0)
            
        elif "sit" in state:
            res["stance"] = "sitting"
            # Sit down: shift pelvis downwards (Z-axis offset)
            chair_height = oz + 0.45  # average chair seat height
            res["approach_position"] = (ox, oy, cz)
            res["balance_adjustment"] = (-0.1, 0.0, 0.0)  # lean back slightly into seat
            res["reach_target"] = (ox, oy, chair_height)
            res["eye_focus"] = (ox, oy + 2.0, cz + 1.2)  # look forward
            
        elif "open_door" in state or "push" in state or "pull" in state:
            res["grasp_time"] = shot_duration * 0.3
            res["release_time"] = shot_duration * 0.8
            res["stance"] = "push_pull"
            # Pushing requires leaning forward, pulling requires leaning backward
            if "pull" in state:
                res["balance_adjustment"] = (-0.15, 0.0, 0.0)
            else:
                res["balance_adjustment"] = (0.15, 0.0, 0.0)
                
        return res

    def compute_avoidance_path(
        self,
        start_pos: Tuple[float, float, float],
        end_pos: Tuple[float, float, float],
        obstacles: List[Tuple[float, float, float, float]]  # List of (x, y, radius, margin)
    ) -> List[Tuple[float, float, float]]:
        """
        Calculates path waypoints avoiding obstacles on a 2D plane (X, Y).
        """
        waypoints = [start_pos]
        sx, sy, sz = start_pos
        ex, ey, ez = end_pos
        
        # Simple single-obstacle raycast & dodge solver
        cx, cy = sx, sy
        step_factor = 0.2
        steps = 10
        
        for i in range(1, steps + 1):
            t = i / steps
            target_x = sx + (ex - sx) * t
            target_y = sy + (ey - sy) * t
            
            # Check collisions
            collision = False
            for ox, oy, r, margin in obstacles:
                dx = target_x - ox
                dy = target_y - oy
                d = math.sqrt(dx*dx + dy*dy)
                limit = r + margin
                
                if d < limit:
                    # Push waypoint away from obstacle center orthogonally
                    collision = True
                    angle = math.atan2(dy, dx)
                    target_x = ox + limit * math.cos(angle)
                    target_y = oy + limit * math.sin(angle)
                    
            waypoints.append((target_x, target_y, sz))
            
        return waypoints
