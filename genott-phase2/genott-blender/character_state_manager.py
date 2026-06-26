# character_state_manager.py
import os
import json
from typing import Dict, Any

class CharacterStateManager:
    """
    Manages persistent state profiles for characters in the movie production timeline.
    Prevents regeneration of identical characters by mapping them to stable global IDs.
    """
    def __init__(self, state_file: str = "character_states.json"):
        self.state_file = os.path.abspath(state_file)
        self._states: Dict[str, Dict[str, Any]] = {}
        self.load()

    def load(self):
        """Loads persistent character profiles from disk."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    self._states = json.load(f)
            except Exception as e:
                print(f"[CharacterStateManager] Error loading states: {e}")
                self._states = {}

    def save(self):
        """Persists character profiles to disk."""
        try:
            with open(self.state_file, "w") as f:
                json.dump(self._states, f, indent=4)
        except Exception as e:
            print(f"[CharacterStateManager] Error saving states: {e}")

    def get_character_state(self, character_id: str) -> Dict[str, Any]:
        """Retrieves or initializes state for a persistent character ID (e.g., 'hero_001')."""
        key = character_id.lower().strip()
        if key not in self._states:
            # Initialize with default structure
            self._states[key] = {
                "id": key,
                "outfit": "default",
                "accessories": [],
                "mood_baseline": "neutral",
                "inventory": [],
                "scale": [1.0, 1.0, 1.0],
                "last_position": [0.0, 0.0, 0.0],
                "last_rotation": [0.0, 0.0, 0.0]
            }
            self.save()
        return self._states[key]

    def update_character_state(self, character_id: str, updates: Dict[str, Any]):
        """Updates specific fields in a character state profile."""
        state = self.get_character_state(character_id)
        for k, v in updates.items():
            state[k] = v
        self._states[character_id.lower().strip()] = state
        self.save()
