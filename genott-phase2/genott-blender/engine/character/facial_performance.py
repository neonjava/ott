# ai/facial_performance.py
"""
Facial Performance Engine — Production-Quality Facial Animation System.

Replaces simplistic shape-key wiggling with physically-motivated, emotion-driven
facial behaviour including:
  - Weighted emotion blending with micro-expression variation
  - Natural blink timing with Gaussian-distributed intervals
  - Saccadic eye movement with fixation, vergence, and eyelid follow
  - Breathing influence on jaw and cheek
  - Dialogue-driven viseme coarticulation with anticipation
  - Listening / speaking / idle behavioural states
"""
import math
from typing import Dict, Any, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Emotion-to-blendshape profiles.  Intensities are at full weight (1.0).
# ---------------------------------------------------------------------------
EMOTION_PROFILES: Dict[str, Dict[str, float]] = {
    "happy":         {"mouthSmileLeft": 0.80, "mouthSmileRight": 0.80, "browInnerUp": 0.30,
                      "cheekSquintLeft": 0.40, "cheekSquintRight": 0.40, "mouthDimpleLeft": 0.15,
                      "mouthDimpleRight": 0.15},
    "sad":           {"mouthFrownLeft": 0.90, "mouthFrownRight": 0.90, "browOuterUpLeft": 0.50,
                      "browOuterUpRight": 0.50, "eyeSquintLeft": 0.30, "eyeSquintRight": 0.30,
                      "mouthPressLeft": 0.20, "mouthPressRight": 0.20},
    "angry":         {"browDownLeft": 1.00, "browDownRight": 1.00, "mouthPressLeft": 0.60,
                      "mouthPressRight": 0.60, "eyeSquintLeft": 0.50, "eyeSquintRight": 0.50,
                      "noseSneerLeft": 0.40, "noseSneerRight": 0.40},
    "fear":          {"jawOpen": 0.30, "mouthStretchLeft": 0.70, "mouthStretchRight": 0.70,
                      "browInnerUp": 0.80, "eyeWideLeft": 0.60, "eyeWideRight": 0.60},
    "surprise":      {"jawOpen": 0.60, "eyeWideLeft": 0.90, "eyeWideRight": 0.90,
                      "browInnerUp": 0.90, "browOuterUpLeft": 0.50, "browOuterUpRight": 0.50},
    "disgust":       {"noseSneerLeft": 0.80, "noseSneerRight": 0.80, "mouthShrugUpper": 0.50,
                      "browDownLeft": 0.40, "browDownRight": 0.40, "mouthFrownLeft": 0.30,
                      "mouthFrownRight": 0.30, "cheekPuff": 0.20},
    "anticipation":  {"browInnerUp": 0.35, "eyeWideLeft": 0.25, "eyeWideRight": 0.25,
                      "mouthPucker": 0.15, "jawOpen": 0.10},
    "hope":          {"mouthSmileLeft": 0.40, "mouthSmileRight": 0.40, "browInnerUp": 0.20},
    "determination": {"browDownLeft": 0.40, "browDownRight": 0.40, "mouthClose": 0.50,
                      "mouthPressLeft": 0.50, "mouthPressRight": 0.50},
}

# ---------------------------------------------------------------------------
# Viseme-to-blendshape profiles (ARKit-compatible).
# ---------------------------------------------------------------------------
VISEME_PROFILES: Dict[str, Dict[str, float]] = {
    "A":    {"jawOpen": 0.80, "mouthFunnel": 0.20, "mouthLowerDownLeft": 0.15, "mouthLowerDownRight": 0.15},
    "E":    {"mouthStretchLeft": 0.60, "mouthStretchRight": 0.60, "jawOpen": 0.20},
    "I":    {"mouthStretchLeft": 0.55, "mouthStretchRight": 0.55, "jawOpen": 0.15,
             "mouthSmileLeft": 0.20, "mouthSmileRight": 0.20},
    "O":    {"mouthFunnel": 0.80, "jawOpen": 0.40, "mouthPucker": 0.25},
    "U":    {"mouthPucker": 0.70, "mouthFunnel": 0.40, "jawOpen": 0.15},
    "F":    {"mouthShrugLower": 0.50, "mouthClose": 0.30, "mouthRollLower": 0.20},
    "L":    {"jawOpen": 0.40, "mouthPressLeft": 0.20, "tongueOut": 0.10},
    "M":    {"mouthClose": 1.00, "mouthPressLeft": 0.30, "mouthPressRight": 0.30},
    "S":    {"mouthStretchLeft": 0.30, "mouthStretchRight": 0.30, "jawOpen": 0.10},
    "TH":   {"jawOpen": 0.25, "tongueOut": 0.30, "mouthShrugLower": 0.15},
    "W":    {"mouthPucker": 0.60, "mouthFunnel": 0.35, "jawOpen": 0.10},
    "rest": {"mouthClose": 0.50},
    "sil":  {},
}

