#!/usr/bin/env python3
"""
environment_generation_engine.py
Generates detailed environment descriptions (type, atmosphere, weather, lighting)
based on story locations, emotion profiles, and scene descriptions.
"""
import re
from typing import Dict, Any, List

# Core environment types supported by the renderer
ENVIRONMENT_TYPES = [
    "forest", "castle", "village", "cave", "beach", "mountain", "city", "arena",
    "battlefield", "dungeon", "desert", "swamp", "glacier", "volcano", "temple", "ruins"
]

class EnvironmentGenerationEngine:
    def __init__(self):
        pass

    def generate_environment(self, location_name: str, primary_emotion: str, description: str) -> Dict[str, str]:
        """
        Maps a location name, emotion profile, and description text to a structured environment configuration.
        """
        loc_lower = location_name.lower().strip()
        desc_lower = description.lower()
        emo_lower = primary_emotion.lower()

        # 1. Determine Environment Type
        env_type = "forest" # Default
        for etype in ENVIRONMENT_TYPES:
            # Check direct match or plurals/variations (e.g. woods -> forest, castle gate -> castle)
            if etype in loc_lower or etype in desc_lower:
                env_type = etype
                break
                
        # Synonyms fallback
        if env_type == "forest":
            if any(w in loc_lower or w in desc_lower for w in ["woods", "jungle", "meadow", "meadows", "garden", "tree", "trees"]):
                env_type = "forest"
            elif any(w in loc_lower or w in desc_lower for w in ["palace", "throne room", "keep", "tower"]):
                env_type = "castle"
            elif any(w in loc_lower or w in desc_lower for w in ["town", "plaza", "house", "shop", "streets"]):
                env_type = "village"
            elif any(w in loc_lower or w in desc_lower for w in ["canyon", "cliffs", "peaks", "hill", "hills"]):
                env_type = "mountain"
            elif any(w in loc_lower or w in desc_lower for w in ["battle", "war", "army", "ambush", "clash"]):
                env_type = "battlefield"
            elif any(w in loc_lower or w in desc_lower for w in ["crypt", "tomb", "mine", "mines", "cellar"]):
                env_type = "dungeon"

        # 2. Determine Atmosphere
        atmosphere = "peaceful"
        if emo_lower == "angry":
            atmosphere = "chaotic"
        elif emo_lower == "sad":
            atmosphere = "gloomy"
        elif emo_lower == "fear":
            atmosphere = "tense"
        elif emo_lower in ("surprise", "hope"):
            atmosphere = "mystical"
        elif emo_lower == "determination":
            atmosphere = "majestic"

        # Context-based atmosphere overrides
        if any(w in desc_lower for w in ["ancient", "old", "ruins"]):
            atmosphere = "ancient"
        elif any(w in desc_lower for w in ["dark", "shadow", "shadowy"]):
            atmosphere = "ominous"
        elif any(w in desc_lower for w in ["magic", "glowing", "spell", "crystal"]):
            atmosphere = "magical"

        # 3. Determine Weather
        weather = "clear"
        if emo_lower == "sad":
            weather = "rainy"
        elif emo_lower == "angry":
            weather = "stormy"
        elif emo_lower == "fear":
            weather = "foggy"
        
        # Word overrides
        if "snowy" in loc_lower or "glacier" in loc_lower or "cold" in desc_lower:
            weather = "snowy"
        elif "rain" in desc_lower or "storm" in desc_lower:
            weather = "stormy"
        elif "fog" in desc_lower or "mist" in desc_lower:
            weather = "foggy"

        # 4. Determine Lighting
        lighting = "sunlight"
        if weather == "stormy" or weather == "foggy":
            lighting = "overcast"
        elif emo_lower == "sad":
            lighting = "overcast"
        elif emo_lower == "fear":
            lighting = "moonlight"
        elif emo_lower == "hope":
            lighting = "golden_hour"
        elif emo_lower == "surprise":
            lighting = "twilight"

        # Text overrides
        if "night" in desc_lower or "dark" in desc_lower:
            lighting = "moonlight"
        elif "sunset" in desc_lower or "golden" in desc_lower:
            lighting = "golden_hour"
        elif "sunrise" in desc_lower or "dawn" in desc_lower:
            lighting = "twilight"
        elif "candle" in desc_lower or "fire" in desc_lower or "torch" in desc_lower:
            lighting = "firelight"

        return {
            "environment_type": env_type,
            "atmosphere": atmosphere,
            "weather": weather,
            "lighting": lighting
        }

if __name__ == "__main__":
    engine = EnvironmentGenerationEngine()
    test_loc = "snowy forest"
    test_emo = "sad"
    test_desc = "A lonely knight walks slowly in the dark woods."
    res = engine.generate_environment(test_loc, test_emo, test_desc)
    import json
    print(json.dumps(res, indent=2))
