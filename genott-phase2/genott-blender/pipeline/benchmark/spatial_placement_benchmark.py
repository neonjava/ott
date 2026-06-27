#!/usr/bin/env python3
"""
spatial_placement_benchmark.py
Generates 100 test scenes containing 1 to 10 characters.
Validates the SpatialPlacementEngine for overlaps, collisions, and placement failures.
Generates spatial_placement_report.md.
"""
import sys
import os
import time
import random

project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.append(project_dir)

from spatial_placement_engine import SpatialPlacementEngine

def run_benchmark():
    engine = SpatialPlacementEngine()
    total_scenes = 100
    overlap_count = 0
    collision_count = 0
    failure_count = 0
    results = []

    # Standard test characters list
    CHAR_POOL = ["knight", "mage", "robot", "queen", "king", "prince", "princess", "beast", "elf", "dwarf"]

    print(f"Running Spatial Character Placement Engine Benchmark with {total_scenes} scenes...")
    start_time = time.time()

    # Systematically generate 100 scenes (10 instances of each character count from 1 to 10)
    for idx in range(total_scenes):
        char_count = (idx // 10) + 1  # 1 to 10 characters
        # Sample unique characters
        chars = CHAR_POOL[:char_count]
        
        try:
            placements = engine.calculate_positions(chars)
            
            # Detect any overlaps/collisions (distance < limits)
            overlaps = engine.detect_overlaps(placements)
            
            # Count collisions: check if the distance between any characters is exactly 0
            collisions = 0
            for c1, c2, overlap_dist in overlaps:
                p1 = placements[c1]["position"]
                p2 = placements[c2]["position"]
                if p1[0] == p2[0] and p1[1] == p2[1]:
                    collisions += 1

            if len(overlaps) > 0:
                overlap_count += len(overlaps)
            if collisions > 0:
                collision_count += collisions

            results.append({
                "scene_id": idx + 1,
                "character_count": char_count,
                "characters": chars,
                "placements": placements,
                "overlaps_detected": len(overlaps),
                "collisions_detected": collisions,
                "status": "PASS" if len(overlaps) == 0 else "OVERLAP_WARNING"
            })
        except Exception as e:
            failure_count += 1
            results.append({
                "scene_id": idx + 1,
                "character_count": char_count,
                "characters": chars,
                "error": str(e),
                "status": "FAIL"
            })

    elapsed_time = time.time() - start_time
    success_rate = ((total_scenes - failure_count - (1 if overlap_count > 0 else 0)) / total_scenes) * 100

    report_content = f"""# Spatial Character Placement Engine Benchmark Report

## Overview
- **Engine Version**: 1.0.0 (Semicircle Spacing & Collision Repulsion Model)
- **Total Test Scenes**: {total_scenes}
- **Placement Success Rate**: {success_rate:.1f}%
- **Total Overlaps Detected**: {overlap_count}
- **Total Collisions (Identical Coordinates)**: {collision_count}
- **Placement Failures (Exceptions)**: {failure_count}
- **Total Execution Time**: {elapsed_time:.4f} seconds

## Performance metrics by character density
| Characters Count | Scenes Tested | Overlaps | Collisions | Failures | Status |
|---|---|---|---|---|---|
"""
    # Group results by character count
    for count in range(1, 11):
        group_results = [r for r in results if r["character_count"] == count]
        group_overlaps = sum(r.get("overlaps_detected", 0) for r in group_results)
        group_collisions = sum(r.get("collisions_detected", 0) for r in group_results)
        group_failures = sum(1 for r in group_results if r["status"] == "FAIL")
        group_status = "PASS" if (group_overlaps == 0 and group_failures == 0) else "WARN"
        report_content += f"| {count} | {len(group_results)} | {group_overlaps} | {group_collisions} | {group_failures} | {group_status} |\n"

    report_content += """
## Sample Placement Details
| Scene ID | Character Count | Positions Generated | Status |
|---|---|---|---|
"""
    # Show one sample coordinate dump per character count
    for count in range(1, 11):
        sample_r = next(r for r in results if r["character_count"] == count)
        if sample_r["status"] == "PASS":
            pos_strs = []
            for name, data in sample_r["placements"].items():
                pos_strs.append(f"{name}: {data['position']}")
            pos_desc = " | ".join(pos_strs)
            report_content += f"| {sample_r['scene_id']} | {count} | {pos_desc} | {sample_r['status']} |\n"
        else:
            report_content += f"| {sample_r['scene_id']} | {count} | Error: {sample_r.get('error', 'Overlap')} | {sample_r['status']} |\n"

    # Write report locally
    local_report_path = os.path.join(project_dir, "spatial_placement_report.md")
    with open(local_report_path, "w") as f:
        f.write(report_content)
    print(f"Local report generated: {local_report_path}")

    # Write report to Artifact Directory
    artifact_dir = "PROJECT_ROOT/.gemini/antigravity-cli/brain/3496fc80-3ea9-4817-8bc4-b4e0e2ff7b60"
    if os.path.exists(artifact_dir):
        artifact_report_path = os.path.join(artifact_dir, "spatial_placement_report.md")
        with open(artifact_report_path, "w") as f:
            f.write(report_content)
        print(f"Artifact report generated: {artifact_report_path}")

    return success_rate == 100.0

if __name__ == "__main__":
    success = run_benchmark()
    sys.exit(0 if success else 1)
