#!/usr/bin/env python3
"""
director_v2_benchmark.py
Validates the DirectorV2 system with 100 generated storyboards.
Outputs director_v2_report.md.
"""
import sys
import os
import time
import json

project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.append(project_dir)

from story_understanding_engine import StoryUnderstandingEngine
from scene_planner_v2 import ScenePlannerV2
from character_interaction_engine import CharacterInteractionEngine
from environment_generation_engine import EnvironmentGenerationEngine
from director_v2 import DirectorV2
from story_understanding_benchmark import STORIES

def run_benchmark():
    su_engine = StoryUnderstandingEngine()
    scene_planner = ScenePlannerV2()
    interaction_engine = CharacterInteractionEngine()
    env_engine = EnvironmentGenerationEngine()
    director = DirectorV2()

    # Expand CHARACTERS_LEXICON dynamically for custom character matches in test pool
    for story in STORIES:
        from character_interaction_engine import CHARACTERS_LEXICON as CI_LEX
        from story_understanding_engine import CHARACTERS_LEXICON as SU_LEX
        # Parse characters in story and add to dictionaries
        words = story.lower().split()
        for w in words:
            # Clean punctuation
            w_clean = "".join(c for c in w if c.isalnum())
            if w_clean in ["samurai", "ninja", "soldier", "captain", "villager", "traveler", "merchant", "elf", "dwarf", "wolf", "dog", "hulk", "giant", "monster"]:
                CI_LEX.add(w_clean)
                SU_LEX.add(w_clean)

    total = len(STORIES)
    passed = 0
    failed = 0
    results = []

    shot_counts = {}
    movement_counts = {}
    pacing_counts = {}
    transition_counts = {}
    total_duration = 0.0
    importance_scores = []

    print(f"Running Director AI V2 Benchmark with {total} storyboards...")
    start_time = time.time()

    for idx, story in enumerate(STORIES):
        try:
            # 1. Story Understanding
            story_data = su_engine.understand_story(story)
            # 2. Scene Planner
            planned_scenes = scene_planner.plan_scenes(story_data)
            # 3. Character Interactions
            interactions = interaction_engine.detect_interactions(story_data)
            
            # 4. Environments for all locations
            env_configs = {}
            for loc in story_data.get("locations", []):
                name = loc["name"]
                emo = story_data["emotions"][0]["emotion"] if story_data["emotions"] else "neutral"
                env_configs[name] = env_engine.generate_environment(name, emo, story)

            # Pass planned scenes in a wrapper
            storyboard = {"scenes": planned_scenes}

            # 5. Direct Storyboard
            directed = director.direct_storyboard(storyboard, interactions, env_configs)

            # Validation checks
            assert "scenes" in directed, "Missing directed scenes"
            assert "transitions" in directed, "Missing directed transitions"
            for scene in directed["scenes"]:
                assert "camera_shot" in scene, "Missing camera_shot"
                assert "camera_movement" in scene, "Missing camera_movement"
                assert "pacing" in scene, "Missing pacing"
                assert "duration" in scene, "Missing duration"
                assert "transition" in scene, "Missing transition"
                assert "importance_score" in scene, "Missing importance_score"

                # Metric gathering
                shot = scene["camera_shot"]
                move = scene["camera_movement"]
                pace = scene["pacing"]
                trans = scene["transition"]
                dur = scene["duration"]
                imp = scene["importance_score"]

                shot_counts[shot] = shot_counts.get(shot, 0) + 1
                movement_counts[move] = movement_counts.get(move, 0) + 1
                pacing_counts[pace] = pacing_counts.get(pace, 0) + 1
                transition_counts[trans] = transition_counts.get(trans, 0) + 1
                total_duration += dur
                importance_scores.append(imp)

            passed += 1
            results.append({
                "index": idx + 1,
                "story": story,
                "scenes_directed": len(directed["scenes"]),
                "directed_scenes": directed["scenes"],
                "status": "PASS"
            })
        except Exception as e:
            failed += 1
            results.append({
                "index": idx + 1,
                "story": story,
                "error": str(e),
                "status": "FAIL"
            })

    elapsed_time = time.time() - start_time
    success_rate = (passed / total) * 100
    avg_importance = sum(importance_scores)/len(importance_scores) if importance_scores else 0

    # Format distributions
    shot_dist = "\n".join([f"- **{k}**: {v}" for k, v in sorted(shot_counts.items(), key=lambda x: x[1], reverse=True)])
    movement_dist = "\n".join([f"- **{k}**: {v}" for k, v in sorted(movement_counts.items(), key=lambda x: x[1], reverse=True)])
    pacing_dist = "\n".join([f"- **{k}**: {v}" for k, v in sorted(pacing_counts.items(), key=lambda x: x[1], reverse=True)])
    trans_dist = "\n".join([f"- **{k}**: {v}" for k, v in sorted(transition_counts.items(), key=lambda x: x[1], reverse=True)])

    report_content = f"""# Director AI V2 Benchmark Report

## Overview
- **Director Version**: 2.0.0 (Emotion-Interaction-Environment Informed Cinematic Director)
- **Total Storyboards Directed**: {total}
- **Passed**: {passed}
- **Failed**: {failed}
- **Success Rate**: {success_rate:.1f}%
- **Average Scene Importance Score**: {avg_importance:.2f}
- **Total Directing Time**: {elapsed_time:.4f} seconds

## Cinematic Decisions Distributions

### Camera Shot Types
{shot_dist}

### Camera Movements
{movement_dist}

### Scene Pacing
{pacing_dist}

### Transitions
{trans_dist}

## Detailed Results
| ID | Story | Scenes Directed | Total Film Duration | Avg Scene Importance | Primary Shots |
|---|---|---|---|---|---|
"""
    for r in results:
        if r["status"] == "PASS":
            scenes = r["directed_scenes"]
            avg_imp_scene = sum(s["importance_score"] for s in scenes) / len(scenes)
            dur = sum(s["duration"] for s in scenes)
            shots_used = ", ".join(list(set(s["camera_shot"] for s in scenes)))
            report_content += f"| {r['index']} | {r['story']} | {r['scenes_directed']} | {dur:.1f}s | {avg_imp_scene:.2f} | {shots_used} |\n"
        else:
            report_content += f"| {r['index']} | {r['story']} | - | - | - | Error: {r['error']} |\n"

    # Write report locally
    local_report_path = os.path.join(project_dir, "director_v2_report.md")
    with open(local_report_path, "w") as f:
        f.write(report_content)
    print(f"Local report generated: {local_report_path}")

    # Write report to Artifact Directory
    artifact_dir = "PROJECT_ROOT/.gemini/antigravity-cli/brain/3496fc80-3ea9-4817-8bc4-b4e0e2ff7b60"
    if os.path.exists(artifact_dir):
        artifact_report_path = os.path.join(artifact_dir, "director_v2_report.md")
        with open(artifact_report_path, "w") as f:
            f.write(report_content)
        print(f"Artifact report generated: {artifact_report_path}")

    return success_rate == 100.0

if __name__ == "__main__":
    success = run_benchmark()
    sys.exit(0 if success else 1)
