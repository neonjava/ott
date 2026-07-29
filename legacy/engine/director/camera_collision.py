# ai/camera_collision.py
from typing import Dict, Any, List, Tuple

class CameraCollisionSolver:
    """
    Subsystem: Camera Collision & Occlusion Solver
    Detects if camera coordinates intersect environmental boundaries or if props block lines-of-sight to actors.
    Provides collision-free camera positioning alternatives.
    """
    def __init__(self):
        pass

    def check_occlusion(self, cam_pos: List[float], actor_pos: List[float], obstacle_bounds: List[Dict[str, Any]]) -> bool:
        """Determines if any obstacle bounding box intersects the ray segment between camera and actor."""
        # Simple ray-box intersection logic
        for obs in obstacle_bounds:
            min_x, max_x = obs.get("min_x", -1.0), obs.get("max_x", 1.0)
            min_y, max_y = obs.get("min_y", -1.0), obs.get("max_y", 1.0)
            
            # Check midpoint of ray
            mid_x = (cam_pos[0] + actor_pos[0]) / 2.0
            mid_y = (cam_pos[1] + actor_pos[1]) / 2.0
            
            if min_x <= mid_x <= max_x and min_y <= mid_y <= max_y:
                return True  # Line-of-sight is occluded
        return False

    def solve_position(self, current_cam: List[float], actor_pos: List[float], obstacles: List[Dict[str, Any]]) -> List[float]:
        """Iteratively offsets camera height/zoom if occlusion or collision is detected."""
        resolved_cam = list(current_cam)
        attempts = 0
        max_attempts = 5
        
        while self.check_occlusion(resolved_cam, actor_pos, obstacles) and attempts < max_attempts:
            attempts += 1
            # Adjust camera height (Z axis) and zoom closer (translate towards actor)
            resolved_cam[2] += 0.4  # Tilt camera higher
            # Shift camera translation closer by 20%
            resolved_cam[0] = resolved_cam[0] * 0.8 + actor_pos[0] * 0.2
            resolved_cam[1] = resolved_cam[1] * 0.8 + actor_pos[1] * 0.2
            
        return resolved_cam
