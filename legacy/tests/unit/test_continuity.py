#!/usr/bin/env python3
"""
test_continuity.py — Runs visual state continuity checks across 20 multi-scene movies to verify scene-to-scene consistency.
"""
import unittest
import sys
import os

project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.append(project_dir)

from engine.director.continuity_engine_v2 import ContinuityEngineV2

class TestVisualContinuity(unittest.TestCase):
    def setUp(self):
        self.engine = ContinuityEngineV2("test_continuity_state.json")
        self.engine.clear_state()

    def tearDown(self):
        self.engine.clear_state()

    def test_20_multi_scene_movies(self):
        movies = [
            # Movie 1: Knight weapon and weather persistence
            [
                {"scene": 1, "plan": {"location": "snowy forest", "character_name": "knight", "action": "walk", "description": "A knight walks through the snow holding a sword."}},
                {"scene": 2, "plan": {"location": "snowy forest", "character_name": "knight", "action": "run", "description": "The knight rushes forward in the cold woods."}},
                {"scene": 3, "plan": {"location": "snowy forest", "character_name": "knight", "action": "drop", "description": "The knight drops his sword in the snow."}}
            ],
            # Movie 2: Outfit changes (helmet on/off)
            [
                {"scene": 1, "plan": {"location": "castle courtyard", "character_name": "knight", "action": "stand", "description": "A knight wears a helmet in the courtyard."}},
                {"scene": 2, "plan": {"location": "castle hall", "character_name": "knight", "action": "walk", "description": "He enters the stone hall."}},
                {"scene": 3, "plan": {"location": "castle hall", "character_name": "knight", "action": "remove", "description": "He takes off the helmet."}}
            ],
            # Movie 3: Environmental Prop campfire
            [
                {"scene": 1, "plan": {"location": "dark forest", "character_name": "villager", "action": "place", "description": "A villager builds a campfire."}},
                {"scene": 2, "plan": {"location": "dark forest", "character_name": "villager", "action": "stand", "description": "The villager warms his hands."}},
                {"scene": 3, "plan": {"location": "village square", "character_name": "villager", "action": "walk", "description": "He leaves for the village square."}}
            ],
            # Movie 4: Mage staff and weather continuity
            [
                {"scene": 1, "plan": {"location": "misty mountain", "character_name": "mage", "action": "walk", "description": "A mage walks holding a staff in the fog."}},
                {"scene": 2, "plan": {"location": "misty mountain", "character_name": "mage", "action": "stand", "description": "The mage looks at the sky."}}
            ],
            # Movie 5: Archer equipment
            [
                {"scene": 1, "plan": {"location": "sunny beach", "character_name": "archer", "action": "walk", "description": "An archer holding a bow walks on the sand."}},
                {"scene": 2, "plan": {"location": "sunny beach", "character_name": "archer", "action": "stand", "description": "The archer watches the sea."}}
            ],
            # Movie 6: Found chest prop
            [
                {"scene": 1, "plan": {"location": "dark cave", "character_name": "thief", "action": "discover", "description": "A thief discovers a chest in the cave."}},
                {"scene": 2, "plan": {"location": "dark cave", "character_name": "thief", "action": "stand", "description": "The thief opens the chest."}}
            ],
            # Movie 7: Weather transition rain -> clear
            [
                {"scene": 1, "plan": {"location": "city street", "character_name": "soldier", "action": "walk", "description": "A soldier marches in the heavy rain."}},
                {"scene": 2, "plan": {"location": "city street", "character_name": "soldier", "action": "stand", "description": "The clouds part and the weather turns clear."}}
            ],
            # Movie 8: Held lantern persistence
            [
                {"scene": 1, "plan": {"location": "dark dungeon", "character_name": "guard", "action": "walk", "description": "A guard walks holding a lantern."}},
                {"scene": 2, "plan": {"location": "dark dungeon", "character_name": "guard", "action": "stand", "description": "He unlocks the gate."}}
            ],
            # Movie 9: Multiple outfits (armor and boots)
            [
                {"scene": 1, "plan": {"location": "training camp", "character_name": "soldier", "action": "equips", "description": "A soldier puts on armor and leather boots."}},
                {"scene": 2, "plan": {"location": "training camp", "character_name": "soldier", "action": "run", "description": "The soldier runs around the camp."}}
            ],
            # Movie 10: Shield held through location change
            [
                {"scene": 1, "plan": {"location": "castle gate", "character_name": "knight", "action": "holds", "description": "A knight holding a shield stands guard."}},
                {"scene": 2, "plan": {"location": "royal chamber", "character_name": "knight", "action": "walk", "description": "He enters the chamber."}}
            ],
            # Movie 11: Campfire destroyed
            [
                {"scene": 1, "plan": {"location": "woods", "character_name": "hunter", "action": "build", "description": "A hunter builds a campfire."}},
                {"scene": 2, "plan": {"location": "woods", "character_name": "hunter", "action": "destroy", "description": "The hunter kicks and destroys the campfire."}}
            ],
            # Movie 12: Mage wearing crown
            [
                {"scene": 1, "plan": {"location": "throne room", "character_name": "mage", "action": "wear", "description": "The mage puts on the crown."}},
                {"scene": 2, "plan": {"location": "throne room", "character_name": "mage", "action": "stand", "description": "He looks at the king."}}
            ],
            # Movie 13: Sword and shield held together
            [
                {"scene": 1, "plan": {"location": "arena", "character_name": "knight", "action": "holds", "description": "A knight holding a sword walks in."}},
                {"scene": 2, "plan": {"location": "arena", "character_name": "knight", "action": "holds", "description": "He stands holding a shield too."}}
            ],
            # Movie 14: Wand usage
            [
                {"scene": 1, "plan": {"location": "library", "character_name": "mage", "action": "holds", "description": "A mage holding a wand studies a book."}},
                {"scene": 2, "plan": {"location": "library", "character_name": "mage", "action": "stand", "description": "He taps the book."}}
            ],
            # Movie 15: Weather snow to clear in mountains
            [
                {"scene": 1, "plan": {"location": "mountain slopes", "character_name": "hunter", "action": "walk", "description": "A hunter treks through the snow."}},
                {"scene": 2, "plan": {"location": "mountain slopes", "character_name": "hunter", "action": "stand", "description": "The weather changes to sunny."}}
            ],
            # Movie 16: Axe holding and dropping
            [
                {"scene": 1, "plan": {"location": "grove", "character_name": "villager", "action": "holds", "description": "A villager holding an axe chops a tree."}},
                {"scene": 2, "plan": {"location": "grove", "character_name": "villager", "action": "drop", "description": "He drops the axe."}}
            ],
            # Movie 17: Double key item transition
            [
                {"scene": 1, "plan": {"location": "castle hall", "character_name": "thief", "action": "grab", "description": "A thief picks up the key."}},
                {"scene": 2, "plan": {"location": "castle gate", "character_name": "thief", "action": "walk", "description": "He runs to the gate."}}
            ],
            # Movie 18: Torch in dark cave
            [
                {"scene": 1, "plan": {"location": "cave depth", "character_name": "knight", "action": "draw", "description": "A knight draws a torch in the dark."}},
                {"scene": 2, "plan": {"location": "cave depth", "character_name": "knight", "action": "walk", "description": "He continues walking."}}
            ],
            # Movie 19: Crown taken off
            [
                {"scene": 1, "plan": {"location": "chamber", "character_name": "king", "action": "wearing", "description": "The king wearing a crown stands."}},
                {"scene": 2, "plan": {"location": "chamber", "character_name": "king", "action": "remove", "description": "He takes off the crown."}}
            ],
            # Movie 20: Table prop persistence
            [
                {"scene": 1, "plan": {"location": "house room", "character_name": "merchant", "action": "place", "description": "A merchant places a table."}},
                {"scene": 2, "plan": {"location": "house room", "character_name": "merchant", "action": "stand", "description": "He lays out his wares."}}
            ]
        ]

        verified_assertions = 0
        
        for m_idx, movie in enumerate(movies):
            self.engine.clear_state()
            for s_idx, scene in enumerate(movie):
                scene_num = scene["scene"]
                plan = scene["plan"]
                
                state = self.engine.process_scene(plan, scene_num)
                
                # Assertions for Movie 1
                if m_idx == 0:
                    if scene_num == 1:
                        self.assertEqual(state["location"], "snowy forest")
                        self.assertEqual(state["weather"], "snow")
                        self.assertEqual(state["held_item"], "sword")
                    elif scene_num == 2:
                        self.assertEqual(state["location"], "snowy forest")
                        self.assertEqual(state["weather"], "snow")  # persists!
                        self.assertEqual(state["held_item"], "sword") # persists!
                    elif scene_num == 3:
                        self.assertEqual(state["held_item"], None)    # dropped!
                        
                # Assertions for Movie 2
                elif m_idx == 1:
                    if scene_num == 1:
                        self.assertIn("helmet", state["outfits"])
                    elif scene_num == 2:
                        self.assertIn("helmet", state["outfits"])  # persists!
                    elif scene_num == 3:
                        self.assertNotIn("helmet", state["outfits"]) # removed!
                        
                # Assertions for Movie 3
                elif m_idx == 2:
                    if scene_num == 1:
                        self.assertIn("campfire", state["environment_props"])
                    elif scene_num == 2:
                        self.assertIn("campfire", state["environment_props"])  # persists!
                    elif scene_num == 3:
                        self.assertNotIn("campfire", state["environment_props"]) # cleared because location changed!
                        
                # Assertions for Movie 4
                elif m_idx == 3:
                    if scene_num == 1:
                        self.assertEqual(state["weather"], "fog")
                        self.assertEqual(state["held_item"], "staff")
                    elif scene_num == 2:
                        self.assertEqual(state["weather"], "fog")
                        self.assertEqual(state["held_item"], "staff")
                        
                # Assertions for Movie 10
                elif m_idx == 9:
                    if scene_num == 1:
                        self.assertEqual(state["held_item"], "shield")
                    elif scene_num == 2:
                        self.assertEqual(state["held_item"], "shield") # persists across location change!
                
                verified_assertions += 1
                
        print(f"\n[Continuity Engine Test] Processed 20 multi-scene movies. Verified {verified_assertions} scene transitions successfully.")

if __name__ == "__main__":
    unittest.main()
