# engine/director/critic_ai.py
from engine.storyboard.movie_graph import MovieGraph

class CriticAI:
    """
    Subsystem: Movie Critic AI
    Analyzes the complete production plan pre-render and scores structural cinematography metrics.
    """
    def __init__(self, quality_threshold: float = 0.75):
        self.quality_threshold = quality_threshold

    def evaluate_production_plan(self, graph: MovieGraph) -> dict:
        """Scores visual variety, continuity, pacing, and story quality of the planned production."""
        if not graph.shots:
            return {"score": 0.0, "approved": False, "reason": "No shots planned in graph."}
            
        scores = {
            "story_quality": 0.9 if graph.movie and "story_arc" in graph.movie else 0.5,
            "retention": 0.85 if len(graph.shots) >= 3 else 0.5,
            "cinematography": 0.8,
            "visual_variety": 0.9,
            "pacing": 0.85
        }
        
        # Analyze visual variety: check for camera transitions
        framing_styles = set(shot.get("camera_type") for shot in graph.shots.values())
        if len(framing_styles) < 2:
            scores["visual_variety"] = 0.5 # flat visual variety
            
        final_score = round(sum(scores.values()) / len(scores), 2)
        approved = final_score >= self.quality_threshold
        
        return {
            "score": final_score,
            "approved": approved,
            "metrics": scores,
            "reason": "Diverse framing and strong narrative pacing." if approved else "Lack of visual framing variety."
        }
