# engine/director/director_agent.py
import os
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class DirectorAgent:
    """
    Autonomous AI Film Director for GenOTT V2.
    Analyzes screenplays, detects emotional arcs, identifies story beats, determines pacing,
    selects camera styles, chooses lighting moods, decides shot durations, controls scene transitions,
    and produces a comprehensive `DirectorPlan.json`.
    """

    def generate_director_plan(self, screenplay: Dict[str, Any], output_path: Optional[str] = None) -> Dict[str, Any]:
        title = screenplay.get("title", "Untitled AI Production")
        logline = screenplay.get("logline", "An epic autonomous AI short film.")
        acts = screenplay.get("acts", screenplay.get("scenes", []))

        scene_plans = []
        overall_emotional_arc = []

        for idx, act in enumerate(acts, start=1):
            act_title = act.get("title", f"Act {idx}")
            shots = act.get("shots", [])
            shot_count = len(shots) if isinstance(shots, list) else 4

            # Determine Scene Objective & Emotional Intensity (1.0 to 10.0 scale)
            intensity = round(3.0 + (idx * 1.2), 1)
            if idx == len(acts) - 1:
                intensity = 9.8  # Climax
            elif idx == len(acts):
                intensity = 5.0  # Resolution

            overall_emotional_arc.append({"act_id": idx, "act_title": act_title, "intensity": intensity})

            # Color palette & Visual strategy based on narrative act progression
            color_palettes = [
                "Deep Obsidian & Cold Cyan Nebulae",
                "Monochromatic Tactical Charcoal",
                "High-Contrast Crimson & Warning Amber",
                "Radiant Plasma Gold & Shimmering Violet",
                "Sunburst Amber & Crystal Diamond Light",
                "Warm Golden Hour & Cosmic Horizon Blue"
            ]
            palette = color_palettes[(idx - 1) % len(color_palettes)]

            camera_strategies = [
                "Wide Establishing Glides & Slow Push-Ins",
                "Over-the-Shoulder Tracking & Macro Close-Ups",
                "Dynamic Handheld Shake & Sudden Dolly Zooms",
                "Fast Forward Superluminal Tracking & Crane Tilts",
                "360-Degree Orbital Parallax & Descending Crane Sweeps",
                "Gentle Hero Low Angle Push-In & Slow Fade Transitions"
            ]
            cam_strat = camera_strategies[(idx - 1) % len(camera_strategies)]

            lighting_strategies = [
                "Volumetric Cold Blue Rim Lighting",
                "Sharp Tactical Key Lighting with Deep Shadows",
                "Pulsing Emergency Strobe & High-Contrast Rim",
                "Radiant Plasma Glow & Anamorphic Lens Flare",
                "Twin Sun Warm Golden Key & Volumetric Rays",
                "Soft Natural Ambient Glow & Cinematic Rim"
            ]
            lighting_strat = lighting_strategies[(idx - 1) % len(lighting_strategies)]

            scene_plan = {
                "scene_id": idx,
                "act_title": act_title,
                "scene_objective": f"Fulfill act objective for '{act_title}'",
                "emotional_intensity": intensity,
                "pacing": "Rapid Action" if intensity > 8.0 else ("Slow Suspense" if intensity < 4.0 else "Balanced Narrative"),
                "visual_style": "Hyper-realistic Sci-Fi Masterpiece, 8K Photorealistic",
                "color_palette": palette,
                "camera_strategy": cam_strat,
                "lighting_strategy": lighting_strat,
                "regeneration_criteria": {
                    "min_quality_score": 0.80,
                    "max_motion_blur_artifact": 0.15,
                    "require_character_consistency": True
                }
            }
            scene_plans.append(scene_plan)

        director_plan = {
            "title": title,
            "logline": logline,
            "director_vision": "Create a high-impact, emotionally resonant 2-minute sci-fi cinematic experience with seamless visual continuity and dynamic camera movement.",
            "emotional_arc": overall_emotional_arc,
            "scene_plans": scene_plans
        }

        if output_path:
            output_abs = os.path.abspath(output_path)
            os.makedirs(os.path.dirname(output_abs), exist_ok=True)
            with open(output_abs, "w") as f:
                json.dump(director_plan, f, indent=2)
            logger.info(f"[DirectorAgent] Exported complete DirectorPlan to {output_abs}")

        return director_plan

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
            f"Director Pacing Assessment: {pacing['pacing_notes']} (Pacing Score: {pacing['pacing_score']})",
            f"Director MovieGraph Assessment: {len(review['weak_scenes_detected'])} weak scenes detected."
        ]
        notes.extend(review["improvement_suggestions"])
        return notes
