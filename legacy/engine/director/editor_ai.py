# engine/director/editor_ai.py
from engine.storyboard.movie_graph import MovieGraph

class EditorAI:
    """
    Subsystem: Editor AI
    Performs automated post-planning optimization on MovieGraph.
    Prunes duplicate consecutive framing styles and refines transitions.
    """
    def __init__(self):
        pass

    def optimize_plan(self, graph: MovieGraph):
        """Edits and improves the shot sequence plan in-place inside the MovieGraph."""
        shot_ids = sorted(list(graph.shots.keys()))
        if len(shot_ids) <= 1:
            return
            
        previous_camera_type = None
        for shot_id in shot_ids:
            shot = graph.shots[shot_id]
            current_camera_type = shot.get("camera_type")
            
            # Rule 1: Avoid consecutive identical camera layouts (jump cut prevention)
            if current_camera_type == previous_camera_type:
                # Alter current shot camera profile/type to vary pacing
                new_type = "close_up" if current_camera_type != "close_up" else "medium"
                shot["camera_type"] = new_type
                shot["lens"] = 50.0 if new_type == "close_up" else 35.0
                shot["camera_movement"] = "push_in"
                
            previous_camera_type = shot["camera_type"]
            
            # Rule 2: Ensure fast pacing for short-form clips
            if shot.get("duration", 3.0) > 6.0:
                shot["duration"] = 4.0
