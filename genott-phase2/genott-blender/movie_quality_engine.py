import os
import subprocess
import json

def score_movie(filepath: str, scenes: list, transitions: list = None, threshold: int = 70) -> dict:
    """
    Evaluates the quality of a compiled movie and returns a score from 0-100.
    
    Metrics analyzed:
    1. Video integrity and playback (20 pts)
    2. Camera diversity (15 pts)
    3. Scene diversity (15 pts)
    4. Environment diversity (15 pts)
    5. Transition quality (15 pts)
    6. Continuity quality (10 pts)
    7. Character visibility & framing (10 pts)
    """
    metrics = {
        "integrity": 0,
        "camera_diversity": 0,
        "scene_diversity": 0,
        "environment_diversity": 0,
        "transition_quality": 0,
        "continuity": 0,
        "visibility": 0
    }
    reasons = []
    bad_scenes = []
    
    # 1. File & Stream Integrity (20 pts)
    if not os.path.exists(filepath):
        reasons.append("Compiled movie file does not exist.")
        return {
            "score": 0,
            "status": "rejected",
            "metrics": metrics,
            "reasons": reasons,
            "bad_scenes": list(range(len(scenes)))
        }
        
    actual_duration = 0
    has_video = False
    has_audio = False
    resolution = 0
    fps = 0
    
    try:
        cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams", filepath
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        data = json.loads(result.stdout)
        
        streams = data.get("streams", [])
        format_data = data.get("format", {})
        
        for s in streams:
            if s.get("codec_type") == "video":
                has_video = True
                resolution = int(s.get("height", 0))
                fr_str = s.get("r_frame_rate", "0/1").split('/')
                if len(fr_str) == 2 and int(fr_str[1]) > 0:
                    fps = int(fr_str[0]) / int(fr_str[1])
            elif s.get("codec_type") == "audio":
                has_audio = True
                
        actual_duration = float(format_data.get("duration", 0))
    except Exception as e:
        reasons.append(f"Ffprobe failed to parse video: {str(e)}")
        
    if has_video:
        metrics["integrity"] += 10
    else:
        reasons.append("No video stream found in compiled file.")
        
    if has_audio:
        metrics["integrity"] += 10
    else:
        reasons.append("No audio stream found in compiled file (missing dialogue/narration narration).")
        
    # 2. Camera Diversity (15 pts)
    # Count distinct camera presets and camera moves across all scenes
    shot_types = set()
    movements = set()
    for idx, scene in enumerate(scenes):
        shot = getattr(scene, "camera_shot", None) or getattr(scene, "camera_preset", None)
        move = getattr(scene, "camera_movement", None) or getattr(scene, "camera_move", None)
        
        # Check dictionary-like object if needed
        if isinstance(scene, dict):
            shot = scene.get("camera_shot") or scene.get("camera_preset")
            move = scene.get("camera_movement") or scene.get("camera_move")
            
        if shot:
            shot_types.add(shot)
        if move:
            movements.add(move)
            
    num_presets = len(shot_types)
    num_moves = len(movements)
    
    if num_presets >= 3:
        metrics["camera_diversity"] += 10
    elif num_presets >= 2:
        metrics["camera_diversity"] += 7
    elif num_presets >= 1:
        metrics["camera_diversity"] += 4
    else:
        reasons.append("No camera presets found in scene plans.")
        
    if num_moves >= 2:
        metrics["camera_diversity"] += 5
    elif num_moves >= 1:
        metrics["camera_diversity"] += 3
    else:
        reasons.append("No camera movements (static cameras only).")
        
    # 3. Scene Diversity (15 pts)
    num_scenes = len(scenes)
    if num_scenes >= 3:
        metrics["scene_diversity"] += 15
    elif num_scenes == 2:
        metrics["scene_diversity"] += 10
    elif num_scenes == 1:
        metrics["scene_diversity"] += 5
        reasons.append("Movie has only 1 scene (low scene diversity).")
        
    # 4. Environment Diversity (15 pts)
    environments = set()
    for scene in scenes:
        env = getattr(scene, "location", None) or getattr(scene, "environment", None)
        if isinstance(scene, dict):
            env = scene.get("location") or scene.get("environment")
        if env:
            environments.add(env.lower().strip())
            
    num_envs = len(environments)
    if num_envs >= 2:
        metrics["environment_diversity"] += 15
    elif num_envs == 1:
        metrics["environment_diversity"] += 8
        reasons.append("Single environment used throughout the movie.")
    else:
        reasons.append("No environment/location specified in scene plans.")
        
    # 5. Transition Quality (15 pts)
    if num_scenes <= 1:
        # Single-scene movies need no transitions
        metrics["transition_quality"] += 15
    else:
        trans_list = transitions or []
        # Check transition count
        valid_transitions = [t for t in trans_list if t in ("fade", "crossfade", "wipe", "cut")]
        if len(valid_transitions) == num_scenes - 1:
            metrics["transition_quality"] += 15
        elif len(valid_transitions) > 0:
            metrics["transition_quality"] += 10
            reasons.append("Some transitions between scenes are missing or invalid.")
        else:
            metrics["transition_quality"] += 5
            reasons.append("No valid transitions configured between scenes (hard cuts only).")
            
    # 6. Continuity Quality (10 pts)
    # Checks character profiles and locations across scene transitions
    continuity_score = 10
    for i in range(num_scenes - 1):
        s1 = scenes[i]
        s2 = scenes[i+1]
        
        char1 = getattr(s1, "character_name", None)
        char2 = getattr(s2, "character_name", None)
        loc1 = getattr(s1, "location", None)
        loc2 = getattr(s2, "location", None)
        
        if isinstance(s1, dict):
            char1 = s1.get("character_name")
            loc1 = s1.get("location")
        if isinstance(s2, dict):
            char2 = s2.get("character_name")
            loc2 = s2.get("location")
            
        # If the character transitions from scene to scene, make sure it is valid
        if char1 and char2 and char1 != char2:
            # Multi-character is fine, but if it is the same character name with spelling variations:
            if char1.lower().strip()[:4] == char2.lower().strip()[:4] and char1 != char2:
                continuity_score -= 3
                reasons.append(f"Character continuity warning: spelling difference between '{char1}' and '{char2}'")
                bad_scenes.append(i+1)
                
        # Jarring jump cut check: same location, same action, but no transition and short scene duration
        if loc1 == loc2 and getattr(s1, "action", "") == getattr(s2, "action", ""):
            action = getattr(s1, "action", "")
            if isinstance(s1, dict):
                action = s1.get("action", "")
            if action in ("walk", "run", "jump") and (transitions and transitions[i] == "cut"):
                continuity_score -= 2
                reasons.append(f"Jarring jump cut detected in scene {i+2} (same character, location, and action without transition).")
                bad_scenes.append(i+1)
                
    metrics["continuity"] = max(0, continuity_score)
    
    # 7. Character Visibility & Framing (10 pts)
    # Appropriate camera shots for the actions. E.g. Dialogue -> Close up or Medium. Run/Walk -> Wide or Tracking.
    visibility_score = 10
    for idx, scene in enumerate(scenes):
        action = getattr(scene, "action", None)
        shot = getattr(scene, "camera_shot", None) or getattr(scene, "camera_preset", None)
        has_dialogue = getattr(scene, "dialogue", None) is not None
        
        if isinstance(scene, dict):
            action = scene.get("action")
            shot = scene.get("camera_shot") or scene.get("camera_preset")
            has_dialogue = scene.get("dialogue") is not None
            
        scene_penalty = 0
        if has_dialogue and shot in ("establishing shot", "wide shot"):
            scene_penalty += 3
            reasons.append(f"Scene {idx+1}: Speaking character is too far from camera (Shot: {shot} with dialogue).")
        if action in ("run", "walk", "jump") and shot in ("close up", "over shoulder"):
            scene_penalty += 3
            reasons.append(f"Scene {idx+1}: Fast moving character is too close to camera (Shot: {shot} with movement).")
            
        if scene_penalty > 0:
            visibility_score -= scene_penalty
            if idx not in bad_scenes:
                bad_scenes.append(idx)
                
    metrics["visibility"] = max(0, visibility_score)
    
    # Calculate Total Score
    total_score = sum(metrics.values())
    status = "passed" if total_score >= threshold else "rejected"
    
    return {
        "score": int(total_score),
        "status": status,
        "metrics": metrics,
        "reasons": reasons,
        "bad_scenes": sorted(list(set(bad_scenes)))
    }
