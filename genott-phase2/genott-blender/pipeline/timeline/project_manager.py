# ai/project_manager.py
import os
import json
import uuid
from typing import Dict, Any, List

class MovieProjectManager:
    """
    Subsystem: Movie Project Manager
    Manages acts, scenes, and shots referenced by UUIDs and handles undo/redo project history.
    """
    def __init__(self, project_dir: str = "PROJECT_ROOT/Documents/LLM/ott/genott-phase2/genott-blender"):
        self.project_dir = project_dir
        self.project_file = os.path.join(project_dir, "movie_project", "project.json")
        self.history_stack: List[Dict[str, Any]] = []
        self.redo_stack: List[Dict[str, Any]] = []
        
        self.project_data = {
            "movie_id": str(uuid.uuid4()),
            "name": "Untitled Movie",
            "scenes": {},
            "metadata": {}
        }
        
    def load_project(self) -> bool:
        """Loads persistent project definitions from movie_project/project.json."""
        if os.path.exists(self.project_file):
            try:
                with open(self.project_file, "r") as f:
                    self.project_data = json.load(f)
                return True
            except Exception as e:
                print(f"[ProjectManager] Failed to load project: {e}")
        return False

    def save_project(self) -> None:
        """Saves current project state to movie_project/project.json."""
        os.makedirs(os.path.dirname(self.project_file), exist_ok=True)
        try:
            # Capture current state to history stack before saving
            self.history_stack.append(json.loads(json.dumps(self.project_data)))
            # Keep history to max 20 steps
            if len(self.history_stack) > 20:
                self.history_stack.pop(0)
                
            with open(self.project_file, "w") as f:
                json.dump(self.project_data, f, indent=4)
        except Exception as e:
            print(f"[ProjectManager] Failed to save project: {e}")

    def add_scene(self, scene_name: str, scene_script: str) -> str:
        """Registers a new scene referenced by a unique UUID."""
        scene_id = str(uuid.uuid4())
        self.project_data["scenes"][scene_id] = {
            "uuid": scene_id,
            "name": scene_name,
            "script": scene_script,
            "shots": {}
        }
        self.save_project()
        return scene_id

    def add_shot(self, scene_id: str, camera_shot: str, duration: float) -> str:
        """Registers a new shot within a parent scene UUID."""
        if scene_id not in self.project_data["scenes"]:
            raise ValueError(f"Scene UUID {scene_id} not found.")
            
        shot_id = str(uuid.uuid4())
        self.project_data["scenes"][scene_id]["shots"][shot_id] = {
            "uuid": shot_id,
            "camera_shot": camera_shot,
            "duration": duration,
            "status": "pending"
        }
        self.save_project()
        return shot_id

    def undo(self) -> bool:
        """Restores the previous project version from history stack."""
        if len(self.history_stack) > 1:
            # Current state is at the top, pop it to redo stack
            curr = self.history_stack.pop()
            self.redo_stack.append(curr)
            
            # Load the previous state
            prev = self.history_stack[-1]
            self.project_data = json.loads(json.dumps(prev))
            
            # Save without adding to history again
            os.makedirs(os.path.dirname(self.project_file), exist_ok=True)
            with open(self.project_file, "w") as f:
                json.dump(self.project_data, f, indent=4)
            return True
        return False
