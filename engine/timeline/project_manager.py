# engine/timeline/project_manager.py
import os
import json
import uuid
import time
import shutil
from typing import Dict, Any, List, Optional

class MovieProjectManager:
    """
    Subsystem: GenOTT Project System Manager
    Manages short-form movie projects, schema validations, portability directories, backends,
    and undo/redo transaction history.
    """
    def __init__(self, base_dir: str = "PROJECT_ROOT/Documents/LLM/ott"):
        self.base_dir = base_dir
        self.projects_dir = os.path.join(base_dir, "movie_projects")
        os.makedirs(self.projects_dir, exist_ok=True)
        
        self.project_name: Optional[str] = None
        self.project_path: Optional[str] = None
        self.project_file: Optional[str] = None
        
        self.history_stack: List[Dict[str, Any]] = []
        self.redo_stack: List[Dict[str, Any]] = []
        
        # Initialize a default blank project data mapping for compatibility
        self.project_data = {
            "movie_id": str(uuid.uuid4()),
            "name": "Untitled Movie",
            "project_id": str(uuid.uuid4()),
            "project_version": "1.0.0",
            "created_at": time.time(),
            "updated_at": time.time(),
            "author": "System",
            "engine_version": "2.0.0",
            "supported_backends": ["Blender"],
            "language": "en",
            "style": "cinematic",
            "target_platform": "YouTube Shorts",
            "target_duration": 30.0,
            "resolution": "1080x1920",
            "fps": 24,
            "status": "Draft",
            "scenes": {},
            "metadata": {},
            "story": {},
            "shots": {},
            "shot_specs": [],
            "backend_decisions": [],
            "generation_history": [],
            "review_history": []
        }
        
    def _get_project_folders(self, project_path: str) -> List[str]:
        return [
            os.path.join(project_path, "script"),
            os.path.join(project_path, "storyboard"),
            os.path.join(project_path, "timeline"),
            os.path.join(project_path, "scenes"),
            os.path.join(project_path, "shots"),
            os.path.join(project_path, "characters"),
            os.path.join(project_path, "locations"),
            os.path.join(project_path, "assets"),
            os.path.join(project_path, "references"),
            os.path.join(project_path, "outputs"),
            os.path.join(project_path, "cache"),
            os.path.join(project_path, "reviews"),
            os.path.join(project_path, "exports"),
            os.path.join(project_path, "versions")
        ]

    def create_project(self, name: str, author: str = "System") -> str:
        """Initializes a new portable project directory structure and metadata template."""
        clean_name = "".join(c for c in name if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_")
        project_path = os.path.join(self.projects_dir, clean_name)
        os.makedirs(project_path, exist_ok=True)
        
        # Create schema folders
        for folder in self._get_project_folders(project_path):
            os.makedirs(folder, exist_ok=True)
            
        self.project_name = clean_name
        self.project_path = project_path
        self.project_file = os.path.join(project_path, "project.json")
        
        self.project_data = {
            "movie_id": str(uuid.uuid4()),
            "project_id": str(uuid.uuid4()),
            "name": name,
            "project_version": "1.0.0",
            "created_at": time.time(),
            "updated_at": time.time(),
            "author": author,
            "engine_version": "2.0.0",
            "supported_backends": ["Blender"],
            "language": "en",
            "style": "cinematic",
            "target_platform": "YouTube Shorts",
            "target_duration": 30.0,
            "resolution": "1080x1920",
            "fps": 24,
            "status": "Draft",
            "scenes": {},
            "metadata": {},
            "story": {},
            "shots": {},
            "shot_specs": [],
            "backend_decisions": [],
            "generation_history": [],
            "review_history": []
        }
        self.save_project()
        return project_path

    def open_project(self, name: str) -> bool:
        """Opens and loads project specifications from the target project_name folder."""
        clean_name = name.replace(" ", "_")
        project_path = os.path.join(self.projects_dir, clean_name)
        project_file = os.path.join(project_path, "project.json")
        
        if os.path.exists(project_file):
            try:
                with open(project_file, "r") as f:
                    self.project_data = json.load(f)
                self.project_name = clean_name
                self.project_path = project_path
                self.project_file = project_file
                self.history_stack = []
                self.redo_stack = []
                return True
            except Exception as e:
                print(f"[ProjectManager] Failed to load project: {e}")
        return False

    def load_project(self) -> bool:
        """Fallback wrapper mapping older project formats to active directory scopes."""
        if self.project_file and os.path.exists(self.project_file):
            try:
                with open(self.project_file, "r") as f:
                    self.project_data = json.load(f)
                return True
            except Exception as e:
                print(f"[ProjectManager] load_project wrapper failure: {e}")
        return False

    def save_project(self) -> None:
        """Persists the active project JSON definition on disk, capturing undo states."""
        if not self.project_file:
            # Fallback path mapping if no active project is opened/saved
            fallback_dir = os.path.join(self.base_dir, "movie_project")
            os.makedirs(fallback_dir, exist_ok=True)
            self.project_file = os.path.join(fallback_dir, "project.json")
            
        try:
            # Save undo snapshot state
            self.history_stack.append(json.loads(json.dumps(self.project_data)))
            if len(self.history_stack) > 25:
                self.history_stack.pop(0)
                
            self.project_data["updated_at"] = time.time()
            with open(self.project_file, "w") as f:
                json.dump(self.project_data, f, indent=4)
        except Exception as e:
            print(f"[ProjectManager] Save project failed: {e}")

    def validate_project(self) -> Dict[str, Any]:
        """Performs versioned schema integrity checks on the opened project folder."""
        issues = []
        required_fields = ["project_id", "project_version", "status", "supported_backends", "fps", "target_duration"]
        
        for rf in required_fields:
            if rf not in self.project_data:
                issues.append(f"Missing required field: {rf}")
                
        if self.project_path:
            for folder in self._get_project_folders(self.project_path):
                if not os.path.exists(folder):
                    issues.append(f"Missing schema directory path: {os.path.basename(folder)}")
                    
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }

    def upgrade_project_version(self, new_version: str) -> None:
        """Upgrades the engine project version tracker inside metadata."""
        self.project_data["project_version"] = new_version
        self.save_project()

    def backup_project(self) -> str:
        """Zips the portable project folder structure into target backup formats."""
        if not self.project_path:
            raise ValueError("No active project loaded to backup.")
        backup_zip = self.project_path + f"_backup_{int(time.time())}.zip"
        shutil.make_archive(self.project_path + "_temp", 'zip', self.project_path)
        shutil.move(self.project_path + "_temp.zip", backup_zip)
        return backup_zip

    def clone_project(self, source_name: str, target_name: str) -> str:
        """Clones a source portable folder config entirely into a target folder name."""
        src_path = os.path.join(self.projects_dir, source_name.replace(" ", "_"))
        target_clean = target_name.replace(" ", "_")
        dst_path = os.path.join(self.projects_dir, target_clean)
        
        if not os.path.exists(src_path):
            raise ValueError(f"Source project path {src_path} not found.")
            
        shutil.copytree(src_path, dst_path)
        
        # Rewrite project JSON name
        project_json_file = os.path.join(dst_path, "project.json")
        if os.path.exists(project_json_file):
            with open(project_json_file, "r") as f:
                data = json.load(f)
            data["name"] = target_name
            data["project_id"] = str(uuid.uuid4())
            with open(project_json_file, "w") as f:
                json.dump(data, f, indent=4)
                
        return dst_path

    def archive_project(self) -> None:
        """Sets project lifecycle status to Archived."""
        self.project_data["status"] = "Archived"
        self.save_project()

    def add_scene(self, scene_name: str, scene_script: str) -> str:
        """Registers a scene item for compatibility specs."""
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
        """Registers a shot item inside a scene."""
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
        """Rolls back the current project structure definition."""
        if len(self.history_stack) > 1:
            curr = self.history_stack.pop()
            self.redo_stack.append(curr)
            prev = self.history_stack[-1]
            self.project_data = json.loads(json.dumps(prev))
            
            if self.project_file:
                with open(self.project_file, "w") as f:
                    json.dump(self.project_data, f, indent=4)
            return True
        return False
