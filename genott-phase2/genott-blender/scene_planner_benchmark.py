#!/usr/bin/env python3
"""
scene_planner_benchmark.py
Validates the scene_planner_v2.py with 100 stories.
Generates scene_planner_report.md.
"""
import sys
import os
import time

project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.append(project_dir)

from story_understanding_engine import StoryUnderstandingEngine
from scene_planner_v2 import ScenePlannerV2
from story_understanding_benchmark import STORIES

def run_benchmark():
    engine = StoryUnderstandingEngine()
    planner = ScenePlannerV2()

    total = len(STORIES)
    passed = 0
    failed = 0
    results = []

    total_scenes = 0
    total_duration = 0.0
    camera_counts = {}
    action_counts = {}
    mood_counts = {}

    print(f"Running Scene Planner Benchmark with {total} stories...")
    start_time = time.time()

    for idx, story in enumerate(STORIES):
        try:
            story_data = engine.understand_story(story)
            scenes = planner.plan_scenes(story_data)
            
            # Validation checks
            assert len(scenes) > 0, "No scenes generated"
            for scene in scenes:
                assert "scene_number" in scene, "Missing scene_number"
                assert "character_name" in scene, "Missing character_name"
                assert "location" in scene, "Missing location"
                assert "action" in scene, "Missing action"
                assert "camera_shot" in scene, "Missing camera_shot"
                assert "duration" in scene, "Missing duration"
                assert "mood" in scene, "Missing mood"
                assert "speed" in scene, "Missing speed"
                assert "narration" in scene, "Missing narration"

                # Metric tracking
                camera_shot = scene["camera_shot"]
                action = scene["action"]
                mood = scene["mood"]
                duration = scene["duration"]

                camera_counts[camera_shot] = camera_counts.get(camera_shot, 0) + 1
                action_counts[action] = action_counts.get(action, 0) + 1
                mood_counts[mood] = mood_counts.get(mood, 0) + 1
                total_duration += duration

            total_scenes += len(scenes)
            passed += 1

            results.append({
                "index": idx + 1,
                "story": story,
                "scenes_count": len(scenes),
                "scenes": scenes,
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

    # Format distributions for report
    camera_dist = "\n".join([f"- **{cam}**: {count}" for cam, count in sorted(camera_counts.items(), key=lambda x: x[1], reverse=True)])
    action_dist = "\n".join([f"- **{act}**: {count}" for act, count in sorted(action_counts.items(), key=lambda x: x[1], reverse=True)])
    mood_dist = "\n".join([f"- **{m}**: {count}" for m, count in sorted(mood_counts.items(), key=lambda x: x[1], reverse=True)])

    report_content = f"""# Scene Planner V2 Benchmark Report

## Overview
- **Planner Version**: 2.0.0 (Rule-based Event-to-Scene Mapper)
- **Total Test Stories**: {total}
- **Passed**: {passed}
- **Failed**: {failed}
- **Success Rate**: {success_rate:.1f}%
- **Total Execution Time**: {elapsed_time:.3f} seconds

## Scene Generation Metrics
- **Total Scenes Generated**: {total_scenes} (Avg: {total_scenes/total:.1f}/story)
- **Total Movie Planned Duration**: {total_duration:.1f} seconds (Avg: {total_duration/total:.1f} seconds/story)

### Camera Shot Distribution
{camera_dist}

### Action Distribution
{action_dist}

### Mood/Emotion Distribution
{mood_dist}

## Detailed Results
| ID | Story | Status | Scenes Planned | Total Duration | Cameras Used | Actions Used |
|---|---|---|---|---|---|---|
"""
    for r in results:
        if r["status"] == "PASS":
            scenes = r["scenes"]
            cams = ", ".join(list(set([s["camera_shot"] for s in scenes])))
            acts = ", ".join(list(set([s["action"] for s in scenes])))
            dur = sum([s["duration"] for s in scenes])
            report_content += f"| {r['index']} | {r['story']} | {r['status']} | {r['scenes_count']} | {dur:.1f}s | {cams} | {acts} |\n"
        else:
            report_content += f"| {r['index']} | {r['story']} | {r['status']} (Error: {r['error']}) | - | - | - | - |\n"

    # Write report locally
    local_report_path = os.path.join(project_dir, "scene_planner_report.md")
    with open(local_report_path, "w") as f:
        f.write(report_content)
    print(f"Local report generated: {local_report_path}")

    # Write report to Artifact Directory
    artifact_dir = "PROJECT_ROOT/.gemini/antigravity-cli/brain/3496fc80-3ea9-4817-8bc4-b4e0e2ff7b60"
    if os.path.exists(artifact_dir):
        artifact_report_path = os.path.join(artifact_dir, "scene_planner_report.md")
        with open(artifact_report_path, "w") as f:
            f.write(report_content)
        print(f"Artifact report generated: {artifact_report_path}")

    print(f"Benchmark finished: {passed}/{total} passed. Success Rate: {success_rate:.1f}%")
    return success_rate == 100

if __name__ == "__main__":
    success = run_benchmark()
    sys.exit(0 if success else 1)
