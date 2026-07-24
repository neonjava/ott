# engine/director/director_agent.py
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class DirectorAgent:
    """
    Autonomous AI Film Director for GenOTT V2.
    Reads screenplays, evaluates narrative pacing, reviews MovieGraph nodes,
    detects weak scenes, generates production notes, and suggests improvements.
    """

    def analyze_screenplay_pacing(self, screenplay: Dict[str, Any]) -> Dict[str, Any]:
        shots = screenplay.get("shots", [])
        total_duration = sum(s.get("duration", 5.0) for s in shots)
        num_shots = len(shots)
        avg_shot_length = round(total_duration / max(1, num_shots), 2)

        pacing_score = 0.90
        pacing_notes = "Balanced dramatic rhythm."
        if avg_shot_length > 8.0:
            pacing_score = 0.70
            pacing_notes = "Slow pacing detected. Recommend adding dynamic camera movement or quickening cuts."
        elif avg_shot_length < 3.0:
            pacing_score = 0.75
            pacing_notes = "Rapid cutting detected. Ensure key story beats have breath."

        return {
            "total_duration_sec": total_duration,
            "num_shots": num_shots,
            "avg_shot_length_sec": avg_shot_length,
            "pacing_score": pacing_score,
            "pacing_notes": pacing_notes
        }

    def review_movie_graph(self, movie_graph: Dict[str, Any]) -> Dict[str, Any]:
        shots = movie_graph.get("shots", [])
        weak_scenes = []
        improvements = []

        for idx, shot in enumerate(shots, start=1):
            action = shot.get("action", "")
            framing = shot.get("framing", "")
            if len(action) < 15:
                weak_scenes.append({"shot_id": idx, "reason": "Action description lacks sensory/visual depth."})
                improvements.append(f"Shot {idx}: Enrich action details with lighting and atmospheric specs.")
            if not framing:
                improvements.append(f"Shot {idx}: Assign explicit cinematography framing.")

        return {
            "total_reviewed": len(shots),
            "weak_scenes_detected": weak_scenes,
            "improvement_suggestions": improvements,
            "director_approval": len(weak_scenes) == 0
        }

    def generate_production_notes(self, screenplay: Dict[str, Any], movie_graph: Dict[str, Any]) -> List[str]:
        pacing = self.analyze_screenplay_pacing(screenplay)
        review = self.review_movie_graph(movie_graph)
        
        notes = [
            f"Director Note: Screenplay pacing score: {pacing['pacing_score']*100:.0f}% ({pacing['pacing_notes']})",
            f"Director Note: {len(review['weak_scenes_detected'])} weak scene transitions flagged for enhancement."
        ]
        notes.extend(review["improvement_suggestions"])
        return notes
