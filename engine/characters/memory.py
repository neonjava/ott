# engine/characters/memory.py
import json
import os
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class CharacterMemory:
    """
    Persistent Character Identity Memory System for GenOTT V2.
    Tracks face features, clothing, hairstyle, age, body proportions, accessories,
    personality traits, and speaking styles across multi-scene film productions.
    """

    def __init__(self, storage_path: str = "configs/characters_memory.json"):
        self.storage_path = os.path.abspath(storage_path)
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        self.characters: Dict[str, Dict[str, Any]] = self._load()

    def register_character(
        self,
        name: str,
        appearance: str,
        clothing: str,
        personality: str = "",
        face: str = "chiseled jawline, sharp focused eyes",
        hairstyle: str = "cropped dark tactical hair",
        age: str = "late 30s",
        proportions: str = "athletic build, 6ft tall",
        accessories: str = "tactical comms earpiece, cybernetic wrist display",
        speaking_style: str = "authoritative, calm, direct"
    ) -> Dict[str, Any]:
        spec = {
            "name": name,
            "appearance": appearance,
            "clothing": clothing,
            "face": face,
            "hairstyle": hairstyle,
            "age": age,
            "proportions": proportions,
            "accessories": accessories,
            "personality": personality,
            "speaking_style": speaking_style
        }
        self.characters[name] = spec
        self._save()
        logger.info(f"[CharacterMemory] Registered character identity for '{name}'")
        return spec

    def get_character(self, name: str) -> Optional[Dict[str, Any]]:
        return self.characters.get(name)

    def get_prompt_description(self, name: str) -> str:
        c = self.characters.get(name)
        if not c:
            return f"character named {name}"
        return f"{c['name']} ({c['age']}, {c['face']}, {c['hairstyle']}, {c['proportions']}, wearing {c['clothing']}, equipped with {c['accessories']})"

    def _save(self):
        with open(self.storage_path, "w") as f:
            json.dump(self.characters, f, indent=2)

    def _load(self) -> Dict[str, Dict[str, Any]]:
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load character memory ({e}). Starting fresh.")
        return {}
