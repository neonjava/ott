#!/usr/bin/env python3
"""
emotion_benchmark.py
Validates the emotion_engine.py with 100 distinct emotional sentences.
Generates emotion_report.md.
"""
import sys
import os
import time

project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.append(project_dir)

from emotion_engine import EmotionEngine

# 100 emotional phrases with their expected labels (7 main categories + neutral)
TEST_PHRASES = [
    # Happy (14)
    ("The prince smiled cheerfully at the cheering crowd.", "happy"),
    ("A happy villager joyfully celebrates the harvest.", "happy"),
    ("The princess danced happily in the golden sunlight.", "happy"),
    ("A victorious knight raised his hands, laughing gleefully.", "happy"),
    ("The team was delighted to win the grand tournament.", "happy"),
    ("A cheerful anime boy waves his hands with joy.", "happy"),
    ("He was extremely proud of his achievements today.", "happy"),
    ("The children played gleefully on the green fields.", "happy"),
    ("A triumphant commander rode into the city.", "happy"),
    ("She smiled warmly as she saw her family safe.", "happy"),
    ("They cheered and laughed, celebrating their hard-won victory.", "happy"),
    ("The cute fox leaped around the garden in pure delight.", "happy"),
    ("A glad traveler sang a beautiful song of joy.", "happy"),
    ("The crowd welcomed the hero with excited cheers.", "happy"),

    # Sad (14)
    ("A lonely knight weep in the silent dark forest.", "sad"),
    ("The exhausted traveler lost all hope of finding his way.", "sad"),
    ("A sad queen stands alone, mourning the fallen king.", "sad"),
    ("The robot sits in the rain, losing memory and depressed.", "sad"),
    ("He wept bitterly over the tragic loss of his home.", "sad"),
    ("A lonely shadow wanders through the ruins, filled with grief.", "sad"),
    ("The child felt unhappy and abandoned in the storm.", "sad"),
    ("A sorrowful mage looks down at his broken wand.", "sad"),
    ("The old man sighed mournfully, thinking of his youth.", "sad"),
    ("She wept silently in her dark room, losing faith in her friends.", "sad"),
    ("The dog sat by the grave, showing deep grief.", "sad"),
    ("A hopeless warrior dropped his sword and sat in the dust.", "sad"),
    ("The village was filled with tears and unhappiness.", "sad"),
    ("A depressed wizard isolated himself in the cold tower.", "sad"),

    # Angry (14)
    ("The angry giant roared and smashed the table in fury.", "angry"),
    ("A furious warrior violently strikes the shield.", "angry"),
    ("The robot runs aggressively, firing laser beams in rage.", "angry"),
    ("The captain was mad and yelled at his lazy crew.", "angry"),
    ("A hateful villain cursed the hero with intense bitterness.", "angry"),
    ("She stared at him with angry, vengeful eyes.", "angry"),
    ("The beast growled furiously, showing sharp teeth.", "angry"),
    ("A resentful soldier refused the order, full of bitterness.", "angry"),
    ("He slammed the door shut in an enraged fit.", "angry"),
    ("The customer shouted angrily at the merchant.", "angry"),
    ("They fought aggressively, fueled by years of hostility.", "angry"),
    ("An annoyed guard pushed the intruder out of the castle.", "angry"),
    ("The crowd rioted, shouting hostile slogans.", "angry"),
    ("The dragon roared in rage when its cave was entered.", "angry"),

    # Fear (14)
    ("A terrified child hides in the dark closet, trembling with fear.", "fear"),
    ("The scared traveler runs from the shadow in the forest.", "fear"),
    ("A terrified captain flees from the giant sea monster.", "fear"),
    ("She felt tense and afraid when the lights went out.", "fear"),
    ("A nervous guard stands at the gate, checking every noise.", "fear"),
    ("The panicked villagers ran in all directions.", "fear"),
    ("He was frightened by the sudden loud roar.", "fear"),
    ("A tense mage crouches in the bushes, fearing the beast.", "fear"),
    ("The captain looked at the storm with deep dread.", "fear"),
    ("A cowardly thief ran away, shivering in terror.", "fear"),
    ("She was spooked by the strange voice behind her.", "fear"),
    ("They walked tively through the haunted graveyard.", "fear"),
    ("The animal cowers in the corner, terrified of the whip.", "fear"),
    ("A panic-stricken soldier abandoned his post in fear.", "fear"),

    # Hope (14)
    ("The exhausted wizard regains hope after finding the amulet.", "hope"),
    ("A determined hero regains purpose and stands tall.", "hope"),
    ("She felt reassured by the kind words of the priest.", "hope"),
    ("A hopeful traveler looks at the sunrise breaking through clouds.", "hope"),
    ("The peaceful village slept under a clear starry sky.", "hope"),
    ("He smiled with relief when he found the water source.", "hope"),
    ("A trustful child holds the hand of the giant.", "hope"),
    ("She felt optimistic about the success of their journey.", "hope"),
    ("They looked forward to the future with faith and hope.", "hope"),
    ("A reassured captain guided the ship to the shore.", "hope"),
    ("The warm fire brought comfort and relief to the cold scouts.", "hope"),
    ("He dreamed of a peaceful world free of war.", "hope"),
    ("The community felt a sense of relief after the dragon left.", "hope"),
    ("She was inspired by the ancient story of courage.", "hope"),

    # Surprise (14)
    ("The surprised queen notices a hidden letter in the drawer.", "surprise"),
    ("A traveler unexpectedly spots a beautiful oasis.", "surprise"),
    ("The child discovers a secret room behind the bookcase.", "surprise"),
    ("She was shocked to see a dragon flying in the sky.", "surprise"),
    ("He suddenly saw the glowing crystal in the dark cave.", "surprise"),
    ("A surprised fox noticed the trap and stopped.", "surprise"),
    ("They were amazed by the magical lights in the sky.", "surprise"),
    ("He stared in shock as the ancient door slowly opened.", "surprise"),
    ("She spotted a hidden path that wasn't on the map.", "surprise"),
    ("The mage noticed the runes glowing and gasped in surprise.", "surprise"),
    ("They found a chest of gold coins buried in the sand.", "surprise"),
    ("A sudden flash of lightning illuminated the valley.", "surprise"),
    ("The robot was surprised by the human's friendly gesture.", "surprise"),
    ("She was astonished by the speed of the warrior.", "surprise"),

    # Determination (14)
    ("A determined knight enters the cave to face the dragon.", "determination"),
    ("The brave warrior stands tall and draws his sword.", "determination"),
    ("She climbed the steep mountain peak with steadfast resolve.", "determination"),
    ("The team is focused on winning the final battle.", "determination"),
    ("A courageous elf prepares her bow to defend the forest.", "determination"),
    ("He resolved to complete the quest no matter what.", "determination"),
    ("A bold captain steers the ship straight into the storm.", "determination"),
    ("They stood firm against the onslaught of the enemy.", "determination"),
    ("She valiantly fought the monster to protect the town.", "determination"),
    ("A determined ninja crawls silently through the guards.", "determination"),
    ("The soldier stood steadfast at his post until dawn.", "determination"),
    ("He made a firm decision to speak the truth.", "determination"),
    ("The team showed great courage and persistence.", "determination"),
    ("An unstoppable hero charges forward, defying all odds.", "determination"),

    # Neutral (2)
    ("A merchant stands by the counter counting coins.", "neutral"),
    ("The robot sits on the metal chair, idling.", "neutral")
]

