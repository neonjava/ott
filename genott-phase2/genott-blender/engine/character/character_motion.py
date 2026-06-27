# ai/character_motion.py
"""
Character Motion Engine — Production-Quality Procedural Body Animation.

Generates per-frame bone rotation and translation offsets for procedural body dynamics:
  - Multi-frequency breathing (spine, chest, shoulders)
  - Weight shifting and center of mass balance simulation
  - Anticipation and follow-through on transitions
  - Body balance dynamics (leaning into acceleration, deceleration, momentum)
  - Foot planting and Foot IK foot-locking (preventing sliding, floating, clipping)
  - Stride prediction (cadence, length, height based on speed)
  - Reach / object interaction targeting (inverse kinematics proxy)
  - Finger curl and hand relaxation
  - Motion blending (weighted interpolation for smooth transition graphs)
"""
import math
from typing import Dict, Tuple, Optional, Any, List

def _noise(t: float, seed: int) -> float:
    """Multi-octave continuous noise in [-1, 1]."""
    v  = 0.50 * math.sin(t * 1.1412 + (seed % 7) * 0.9)
    v += 0.25 * math.cos(t * 2.7183 + (seed * 3 % 11) * 0.7)
    v += 0.125 * math.sin(t * 5.618 + (seed * 7 % 13) * 0.5)
    return v

def _smoothstep(edge0: float, edge1: float, x: float) -> float:
    if edge1 == edge0:
        return 1.0 if x >= edge1 else 0.0
    t = max(0.0, min(1.0, (x - edge0) / (edge1 - edge0)))
    return t * t * (3.0 - 2.0 * t)

def classify_action(action_name: str) -> str:
    """Return one of: 'idle', 'walk', 'run', 'jump', 'talk', 'reach', 'turn_in_place', 'other'."""
    a = str(action_name).lower()
    if "run" in a:
        return "run"
    if "walk" in a:
        return "walk"
    if "jump" in a:
        return "jump"
    if "talk" in a or "speak" in a:
        return "talk"
    if "reach" in a or "grab" in a or "interact" in a:
        return "reach"
    if "turn" in a:
        return "turn_in_place"
    if "idle" in a or "stand" in a:
        return "idle"
    return "other"

