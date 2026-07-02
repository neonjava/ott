# engine/director/scene_ai.py
from engine.storyboard.movie_graph import MovieGraph

class SceneAI:
    """
    Subsystem: Scene AI
    Transforms story outlines and characters from the MovieGraph into structured scenes.
    """
    def __init__(self):
        pass

    def plan_scenes(self, graph: MovieGraph):
        """Converts the Story Arc in MovieGraph into sequential scenes."""
        if not graph.movie or "story_arc" not in graph.movie:
            raise ValueError("MovieGraph does not contain a story_arc to plan scenes from.")
            
        story_arc = graph.movie["story_arc"]
        char_list = list(graph.characters.keys())
        primary_char = char_list[0] if char_list else "char_humanoid"
        location_id = list(graph.locations.keys())[0] if list(graph.locations.keys()) else "loc_forest"
        
        # We create 3 scenes corresponding to Beginning, Conflict/Climax, and Resolution
        scenes_data = [
            {
                "id": "scene_01",
                "purpose": "Introduce the character entering the environment",
                "emotion": "mysterious",
                "location_id": location_id,
                "weather": "foggy",
                "lighting": "colder",
                "duration": 6.0
            },
            {
                "id": "scene_02",
                "purpose": "A high-tension moment discovering the subject",
                "emotion": "surprise",
                "location_id": location_id,
                "weather": "clear",
                "lighting": "dramatic",
                "duration": 8.0
            },
            {
                "id": "scene_03",
                "purpose": "Resolution and reflection on the encounter",
                "emotion": "hopeful",
                "location_id": location_id,
                "weather": "clear",
                "lighting": "cheerful",
                "duration": 6.0
            }
        ]
        
        for s in scenes_data:
            graph.add_scene(
                scene_id=s["id"],
                purpose=s["purpose"],
                emotion=s["emotion"],
                location_id=s["location_id"],
                weather=s["weather"],
                duration=s["duration"]
            )
            # Add lighting metadata
            graph.scenes[s["id"]]["lighting"] = s["lighting"]
