#!/usr/bin/env python3
"""
cinematic_sequencer.py — Cinematic Sequencer.
Converts a scene storyboard/plan into a detailed shot timeline and camera timeline.
Flow: Scene -> Shot Plan -> Camera Timeline -> Render
"""
import math
from typing import Dict, Any, List
from ai.storyboard.models import ScenePlan

def generate_shot_plan(scene: ScenePlan) -> List[Dict[str, Any]]:
    """
    Splits a single scene into multiple sub-shots based on duration, action, and mood.
    """
    duration = scene.duration or 4.0
    action = (scene.action or "idle").lower()
    mood = (scene.mood or "neutral").lower()
    
    shots = []
    
    # Segment rules
    if duration >= 5.0:
        # Long shot: split into 3 segments
        d1 = 1.5
        d2 = 2.0
        d3 = max(1.0, duration - d1 - d2)
        
        if "talk" in action:
            shots.append({"camera_shot": "over_shoulder", "camera_movement": "static", "duration": d1})
            shots.append({"camera_shot": "close_up", "camera_movement": "static", "duration": d2})
            shots.append({"camera_shot": "medium_shot", "camera_movement": "static", "duration": d3})
        elif "walk" in action or "run" in action:
            shots.append({"camera_shot": "establishing_shot", "camera_movement": "static", "duration": d1})
            shots.append({"camera_shot": "tracking_shot", "camera_movement": "tracking", "duration": d2})
            shots.append({"camera_shot": "wide_shot", "camera_movement": "tracking", "duration": d3})
        elif "attack" in action:
            shots.append({"camera_shot": "low_angle", "camera_movement": "static", "duration": d1})
            shots.append({"camera_shot": "orbit_shot", "camera_movement": "orbit", "duration": d2})
            shots.append({"camera_shot": "close_up", "camera_movement": "static", "duration": d3})
        else:
            shots.append({"camera_shot": "wide_shot", "camera_movement": "static", "duration": d1})
            shots.append({"camera_shot": "medium_shot", "camera_movement": "static", "duration": d2})
            shots.append({"camera_shot": "high_angle", "camera_movement": "static", "duration": d3})
    elif duration >= 3.0:
        # Medium shot: split into 2 segments
        d1 = 1.5
        d2 = max(1.0, duration - d1)
        
        if "talk" in action:
            shots.append({"camera_shot": "over_shoulder", "camera_movement": "static", "duration": d1})
            shots.append({"camera_shot": "close_up", "camera_movement": "static", "duration": d2})
        elif "walk" in action or "run" in action:
            shots.append({"camera_shot": "tracking_shot", "camera_movement": "tracking", "duration": d1})
            shots.append({"camera_shot": "wide_shot", "camera_movement": "tracking", "duration": d2})
        elif "attack" in action:
            shots.append({"camera_shot": "low_angle", "camera_movement": "static", "duration": d1})
            shots.append({"camera_shot": "orbit_shot", "camera_movement": "orbit", "duration": d2})
        else:
            shots.append({"camera_shot": "wide_shot", "camera_movement": "static", "duration": d1})
            shots.append({"camera_shot": "medium_shot", "camera_movement": "static", "duration": d2})
    else:
        # Short shot: single segment
        shots.append({
            "camera_shot": scene.camera_shot or "wide_shot",
            "camera_movement": "tracking" if "walk" in action or "run" in action else "static",
            "duration": duration
        })
        
    return shots

