#!/usr/bin/env python3
"""
environment_generation_benchmark.py
Generates environment details for 100 test stories.
Validates the EnvironmentGenerationEngine and outputs environment_generation_report.md.
"""
import sys
import os
import time

project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.append(project_dir)

from story_understanding_engine import StoryUnderstandingEngine
from environment_generation_engine import EnvironmentGenerationEngine
from story_understanding_benchmark import STORIES

def run_benchmark():
    su_engine = StoryUnderstandingEngine()
    env_engine = EnvironmentGenerationEngine()

    total = len(STORIES)
    passed = 0
    failed = 0
    results = []

    type_counts = {}
    atmos_counts = {}
    weather_counts = {}
    lighting_counts = {}

    print(f"Running Environment Generation Engine Benchmark with {total} stories...")
    start_time = time.time()

    for idx, story in enumerate(STORIES):
        try:
            story_data = su_engine.understand_story(story)
            # Find primary location and emotion
            loc_name = story_data["locations"][0]["name"] if story_data["locations"] else "environment"
            primary_emo = story_data["emotions"][0]["emotion"] if story_data["emotions"] else "neutral"
            
            env_config = env_engine.generate_environment(loc_name, primary_emo, story)
            
            # Validation checks
            assert "environment_type" in env_config, "Missing environment_type"
            assert "atmosphere" in env_config, "Missing atmosphere"
            assert "weather" in env_config, "Missing weather"
            assert "lighting" in env_config, "Missing lighting"

            # Metrics
            etype = env_config["environment_type"]
            atmos = env_config["atmosphere"]
            weather = env_config["weather"]
            lighting = env_config["lighting"]

            type_counts[etype] = type_counts.get(etype, 0) + 1
            atmos_counts[atmos] = atmos_counts.get(atmos, 0) + 1
            weather_counts[weather] = weather_counts.get(weather, 0) + 1
            lighting_counts[lighting] = lighting_counts.get(lighting, 0) + 1

            passed += 1
            results.append({
                "index": idx + 1,
                "story": story,
                "location": loc_name,
                "emotion": primary_emo,
                "config": env_config,
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

    # Format distributions
    type_dist = "\n".join([f"- **{k}**: {v}" for k, v in sorted(type_counts.items(), key=lambda x: x[1], reverse=True)])
    atmos_dist = "\n".join([f"- **{k}**: {v}" for k, v in sorted(atmos_counts.items(), key=lambda x: x[1], reverse=True)])
    weather_dist = "\n".join([f"- **{k}**: {v}" for k, v in sorted(weather_counts.items(), key=lambda x: x[1], reverse=True)])
    lighting_dist = "\n".join([f"- **{k}**: {v}" for k, v in sorted(lighting_counts.items(), key=lambda x: x[1], reverse=True)])

    report_content = f"""# Environment Generation Engine Benchmark Report

## Overview
- **Engine Version**: 1.0.0 (Rules-based Atmosphere/Weather/Lighting Classifier)
- **Total Test Stories**: {total}
- **Passed**: {passed}
- **Failed**: {failed}
- **Success Rate**: {success_rate:.1f}%
- **Execution Time**: {elapsed_time:.4f} seconds

## Environmental Distributions

### Environment Type
{type_dist}

### Atmosphere
{atmos_dist}

### Weather
{weather_dist}

### Lighting
{lighting_dist}

## Detailed Results
| ID | Story | Location | Emotion | Generated Config | Status |
|---|---|---|---|---|---|
"""
    for r in results:
        if r["status"] == "PASS":
            c = r["config"]
            cfg_str = f"Type: {c['environment_type']}, Atmos: {c['atmosphere']}, Weather: {c['weather']}, Light: {c['lighting']}"
            report_content += f"| {r['index']} | {r['story']} | {r['location']} | {r['emotion']} | {cfg_str} | {r['status']} |\n"
        else:
            report_content += f"| {r['index']} | {r['story']} | - | - | Error: {r['error']} | {r['status']} |\n"

    # Write report locally
    local_report_path = os.path.join(project_dir, "environment_generation_report.md")
    with open(local_report_path, "w") as f:
        f.write(report_content)
    print(f"Local report generated: {local_report_path}")

    # Write report to Artifact Directory
    artifact_dir = "PROJECT_ROOT/.gemini/antigravity-cli/brain/3496fc80-3ea9-4817-8bc4-b4e0e2ff7b60"
    if os.path.exists(artifact_dir):
        artifact_report_path = os.path.join(artifact_dir, "environment_generation_report.md")
        with open(artifact_report_path, "w") as f:
            f.write(report_content)
        print(f"Artifact report generated: {artifact_report_path}")

    return success_rate == 100.0

if __name__ == "__main__":
    success = run_benchmark()
    sys.exit(0 if success else 1)
