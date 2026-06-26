# ai/animation_graph.py
from typing import Dict, Any, List

class AnimationGraph:
    """
    Subsystem: Animation Graph & Blend Tree Engine
    Manages active skeletal locomotion states and computes transition weight balances between distinct tracks.
    """
    def __init__(self):
        self.states = ["idle", "walk", "run", "jump"]
        self.transitions = {
            "idle": ["walk", "jump"],
            "walk": ["idle", "run", "jump"],
            "run": ["walk", "jump"],
            "jump": ["idle", "walk"]
        }

    def update_state(self, current_state: str, velocity: float) -> str:
        """Determines next logical state based on character motion velocity."""
        curr = current_state.lower().strip()
        if curr not in self.states:
            curr = "idle"
            
        # State transition logic
        if velocity <= 0.05:
            next_state = "idle"
        elif 0.05 < velocity <= 1.5:
            next_state = "walk"
        else:
            next_state = "run"
            
        # Validate that the transition is registered
        if next_state in self.transitions[curr]:
            return next_state
        return curr  # Fallback to current if transition invalid

    def evaluate_blend(self, state: str, speed: float) -> Dict[str, float]:
        """Calculates blend coefficients for animation clips based on current speed."""
        blend = {"idle": 0.0, "walk": 0.0, "run": 0.0}
        
        if state == "idle":
            blend["idle"] = 1.0
        elif state == "walk":
            # Speed scaling between idle (0.0) and walk (1.0) and run (1.5)
            if speed <= 0.5:
                # Blend idle and walk
                blend["walk"] = speed / 0.5
                blend["idle"] = 1.0 - blend["walk"]
            else:
                blend["walk"] = 1.0
        elif state == "run":
            if speed <= 2.0:
                # Blend walk and run (1.0 to 2.0)
                diff = speed - 1.0
                blend["run"] = max(0.0, min(1.0, diff / 1.0))
                blend["walk"] = 1.0 - blend["run"]
            else:
                blend["run"] = 1.0
                
        return blend
