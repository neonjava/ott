#!/usr/bin/env python3
"""
spatial_placement_engine.py
Calculates deterministic, collision-free 3D coordinate positions, entry/exit vectors,
and orientations for 1 to 10 characters. Ensures camera-safe and overlap-free layouts.
"""
import math
from typing import Dict, Any, List, Tuple

class SpatialPlacementEngine:
    def __init__(self, char_radius: float = 0.8, min_separation: float = 1.2):
        self.char_radius = char_radius
        self.min_separation = min_separation

    def calculate_positions(
        self,
        characters: List[str],
        camera_target: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        layout_style: str = "semicircle"
    ) -> Dict[str, Dict[str, Any]]:
        """
        Deterministically places characters in 3D space to avoid mesh overlaps.
        Returns a dictionary containing position, rotation, entry_position, and exit_position.
        """
        num_chars = len(characters)
        if num_chars == 0:
            return {}

        placements = {}
        
        # Camera is assumed to look towards the target from negative Y
        # So facing direction is along positive Y.
        # Characters are placed around the camera target.
        
        # Determine radius from target based on character count to avoid crowding
        # Minimal radius is 2.0m, increasing by 0.5m for every 2 characters
        base_radius = 2.0 + (num_chars // 2) * 0.5

        if num_chars == 1:
            # Single actor directly in front of the camera looking at target
            pos = (camera_target[0], camera_target[1] + base_radius, camera_target[2])
            # Rotation in radians: facing the target (facing negative Y)
            rot = (0.0, 0.0, math.pi)
            
            placements[characters[0]] = {
                "position": list(pos),
                "rotation": list(rot),
                "entry_position": [pos[0], pos[1] + 3.0, pos[2]], # Walk in from behind
                "exit_position": [pos[0], pos[1] - 3.0, pos[2]],  # Walk forward past camera
                "radius": self.char_radius
            }
            return placements

        # Multiple characters: arrange in a semicircle or line facing the target
        # Semicircle arc angles from -50 degrees to +50 degrees
        max_angle = math.radians(50.0)
        angle_step = (2 * max_angle) / (num_chars - 1)
        start_angle = -max_angle

        for i, char_id in enumerate(characters):
            # Calculate angle along the arc
            angle = start_angle + i * angle_step
            
            # Position coordinates relative to camera_target
            # Arc spreads on X, centered on Y
            dx = base_radius * math.sin(angle)
            dy = base_radius * math.cos(angle)
            
            pos_x = camera_target[0] + dx
            pos_y = camera_target[1] + dy
            pos_z = camera_target[2]
            
            # Face the target (opposite vector to displacement)
            # angle from pos to target:
            target_vector_x = camera_target[0] - pos_x
            target_vector_y = camera_target[1] - pos_y
            yaw = math.atan2(target_vector_y, target_vector_x) - (math.pi / 2)
            rot = (0.0, 0.0, yaw)

            # Entry position (walk in from outer radius)
            entry_radius = base_radius + 3.0
            entry_x = camera_target[0] + entry_radius * math.sin(angle)
            entry_y = camera_target[1] + entry_radius * math.cos(angle)
            
            # Exit position (walk out past target or sideways)
            exit_radius = base_radius - 2.5
            exit_x = camera_target[0] + exit_radius * math.sin(angle)
            exit_y = camera_target[1] + exit_radius * math.cos(angle)

            placements[char_id] = {
                "position": [round(pos_x, 3), round(pos_y, 3), round(pos_z, 3)],
                "rotation": [0.0, 0.0, round(yaw, 3)],
                "entry_position": [round(entry_x, 3), round(entry_y, 3), round(pos_z, 3)],
                "exit_position": [round(exit_x, 3), round(exit_y, 3), round(pos_z, 3)],
                "radius": self.char_radius
            }

        # Validate separation (collision avoidance check)
        self.resolve_collisions(placements)

        return placements

    def resolve_collisions(self, placements: Dict[str, Dict[str, Any]]):
        """
        Pushes overlapping characters apart if they violate the minimum separation distance.
        """
        keys = list(placements.keys())
        n = len(keys)
        if n <= 1:
            return

        # Simple iterative repulsion algorithm
        max_iterations = 10
        for _ in range(max_iterations):
            collision_resolved = True
            for i in range(n):
                for j in range(i + 1, n):
                    char1 = placements[keys[i]]
                    char2 = placements[keys[j]]
                    
                    p1 = char1["position"]
                    p2 = char2["position"]
                    
                    dx = p2[0] - p1[0]
                    dy = p2[1] - p1[1]
                    dist = math.sqrt(dx*dx + dy*dy)
                    
                    required_dist = char1["radius"] + char2["radius"] + 0.2
                    if dist < required_dist:
                        collision_resolved = False
                        # Push them apart along the vector connecting them
                        if dist == 0:
                            # Avoid divide by zero
                            dx = 0.1
                            dist = 0.1
                        
                        overlap = required_dist - dist
                        push_x = (dx / dist) * (overlap / 2.0)
                        push_y = (dy / dist) * (overlap / 2.0)
                        
                        char1["position"][0] -= round(push_x, 3)
                        char1["position"][1] -= round(push_y, 3)
                        char2["position"][0] += round(push_x, 3)
                        char2["position"][1] += round(push_y, 3)

            if collision_resolved:
                break

    def detect_overlaps(self, placements: Dict[str, Dict[str, Any]]) -> List[Tuple[str, str, float]]:
        """
        Detects any remaining overlaps. Returns a list of (char1, char2, overlap_distance) tuples.
        """
        overlaps = []
        keys = list(placements.keys())
        n = len(keys)
        for i in range(n):
            for j in range(i + 1, n):
                char1 = placements[keys[i]]
                char2 = placements[keys[j]]
                p1 = char1["position"]
                p2 = char2["position"]
                dist = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
                limit = char1["radius"] + char2["radius"]
                if dist < limit:
                    overlaps.append((keys[i], keys[j], round(limit - dist, 3)))
        return overlaps

if __name__ == "__main__":
    engine = SpatialPlacementEngine()
    test_chars = ["knight", "mage", "robot", "queen", "king"]
    results = engine.calculate_positions(test_chars)
    import json
    print(json.dumps(results, indent=2))
    print("Overlaps:", engine.detect_overlaps(results))
