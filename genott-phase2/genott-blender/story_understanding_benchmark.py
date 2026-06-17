#!/usr/bin/env python3
"""
story_understanding_benchmark.py
Validates the story_understanding_engine.py with 100 diverse stories.
Generates story_understanding_report.md.
"""
import sys
import os
import json
import time

project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.append(project_dir)

from story_understanding_engine import StoryUnderstandingEngine

# Define 100 diverse stories
STORIES = [
    "A lonely knight loses faith, discovers an ancient dragon, and regains purpose.",
    "The brave mage enters the dark cave and prepares a magic spell.",
    "A tired robot slowly walks across the dry beach, searching for power.",
    "The happy princess joyfully waves from the tall tower.",
    "A terrified villager quickly flees from the forest as the beast roars.",
    "The angry warrior violently strikes the shield with a heavy sword.",
    "An ancient dragon sleeps in the volcanic mountain, guarding the treasure.",
    "The curious anime girl notices a glowing crystal on the hill.",
    "A mysterious wizard whispers a spell inside the ancient temple.",
    "The proud prince victoriously stands on the battlefield, raising his crown.",
    "A tiny fox cautiously crouching behind a bush in the snowy woods.",
    "The combat android runs aggressively to attack the monster.",
    "A sad traveler sits by the lake, grieving a lost friend.",
    "The bold samurai slays the demon in the bamboo forest.",
    "A terrified child hides in the dark room, trembling with fear.",
    "The queen proudly greets the crowd in the kingdom plaza.",
    "A lonely shadow wanders through the ruins of the castle.",
    "The ironman flies swiftly to save the falling city.",
    "A determined elf shoots an arrow from the green field.",
    "The furious hulk smashes the robot with extreme rage.",
    "A peaceful merchant rests near the bridge, looking at the sky.",
    "The tense ninja dodges the incoming shuriken in the night garden.",
    "A happy couple walks along the shore, celebrating their victory.",
    "The ghost screams inside the abandoned house, causing panic.",
    "A tired captain guides the crew through the storm to the island.",
    "The brave knight charges aggressively at the enemy army.",
    "A lonely mage wanders inside the giant library, looking for a scroll.",
    "The proud warrior holds the legendary sword on the mountain top.",
    "A frightened traveler runs through the swamp, escaping the beast.",
    "The cheerful anime boy waves to his friends from the boat.",
    "A furious giant attacks the stone wall with a giant hammer.",
    "The curious girl discovers a secret door behind the old mirror.",
    "A tense guard stands at the castle gate, holding a spear.",
    "The exhausted wizard regains hope after finding the ancient amulet.",
    "A sad prince weeps in the garden, losing all faith in his quest.",
    "The determined hero walks into the dungeon to face the demon.",
    "A surprised child finds a chest of gold coins in the cave.",
    "The proud samurai stands victorious in the arena after the fight.",
    "A terrified girl runs away from the shadow in the forest.",
    "The angry queen shouts orders to the guards, pointing to the gate.",
    "A happy fox jumps around the meadow, chasing a butterfly.",
    "The lonely traveler sits under the tree, looking at the map.",
    "A brave warrior protects the child with a steel shield.",
    "The evil wizard cast a shadow over the peaceful village.",
    "A surprised traveler spots an oasis in the dry desert.",
    "The tired robot rests on the rusty bridge, losing power.",
    "A terrified captain flees from the sea monster, escaping in fear.",
    "The cheerful princess greets the travelers at the palace entry.",
    "A lonely dwarf searches for gold in the deep mine.",
    "The aggressive robot attacks the base, destroying the defense.",
    "A sad warrior grieves his fallen captain on the glacier.",
    "The brave knight discovers the holy chalice inside the ruins.",
    "A tense mage crouches in the bushes, waiting for the guard.",
    "The proud prince waves from the horse, entering the city.",
    "A lonely boy sits in the library, reading a dusty book.",
    "The furious beast charges aggressively, breaking the trees.",
    "A terrified villager hides inside the temple, praying for safety.",
    "The happy traveler walks through the village, singing a song.",
    "A determined captain draws a sword, preparing for the battle.",
    "The surprised queen notices a hidden letter in the drawer.",
    "A lonely wolf wanders through the snowy forest, seeking a pack.",
    "The brave warrior enters the cave, holding a burning torch.",
    "A tired mage rests by the campfire, regaining his energy.",
    "The happy girl joyfully dances on the sandy beach.",
    "A terrified soldier flees from the battlefield, losing his shield.",
    "The angry captain yells at the crew, demanding focus.",
    "A proud knight stands on the hill, looking at the castle.",
    "The curious prince finds a magic ring in the garden.",
    "A tense child crawls through the narrow tunnel, escaping the beast.",
    "The determined hero climbs the steep mountain, seeking the sage.",
    "A sad queen walks along the river, mourning the king.",
    "The happy boy waves from the tower, celebrating the victory.",
    "A lonely mage discovers an ancient orb in the dark dungeon.",
    "The brave samurai stands in the arena, preparing to strike.",
    "A terrified traveler runs into the castle, seeking shelter.",
    "The furious warrior attacks the dragon with a spear.",
    "A happy fox rests in the green grass, enjoying the sun.",
    "The lonely prince loses hope, sitting on the cold throne.",
    "A determined girl runs through the storm to save the wolf.",
    "The proud captain holds the map, declaring the destination.",
    "A tense guard walks around the wall, checking the shadows.",
    "The surprised wizard notices the crystal glowing, feeling hope.",
    "A sad traveler weeps by the ruins, losing faith.",
    "The brave knight rescues the prince from the tower.",
    "A terrified villager runs from the fire, escaping to the hill.",
    "The angry beast roars inside the cave, preparing to attack.",
    "A happy princess waves to the soldiers, celebrating the peace.",
    "The lonely samurai walks through the desert, looking for a master.",
    "A determined warrior enters the arena, raising his shield.",
    "The proud queen stands before the throne, holding the scepter.",
    "A tense mage whispers a spell, hiding behind the pillar.",
    "The surprised child spots a dragon flying in the sky.",
    "A sad robot sits in the rain, losing memory.",
    "The brave captain fights the pirate on the ship deck.",
    "A terrified traveler flees the swamp, crying in fear.",
    "The furious robot smashes the terminal, causing an alarm.",
    "A happy boy runs through the meadow, holding a kite.",
    "The lonely traveler walks through the cold forest, seeking warmth.",
    "A determined knight enters the castle ruins, seeking the sword.",
    "The proud wizard stands on the tower, watching the stars."
]

