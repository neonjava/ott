# engine/characters/memory.py
import os
import json
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class CharacterMemory:
    """
    Persistent Character Memory System for GenOTT V2.
    Stores appearance, voice, age, clothing, personality, relationships, speaking/motion style,
    and history to ensure visual and character consistency across all scenes.
    """

    def __init__(self, memory_file: str = "configs/characters_memory.json"):
        self.memory_file = os.path.abspath(memory_file)
        self.characters: Dict[str, Dict[str, Any]] = {}
        self.load_memory()

    def load_memory(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r") as f:
                    self.characters = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load character memory from {self.memory_file}: {e}")
                self.characters = {}

    def save_memory(self):
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        with open(self.memory_file, "w") as f:
            json.dump(self.characters, f, indent=2)

    def register_character(
        self,
        name: str,
        appearance: str,
        age: int = 30,
        clothing: str = "standard attire",
        voice: str = "male_dramatic",
        personality: str = "determined",
        motion_style: str = "confident graceful movement",
        history: str = ""
    ) -> Dict[str, Any]:
        char_data = {
            "name": name,
            "appearance": appearance,
            "age": age,
            "clothing": clothing,
            "voice": voice,
            "personality": personality,
            "motion_style": motion_style,
            "history": history,
            "prompt_signature": f"{name} ({age}yo, {appearance}, wearing {clothing}, {motion_style})"
        }
        self.characters[name.lower()] = char_data
        self.save_memory()
        logger.info(f"Registered character memory signature for '{name}'")
        return char_data

    def get_character(self, name: str) -> Optional[Dict[str, Any]]:
        return self.characters.get(name.lower())

    def get_prompt_description(self, name: str) -> str:
        char = self.get_character(name)
        if char:
            return char["prompt_signature"]
        return f"{name}: distinct visual features"
