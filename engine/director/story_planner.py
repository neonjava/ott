# engine/director/story_planner.py
import re
from typing import Dict, Any, List

class StoryPlanner:
    """
    Subsystem: Story Planner
    Converts a raw user idea string into a structured screenplay planning outline.
    Optimized for 15-60 second short-form cinematic videos.
    """
    def __init__(self):
        pass

    def plan_story(self, idea_text: str) -> Dict[str, Any]:
        """Heuristically parses the user prompt/idea to build a structured story outline."""
        # Simple extraction rules
        idea_lower = idea_text.lower()
        
        # Genre detection
        genre = "Sci-Fi" if "robot" in idea_lower or "space" in idea_lower or "cyber" in idea_lower else "Drama"
        if "action" in idea_lower or "fight" in idea_lower or "attack" in idea_lower:
            genre = "Action"
        elif "magic" in idea_lower or "wizard" in idea_lower or "dragon" in idea_lower:
            genre = "Fantasy"
            
        # Hook and Ending generation
        hook = f"Introduce the main character encountering a sudden shift in their surroundings."
        ending = f"A resolution where the discovery changes the character's journey."
        
        # Extract location nouns
        locations = ["forest"]
        loc_matches = re.findall(r"in the (\w+)|through the (\w+)|inside the (\w+)", idea_lower)
        for match in loc_matches:
            found = next((m for m in match if m), None)
            if found and found not in locations:
                locations.append(found)

        # Extract character nouns
        characters = ["humanoid"]
        if "knight" in idea_lower:
            characters = ["knight"]
        elif "mage" in idea_lower:
            characters = ["mage"]
            
        if "robot" in idea_lower:
            characters.append("robot")
        elif "dragon" in idea_lower:
            characters.append("dragon")
            
        title = "The Discovery"
        if "robot" in idea_lower:
            title = "Iron and Moss"
        elif "knight" in idea_lower:
            title = "A Knight's Path"
            
        return {
            "title": title,
            "genre": genre,
            "tone": "mysterious" if "discover" in idea_lower else "epic",
            "audience": "general short-form",
            "target_duration": 30.0,
            "hook": hook,
            "ending": ending,
            "characters": characters,
            "locations": locations,
            "raw_idea": idea_text
        }