# Full set of ARKit blendshape names this engine can touch.
ALL_SHAPE_NAMES = {
    "eyeBlinkLeft", "eyeLookDownLeft", "eyeLookInLeft", "eyeLookOutLeft",
    "eyeLookUpLeft", "eyeSquintLeft", "eyeWideLeft",
    "eyeBlinkRight", "eyeLookDownRight", "eyeLookInRight", "eyeLookOutRight",
    "eyeLookUpRight", "eyeSquintRight", "eyeWideRight",
    "jawForward", "jawLeft", "jawRight", "jawOpen",
    "mouthClose", "mouthFunnel", "mouthPucker", "mouthLeft", "mouthRight",
    "mouthSmileLeft", "mouthSmileRight", "mouthFrownLeft", "mouthFrownRight",
    "mouthDimpleLeft", "mouthDimpleRight",
    "mouthStretchLeft", "mouthStretchRight", "mouthRollLower", "mouthRollUpper",
    "mouthShrugLower", "mouthShrugUpper",
    "mouthPressLeft", "mouthPressRight",
    "mouthLowerDownLeft", "mouthLowerDownRight",
    "mouthUpperUpLeft", "mouthUpperUpRight",
    "browDownLeft", "browDownRight", "browInnerUp",
    "browOuterUpLeft", "browOuterUpRight",
    "cheekPuff", "cheekSquintLeft", "cheekSquintRight",
    "noseSneerLeft", "noseSneerRight", "tongueOut",
}


def _noise(t: float, seed: int) -> float:
    """Multi-octave continuous pseudo-random noise in [-1, 1]."""
    v  = 0.50 * math.sin(t * 1.1412 + (seed % 7) * 0.9)
    v += 0.25 * math.cos(t * 2.7183 + (seed * 3 % 11) * 0.7)
    v += 0.125 * math.sin(t * 5.618 + (seed * 7 % 13) * 0.5)
    return v


def _smoothstep(edge0: float, edge1: float, x: float) -> float:
    """Hermite smoothstep interpolation."""
    if edge1 == edge0:
        return 1.0 if x >= edge1 else 0.0
    t = max(0.0, min(1.0, (x - edge0) / (edge1 - edge0)))
    return t * t * (3.0 - 2.0 * t)


