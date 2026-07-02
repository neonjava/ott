# ai/scene_streaming.py
from typing import Dict, Any, List

class SceneStreamingAgent:
    """
    Subsystem: Scene Streaming
    Optimizes asset memory footprint by dividing film timelines into chunked loading sequences.
    """
    def __init__(self, max_concurrent_assets: int = 15):
        self.max_concurrent_assets = max_concurrent_assets

    def build_stream_schedule(self, scene_timeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Splits a timeline sequence into chunks with active/inactive asset lists."""
        chunks = []
        for idx, shot in enumerate(scene_timeline):
            # Resolve all assets present in this specific shot
            active_assets = []
            if shot.get("character"):
                active_assets.append(shot["character"])
            for asset in shot.get("scene_assets", []):
                noun = asset.get("noun")
                if noun:
                    active_assets.append(noun)
                    
            chunks.append({
                "shot_index": idx,
                "duration": shot.get("duration", 3.0),
                "load_assets": list(set(active_assets)),
                "unload_assets": []  # Solved dynamically in downstream stages
            })
            
        # Build unloading schedule to stay under max_concurrent_assets threshold
        loaded = set()
        for idx, chunk in enumerate(chunks):
            # Assets to load
            to_load = [a for a in chunk["load_assets"] if a not in loaded]
            loaded.update(to_load)
            
            # If we exceed the capacity, find assets not needed in next shots and mark them to unload
            to_unload = []
            if len(loaded) > self.max_concurrent_assets:
                needed_future = set()
                for future in chunks[idx+1:]:
                    needed_future.update(future["load_assets"])
                
                # Pick candidates not needed in immediate future
                candidates = list(loaded - set(chunk["load_assets"]))
                candidates.sort(key=lambda x: x in needed_future)
                while len(loaded) > self.max_concurrent_assets and candidates:
                    target = candidates.pop(0)
                    loaded.remove(target)
                    to_unload.append(target)
                    
            chunk["unload_assets"] = to_unload
            
        return chunks
