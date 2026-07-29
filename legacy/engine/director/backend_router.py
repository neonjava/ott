# engine/director/backend_router.py
from typing import Dict, Any, List
from models.adapters.base import BackendAdapter

class BackendRouter:
    """
    Subsystem: Backend Router
    Scores and matches available backend adapters against shot specification requirements.
    """
    def __init__(self, adapters: List[BackendAdapter]):
        self.adapters = adapters

    def route_shot(self, shot_spec: Dict[str, Any], weights: Dict[str, float] = None) -> BackendAdapter:
        """
        Evaluates capabilities and scores each registered adapter.
        Returns the adapter with the highest score.
        """
        if not self.adapters:
            raise ValueError("No backend adapters registered in the router.")
            
        if not weights:
            # Default scoring weights
            weights = {
                "quality": 0.4,
                "speed": 0.2,
                "cost": 0.2,
                "vram": 0.2
            }
            
        best_adapter = self.adapters[0]
        best_score = -999.0
        
        reqs = shot_spec.get("backend_requirements", {})
        mult_char_req = len(shot_spec.get("characters", [])) > 1
        
        for adapter in self.adapters:
            caps = adapter.get_capabilities()
            score = 0.0
            
            # Check hard compatibility flags
            if mult_char_req and not caps.get("supports_multi_character", True):
                continue # Skip if multi-character is requested but not supported
                
            # Perform scoring
            score += caps.get("estimated_quality", 0.5) * weights["quality"]
            score += caps.get("estimated_speed", 0.5) * weights["speed"]
            
            # Cost penalty: lower cost is better
            cost = caps.get("estimated_cost", 0.0)
            score += (1.0 - (cost / 10.0)) * weights["cost"]
            
            # VRAM optimization: lower VRAM overhead is better
            vram = caps.get("estimated_vram", 8.0)
            score += (1.0 - (vram / 48.0)) * weights["vram"]
            
            if score > best_score:
                best_score = score
                best_adapter = adapter
                
        return best_adapter