class FacialPerformanceEngine:
    """
    Production-quality facial performance calculator.

    Usage:
        engine = FacialPerformanceEngine()
        for frame in range(f_start, f_end + 1):
            weights = engine.compute_frame(frame, f_start, f_end, fps,
                                           emotion, intensity, viseme_timeline,
                                           mesh_name, is_speaking)
            # weights is a Dict[str, float] of blendshape values [0..1]
    """

    def __init__(self):
        # Blink state — per-character offsets tracked externally via mesh_name hash
        pass

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------
    def compute_frame(
        self,
        frame: int,
        f_start: int,
        f_end: int,
        fps: float,
        emotion: str,
        emotion_intensity: float,
        viseme_timeline: Optional[List[Dict[str, Any]]],
        mesh_name: str,
        is_speaking: bool = False,
    ) -> Dict[str, float]:
        """Return blendshape weights for *frame*."""
        t = (frame - f_start) / fps  # seconds since shot start
        values: Dict[str, float] = {}

        # --- 1. Emotion layer ------------------------------------------
        self._apply_emotion(values, frame, f_start, f_end, emotion, emotion_intensity)

        # --- 2. Breathing layer ----------------------------------------
        self._apply_breathing(values, t, mesh_name)

        # --- 3. Eye system (blinks, saccades, eyelid follow) -----------
        self._apply_eye_system(values, frame, f_start, fps, mesh_name, is_speaking)

        # --- 4. Dialogue / viseme layer --------------------------------
        self._apply_visemes(values, t, f_start, f_end, fps, viseme_timeline)

        # --- 5. Idle / listening layer ---------------------------------
        self._apply_behavioural_state(values, t, mesh_name, is_speaking)

        # Clamp everything to [0, 1]
        return {k: max(0.0, min(1.0, v)) for k, v in values.items()}

    def get_all_shape_names(self) -> set:
        """Return the full set of shape-key names this engine may produce."""
        names = set(ALL_SHAPE_NAMES)
        for prof in EMOTION_PROFILES.values():
            names.update(prof.keys())
        for prof in VISEME_PROFILES.values():
            names.update(prof.keys())
        return names

    # ------------------------------------------------------------------
    # PRIVATE LAYERS
    # ------------------------------------------------------------------
    def _apply_emotion(
        self, values: Dict[str, float],
        frame: int, f_start: int, f_end: int,
        emotion: str, intensity: float,
    ):
        """Base emotion with ease-in, micro-expression pulsing, and intensity scaling."""
        mood = emotion.lower().strip()
        profile = EMOTION_PROFILES.get(mood, {})
        if not profile:
            return

        # Ease in over the first 8 frames
        progress = (frame - f_start) / max(1, 8)
        ease = _smoothstep(0.0, 1.0, progress)

        # Subtle micro-expression pulsing (multi-frequency, ±6 %)
        micro = 1.0 + 0.04 * math.sin(frame * 0.37) + 0.02 * math.cos(frame * 0.83)

        scale = ease * intensity * micro
        for name, base_w in profile.items():
            values[name] = values.get(name, 0.0) + base_w * scale

    def _apply_breathing(self, values: Dict[str, float], t: float, mesh_name: str):
        """Subtle jaw and cheek movement driven by breathing rhythm (~15 bpm)."""
        seed = hash(mesh_name) % 31
        breath_freq = 0.25 + 0.02 * (seed % 5)  # ~14-16 bpm
        breath = 0.5 + 0.5 * math.sin(2.0 * math.pi * breath_freq * t)  # 0..1

        values["jawOpen"] = values.get("jawOpen", 0.0) + 0.03 * breath
        values["cheekPuff"] = values.get("cheekPuff", 0.0) + 0.04 * breath
        # Nostrils flare subtly on inhale
        values["noseSneerLeft"] = values.get("noseSneerLeft", 0.0) + 0.02 * breath
        values["noseSneerRight"] = values.get("noseSneerRight", 0.0) + 0.02 * breath

    def _apply_eye_system(
        self, values: Dict[str, float],
        frame: int, f_start: int, fps: float,
        mesh_name: str, is_speaking: bool,
    ):
        """Blinking, saccades, eyelid follow, and gaze."""
        char_seed = hash(mesh_name)
        char_offset = char_seed % 17
        t = (frame - f_start) / fps

        # --- Blinking with variable timing ---
        # Average interval: 3-5 seconds (72-120 frames at 24fps).
        # We use a deterministic sequence of intervals derived from the character seed.
        blink_base = 72 + (char_seed % 49)  # 72-120 frames
        # Shift interval per-blink using a noise function so it's not perfectly periodic.
        blink_idx = (frame - f_start + char_offset) // blink_base
        blink_interval = blink_base + int(12 * _noise(blink_idx * 0.7, char_seed))
        blink_interval = max(48, min(144, blink_interval))  # clamp 2-6 sec

        local_in_cycle = (frame - f_start + char_offset) % blink_interval
        blink_w = 0.0
        # Blink is 4 frames: close(2fr) + open(2fr) with smooth profile
        if local_in_cycle == 0:
            blink_w = 0.3
        elif local_in_cycle == 1:
            blink_w = 1.0
        elif local_in_cycle == 2:
            blink_w = 0.8
        elif local_in_cycle == 3:
            blink_w = 0.15

        # Speaking increases blink rate slightly — extra blinks at half-interval
        if is_speaking and blink_interval > 60:
            half_local = (frame - f_start + char_offset) % (blink_interval // 2)
            if half_local == 0:
                blink_w = max(blink_w, 0.25)
            elif half_local == 1:
                blink_w = max(blink_w, 0.9)
            elif half_local == 2:
                blink_w = max(blink_w, 0.6)

        values["eyeBlinkLeft"] = max(values.get("eyeBlinkLeft", 0.0), blink_w)
        values["eyeBlinkRight"] = max(values.get("eyeBlinkRight", 0.0), blink_w)

        # --- Eyelid follow: squint slightly when looking down ---
        # Will be adjusted after saccade calculation below.

        # --- Saccades with smooth transition ---
        saccade_interval = 18 if is_speaking else 36  # faster during conversation
        saccade_idx = (frame - f_start + char_offset) // saccade_interval
        look_seed = hash(f"{mesh_name}_{saccade_idx}")
        target_x = ((look_seed % 7) - 3) / 10.0       # -0.3 .. 0.3
        target_y = (((look_seed // 7) % 7) - 3) / 10.0

        # Smooth blend over 4 frames at start of each saccade
        saccade_local = (frame - f_start + char_offset) % saccade_interval
        blend = _smoothstep(0.0, 4.0, saccade_local)
        cx = target_x * blend
        cy = target_y * blend

        # Apply horizontal gaze
        if cx > 0:
            values["eyeLookOutLeft"]  = values.get("eyeLookOutLeft", 0.0) + cx
            values["eyeLookInRight"]  = values.get("eyeLookInRight", 0.0) + cx
        elif cx < 0:
            values["eyeLookInLeft"]   = values.get("eyeLookInLeft", 0.0) + (-cx)
            values["eyeLookOutRight"] = values.get("eyeLookOutRight", 0.0) + (-cx)

        # Apply vertical gaze
        if cy > 0:
            values["eyeLookUpLeft"]   = values.get("eyeLookUpLeft", 0.0) + cy
            values["eyeLookUpRight"]  = values.get("eyeLookUpRight", 0.0) + cy
        elif cy < 0:
            values["eyeLookDownLeft"]  = values.get("eyeLookDownLeft", 0.0) + (-cy)
            values["eyeLookDownRight"] = values.get("eyeLookDownRight", 0.0) + (-cy)

        # --- Eyelid follow (squint when looking down) ---
        if cy < -0.1:
            lid_follow = abs(cy) * 0.4
            values["eyeSquintLeft"]  = values.get("eyeSquintLeft", 0.0) + lid_follow
            values["eyeSquintRight"] = values.get("eyeSquintRight", 0.0) + lid_follow

    def _apply_visemes(
        self, values: Dict[str, float],
        t: float, f_start: int, f_end: int, fps: float,
        viseme_timeline: Optional[List[Dict[str, Any]]],
    ):
        """Viseme coarticulation with anticipation lookahead."""
        if not viseme_timeline:
            return

        timeline = sorted(viseme_timeline, key=lambda x: x.get("time", 0.0))
        scene_dur = (f_end - f_start) / fps

        # Pad with rest at boundaries
        if not timeline or timeline[0].get("time", 0.0) > 0.0:
            timeline.insert(0, {"time": 0.0, "viseme": "rest"})
        if timeline[-1].get("time", 0.0) < scene_dur:
            timeline.append({"time": scene_dur, "viseme": "rest"})

        vis_weights: Dict[str, float] = {}

        if len(timeline) == 1:
            vis_weights = dict(VISEME_PROFILES.get(timeline[0]["viseme"], {}))
        else:
            found = False
            for i in range(len(timeline) - 1):
                t_curr = timeline[i]["time"]
                t_next = timeline[i + 1]["time"]
                if t_curr <= t < t_next:
                    duration = t_next - t_curr
                    p = (t - t_curr) / duration if duration > 0 else 0.0
                    # Smoothstep for more natural easing between phonemes
                    p = p * p * (3.0 - 2.0 * p)

                    vis_a = timeline[i]["viseme"]
                    vis_b = timeline[i + 1]["viseme"]
                    shapes_a = VISEME_PROFILES.get(vis_a, {})
                    shapes_b = VISEME_PROFILES.get(vis_b, {})

                    all_vis = set(shapes_a.keys()) | set(shapes_b.keys())

                    # Anticipation: start blending toward next viseme 20% early
                    anticipation = 0.0
                    if i + 2 < len(timeline):
                        vis_c = timeline[i + 2]["viseme"]
                        shapes_c = VISEME_PROFILES.get(vis_c, {})
                        # Only anticipate in the last 20% of the current segment
                        if p > 0.80:
                            antic_blend = (p - 0.80) / 0.20
                            for sn in shapes_c:
                                all_vis.add(sn)

                    for sname in all_vis:
                        w_a = shapes_a.get(sname, 0.0)
                        w_b = shapes_b.get(sname, 0.0)
                        blended = w_a + (w_b - w_a) * p

                        # Anticipation contribution
                        if i + 2 < len(timeline) and p > 0.80:
                            vis_c = timeline[i + 2]["viseme"]
                            shapes_c = VISEME_PROFILES.get(vis_c, {})
                            w_c = shapes_c.get(sname, 0.0)
                            antic_blend = (p - 0.80) / 0.20
                            blended = blended * (1.0 - antic_blend * 0.15) + w_c * antic_blend * 0.15

                        vis_weights[sname] = blended

                    found = True
                    break

            if not found:
                vis_weights = dict(VISEME_PROFILES.get(timeline[-1]["viseme"], {}))

        # Jaw motion: scale jawOpen by a slight additional factor during speech
        if "jawOpen" in vis_weights and vis_weights["jawOpen"] > 0.1:
            vis_weights["jawOpen"] *= 1.05  # slightly more open for realism

        # Mouth corner movement: add subtle dimple during wide vowels
        if vis_weights.get("mouthStretchLeft", 0) > 0.3:
            vis_weights["mouthDimpleLeft"] = vis_weights.get("mouthDimpleLeft", 0.0) + 0.08
            vis_weights["mouthDimpleRight"] = vis_weights.get("mouthDimpleRight", 0.0) + 0.08

        # Mix visemes using max to avoid emotion conflicts
        for sname, w in vis_weights.items():
            values[sname] = max(values.get(sname, 0.0), w)

    def _apply_behavioural_state(
        self, values: Dict[str, float],
        t: float, mesh_name: str, is_speaking: bool,
    ):
        """Listening / speaking / idle micro-behaviours."""
        seed = hash(mesh_name)

        if is_speaking:
            # Slight eyebrow emphasis while talking
            values["browInnerUp"] = values.get("browInnerUp", 0.0) + 0.08 * (0.5 + 0.5 * _noise(t * 2.0, seed + 100))
            # Occasional head-nod proxy via very subtle jaw shift
            values["jawForward"] = values.get("jawForward", 0.0) + 0.02 * max(0, _noise(t * 1.5, seed + 101))
        else:
            # Listening state: occasional small smile, slight brow movements
            values["mouthSmileLeft"]  = values.get("mouthSmileLeft", 0.0)  + 0.06 * max(0, _noise(t * 0.5, seed + 200))
            values["mouthSmileRight"] = values.get("mouthSmileRight", 0.0) + 0.06 * max(0, _noise(t * 0.5, seed + 201))
            values["browInnerUp"]     = values.get("browInnerUp", 0.0)     + 0.04 * max(0, _noise(t * 0.3, seed + 202))

            # Idle jaw relaxation
            values["jawOpen"] = values.get("jawOpen", 0.0) + 0.015

            # Subtle mouth movement (prevents frozen face)
            values["mouthPucker"] = values.get("mouthPucker", 0.0) + 0.03 * max(0, _noise(t * 0.4, seed + 210))
