# ai/visual_continuity.py
import json
import os
from typing import Dict, Any, List

class VisualContinuityEngine:
    """
    Subsystem: Visual Continuity
    Maintains persistent states across sequence cuts, checking for clothing mismatches, missing props, and lighting shifts.
    """
    def __init__(self, persistence_file: str = "continuity_state.json"):
        self.persistence_file = persistence_file
        self.shot_states: List[Dict[str, Any]] = []
        self.load_states()

    def load_states(self):
        if os.path.exists(self.persistence_file):
            try:
                with open(self.persistence_file, "r") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.shot_states = data
                    else:
                        self.shot_states = []
            except Exception:
                self.shot_states = []
        else:
            self.shot_states = []

    def save_states(self):
        try:
            with open(self.persistence_file, "w") as f:
                json.dump(self.shot_states, f, indent=4)
        except Exception:
            pass

    def record_shot_state(self, shot_index: int, state_snapshot: Dict[str, Any]):
        """Records a snapshot of character positions, outfits, held objects, and lighting directions."""
        snapshot = {
            "shot_index": shot_index,
            "data": state_snapshot
        }
        # Clear forward states if we are rewriting history
        self.shot_states = [s for s in self.shot_states if isinstance(s, dict) and s.get("shot_index", 0) < shot_index]
        self.shot_states.append(snapshot)
        self.save_states()

    def check_continuity(self) -> List[Dict[str, Any]]:
        """Compares adjacent shots to find continuity discrepancies (e.g. outfit changes, teleporting assets)."""
        discrepancies = []
        valid_states = [s for s in self.shot_states if isinstance(s, dict) and "data" in s]
        if len(valid_states) < 2:
            return discrepancies
            
        for i in range(1, len(valid_states)):
            prev = valid_states[i - 1]["data"]
            curr = valid_states[i]["data"]
            shot_idx = valid_states[i]["shot_index"]
            
            # 1. Outfit Check
            prev_outfits = prev.get("outfits", {})
            curr_outfits = curr.get("outfits", {})
            for char_id, outfit in curr_outfits.items():
                if char_id in prev_outfits and prev_outfits[char_id] != outfit:
                    discrepancies.append({
                        "shot_index": shot_idx,
                        "type": "outfit_continuity_error",
                        "description": f"Character '{char_id}' changed outfit from '{prev_outfits[char_id]}' to '{outfit}' abruptly."
                    })
                    
            # 2. Held Object / Prop Check
            prev_props = prev.get("held_props", {})
            curr_props = curr.get("held_props", {})
            for char_id, prop in curr_props.items():
                if char_id in prev_props and prev_props[char_id] != prop:
                    discrepancies.append({
                        "shot_index": shot_idx,
                        "type": "prop_continuity_error",
                        "description": f"Character '{char_id}' was holding '{prev_props[char_id]}' but is now holding '{prop}' without transition."
                    })
                    
            # 3. Environment/Lighting shift check
            if prev.get("lighting_color") != curr.get("lighting_color"):
                discrepancies.append({
                    "shot_index": shot_idx,
                    "type": "lighting_continuity_error",
                    "description": f"Lighting color changed from {prev.get('lighting_color')} to {curr.get('lighting_color')} between cuts."
                })
                
        return discrepancies