class CharacterMotionEngine:
    """
    Computes per-frame procedural bone rotation and translation offsets.
    Supports foot locking, momentum, balance leans, and arm reaches.
    """
    def __init__(self):
        # Cache for transition blending state
        self.transition_duration = 0.5  # seconds
        
    def compute_frame(
        self,
        frame: int,
        f_start: int,
        f_end: int,
        fps: float,
        action_name: str,
        char_name: str,
        target_location: Optional[Tuple[float, float, float]] = None,
        char_location: Optional[Tuple[float, float, float]] = None,
        velocity: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        acceleration: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        prev_action_name: Optional[str] = None,
        transition_t: float = 0.0
    ) -> Dict[str, Any]:
        """
        Return bone rotation and translation offsets for this frame.
        Format:
        {
            "bones": {
                "Hips": {"rotation": (rx, ry, rz), "location": (lx, ly, lz)},
                "Spine": {"rotation": (rx, ry, rz)},
                ...
            },
            "foot_locking": {
                "Foot.L": {"planted": True, "slide_offset": 0.0},
                "Foot.R": {"planted": False, "slide_offset": 0.0}
            }
        }
        """
        t = (frame - f_start) / fps
        seed = hash(char_name)
        state = classify_action(action_name)
        
        # Base offset dicts
        offsets: Dict[str, Dict[str, Tuple[float, float, float]]] = {}
        
        # 1. Natural breathing layer (Spine, Spine1, Spine2, Neck, Shoulders)
        self._apply_breathing(offsets, t, seed, state)
        
        # 2. Body dynamics & Balance (leaning into acceleration, deceleration, momentum)
        self._apply_dynamics_and_balance(offsets, t, seed, state, velocity, acceleration)
        
        # 3. Weight shifting & Center of mass (hips sway & balance)
        self._apply_weight_shifting(offsets, t, seed, state)
        
        # 4. Locomotion cycles & stride prediction
        foot_locking = self._apply_locomotion_strides(offsets, t, seed, state, velocity)
        
        # 5. Hand relaxation & finger curl
        self._apply_hand_relaxation(offsets, t, seed, state)
        
        # 6. Reach animations & object interaction
        self._apply_reach_interaction(offsets, t, seed, state, target_location, char_location)
        
        # 7. Head stabilization
        self._apply_head_stabilization(offsets, t, seed, state)
        
        # 8. Action transition blending (prevent snapping)
        if prev_action_name and transition_t < self.transition_duration:
            prev_state = classify_action(prev_action_name)
            prev_offsets: Dict[str, Dict[str, Tuple[float, float, float]]] = {}
            self._apply_breathing(prev_offsets, t, seed, prev_state)
            self._apply_dynamics_and_balance(prev_offsets, t, seed, prev_state, velocity, acceleration)
            self._apply_weight_shifting(prev_offsets, t, seed, prev_state)
            self._apply_locomotion_strides(prev_offsets, t, seed, prev_state, velocity)
            self._apply_hand_relaxation(prev_offsets, t, seed, prev_state)
            self._apply_reach_interaction(prev_offsets, t, seed, prev_state, target_location, char_location)
            self._apply_head_stabilization(prev_offsets, t, seed, prev_state)
            
            blend_w = _smoothstep(0.0, self.transition_duration, transition_t)
            offsets = self._blend_offsets(prev_offsets, offsets, blend_w)
            
        return {
            "bones": offsets,
            "foot_locking": foot_locking
        }
        
    def _apply_breathing(self, offsets, t, seed, state):
        rate = 0.25 + 0.02 * (seed % 5)  # ~15 bpm
        if state == "run":
            rate *= 2.2
        elif state == "walk":
            rate *= 1.4
            
        phase = 2.0 * math.pi * rate * t
        breath = math.sin(phase)
        
        # Spine breathing
        offsets["Spine"] = {"rotation": (0.02 * breath, 0.004 * _noise(t, seed), 0.0)}
        offsets["Spine1"] = {"rotation": (0.012 * breath, 0.0, 0.0)}
        offsets["Spine2"] = {"rotation": (0.008 * breath, 0.0, 0.0)}
        
        # Shoulder breathing wiggles
        offsets["Shoulder.L"] = {"rotation": (0.0, 0.005 * breath, 0.0)}
        offsets["Shoulder.R"] = {"rotation": (0.0, -0.005 * breath, 0.0)}
        
    def _apply_dynamics_and_balance(self, offsets, t, seed, state, velocity, acceleration):
        # Lean into acceleration/deceleration (inertia & balance recovery)
        ax, ay, az = acceleration
        vx, vy, vz = velocity
        speed = math.sqrt(vx*vx + vy*vy + vz*vz)
        
        # Anticipation & balance lean angles
        lean_x = -ax * 0.05  # pitch lean
        lean_y = -ay * 0.05  # roll lean
        
        # Momentum recovery wiggle
        wiggle_decay = math.exp(-t * 1.5)
        recovery_pitch = 0.02 * math.sin(t * 5.0) * wiggle_decay
        
        # Accumulate to hips/spine
        if "Hips" not in offsets:
            offsets["Hips"] = {}
        h_rot = offsets["Hips"].get("rotation", (0.0, 0.0, 0.0))
        offsets["Hips"]["rotation"] = (h_rot[0] + lean_x + recovery_pitch, h_rot[1] + lean_y, h_rot[2])
        
    def _apply_weight_shifting(self, offsets, t, seed, state):
        if state in ("walk", "run"):
            return
            
        # Idle/Talk weight shift: periodically sway hips side to side
        sway = 0.025 * math.sin(t * 0.12 * 2 * math.pi + (seed % 3))
        shift_z = 0.01 * _noise(t * 0.15, seed + 99)
        
        if "Hips" not in offsets:
            offsets["Hips"] = {}
        h_rot = offsets["Hips"].get("rotation", (0.0, 0.0, 0.0))
        offsets["Hips"]["rotation"] = (h_rot[0], h_rot[1] + shift_z, h_rot[2] + sway)
        
        # Shift translation slightly to simulate Center of Mass shift over support foot
        h_loc = offsets["Hips"].get("location", (0.0, 0.0, 0.0))
        offsets["Hips"]["location"] = (h_loc[0] + sway * 0.4, h_loc[1], h_loc[2] - abs(sway) * 0.1)
        
    def _apply_locomotion_strides(self, offsets, t, seed, state, velocity) -> Dict[str, Any]:
        foot_locking = {
            "Foot.L": {"planted": True, "slide_offset": 0.0},
            "Foot.R": {"planted": True, "slide_offset": 0.0}
        }
        
        if state not in ("walk", "run"):
            # Fully planted foot locking for idles
            return foot_locking
            
        vx, vy, vz = velocity
        speed = math.sqrt(vx*vx + vy*vy)
        
        # Stride prediction: Cadence increases with speed
        freq = 1.8 + speed * 0.3
        phase = t * freq * 2.0 * math.pi
        
        # Cadence vertical bobbing
        vertical_bob = 0.025 * abs(math.sin(phase)) * (1.0 + speed * 0.2)
        hip_roll = 0.06 * math.sin(phase)
        hip_yaw = 0.04 * math.cos(phase)
        
        if "Hips" not in offsets:
            offsets["Hips"] = {}
        h_rot = offsets["Hips"].get("rotation", (0.0, 0.0, 0.0))
        offsets["Hips"]["rotation"] = (h_rot[0] + 0.02 * math.sin(phase), h_rot[1] + hip_yaw, h_rot[2] + hip_roll)
        
        h_loc = offsets["Hips"].get("location", (0.0, 0.0, 0.0))
        offsets["Hips"]["location"] = (h_loc[0], h_loc[1], h_loc[2] - vertical_bob)
        
        # Alternating foot plants
        left_plant = math.sin(phase) > 0.0
        foot_locking["Foot.L"]["planted"] = left_plant
        foot_locking["Foot.R"]["planted"] = not left_plant
        
        # Stride rotations
        leg_pitch_l = 0.3 * math.sin(phase)
        leg_pitch_r = -0.3 * math.sin(phase)
        
        offsets["UpperLeg.L"] = {"rotation": (leg_pitch_l, 0.0, 0.0)}
        offsets["UpperLeg.R"] = {"rotation": (leg_pitch_r, 0.0, 0.0)}
        offsets["LowerLeg.L"] = {"rotation": (max(0.0, -leg_pitch_l * 1.5), 0.0, 0.0)}
        offsets["LowerLeg.R"] = {"rotation": (max(0.0, -leg_pitch_r * 1.5), 0.0, 0.0)}
        
        return foot_locking
        
    def _apply_hand_relaxation(self, offsets, t, seed, state):
        curl = 0.4 if state == "idle" else (0.2 if state in ("walk", "run") else 0.1)
        curl_offset = 0.05 * _noise(t * 0.5, seed)
        
        # Finger curl joints
        for finger in ["Thumb", "Index", "Middle", "Ring", "Pinky"]:
            for suffix in [".L", ".R"]:
                offsets[f"{finger}_01{suffix}"] = {"rotation": (curl + curl_offset, 0.0, 0.0)}
                offsets[f"{finger}_02{suffix}"] = {"rotation": ((curl + curl_offset) * 0.8, 0.0, 0.0)}
                
        # Hand relaxation/wrist drift
        offsets["Hand.L"] = {"rotation": (0.0, 0.0, 0.02 * _noise(t, seed + 10))}
        offsets["Hand.R"] = {"rotation": (0.0, 0.0, -0.02 * _noise(t, seed + 11))}
        
    def _apply_reach_interaction(self, offsets, t, seed, state, target_loc, char_loc):
        if state != "reach" or not target_loc or not char_loc:
            return
            
        # Procedural reach targeting
        dx = target_loc[0] - char_loc[0]
        dy = target_loc[1] - char_loc[1]
        dz = target_loc[2] - char_loc[2]
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        if dist > 0.001:
            # Simple IK look-at target for arm bones
            reach_factor = _smoothstep(0.0, 1.0, min(t * 2.0, 1.0))
            yaw = math.atan2(dx, dy)
            pitch = -math.asin(dz / dist)
            
            offsets["UpperArm.R"] = {"rotation": (pitch * reach_factor, 0.0, yaw * reach_factor)}
            offsets["LowerArm.R"] = {"rotation": (0.2 * reach_factor, 0.0, 0.0)}
            offsets["Hand.R"] = {"rotation": (0.0, 0.0, -0.1 * reach_factor)}
            
    def _apply_head_stabilization(self, offsets, t, seed, state):
        # Compensate for hips/spine movement to keep the head steady and look straight
        h_rot = offsets.get("Hips", {}).get("rotation", (0.0, 0.0, 0.0))
        s_rot = offsets.get("Spine", {}).get("rotation", (0.0, 0.0, 0.0))
        
        stabilize_x = -(h_rot[0] + s_rot[0]) * 0.8
        stabilize_z = -(h_rot[2] + s_rot[2]) * 0.8
        
        # Natural head tracking micro-nods
        nod = 0.02 * _noise(t * 0.6, seed + 4)
        
        offsets["Head"] = {"rotation": (stabilize_x + nod, 0.0, stabilize_z)}
        offsets["Neck"] = {"rotation": (stabilize_x * 0.3, 0.0, stabilize_z * 0.3)}
        
    def _blend_offsets(self, prev, curr, weight):
        blended: Dict[str, Dict[str, Tuple[float, float, float]]] = {}
        all_keys = set(prev.keys()) | set(curr.keys())
        
        for k in all_keys:
            p_val = prev.get(k, {})
            c_val = curr.get(k, {})
            blended[k] = {}
            
            for transform in ["rotation", "location"]:
                p_t = p_val.get(transform, (0.0, 0.0, 0.0))
                c_t = c_val.get(transform, (0.0, 0.0, 0.0))
                
                blended[k][transform] = (
                    p_t[0] * (1.0 - weight) + c_t[0] * weight,
                    p_t[1] * (1.0 - weight) + c_t[1] * weight,
                    p_t[2] * (1.0 - weight) + c_t[2] * weight
                )
        return blended
