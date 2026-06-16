#!/usr/bin/env python3
"""
storyboard_validation_benchmark.py — Run 25 storyboard validation tests and report metrics.
"""
import os
import sys
import json
import time
import requests

API_URL = "http://127.0.0.1:5001/api/generate-storyboard"

# Ground Truth for 25 different scripts
TEST_CASES = [
    # Knight
    {
        "character": "knight",
        "script": "A knight walks through a snowy forest.",
        "expected": {
            "scenes": [
                {"location": "snowy forest", "character": "knight", "action": "walk", "camera": "wide_shot", "mood": "mysterious"}
            ]
        }
    },
    {
        "character": "knight",
        "script": "The knight attacks a dragon in a dark cave.",
        "expected": {
            "scenes": [
                {"location": "dark cave", "character": "knight", "action": "attack", "camera": "close_up", "mood": "mysterious"}
            ]
        }
    },
    {
        "character": "knight",
        "script": "Knight waves to the king at the castle gate.",
        "expected": {
            "scenes": [
                {"location": "castle gate", "character": "knight", "action": "wave", "camera": "medium_shot", "mood": "mysterious"}
            ]
        }
    },
    {
        "character": "knight",
        "script": "He jumps over a rock on the mountain path.",
        "expected": {
            "scenes": [
                {"location": "mountain path", "character": "knight", "action": "jump", "camera": "low_angle", "mood": "epic"}
            ]
        }
    },
    {
        "character": "knight",
        "script": "The knight stands still inside the armor chamber.",
        "expected": {
            "scenes": [
                {"location": "armor chamber", "character": "knight", "action": "idle", "camera": "wide_shot", "mood": "neutral"}
            ]
        }
    },
    # Anime Girl
    {
        "character": "anime_girl",
        "script": "Anime Girl walks across the school yard.",
        "expected": {
            "scenes": [
                {"location": "school yard", "character": "anime_girl", "action": "walk", "camera": "wide_shot", "mood": "neutral"}
            ]
        }
    },
    {
        "character": "anime_girl",
        "script": "She jumps with joy in the sunny park.",
        "expected": {
            "scenes": [
                {"location": "sunny park", "character": "anime_girl", "action": "jump", "camera": "low_angle", "mood": "neutral"}
            ]
        }
    },
    {
        "character": "anime_girl",
        "script": "Anime Girl waves to her friend at the train station.",
        "expected": {
            "scenes": [
                {"location": "train station", "character": "anime_girl", "action": "wave", "camera": "medium_shot", "mood": "neutral"}
            ]
        }
    },
    {
        "character": "anime_girl",
        "script": "She runs quickly to the classroom.",
        "expected": {
            "scenes": [
                {"location": "classroom", "character": "anime_girl", "action": "run", "camera": "tracking_shot", "mood": "neutral"}
            ]
        }
    },
    {
        "character": "anime_girl",
        "script": "Anime Girl stands quietly in the library.",
        "expected": {
            "scenes": [
                {"location": "library", "character": "anime_girl", "action": "idle", "camera": "wide_shot", "mood": "neutral"}
            ]
        }
    },
    # Anime Boy
    {
        "character": "anime_boy",
        "script": "Anime Boy runs along the beach.",
        "expected": {
            "scenes": [
                {"location": "beach", "character": "anime_boy", "action": "run", "camera": "tracking_shot", "mood": "neutral"}
            ]
        }
    },
    {
        "character": "anime_boy",
        "script": "He jumps over the fence in the backyard.",
        "expected": {
            "scenes": [
                {"location": "backyard", "character": "anime_boy", "action": "jump", "camera": "low_angle", "mood": "neutral"}
            ]
        }
    },
    {
        "character": "anime_boy",
        "script": "Anime Boy walks into the gaming cafe.",
        "expected": {
            "scenes": [
                {"location": "gaming cafe", "character": "anime_boy", "action": "walk", "camera": "wide_shot", "mood": "neutral"}
            ]
        }
    },
    {
        "character": "anime_boy",
        "script": "He waves at the teacher in the hallway.",
        "expected": {
            "scenes": [
                {"location": "hallway", "character": "anime_boy", "action": "wave", "camera": "medium_shot", "mood": "neutral"}
            ]
        }
    },
    {
        "character": "anime_boy",
        "script": "Anime Boy attacks the target in the training room.",
        "expected": {
            "scenes": [
                {"location": "training room", "character": "anime_boy", "action": "attack", "camera": "close_up", "mood": "aggressive"}
            ]
        }
    },
    # Mage
    {
        "character": "mage",
        "script": "Mage walks through the ancient library.",
        "expected": {
            "scenes": [
                {"location": "ancient library", "character": "mage", "action": "walk", "camera": "wide_shot", "mood": "neutral"}
            ]
        }
    },
    {
        "character": "mage",
        "script": "He attacks with magic spells on the high tower.",
        "expected": {
            "scenes": [
                {"location": "high tower", "character": "mage", "action": "attack", "camera": "close_up", "mood": "aggressive"}
            ]
        }
    },
    {
        "character": "mage",
        "script": "Mage waves his staff in the magic circle.",
        "expected": {
            "scenes": [
                {"location": "magic circle", "character": "mage", "action": "wave", "camera": "medium_shot", "mood": "cheerful"}
            ]
        }
    },
    {
        "character": "mage",
        "script": "He jumps away from the blast in the laboratory.",
        "expected": {
            "scenes": [
                {"location": "laboratory", "character": "mage", "action": "jump", "camera": "low_angle", "mood": "neutral"}
            ]
        }
    },
    {
        "character": "mage",
        "script": "Mage stands near the crystal ball.",
        "expected": {
            "scenes": [
                {"location": "crystal ball", "character": "mage", "action": "idle", "camera": "wide_shot", "mood": "neutral"}
            ]
        }
    },
    # Robot
    {
        "character": "robot",
        "script": "Robot walks into the factory.",
        "expected": {
            "scenes": [
                {"location": "factory", "character": "robot", "action": "walk", "camera": "wide_shot", "mood": "neutral"}
            ]
        }
    },
    {
        "character": "robot",
        "script": "It runs on the conveyor belt.",
        "expected": {
            "scenes": [
                {"location": "conveyor belt", "character": "robot", "action": "run", "camera": "tracking_shot", "mood": "neutral"}
            ]
        }
    },
    {
        "character": "robot",
        "script": "Robot jumps down from the platform.",
        "expected": {
            "scenes": [
                {"location": "platform", "character": "robot", "action": "jump", "camera": "low_angle", "mood": "neutral"}
            ]
        }
    },
    {
        "character": "robot",
        "script": "It waves its metallic arm at the operator.",
        "expected": {
            "scenes": [
                {"location": "operator", "character": "robot", "action": "wave", "camera": "medium_shot", "mood": "cheerful"}
            ]
        }
    },
    {
        "character": "robot",
        "script": "Robot attacks the rogue drone in the warehouse.",
        "expected": {
            "scenes": [
                {"location": "warehouse", "character": "robot", "action": "attack", "camera": "close_up", "mood": "aggressive"}
            ]
        }
    }
]

