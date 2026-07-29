# ai/fluid_cache.py
import os
import json
import hashlib
from typing import Dict, Any, Optional

class FluidCacheManager:
    """
    Subsystem: Fluid Simulation Cache Manager
    Generates deterministic SHA256 hashes of fluid physics parameters to cache and reuse Blender simulation bakes.
    """
    def __init__(self, project_dir: str = "PROJECT_ROOT/Documents/LLM/ott/genott-phase2/genott-blender"):
        self.project_dir = project_dir
        self.cache_dir = os.path.join(project_dir, "static", "videos", "fluid_cache")
        os.makedirs(self.cache_dir, exist_ok=True)

    def generate_cache_key(self, scene_uuid: str, sim_type: str, object_uuid: str, resolution: int, settings: Dict[str, Any], frame_range: tuple) -> str:
        """Generates a deterministic SHA256 hash from fluid config parameters."""
        serialized_settings = json.dumps(settings, sort_keys=True)
        raw_key = f"{scene_uuid}:{sim_type}:{object_uuid}:{resolution}:{serialized_settings}:{frame_range[0]}-{frame_range[1]}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    def check_cache(self, cache_key: str) -> Optional[str]:
        """Returns the path to the cached simulation folder if it exists and is valid."""
        meta_path = os.path.join(self.cache_dir, f"{cache_key}.json")
        sim_path = os.path.join(self.cache_dir, cache_key)
        if os.path.exists(meta_path) and os.path.exists(sim_path):
            return sim_path
        return None

    def register_cache(self, cache_key: str, metadata: Dict[str, Any]) -> str:
        """Saves cache metadata and returns the simulation folder path."""
        meta_path = os.path.join(self.cache_dir, f"{cache_key}.json")
        sim_path = os.path.join(self.cache_dir, cache_key)
        os.makedirs(sim_path, exist_ok=True)
        
        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=4)
            
        print(f"[FluidCacheManager] Simulation cache registered: {cache_key}")
        return sim_path
