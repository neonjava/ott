# engine/director/story_ai.py
import re
from engine.storyboard.movie_graph import MovieGraph

class StoryAI:
    """
    Subsystem: Story AI
    Evaluates and plans structured narrative arcs (Beginning, Conflict, Escalation, Climax, Resolution)
    and updates the MovieGraph.
    """
    def __init__(self):
        pass

    def plan_story(self, graph: MovieGraph, idea_text: str):
        """Generates narrative acts and outline, writing directly to the MovieGraph."""
        idea_lower = idea_text.lower()
        title = "Iron and Moss" if "robot" in idea_lower else "The Journey"
        genre = "Sci-Fi" if "robot" in idea_lower or "space" in idea_lower else "Drama"
        
        # Structure the Story Arc
        story_arc = {
            "beginning": "A quiet environment setting the scene and introducing our character.",
            "conflict": "The discovery of an unexpected element that disrupts the peace.",
            "escalation": "An attempt to interact or resolve the discovery, raising the emotional stakes.",
            "climax": "A high-tension moment of interaction or confrontation.",
            "resolution": "A final quiet look at the resulting transformation."
        }
        
        # Determine characters and locations
        characters = ["humanoid"]
        if "robot" in idea_lower:
            characters.append("robot")
        elif "knight" in idea_lower:
            characters = ["knight"]
            
        locations = ["forest"]
        
        graph.set_movie(title, genre, tone="mysterious", duration=30.0)
        
        # Save story outline to movie graph
        graph.movie["story_arc"] = story_arc
        graph.movie["characters"] = characters
        graph.movie["locations"] = locations
        
        for c in characters:
            graph.add_character(f"char_{c}", c)
        for l in locations:
            graph.add_location(f"loc_{l}", l)
