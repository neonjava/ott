#!/usr/bin/env python3
"""
director_ai.py — Director AI Rules Engine.
Analyzes storyboards and makes smart cinematic choices: shots, camera movements, transitions, and pacing.
"""
from typing import Dict, Any, List

def direct_storyboard(storyboard: Dict[str, Any]) -> Dict[str, Any]:
    """
    Directs a raw storyboard by assigning camera shots, movements, pacing, and transitions.
    """
    scenes = storyboard.get("scenes", [])
    num_scenes = len(scenes)
    directed_scenes = []
    
    # Track the previous scene's location and mood for transitions
    prev_loc = None
    prev_mood = None
    
    for idx, scene in enumerate(scenes):
        directed = scene.copy()
        
        action = scene.get("action", "idle").lower()
        mood = scene.get("mood", "neutral").lower()
        location = scene.get("location", "environment").lower()
        
        # 1. Determine Camera Shot
        camera_shot = "wide_shot"
        if idx == 0:
            # First shot is establishing or wide shot
            camera_shot = "establishing_shot" if "forest" in location or "castle" in location or "kingdom" in location else "wide_shot"
        elif "talk" in action or "say" in action or "speak" in action:
            # Dialogue focus
            camera_shot = "close_up" if idx % 2 == 0 else "over_shoulder"
        elif "attack" in action or "strike" in action:
            # Combat focus
            camera_shot = "low_angle" if mood == "epic" else "orbit_shot"
        elif "wave" in action or "greet" in action:
            camera_shot = "medium_shot"
        elif "duck" in action or "crouch" in action:
            camera_shot = "low_angle"
        elif "run" in action or "walk" in action:
            camera_shot = "tracking_shot"
        else:
            # Fallback based on mood
            if mood == "epic":
                camera_shot = "low_angle"
            elif mood == "tense":
                camera_shot = "high_angle"
            elif mood == "sad":
                camera_shot = "medium_shot"
            else:
                camera_shot = "wide_shot"
                
        # 2. Determine Camera Movement
        camera_movement = "static"
        if "walk" in action or "run" in action:
            camera_movement = "tracking"
        elif "attack" in action:
            camera_movement = "orbit"
        elif "wave" in action:
            camera_movement = "pan"
        elif "discover" in action:
            camera_movement = "tilt"
        elif mood == "epic":
            camera_movement = "zoom"
            
        # 3. Determine Pacing & Duration
        pacing = "standard"
        duration = 4.0
        
        if "attack" in action or "run" in action:
            pacing = "fast"
            duration = 3.0
        elif "talk" in action or mood in ("sad", "mysterious"):
            pacing = "slow"
            duration = 5.5
        else:
            pacing = "standard"
            duration = 4.5
            
        # 4. Determine Transition from previous scene
        transition = "cut"
        if idx > 0:
            if location != prev_loc:
                transition = "fade"
            elif mood != prev_mood and mood in ("mysterious", "epic", "tense"):
                transition = "fade"
            elif "attack" in action and "attack" not in scenes[idx - 1].get("action", ""):
                transition = "white"
                
        # Apply overrides
        directed["camera_shot"] = camera_shot
        directed["camera_movement"] = camera_movement
        directed["pacing"] = pacing
        directed["duration"] = duration
        
        # If we have a previous scene, record the transition into this scene.
        # Otherwise, the transition is from start (default: cut).
        directed["transition"] = transition
        
        directed_scenes.append(directed)
        
        prev_loc = location
        prev_mood = mood

    # Reconstruct transitions list for the assembler
    transitions = [s["transition"] for s in directed_scenes[1:]] if len(directed_scenes) > 1 else []
    
    return {
        "scenes": directed_scenes,
        "transitions": transitions
    }
