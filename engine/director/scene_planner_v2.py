#!/usr/bin/env python3
"""
scene_planner_v2.py
Converts story understanding output into sequential, detailed movie scenes.
Supports camera mapping, duration mapping, dialogue extraction, and visual configurations.
"""
from typing import Dict, Any, List

class ScenePlannerV2:
    def __init__(self):
        # Maps action keys to camera shots
        self.camera_map = {
            "walk": "cinematic wide",
            "run": "close-up tracking shot",
            "jump": "low-angle dramatic wide shot",
            "attack": "low-angle dramatic wide shot",
            "wave": "rotating orbit shot around the character",
            "duck": "close-up helmet shot",
            "enter": "cinematic wide",
            "discover": "rotating orbit shot around the character",
            "idle": "cinematic wide",
            "talk": "close-up helmet shot",
            "follow": "close-up tracking shot",
            "help": "rotating orbit shot around the character"
        }

        # Default voice map based on character names
        self.voice_map = {
            "anime_girl": "en-US-JennyNeural",
            "anime_boy": "en-US-GuyNeural",
            "knight": "en-US-ChristopherNeural",
            "mage": "en-US-EricNeural",
            "robot": "en-US-SteffanNeural",
            "humanoid": "en-US-ChristopherNeural",
            "fox": "en-US-JennyNeural",
            "thor": "en-US-ChristopherNeural",
            "tony_stark": "en-US-GuyNeural",
            "hulk": "en-US-GuyNeural"
        }

    def extract_dialogue_from_text(self, text: str, character: str) -> Dict[str, Any]:
        """Extracts text inside quotes as a dialogue line if present."""
        import re
        quotes = re.findall(r'["\'](.*?)(?:["\']|$)', text)
        if quotes:
            dialogue_text = quotes[0].strip()
            voice = self.voice_map.get(character.lower(), "en-US-ChristopherNeural")
            return {
                "speaker": character,
                "text": dialogue_text,
                "voice_profile": voice
            }
        return None

    def plan_scenes(self, story_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Converts story understanding output (events, timeline, characters, etc.) into sequenced scenes.
        """
        events = story_data.get("events", [])
        scenes = []

        for idx, event in enumerate(events):
            actor = event.get("actor", "humanoid")
            action = event.get("action", "idle")
            location = event.get("location", "environment")
            mood = event.get("emotion", "neutral")
            speed = event.get("speed", "normal")
            description = event.get("description", "")
            target = event.get("target")

            # 1. Determine camera shot
            camera_shot = self.camera_map.get(action, "cinematic wide")
            if mood == "sad" and action == "idle":
                camera_shot = "close-up helmet shot" # dramatic close-up for emotion

            # 2. Determine duration based on action and speed modifier
            duration = 4.0
            if action == "walk":
                duration = 5.0 if speed == "normal" else (7.0 if speed == "slow" else 3.5)
            elif action == "run":
                duration = 4.0 if speed == "normal" else (5.5 if speed == "slow" else 3.0)
            elif action == "attack":
                duration = 4.5
            elif action == "talk":
                duration = 5.0
            elif action == "wave":
                duration = 3.5

            # 3. Dialogue extraction
            dialogue = self.extract_dialogue_from_text(description, actor)

            # 4. Narration and visual description
            narration = description
            visual_desc = f"The {actor} is seen performing {action} in the {location}."
            if target:
                visual_desc += f" Target is {target}."

            scene_plan = {
                "scene_number": idx + 1,
                "character_name": actor,
                "location": location,
                "action": action,
                "camera_shot": camera_shot,
                "duration": duration,
                "dialogue": dialogue,
                "narration": narration,
                "visual_description": visual_desc,
                "mood": mood,
                "speed": speed
            }
            scenes.append(scene_plan)

        return scenes

if __name__ == "__main__":
    import json
    planner = ScenePlannerV2()
    sample_story_data = {
      "characters": [{"name": "knight", "modifiers": ["lonely"]}, {"name": "dragon", "modifiers": ["ancient"]}],
      "locations": [{"name": "forest", "modifiers": []}],
      "events": [
        {
          "id": "event_1",
          "actor": "knight",
          "action": "walk",
          "target": None,
          "location": "forest",
          "emotion": "sad",
          "speed": "slow",
          "description": "A lonely knight walks through a forest"
        },
        {
          "id": "event_2",
          "actor": "knight",
          "action": "discover",
          "target": "dragon",
          "location": "forest",
          "emotion": "surprise",
          "speed": "normal",
          "description": "and discovers a dragon"
        }
      ]
    }
    result = planner.plan_scenes(sample_story_data)
    print(json.dumps(result, indent=2))
