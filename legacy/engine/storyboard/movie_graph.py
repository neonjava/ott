# engine/storyboard/movie_graph.py
import json
import uuid
import time
from typing import Dict, Any, List, Optional
from engine.storyboard.event_bus import EventBus

# --- Custom Validation Error ---
class ContractValidationError(ValueError):
    """Custom exception raised when a formal production spec contract fails validation."""
    pass


# --- Spec Schemas ---

class MovieSpec:
    def __init__(self, title: str, genre: str, tone: str, duration: float = 30.0):
        self.movie_id = str(uuid.uuid4())
        self.title = title
        self.genre = genre
        self.tone = tone
        self.duration = duration
        self.validate()

    def validate(self):
        if not getattr(self, "movie_id", None) or not isinstance(self.movie_id, str):
            raise ContractValidationError("MovieSpec contract failed: 'movie_id' must be a valid non-empty string.")
        if not getattr(self, "title", None) or not isinstance(self.title, str) or not self.title.strip():
            raise ContractValidationError("MovieSpec contract failed: 'title' must be a valid non-empty string.")
        if not getattr(self, "genre", None) or not isinstance(self.genre, str) or not self.genre.strip():
            raise ContractValidationError("MovieSpec contract failed: 'genre' must be a valid non-empty string.")
        if not getattr(self, "tone", None) or not isinstance(self.tone, str) or not self.tone.strip():
            raise ContractValidationError("MovieSpec contract failed: 'tone' must be a valid non-empty string.")
        if not isinstance(self.duration, (int, float)) or self.duration <= 0:
            raise ContractValidationError("MovieSpec contract failed: 'duration' must be a positive number.")

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__


class SceneSpec:
    def __init__(self, scene_id: str, purpose: str, emotion: str, location_id: str, weather: str = "clear", duration: float = 5.0):
        self.scene_id = scene_id
        self.purpose = purpose
        self.emotion = emotion
        self.location_id = location_id
        self.weather = weather
        self.duration = duration
        self.validate()

    def validate(self):
        if not self.scene_id or not isinstance(self.scene_id, str):
            raise ContractValidationError("SceneSpec contract failed: 'scene_id' must be a non-empty string.")
        if not self.purpose or not isinstance(self.purpose, str):
            raise ContractValidationError("SceneSpec contract failed: 'purpose' must be a non-empty string.")
        if not self.emotion or not isinstance(self.emotion, str):
            raise ContractValidationError("SceneSpec contract failed: 'emotion' must be a non-empty string.")
        if not self.location_id or not isinstance(self.location_id, str):
            raise ContractValidationError("SceneSpec contract failed: 'location_id' must be a non-empty string.")
        if not self.weather or not isinstance(self.weather, str):
            raise ContractValidationError("SceneSpec contract failed: 'weather' must be a non-empty string.")
        if not isinstance(self.duration, (int, float)) or self.duration <= 0:
            raise ContractValidationError("SceneSpec contract failed: 'duration' must be a positive number.")

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__


class ShotSpec:
    def __init__(self, shot_id: str, scene_id: str, camera_type: str, camera_profile: str, duration: float = 3.0, continuity: Optional[Dict[str, Any]] = None):
        self.shot_id = shot_id
        self.scene_id = scene_id
        self.camera_type = camera_type
        self.camera_profile = camera_profile
        self.duration = duration
        self.characters: List[str] = []
        self.dialogue: Optional[Dict[str, Any]] = None
        self.continuity = continuity or {"seed": 42, "environmental_seed": 100}
        self.validate()

    def validate(self):
        if not self.shot_id or not isinstance(self.shot_id, str):
            raise ContractValidationError("ShotSpec contract failed: 'shot_id' must be a non-empty string.")
        if not self.scene_id or not isinstance(self.scene_id, str):
            raise ContractValidationError("ShotSpec contract failed: 'scene_id' must be a non-empty string.")
        if not self.camera_type or not isinstance(self.camera_type, str):
            raise ContractValidationError("ShotSpec contract failed: 'camera_type' must be a non-empty string.")
        if not self.camera_profile or not isinstance(self.camera_profile, str):
            raise ContractValidationError("ShotSpec contract failed: 'camera_profile' must be a non-empty string.")
        if not isinstance(self.duration, (int, float)) or self.duration <= 0:
            raise ContractValidationError("ShotSpec contract failed: 'duration' must be a positive number.")
        if not isinstance(self.continuity, dict) or "seed" not in self.continuity or "environmental_seed" not in self.continuity:
            raise ContractValidationError("ShotSpec contract failed: 'continuity' dictionary must contain 'seed' and 'environmental_seed' keys.")

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__


