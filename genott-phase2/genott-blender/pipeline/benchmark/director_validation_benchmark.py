#!/usr/bin/env python3
import os
import json
import sys
import unittest
from storyboard_director import parse_script_to_storyboard
from director_ai import direct_storyboard

# Predefined templates to cover a wide variety of cinematic inputs
TEMPLATES = [
    ("hero walks in the forest.", "forest", "walk"),
    ("mage stands still in the castle.", "castle", "idle"),
    ("knight attacks in the city.", "city", "attack"),
    ("robot waves inside the cave.", "cave", "wave"),
    ("queen says 'welcome to my castle' inside the throne room.", "throne room", "talk"),
    ("hero jumps over the canyon.", "canyon", "jump"),
    ("mage discovers a mysterious artifact.", "artifact", "discover"),
    ("knight ducks behind the shield.", "shield", "duck"),
    ("robot enters the factory.", "factory", "enter"),
    ("hero runs across the desert.", "desert", "run"),
]

def generate_50_scripts():
    scripts = []
    actions = ["walk", "run", "jump", "attack", "wave", "duck", "enter", "discover", "idle", "talk"]
    locations = ["forest", "castle", "city", "cave", "beach", "mountain", "village", "arena", "ruins", "dungeon"]
    characters = ["hero", "mage", "knight", "robot", "queen", "prince"]
    moods = ["cheerful", "sad", "aggressive", "tense", "mysterious", "epic", "neutral"]
    
    # Generate combinations
    count = 0
    for char in characters:
        for loc in locations:
            for act in actions:
                for mood in moods:
                    if count >= 50:
                        break
                    # Construct a sentence that triggers character, location, action, and mood keywords
                    sentence = f"The {char} {act}s {mood}ly in the {loc}."
                    # Adjust for normal grammar
                    if act == "talk":
                        sentence = f"The {char} says 'hello' {mood}ly in the {loc}."
                    elif act == "walk":
                        sentence = f"The {char} walks slowly {mood}ly in the {loc}."
                    elif act == "run":
                        sentence = f"The {char} runs quickly {mood}ly in the {loc}."
                        
                    scripts.append((sentence, loc, act, mood))
                    count += 1
            if count >= 50:
                break
        if count >= 50:
            break
            
    return scripts

def run_benchmark():
    print("=== Director AI Validation Benchmark (50 Storyboards) ===")
    scripts = generate_50_scripts()
    
    results = []
    shot_distribution = {}
    movement_distribution = {}
    pacing_distribution = {}
    transition_distribution = {}
    
    for idx, (script_text, loc, act, mood) in enumerate(scripts):
        # 1. Parse raw storyboard
        storyboard = parse_script_to_storyboard(script_text)
        
        # 2. Direct with Director AI
        directed = direct_storyboard(storyboard)
        
        # 3. Analyze output
        scenes = directed.get("scenes", [])
        for scene in scenes:
            shot = scene.get("camera_shot")
            move = scene.get("camera_movement")
            pacing = scene.get("pacing")
            trans = scene.get("transition")
            dur = scene.get("duration")
            
            shot_distribution[shot] = shot_distribution.get(shot, 0) + 1
            movement_distribution[move] = movement_distribution.get(move, 0) + 1
            pacing_distribution[pacing] = pacing_distribution.get(pacing, 0) + 1
            transition_distribution[trans] = transition_distribution.get(trans, 0) + 1
            
            # Validation assertions
            assert shot in ["wide_shot", "medium_shot", "close_up", "establishing_shot", "over_shoulder", "tracking_shot", "orbit_shot", "low_angle", "high_angle"], f"Invalid shot: {shot}"
            assert move in ["static", "pan", "tilt", "zoom", "tracking", "orbit"], f"Invalid movement: {move}"
            assert pacing in ["slow", "standard", "fast"], f"Invalid pacing: {pacing}"
            assert trans in ["cut", "fade", "white"], f"Invalid transition: {trans}"
            assert dur > 0, f"Invalid duration: {dur}"
            
        results.append({
            "id": idx + 1,
            "script": script_text,
            "scenes": scenes,
            "transitions": directed.get("transitions")
        })
        
    print(f"Directing completed successfully for {len(results)} storyboards.")
    
    # Write Markdown Report
    report = f"""# Director AI Validation Report

## Summary
| Metric | Value |
|--------|-------|
| Total Storyboards Evaluated | {len(results)} |
| Directing Success Rate | 100% |

## Camera Shot Distribution
| Shot Type | Count | Percentage |
|-----------|-------|------------|
"""
    for shot, cnt in shot_distribution.items():
        report += f"| {shot} | {cnt} | {(cnt / len(results)) * 100:.1f}% |\n"
        
    report += "\n## Camera Movement Distribution\n| Movement Type | Count | Percentage |\n|---------------|-------|------------|\n"
    for move, cnt in movement_distribution.items():
        report += f"| {move} | {cnt} | {(cnt / len(results)) * 100:.1f}% |\n"
        
    report += "\n## Pacing Distribution\n| Pacing | Count | Percentage |\n|--------|-------|------------|\n"
    for pacing, cnt in pacing_distribution.items():
        report += f"| {pacing} | {cnt} | {(cnt / len(results)) * 100:.1f}% |\n"
        
    report += "\n## Transition Distribution\n| Transition Type | Count | Percentage |\n|-----------------|-------|------------|\n"
    for trans, cnt in transition_distribution.items():
        report += f"| {trans} | {cnt} | {(cnt / len(results)) * 100:.1f}% |\n"
        
    report += """
## Sample Directed Storyboards
| ID | Script | Chosen Shot | Camera Movement | Pacing | Transition | Duration |
|----|--------|-------------|-----------------|--------|------------|----------|
"""
    for r in results[:10]:
        scene = r["scenes"][0]
        report += f"| {r['id']} | {r['script']} | {scene['camera_shot']} | {scene['camera_movement']} | {scene['pacing']} | {scene['transition']} | {scene['duration']}s |\n"
        
    report += "\n## Conclusion\n**The Director AI completed directing 50/50 test storyboards with 100% conformant output fields.**\n"
    
    with open("director_validation_report.md", "w") as f:
        f.write(report)
    print("Saved director_validation_report.md")
    
    # Copy report to md folder
    md_dir = "PROJECT_ROOT/Documents/md"
    os.makedirs(md_dir, exist_ok=True)
    with open(os.path.join(md_dir, "director_validation_report.md"), "w") as f:
        f.write(report)
        
    # Copy to brain artifact directory as well
    artifact_dir = "PROJECT_ROOT/.gemini/antigravity-cli/brain/3496fc80-3ea9-4817-8bc4-b4e0e2ff7b60"
    os.makedirs(artifact_dir, exist_ok=True)
    with open(os.path.join(artifact_dir, "director_validation_report.md"), "w") as f:
        f.write(report)
    print("Report copied to Documents/md and brain artifact directory.")

if __name__ == "__main__":
    run_benchmark()
