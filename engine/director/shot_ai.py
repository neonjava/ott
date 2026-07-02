# engine/director/shot_ai.py
from engine.storyboard.movie_graph import MovieGraph

class ShotAI:
    """
    Subsystem: Shot AI / Cinematographer AI
    Reads scenes from MovieGraph and designs motivated shots using camera grammar rules.
    """
    def __init__(self):
        pass

    def plan_shots(self, graph: MovieGraph):
        """Converts scene lists in MovieGraph into shot specifications."""
        if not graph.scenes:
            raise ValueError("MovieGraph does not contain any scenes to plan shots from.")
            
        char_list = list(graph.characters.keys())
        primary_char = char_list[0] if char_list else "char_humanoid"
        
        shot_counter = 1
        for scene_id, scene in list(graph.scenes.items()):
            # Plan 2 shots per scene to capture the pacing
            # Shot A: Establishing / Medium
            shot_a_id = f"shot_{shot_counter:02d}"
            graph.add_shot(
                shot_id=shot_a_id,
                scene_id=scene_id,
                camera_type="wide" if scene_id == "scene_01" else "medium",
                camera_profile="tripod" if scene["emotion"] == "hopeful" else "steadicam",
                duration=scene["duration"] / 2.0,
                continuity={"seed": 100 + shot_counter, "environmental_seed": 200 + shot_counter}
            )
            
            # Enrich with Cinematography specs
            graph.shots[shot_a_id].update({
                "camera_movement": "static" if scene_id == "scene_03" else "pan",
                "composition": "leading_lines" if scene_id == "scene_01" else "rule_of_thirds",
                "lens": 28.0 if scene_id == "scene_01" else 35.0,
                "transition": "fade" if scene_id == "scene_01" else "cut",
                "actor_focus": primary_char,
                "emotion": scene["emotion"],
                "importance": "high" if scene_id == "scene_02" else "medium"
            })
            shot_counter += 1
            
            # Shot B: Close Up / Detail
            shot_b_id = f"shot_{shot_counter:02d}"
            graph.add_shot(
                shot_id=shot_b_id,
                scene_id=scene_id,
                camera_type="close_up",
                camera_profile="handheld" if scene["emotion"] == "surprise" else "dolly",
                duration=scene["duration"] / 2.0,
                continuity={"seed": 100 + shot_counter, "environmental_seed": 200 + shot_counter}
            )
            
            graph.shots[shot_b_id].update({
                "camera_movement": "push_in" if scene["emotion"] == "surprise" else "static",
                "composition": "rule_of_thirds",
                "lens": 50.0,
                "transition": "cut",
                "actor_focus": primary_char,
                "emotion": scene["emotion"],
                "importance": "high" if scene["emotion"] == "surprise" else "medium"
            })
            shot_counter += 1