class CharacterSpec:
    def __init__(self, character_id: str, name: str, outfit: str = "armor", weapon: str = "sword"):
        self.character_id = character_id
        self.name = name
        self.outfit = outfit
        self.weapon = weapon
        self.validate()

    def validate(self):
        if not self.character_id or not isinstance(self.character_id, str):
            raise ContractValidationError("CharacterSpec contract failed: 'character_id' must be a non-empty string.")
        if not self.name or not isinstance(self.name, str):
            raise ContractValidationError("CharacterSpec contract failed: 'name' must be a non-empty string.")

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__


class LocationSpec:
    def __init__(self, location_id: str, name: str, environment_type: str = "forest"):
        self.location_id = location_id
        self.name = name
        self.environment_type = environment_type
        self.validate()

    def validate(self):
        if not self.location_id or not isinstance(self.location_id, str):
            raise ContractValidationError("LocationSpec contract failed: 'location_id' must be a non-empty string.")
        if not self.name or not isinstance(self.name, str):
            raise ContractValidationError("LocationSpec contract failed: 'name' must be a non-empty string.")

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__


class AssetSpec:
    def __init__(self, asset_id: str, name: str, asset_type: str = "glb", path: str = ""):
        self.asset_id = asset_id
        self.name = name
        self.asset_type = asset_type
        self.path = path
        self.validate()

    def validate(self):
        if not self.asset_id or not isinstance(self.asset_id, str):
            raise ContractValidationError("AssetSpec contract failed: 'asset_id' must be a non-empty string.")
        if not self.name or not isinstance(self.name, str):
            raise ContractValidationError("AssetSpec contract failed: 'name' must be a non-empty string.")

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__


class TimelineSpec:
    def __init__(self, timeline_id: str, shot_ids: List[str]):
        self.timeline_id = timeline_id
        self.shot_ids = shot_ids
        self.validate()

    def validate(self):
        if not self.timeline_id or not isinstance(self.timeline_id, str):
            raise ContractValidationError("TimelineSpec contract failed: 'timeline_id' must be a non-empty string.")
        if not isinstance(self.shot_ids, list):
            raise ContractValidationError("TimelineSpec contract failed: 'shot_ids' must be a valid list of shot IDs.")

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__


class BackendTask:
    def __init__(self, task_id: str, shot_id: str, backend_name: str, status: str = "queued"):
        self.task_id = task_id
        self.shot_id = shot_id
        self.backend_name = backend_name
        self.status = status
        self.validate()

    def validate(self):
        if not self.task_id or not isinstance(self.task_id, str):
            raise ContractValidationError("BackendTask contract failed: 'task_id' must be a non-empty string.")
        if not self.shot_id or not isinstance(self.shot_id, str):
            raise ContractValidationError("BackendTask contract failed: 'shot_id' must be a non-empty string.")
        if not self.backend_name or not isinstance(self.backend_name, str):
            raise ContractValidationError("BackendTask contract failed: 'backend_name' must be a non-empty string.")
        if self.status not in ["queued", "completed", "failed"]:
            raise ContractValidationError("BackendTask contract failed: 'status' must be 'queued', 'completed', or 'failed'.")

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__


