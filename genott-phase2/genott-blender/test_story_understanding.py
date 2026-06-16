#!/usr/bin/env python3
"""
test_story_understanding.py — Verifies advanced semantic script parsing, emotional mapping, and modifiers.
"""
import unittest
import sys
import os

project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.append(project_dir)

from storyboard_director import parse_script_to_storyboard

class TestStoryUnderstanding(unittest.TestCase):
    def test_abstract_knight_story(self):
        # The ultimate test case: "A lonely knight slowly loses faith while travelling through a frozen kingdom."
        script = "A lonely knight slowly loses faith while travelling through a frozen kingdom."
        storyboard = parse_script_to_storyboard(script)
        scenes = storyboard.get("scenes", [])
        
        self.assertEqual(len(scenes), 1)
        scene = scenes[0]
        
        # Verify Knight detection
        self.assertEqual(scene["character"], "knight")
        # Verify Location detection
        self.assertEqual(scene["location"], "frozen kingdom")
        # Verify traveling mapped semantically to walk
        self.assertEqual(scene["action"], "walk")
        # Verify lonely/loses faith maps mood to sad
        self.assertEqual(scene["mood"], "sad")
        # Verify slowly maps speed to slow
        self.assertEqual(scene["speed"], "slow")

    def test_additional_semantic_stories(self):
        # 1. Angry hero charging aggressively
        s1 = "The robot quickly runs aggressively and smashes the wall."
        st1 = parse_script_to_storyboard(s1)
        sc1 = st1["scenes"][0]
        self.assertEqual(sc1["character"], "robot")
        self.assertEqual(sc1["action"], "attack") # smashes/fight maps to attack
        self.assertEqual(sc1["mood"], "aggressive")
        self.assertEqual(sc1["speed"], "fast")
        
        # 2. Happy queen greeting the crowd
        s2 = "A happy queen joyfully waves from the tower."
        st2 = parse_script_to_storyboard(s2)
        sc2 = st2["scenes"][0]
        self.assertEqual(sc2["character"], "queen")
        self.assertEqual(sc2["action"], "wave")
        self.assertEqual(sc2["mood"], "cheerful")
        
        # 3. Terrified mage hiding in the cave
        s3 = "A terrified mage is cautiously crouching inside the dark cave."
        st3 = parse_script_to_storyboard(s3)
        sc3 = st3["scenes"][0]
        self.assertEqual(sc3["character"], "mage")
        self.assertEqual(sc3["action"], "duck") # crouching -> duck
        self.assertEqual(sc3["mood"], "tense")
        
        # 4. Proud prince standing victorious
        s4 = "The prince proudly stands victorious on the hill."
        st4 = parse_script_to_storyboard(s4)
        sc4 = st4["scenes"][0]
        self.assertEqual(sc4["character"], "prince")
        self.assertEqual(sc4["action"], "idle") # stands -> idle
        self.assertEqual(sc4["mood"], "triumphant")

if __name__ == "__main__":
    unittest.main()
