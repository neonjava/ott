# ai/camera_motion.py
import math
from typing import Tuple, List, Dict, Any

class CameraMotionEngine:
    """
    Subsystem: Camera Motion Engine
    Generates physically-realistic camera operator breathing, shoulder sway, walking cadence,
    and profile configurations (Tripod, Handheld, Steadicam, Dolly).
    """
    def __init__(self):
        pass

    def get_noise(self, t: float, seed: int = 42) -> float:
        """Generates continuous, non-repeating fractional brownian motion using irrational frequencies."""
        # Multi-octave pseudo-random noise blending irrational frequencies
        val = 0.5 * math.sin(t * 1.1412 + seed % 7)
        val += 0.25 * math.cos(t * 2.7182 + (seed * 3) % 11)
        val += 0.125 * math.sin(t * 5.618 + (seed * 7) % 13)
        return val

    def apply_profile(self, profile: str, frame: int, fps: float, base_location: Tuple[float, float, float], base_rotation: Tuple[float, float, float], is_walking: bool = False) -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
        """Applies physical camera operator characteristics based on the selected camera profile."""
        t = frame / fps
        p = profile.lower().strip()
        
        loc_offset = [0.0, 0.0, 0.0]
        rot_offset = [0.0, 0.0, 0.0]
        
        if p == "tripod":
            # Perfectly static
            pass
        elif p == "dolly":
            # Constant velocity with slow ease, no camera operator noise
            pass
        elif p == "steadicam":
            # Floating stabilized movement, low breathing sway
            loc_offset[0] = 0.005 * self.get_noise(t * 0.8, seed=1)
            loc_offset[1] = 0.005 * self.get_noise(t * 0.9, seed=2)
            loc_offset[2] = 0.008 * math.sin(t * 1.2)  # subtle breathing
            
            rot_offset[0] = 0.001 * self.get_noise(t * 0.7, seed=3)
            rot_offset[1] = 0.001 * self.get_noise(t * 0.8, seed=4)
            rot_offset[2] = 0.001 * self.get_noise(t * 0.6, seed=5)
        elif p == "handheld":
            # Significant shoulder sway + breathing + cadences
            loc_offset[0] = 0.025 * self.get_noise(t * 1.1, seed=10)
            loc_offset[1] = 0.025 * self.get_noise(t * 1.3, seed=11)
            loc_offset[2] = 0.035 * math.sin(t * 1.5)  # breathing cadence
            
            rot_offset[0] = 0.008 * self.get_noise(t * 1.0, seed=12)
            rot_offset[1] = 0.006 * self.get_noise(t * 1.2, seed=13)
            rot_offset[2] = 0.008 * self.get_noise(t * 0.9, seed=14)
            
            if is_walking:
                # Add human walking footstep cadence impact (typically 2 steps per second)
                walk_frequency = 4.0 * math.pi
                loc_offset[2] += 0.040 * abs(math.sin(t * walk_frequency))  # step vertical bounce
                rot_offset[0] += 0.015 * math.sin(t * walk_frequency)       # step tilt wobble
        else:
            # Default mild handheld rig
            loc_offset[0] = 0.012 * self.get_noise(t, seed=20)
            loc_offset[1] = 0.012 * self.get_noise(t * 1.1, seed=21)
            loc_offset[2] = 0.015 * math.sin(t * 1.3)
            
            rot_offset[0] = 0.004 * self.get_noise(t, seed=22)
            rot_offset[1] = 0.003 * self.get_noise(t * 1.1, seed=23)
            rot_offset[2] = 0.004 * self.get_noise(t * 0.9, seed=24)
            
        final_loc = (
            base_location[0] + loc_offset[0],
            base_location[1] + loc_offset[1],
            base_location[2] + loc_offset[2]
        )
        final_rot = (
            base_rotation[0] + rot_offset[0],
            base_rotation[1] + rot_offset[1],
            base_rotation[2] + rot_offset[2]
        )
        return final_loc, final_rot