class GenerationTask:
    def __init__(self, task_id: str, target_id: str, status: str = "queued"):
        self.task_id = task_id
        self.target_id = target_id
        self.status = status
        self.validate()

    def validate(self):
        if not self.task_id or not isinstance(self.task_id, str):
            raise ContractValidationError("GenerationTask contract failed: 'task_id' must be a non-empty string.")
        if not self.target_id or not isinstance(self.target_id, str):
            raise ContractValidationError("GenerationTask contract failed: 'target_id' must be a non-empty string.")
        if self.status not in ["queued", "generating", "completed", "failed"]:
            raise ContractValidationError("GenerationTask contract failed: 'status' must be one of: queued, generating, completed, failed.")

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__


class ReviewTask:
    def __init__(self, task_id: str, target_id: str, score: float = 0.0, approved: bool = False):
        self.task_id = task_id
        self.target_id = target_id
        self.score = score
        self.approved = approved
        self.validate()

    def validate(self):
        if not self.task_id or not isinstance(self.task_id, str):
            raise ContractValidationError("ReviewTask contract failed: 'task_id' must be a non-empty string.")
        if not self.target_id or not isinstance(self.target_id, str):
            raise ContractValidationError("ReviewTask contract failed: 'target_id' must be a non-empty string.")
        if not isinstance(self.score, (int, float)):
            raise ContractValidationError("ReviewTask contract failed: 'score' must be a numerical value.")

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__


# --- Movie Graph Class ---

