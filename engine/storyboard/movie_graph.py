# engine/storyboard/movie_graph.py
import json
import uuid
import time
from typing import Dict, Any, List, Optional
from engine.storyboard.event_bus import EventBus

# --- Spec Schemas ---

class MovieSpec:
    def __init__(self, title: str, genre: str, tone: str, duration: float = 30.0):
        self.movie_id = str(uuid.uuid4())
        self.title = title
        self.genre = genre
        self.tone = tone
        self.duration = duration

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

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__

class ShotSpec:
    def __init__(self, shot_id: str, scene_id: str, camera_type: str, camera_profile: str, duration: float = 3.0):
        self.shot_id = shot_id
        self.scene_id = scene_id
        self.camera_type = camera_type
        self.camera_profile = camera_profile
        self.duration = duration
        self.characters: List[str] = []
        self.dialogue: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__

class CharacterSpec:
    def __init__(self, character_id: str, name: str, outfit: str = "armor", weapon: str = "sword"):
        self.character_id = character_id
        self.name = name
        self.outfit = outfit
        self.weapon = weapon

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__

class LocationSpec:
    def __init__(self, location_id: str, name: str, environment_type: str = "forest"):
        self.location_id = location_id
        self.name = name
        self.environment_type = environment_type

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__

class AssetSpec:
    def __init__(self, asset_id: str, name: str, asset_type: str = "glb", path: str = ""):
        self.asset_id = asset_id
        self.name = name
        self.asset_type = asset_type
        self.path = path

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__

class TimelineSpec:
    def __init__(self, timeline_id: str, shot_ids: List[str]):
        self.timeline_id = timeline_id
        self.shot_ids = shot_ids

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__

class BackendTask:
    def __init__(self, task_id: str, shot_id: str, backend_name: str, status: str = "queued"):
        self.task_id = task_id
        self.shot_id = shot_id
        self.backend_name = backend_name
        self.status = status

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__

class GenerationTask:
    def __init__(self, task_id: str, target_id: str, status: str = "queued"):
        self.task_id = task_id
        self.target_id = target_id
        self.status = status

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__

class ReviewTask:
    def __init__(self, task_id: str, target_id: str, score: float = 0.0, approved: bool = False):
        self.task_id = task_id
        self.target_id = target_id
        self.score = score
        self.approved = approved

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

    def add_shot(self, shot_id: str, scene_id: str, camera_type: str, camera_profile: str, duration: float = 3.0):
        spec = ShotSpec(shot_id, scene_id, camera_type, camera_profile, duration)
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

    def serialize(self) -> str:
        """Serializes complete MovieGraph state to a JSON string representation."""
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
