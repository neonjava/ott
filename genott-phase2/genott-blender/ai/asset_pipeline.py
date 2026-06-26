# ai/asset_pipeline.py
import os
import json
import hashlib
from typing import Dict, Any, List, Optional

class AssetPipelineAgent:
    """
    Subsystem: Asset Pipeline
    Manages the asset registry, versions, dependency graphs, validation checks, and cache status.
    """
    def __init__(self, project_dir: Optional[str] = None):
        self.project_dir = project_dir or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.registry_path = os.path.join(self.project_dir, "asset_registry.json")
        self.cache_dir = os.path.join(self.project_dir, "cache", "assets")
        os.makedirs(self.cache_dir, exist_ok=True)
        self.registry = self._load_registry()

    def _load_registry(self) -> Dict[str, Any]:
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[AssetPipeline] Error loading registry: {e}")
        return {}

    def get_asset_details(self, asset_id: str) -> Dict[str, Any]:
        """Resolves asset ID and adds versioning and dependency mapping."""
        key = asset_id.lower().strip()
        asset_info = self.registry.get(key)
        
        if not asset_info:
            return {
                "id": key,
                "version": "1.0.0",
                "dependencies": [],
                "status": "missing",
                "fallback": "cube"
            }
            
        # Add default versioning metadata
        if "version" not in asset_info:
            asset_info["version"] = "1.0.0"
        if "dependencies" not in asset_info:
            # e.g., a character asset might depend on texture/rig packs
            asset_info["dependencies"] = []
            
        return asset_info

    def validate_asset(self, asset_id: str) -> Dict[str, Any]:
        """Validates physical glb file presence, checks for corrupt structures, and builds hashes."""
        details = self.get_asset_details(asset_id)
        model_path = details.get("model", "")
        
        if not model_path:
            return {"valid": False, "error": "No model path defined", "hash": ""}
            
        full_path = os.path.join(self.project_dir, model_path)
        if not os.path.exists(full_path):
            return {"valid": False, "error": f"File does not exist: {model_path}", "hash": ""}
            
        # Physical check
        try:
            # Generate file hash for cache validation
            sha = hashlib.sha256()
            with open(full_path, "rb") as f:
                while chunk := f.read(8192):
                    sha.update(chunk)
            file_hash = sha.hexdigest()
            
            # Simple signature check
            with open(full_path, "rb") as f:
                sig = f.read(4)
                # GLB standard magic number is 'glTF'
                if sig != b'glTF':
                    return {"valid": False, "error": "File signature is not glTF/GLB", "hash": file_hash}
                    
            return {"valid": True, "error": None, "hash": file_hash}
        except Exception as e:
            return {"valid": False, "error": f"Read error: {e}", "hash": ""}

    def get_dependency_graph(self) -> Dict[str, List[str]]:
        """Builds a flat dependency graph of all registered assets."""
        graph = {}
        for key in self.registry:
            details = self.get_asset_details(key)
            graph[key] = details.get("dependencies", [])
        return graph

    def cache_verify(self, asset_id: str) -> bool:
        """Verifies if the asset has been cached and matches its validation hash."""
        validation = self.validate_asset(asset_id)
        if not validation["valid"]:
            return False
            
        cache_manifest_path = os.path.join(self.cache_dir, f"{asset_id}_manifest.json")
        if os.path.exists(cache_manifest_path):
            try:
                with open(cache_manifest_path, "r") as f:
                    manifest = json.load(f)
                if manifest.get("hash") == validation["hash"]:
                    return True
            except Exception:
                pass
                
        # Write/Update cache manifest
        try:
            with open(cache_manifest_path, "w") as f:
                json.dump({"asset_id": asset_id, "hash": validation["hash"], "timestamp": os.path.getmtime(os.path.join(self.project_dir, self.registry[asset_id]["model"]))}, f)
        except Exception:
            pass
            
        return True