def run_benchmark():
    engine = EmotionEngine()
    total = len(TEST_PHRASES)
    passed = 0
    failed = 0
    results = []

    print(f"Running Emotion Engine Benchmark with {total} classifications...")
    start_time = time.time()

    for idx, (phrase, expected) in enumerate(TEST_PHRASES):
        actual = engine.classify_emotion(phrase)
        if actual == expected:
            passed += 1
            status = "PASS"
        else:
            failed += 1
            status = "FAIL"

        results.append({
            "index": idx + 1,
            "phrase": phrase,
            "expected": expected,
            "actual": actual,
            "status": status
        })

    elapsed_time = time.time() - start_time
    success_rate = (passed / total) * 100

    report_content = f"""# Emotion Engine Benchmark Report

## Overview
- **Engine Version**: 1.0.0 (Lexicon-based Classifier)
- **Total Test Cases**: {total}
- **Passed (Correct)**: {passed}
- **Failed (Incorrect)**: {failed}
- **Success Rate**: {success_rate:.1f}%
- **Execution Time**: {elapsed_time:.4f} seconds

## Accuracy by Emotion Category
"""
    # Calculate category accuracy
    categories = ["happy", "sad", "angry", "fear", "hope", "surprise", "determination", "neutral"]
    for cat in categories:
        cat_total = sum(1 for p, e in TEST_PHRASES if e == cat)
        cat_passed = sum(1 for r in results if r["expected"] == cat and r["status"] == "PASS")
        cat_acc = (cat_passed / cat_total) * 100 if cat_total > 0 else 0
        report_content += f"- **{cat.capitalize()}**: {cat_passed}/{cat_total} ({cat_acc:.1f}%)\n"

    report_content += """
## Detailed Results
| ID | Phrase | Expected | Actual | Status |
|---|---|---|---|---|
"""
    for r in results:
        report_content += f"| {r['index']} | {r['phrase']} | {r['expected']} | {r['actual']} | {r['status']} |\n"

    # Write report locally
    local_report_path = os.path.join(project_dir, "emotion_report.md")
    with open(local_report_path, "w") as f:
        f.write(report_content)
    print(f"Local report generated: {local_report_path}")

    # Write report to Artifact Directory
    artifact_dir = "PROJECT_ROOT/.gemini/antigravity-cli/brain/3496fc80-3ea9-4817-8bc4-b4e0e2ff7b60"
    if os.path.exists(artifact_dir):
        artifact_report_path = os.path.join(artifact_dir, "emotion_report.md")
        with open(artifact_report_path, "w") as f:
            f.write(report_content)
        print(f"Artifact report generated: {artifact_report_path}")

    print(f"Benchmark finished: {passed}/{total} passed. Success Rate: {success_rate:.1f}%")
    return success_rate >= 90.0 # Benchmark passes if >=90%

if __name__ == "__main__":
    success = run_benchmark()
    sys.exit(0 if success else 1)