class MovieGraph:
    """
    Subsystem: Movie Graph
    The single source of truth representing acts, scenes, shots, characters, locations,
    timeline sequencing, backend jobs, and outputs. Communicates decoupled updates via EventBus.
    """
    def __init__(self, event_bus: Optional[EventBus] = None):
        self.event_bus = event_bus or EventBus()
        
        self.movie: Optional[Dict[str, Any]] = None
        self.acts: List[Dict[str, Any]] = []
        self.scenes: Dict[str, Dict[str, Any]] = {}
        self.shots: Dict[str, Dict[str, Any]] = {}
        self.characters: Dict[str, Dict[str, Any]] = {}
        self.locations: Dict[str, Dict[str, Any]] = {}
        self.assets: Dict[str, Dict[str, Any]] = {}
        self.timeline: Optional[Dict[str, Any]] = None
        self.backend_tasks: Dict[str, Dict[str, Any]] = {}
        self.generation_tasks: Dict[str, Dict[str, Any]] = {}
        self.review_tasks: Dict[str, Dict[str, Any]] = {}
        self.outputs: List[str] = []

    def set_movie(self, title: str, genre: str, tone: str, duration: float = 30.0):
        spec = MovieSpec(title, genre, tone, duration)
        self.movie = spec.to_dict()
        self.event_bus.publish("MovieCreated", self.movie)

    def add_scene(self, scene_id: str, purpose: str, emotion: str, location_id: str, weather: str = "clear", duration: float = 5.0):
        spec = SceneSpec(scene_id, purpose, emotion, location_id, weather, duration)
        self.scenes[scene_id] = spec.to_dict()
        self.event_bus.publish("SceneGenerated", self.scenes[scene_id])

    def add_shot(self, shot_id: str, scene_id: str, camera_type: str, camera_profile: str, duration: float = 3.0, continuity: Optional[Dict[str, Any]] = None):
        spec = ShotSpec(shot_id, scene_id, camera_type, camera_profile, duration, continuity)
        self.shots[shot_id] = spec.to_dict()
        self.event_bus.publish("ShotGenerated", self.shots[shot_id])

    def add_character(self, character_id: str, name: str, outfit: str = "armor", weapon: str = "sword"):
        spec = CharacterSpec(character_id, name, outfit, weapon)
        self.characters[character_id] = spec.to_dict()

    def add_location(self, location_id: str, name: str, environment_type: str = "forest"):
        spec = LocationSpec(location_id, name, environment_type)
        self.locations[location_id] = spec.to_dict()

    def add_asset(self, asset_id: str, name: str, asset_type: str = "glb", path: str = ""):
        spec = AssetSpec(asset_id, name, asset_type, path)
        self.assets[asset_id] = spec.to_dict()

    def add_backend_task(self, task_id: str, shot_id: str, backend_name: str):
        spec = BackendTask(task_id, shot_id, backend_name)
        self.backend_tasks[task_id] = spec.to_dict()
        self.event_bus.publish("BackendSelected", self.backend_tasks[task_id])

    def add_generation_task(self, task_id: str, target_id: str, status: str = "queued"):
        spec = GenerationTask(task_id, target_id, status)
        self.generation_tasks[task_id] = spec.to_dict()
        self.event_bus.publish("GenerationStarted", self.generation_tasks[task_id])

    def update_generation_status(self, task_id: str, status: str):
        if task_id in self.generation_tasks:
            self.generation_tasks[task_id]["status"] = status
            if status == "completed":
                self.event_bus.publish("GenerationCompleted", self.generation_tasks[task_id])

    def add_review_task(self, task_id: str, target_id: str, score: float = 0.0, approved: bool = False):
        spec = ReviewTask(task_id, target_id, score, approved)
        self.review_tasks[task_id] = spec.to_dict()
        self.event_bus.publish("ReviewCompleted", self.review_tasks[task_id])

    def validate(self):
        """Performs repository contract validation across all structured graph assets."""
        if self.movie:
            # Validate movie schema dict
            try:
                ms = MovieSpec(self.movie["title"], self.movie["genre"], self.movie["tone"], self.movie["duration"])
                ms.movie_id = self.movie["movie_id"]
                ms.validate()
            except Exception as e:
                raise ContractValidationError(f"MovieGraph integrity check failed on MovieSpec: {e}")
                
        for scene_id, scene in self.scenes.items():
            try:
                ss = SceneSpec(scene["scene_id"], scene["purpose"], scene["emotion"], scene["location_id"], scene["weather"], scene["duration"])
                ss.validate()
            except Exception as e:
                raise ContractValidationError(f"MovieGraph integrity check failed on SceneSpec {scene_id}: {e}")

        for shot_id, shot in self.shots.items():
            try:
                sh = ShotSpec(shot["shot_id"], shot["scene_id"], shot["camera_type"], shot["camera_profile"], shot["duration"], shot.get("continuity"))
                sh.validate()
            except Exception as e:
                raise ContractValidationError(f"MovieGraph integrity check failed on ShotSpec {shot_id}: {e}")

    def serialize(self) -> str:
        """Serializes complete MovieGraph state to a JSON string representation."""
        self.validate() # Validate before serialization
        state = {
            "movie": self.movie,
            "acts": self.acts,
            "scenes": self.scenes,
            "shots": self.shots,
            "characters": self.characters,
            "locations": self.locations,
            "assets": self.assets,
            "timeline": self.timeline,
            "backend_tasks": self.backend_tasks,
            "generation_tasks": self.generation_tasks,
            "review_tasks": self.review_tasks,
            "outputs": self.outputs
        }
        return json.dumps(state, indent=4)

    def deserialize(self, json_str: str):
        """Reconstructs the MovieGraph state from a JSON string."""
        state = json.loads(json_str)
        self.movie = state.get("movie")
        self.acts = state.get("acts", [])
        self.scenes = state.get("scenes", {})
        self.shots = state.get("shots", {})
        self.characters = state.get("characters", {})
        self.locations = state.get("locations", {})
        self.assets = state.get("assets", {})
        self.timeline = state.get("timeline")
        self.backend_tasks = state.get("backend_tasks", {})
        self.generation_tasks = state.get("generation_tasks", {})
        self.review_tasks = state.get("review_tasks", {})
        self.outputs = state.get("outputs", [])
        
        # Self validate on reconstruction to ensure strict mode contracts hold
        self.validate()