def main():
    print("=== Storyboard Validation Benchmark (25 Scripts) ===\n")
    
    # Wait for API server to be responsive
    for _ in range(10):
        try:
            requests.get("http://127.0.0.1:5001/api/characters", timeout=2)
            break
        except requests.RequestException:
            time.sleep(1)
            
    success_generations = 0
    total_scenes_expected = 0
    total_scenes_correct = 0
    total_actions_expected = 0
    total_actions_correct = 0
    total_locations_expected = 0
    total_locations_correct = 0
    total_characters_expected = 0
    total_characters_correct = 0
    
    results = []
    
    for idx, tc in enumerate(TEST_CASES):
        script = tc["script"]
        char = tc["character"]
        expected = tc["expected"]
        
        print(f"[Test {idx+1}/25] Character: {char} | Script: \"{script}\"")
        
        try:
            resp = requests.post(API_URL, json={"character": char, "script": script}, timeout=10)
            if resp.status_code == 200 and resp.json().get("status") == "success":
                success_generations += 1
                sb = resp.json().get("storyboard", {})
                scenes = sb.get("scenes", [])
                
                exp_scenes = expected.get("scenes", [])
                
                # Check scene count match
                scenes_match = len(scenes) == len(exp_scenes)
                if scenes_match:
                    total_scenes_correct += 1
                total_scenes_expected += 1
                
                # Verify individual fields for each scene
                action_ok = True
                loc_ok = True
                char_ok = True
                
                for s_idx, exp_s in enumerate(exp_scenes):
                    if s_idx < len(scenes):
                        act_s = scenes[s_idx]
                        
                        # Validate action
                        if act_s.get("action") == exp_s.get("action"):
                            total_actions_correct += 1
                        else:
                            action_ok = False
                            print(f"    Action mismatch: expected '{exp_s.get('action')}', got '{act_s.get('action')}'")
                        total_actions_expected += 1
                        
                        # Validate location
                        if act_s.get("location") == exp_s.get("location"):
                            total_locations_correct += 1
                        else:
                            loc_ok = False
                            print(f"    Location mismatch: expected '{exp_s.get('location')}', got '{act_s.get('location')}'")
                        total_locations_expected += 1
                        
                        # Validate character
                        if act_s.get("character") == exp_s.get("character"):
                            total_characters_correct += 1
                        else:
                            char_ok = False
                            print(f"    Character mismatch: expected '{exp_s.get('character')}', got '{act_s.get('character')}'")
                        total_characters_expected += 1
                
                status = "PASS" if (scenes_match and action_ok and loc_ok and char_ok) else "FAIL"
                print(f"  -> {status}")
                results.append({
                    "id": idx + 1,
                    "script": script,
                    "status": status,
                    "scenes_extracted": len(scenes),
                    "scenes_expected": len(exp_scenes)
                })
            else:
                print(f"  -> HTTP FAIL {resp.status_code}: {resp.text}")
                results.append({
                    "id": idx + 1,
                    "script": script,
                    "status": "FAIL",
                    "scenes_extracted": 0,
                    "scenes_expected": len(expected.get("scenes", []))
                })
                total_scenes_expected += 1
                total_actions_expected += len(expected.get("scenes", []))
                total_locations_expected += len(expected.get("scenes", []))
                total_characters_expected += len(expected.get("scenes", []))
        except Exception as e:
            print(f"  -> EXCEPTION: {e}")
            results.append({
                "id": idx + 1,
                "script": script,
                "status": "FAIL",
                "scenes_extracted": 0,
                "scenes_expected": len(expected.get("scenes", []))
            })
            total_scenes_expected += 1
            total_actions_expected += len(expected.get("scenes", []))
            total_locations_expected += len(expected.get("scenes", []))
            total_characters_expected += len(expected.get("scenes", []))

    # Calculate metrics
    success_rate = (success_generations / len(TEST_CASES)) * 100
    scene_accuracy = (total_scenes_correct / total_scenes_expected) * 100 if total_scenes_expected else 0
    action_accuracy = (total_actions_correct / total_actions_expected) * 100 if total_actions_expected else 0
    location_accuracy = (total_locations_correct / total_locations_expected) * 100 if total_locations_expected else 0
    character_accuracy = (total_characters_correct / total_characters_expected) * 100 if total_characters_expected else 0
    
    print("\n" + "=" * 60)
    print("      STORYBOARD VALIDATION REPORT")
    print("=" * 60)
    print(f"Scripts tested:                 {len(TEST_CASES)}")
    print(f"Storyboard success rate:        {success_rate:.2f}%")
    print(f"Scene extraction accuracy:      {scene_accuracy:.2f}%")
    print(f"Action extraction accuracy:     {action_accuracy:.2f}%")
    print(f"Location extraction accuracy:   {location_accuracy:.2f}%")
    print(f"Character extraction accuracy:  {character_accuracy:.2f}%")
    print("=" * 60)

    # Generate storyboard_validation_report.md
    report_md = f"""# Storyboard Validation Report

## Metrics
| Metric | Value |
|--------|-------|
| Scripts Tested | {len(TEST_CASES)} |
| Storyboard Success Rate | {success_rate:.2f}% |
| Scene Extraction Accuracy | {scene_accuracy:.2f}% |
| Action Extraction Accuracy | {action_accuracy:.2f}% |
| Location Extraction Accuracy | {location_accuracy:.2f}% |
| Character Extraction Accuracy | {character_accuracy:.2f}% |

## Individual Storyboard Test Results
| # | Script | Status | Scenes Expected | Scenes Extracted |
|---|--------|--------|-----------------|------------------|
"""

    for r in results:
        script_short = r["script"][:35] + ("..." if len(r["script"]) > 35 else "")
        report_md += f"| {r['id']} | {script_short} | {r['status']} | {r['scenes_expected']} | {r['scenes_extracted']} |\n"

    report_md += f"\n## Conclusion\n{'**25 consecutive storyboard generations succeeded with 100% accuracy.**' if (success_rate == 100 and scene_accuracy == 100 and action_accuracy == 100 and location_accuracy == 100 and character_accuracy == 100) else '**Storyboard validation failed. Please check mismatches above.**'}\n"

    with open("storyboard_validation_report.md", "w") as f:
        f.write(report_md)
    print("\nSaved storyboard_validation_report.md")

if __name__ == "__main__":
    main()
