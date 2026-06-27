# ai/timeline_editing.py
import json
import os
from typing import Dict, Any, List, Optional

class TimelineEditingAgent:
    """
    Subsystem: Timeline Editing
    Implements a multi-track non-linear editor layout representing cuts, audio clips, and camera keys.
    Allows targeting individual shots or scenes for updates.
    """
    def __init__(self, timeline_path: str = "project_timeline.json"):
        self.timeline_path = timeline_path
        self.timeline = {"scenes": [], "tracks": {"video": [], "audio": []}}

    def load_timeline(self):
        if os.path.exists(self.timeline_path):
            try:
                with open(self.timeline_path, "r") as f:
                    self.timeline = json.load(f)
            except Exception:
                pass

    def save_timeline(self):
        try:
            with open(self.timeline_path, "w") as f:
                json.dump(self.timeline, f, indent=4)
        except Exception:
            pass

    def create_clip(self, track_name: str, clip_id: str, start: float, duration: float, source: str) -> Dict[str, Any]:
        """Creates a clip node on a target track layer."""
        clip = {
            "id": clip_id,
            "start": start,
            "duration": duration,
            "source": source,
            "muted": False
        }
        if track_name not in self.timeline["tracks"]:
            self.timeline["tracks"][track_name] = []
        self.timeline["tracks"][track_name].append(clip)
        self.save_timeline()
        return clip

    def regenerate_shot_segment(self, scene_idx: int, shot_idx: int, new_script: str) -> Dict[str, Any]:
        """Calculates timeline boundaries for a single target shot segment to avoid global rebuilds."""
        self.load_timeline()
        
        # Calculate time offsets
        current_time = 0.0
        target_clip = None
        
        for s_idx, scene in enumerate(self.timeline.get("scenes", [])):
            for sh_idx, shot in enumerate(scene.get("shots", [])):
                duration = shot.get("duration", 3.0)
                if s_idx == scene_idx and sh_idx == shot_idx:
                    target_clip = {
                        "scene_index": scene_idx,
                        "shot_index": shot_idx,
                        "start_offset": current_time,
                        "duration": duration,
                        "script": new_script
                    }
                    break
                current_time += duration
            if target_clip:
                break
                
        return target_clip or {"error": "Shot segment not found"}