def sequence_scene(plan: ScenePlan, start_location: List[float], action_name: str, fps: int = 24) -> List[Dict[str, Any]]:
    """
    Converts a scene plan into a frame-by-frame list of camera keyframes with pre-computed coordinates.
    """
    duration = plan.duration or 4.0
    total_frames = int(duration * fps)
    
    # Generate shot plan
    shot_plan = generate_shot_plan(plan)
    
    # Calculate locomotion delta
    delta_loc = [0.0, 0.0, 0.0]
    aname = action_name.lower()
    if "walk" in aname:
        delta_loc = [0.0, -1.0 * duration, 0.0]
    elif "run" in aname:
        delta_loc = [0.0, -3.0 * duration, 0.0]
    elif "jump" in aname:
        delta_loc = [0.0, -0.5 * duration, 0.0]
        
    shot_presets = {
        "wide_shot": ((0, -6.0, 2.2), (math.radians(75), 0, 0)),
        "medium_shot": ((0, -3.0, 1.8), (math.radians(80), 0, 0)),
        "close_up": ((0, -1.2, 1.6), (math.radians(90), 0, 0)),
        "establishing_shot": ((0, -12.0, 6.0), (math.radians(65), 0, 0)),
        "over_shoulder": ((0.5, 1.0, 1.6), (math.radians(85), 0, math.radians(180))),
        "tracking_shot": ((2.0, -3.5, 1.5), (math.radians(80), 0, math.radians(-25))),
        "orbit_shot": ((-3.0, -3.0, 2.0), (math.radians(80), 0, math.radians(-45))),
        "low_angle": ((0, -2.5, 0.5), (math.radians(100), 0, 0)),
        "high_angle": ((0, -3.5, 3.5), (math.radians(55), 0, 0))
    }
    
    def get_shot_preset(name):
        name_clean = str(name).lower().strip().replace(" ", "_")
        for k, v in shot_presets.items():
            if k in name_clean or name_clean in k:
                return v
        return shot_presets["wide_shot"]
        
    timeline = []
    current_frame = 1
    
    for shot in shot_plan:
        shot_dur = shot["duration"]
        shot_frames = int(shot_dur * fps)
        
        start_f = current_frame
        end_f = min(total_frames, current_frame + shot_frames - 1)
        
        offset, rot = get_shot_preset(shot["camera_shot"])
        move = shot.get("camera_movement", "static")
        
        # Precompute character position at start of this shot segment (for static/panning shots)
        factor_start = (start_f - 1) / max(1, total_frames - 1)
        char_pos_start = [
            start_location[0] + delta_loc[0] * factor_start,
            start_location[1] + delta_loc[1] * factor_start,
            start_location[2] + delta_loc[2] * factor_start
        ]
        
        for f in range(start_f, end_f + 1):
            factor = (f - 1) / max(1, total_frames - 1)
            char_pos = [
                start_location[0] + delta_loc[0] * factor,
                start_location[1] + delta_loc[1] * factor,
                start_location[2] + delta_loc[2] * factor
            ]
            
            if move == "tracking":
                cam_loc = [char_pos[0] + offset[0], char_pos[1] + offset[1], char_pos[2] + offset[2]]
                cam_rot = rot
            elif move == "orbit":
                # Rotate offset around character over the course of the shot segment
                progress = (f - start_f) / max(1, end_f - start_f)
                angle = progress * math.radians(90) - math.radians(45) # sweep 90 degrees
                
                ox = offset[0] * math.cos(angle) - offset[1] * math.sin(angle)
                oy = offset[0] * math.sin(angle) + offset[1] * math.cos(angle)
                cam_loc = [char_pos[0] + ox, char_pos[1] + oy, char_pos[2] + offset[2]]
                cam_rot = (rot[0], rot[1], rot[2] + angle)
            elif move == "pan":
                progress = (f - start_f) / max(1, end_f - start_f)
                pan_angle = (progress - 0.5) * math.radians(30) # sweep 30 degrees
                cam_loc = [char_pos_start[0] + offset[0], char_pos_start[1] + offset[1], char_pos_start[2] + offset[2]]
                cam_rot = (rot[0], rot[1], rot[2] + pan_angle)
            else: # static
                cam_loc = [char_pos_start[0] + offset[0], char_pos_start[1] + offset[1], char_pos_start[2] + offset[2]]
                cam_rot = rot
                
            timeline.append({
                "frame": f,
                "location": cam_loc,
                "rotation": cam_rot
            })
            
        current_frame = end_f + 1
        if current_frame > total_frames:
            break
            
    return timeline
