#!/usr/bin/env python3
"""
test_camera.py — Verifies 50 generated storyboard camera suggestions.
"""
import unittest
import sys
import os

project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.append(project_dir)

from storyboard_director import parse_script_to_storyboard

class TestCameraDirector(unittest.TestCase):
    # 50 unique sentences (10 for each of the 5 camera shot types)
    TEST_CASES = [
        # Close Up (10)
        {"text": "A close-up of the knight's face as he frowns.", "expected": "close_up"},
        {"text": "The closeup shows his eyes widening in horror.", "expected": "close_up"},
        {"text": "A close up of the glowing ring.", "expected": "close_up"},
        {"text": "We see the expression of fear on her face.", "expected": "close_up"},
        {"text": "His angry face fills the screen.", "expected": "close_up"},
        {"text": "The camera captures her shock and expression.", "expected": "close_up"},
        {"text": "Close-up of the ticking clock mechanism.", "expected": "close_up"},
        {"text": "A tight closeup on the dagger's hilt.", "expected": "close_up"},
        {"text": "We zoom in close up on the ancient text.", "expected": "close_up"},
        {"text": "The close-up reveals her tears.", "expected": "close_up"},
        
        # Establishing Shot (10)
        {"text": "An establishing shot of the massive castle at dusk.", "expected": "establishing_shot"},
        {"text": "A grand establishing panorama of the snowy mountain range.", "expected": "establishing_shot"},
        {"text": "The camera pans in an establishing view of the kingdom.", "expected": "establishing_shot"},
        {"text": "An establishing shot shows the quiet peaceful village.", "expected": "establishing_shot"},
        {"text": "Establishing shot of the futuristic city skyline.", "expected": "establishing_shot"},
        {"text": "We start with an establishing view of the misty cave entrance.", "expected": "establishing_shot"},
        {"text": "An establishing panorama of the sunny beach.", "expected": "establishing_shot"},
        {"text": "Establishing shot of the empty training field grid.", "expected": "establishing_shot"},
        {"text": "An establishing shot captures the deep pine woods.", "expected": "establishing_shot"},
        {"text": "Establishing view of the gladiator arena.", "expected": "establishing_shot"},
        
        # Over Shoulder (10)
        {"text": "An over the shoulder shot of the knight looking at the dragon.", "expected": "over_shoulder"},
        {"text": "We look over shoulder at the wizard standing before the portal.", "expected": "over_shoulder"},
        {"text": "An over the shoulder view of the queen looking at the court.", "expected": "over_shoulder"},
        {"text": "The camera frames an over shoulder shot looking at the tavern.", "expected": "over_shoulder"},
        {"text": "An over the shoulder perspective of the ranger looking at the wolf.", "expected": "over_shoulder"},
        {"text": "We see an over shoulder perspective looking at the mountain peaks.", "expected": "over_shoulder"},
        {"text": "An over the shoulder shot of the villager looking at the cabin.", "expected": "over_shoulder"},
        {"text": "Over shoulder shot of the teacher looking at the classroom.", "expected": "over_shoulder"},
        {"text": "We look over the shoulder of the blacksmith looking at the furnace.", "expected": "over_shoulder"},
        {"text": "An over shoulder frame of the prince looking at the princess.", "expected": "over_shoulder"},
        
        # Wide Shot (10)
        {"text": "A wide shot of the lonely knight walking through the forest.", "expected": "wide_shot"},
        {"text": "The camera gives a wide view of the quiet library room.", "expected": "wide_shot"},
        {"text": "We see a distant view of the ship sailing away.", "expected": "wide_shot"},
        {"text": "A wide shot of the horse running across the field.", "expected": "wide_shot"},
        {"text": "The scene opens with a wide view of the campfire in the woods.", "expected": "wide_shot"},
        {"text": "A wide shot of the empty classroom hallway.", "expected": "wide_shot"},
        {"text": "We see a far away view of the giant stepping over hills.", "expected": "wide_shot"},
        {"text": "A wide shot captures the entire market town.", "expected": "wide_shot"},
        {"text": "The camera shows a wide perspective of the cozy cottage yard.", "expected": "wide_shot"},
        {"text": "A wide shot of the circular ring inside the fighting arena.", "expected": "wide_shot"},
        
        # Tracking Shot (10)
        {"text": "A tracking shot follows the hero as he runs from the troll.", "expected": "tracking_shot"},
        {"text": "The camera uses a tracking shot to follow the thief down the hallway.", "expected": "tracking_shot"},
        {"text": "We see a tracking shot of the carriage moving along the road.", "expected": "tracking_shot"},
        {"text": "A tracking shot follows the dog chasing the bird.", "expected": "tracking_shot"},
        {"text": "The camera does a tracking shot to follow the wagon.", "expected": "tracking_shot"},
        {"text": "A tracking shot follows the knight entering the ruins.", "expected": "tracking_shot"},
        {"text": "We use a tracking shot to follow the princess running away.", "expected": "tracking_shot"},
        {"text": "A tracking shot follows the soldier marching through the mud.", "expected": "tracking_shot"},
        {"text": "The camera tracks the goblin slithering through the tunnel.", "expected": "tracking_shot"},
        {"text": "A tracking shot follows the archer dodging behind the tree.", "expected": "tracking_shot"}
    ]

    def test_camera_detection(self):
        total_checks = 0
        passed_checks = 0
        
        for idx, tc in enumerate(self.TEST_CASES):
            text = tc["text"]
            expected = tc["expected"]
            
            storyboard = parse_script_to_storyboard(text)
            scenes = storyboard.get("scenes", [])
            
            self.assertEqual(len(scenes), 1, f"Expected 1 scene, got {len(scenes)}")
            actual = scenes[0]["camera"]
            
            total_checks += 1
            with self.subTest(text=text, expected=expected):
                self.assertEqual(actual, expected, f"Sentence '{text}' expected camera '{expected}', got '{actual}'")
                passed_checks += 1
                
        print(f"\n[Camera Director Test] Generated and verified {passed_checks}/{total_checks} storyboard camera shots successfully.")

if __name__ == "__main__":
    unittest.main()