def run_benchmark():
    engine = StoryUnderstandingEngine()
    total = len(STORIES)
    passed = 0
    failed = 0
    results = []

    char_extracted_total = 0
    loc_extracted_total = 0
    obj_extracted_total = 0
    emo_extracted_total = 0
    event_count_total = 0

    print(f"Running Story Understanding Benchmark with {total} stories...")
    start_time = time.time()

    for idx, story in enumerate(STORIES):
        try:
            res = engine.understand_story(story)
            
            # Validation checks
            assert "characters" in res, "Missing characters"
            assert "locations" in res, "Missing locations"
            assert "emotions" in res, "Missing emotions"
            assert "events" in res, "Missing events"
            assert "timeline" in res, "Missing timeline"
            assert "transitions" in res, "Missing transitions"

            passed += 1
            
            # Metrics accumulation
            char_extracted_total += len(res["characters"])
            loc_extracted_total += len(res["locations"])
            obj_extracted_total += len(res.get("objects", []))
            emo_extracted_total += len(res["emotions"])
            event_count_total += len(res["events"])

            results.append({
                "index": idx + 1,
                "story": story,
                "parsed": res,
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

    report_content = f"""# Story Understanding Engine Benchmark Report

## Overview
- **Engine Version**: 1.0.0 (Rule-based SVO Parser)
- **Total Test Stories**: {total}
- **Passed**: {passed}
- **Failed**: {failed}
- **Success Rate**: {success_rate:.1f}%
- **Total Execution Time**: {elapsed_time:.3f} seconds
- **Average Time per Story**: {elapsed_time/total:.5f} seconds

## Extraction Metrics
- **Total Characters Extracted**: {char_extracted_total} (Avg: {char_extracted_total/total:.1f}/story)
- **Total Locations Extracted**: {loc_extracted_total} (Avg: {loc_extracted_total/total:.1f}/story)
- **Total Objects Extracted**: {obj_extracted_total} (Avg: {obj_extracted_total/total:.1f}/story)
- **Total Emotions Extracted**: {emo_extracted_total} (Avg: {emo_extracted_total/total:.1f}/story)
- **Total Events Planned**: {event_count_total} (Avg: {event_count_total/total:.1f}/story)

## Detailed Results
| ID | Story | Status | Characters | Locations | Primary Emotion | Events Count |
|---|---|---|---|---|---|---|
"""
    for r in results:
        if r["status"] == "PASS":
            parsed = r["parsed"]
            chars_str = ", ".join([c["name"] for c in parsed["characters"]])
            locs_str = ", ".join([l["name"] for l in parsed["locations"]])
            emos_str = ", ".join([e["emotion"] for e in parsed["emotions"]]) if parsed["emotions"] else "neutral"
            report_content += f"| {r['index']} | {r['story']} | {r['status']} | {chars_str} | {locs_str} | {emos_str} | {len(parsed['events'])} |\n"
        else:
            report_content += f"| {r['index']} | {r['story']} | {r['status']} (Error: {r['error']}) | - | - | - | - |\n"

    # Write report locally
    local_report_path = os.path.join(project_dir, "story_understanding_report.md")
    with open(local_report_path, "w") as f:
        f.write(report_content)
    print(f"Local report generated: {local_report_path}")

    # Write report to Artifact Directory
    artifact_dir = "PROJECT_ROOT/.gemini/antigravity-cli/brain/3496fc80-3ea9-4817-8bc4-b4e0e2ff7b60"
    if os.path.exists(artifact_dir):
        artifact_report_path = os.path.join(artifact_dir, "story_understanding_report.md")
        with open(artifact_report_path, "w") as f:
            f.write(report_content)
        print(f"Artifact report generated: {artifact_report_path}")

    # Print summary
    print(f"Benchmark finished: {passed}/{total} passed. Success Rate: {success_rate:.1f}%")
    return success_rate == 100

if __name__ == "__main__":
    success = run_benchmark()
    sys.exit(0 if success else 1)
