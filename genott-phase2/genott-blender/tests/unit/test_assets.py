#!/usr/bin/env python3
"""
test_assets.py — Unit tests and regression tests verifying 100 asset noun extractions and resolutions.
"""
import unittest
import sys
import os

project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.append(project_dir)

from engine.director.asset_director import AssetDirector

class TestAssetRegistrySystem(unittest.TestCase):
    # 100 unique sentences, each containing one or more of the 100 registered nouns
    TEST_CASES = [
        # Props: Weapons & Armor (13)
        {"text": "A knight draws a sword.", "expected": ["sword"]},
        {"text": "The shield deflected the blow.", "expected": ["shield"]},
        {"text": "The soldier wields a spear.", "expected": ["spear"]},
        {"text": "An archer pulls back the bow.", "expected": ["bow"]},
        {"text": "The arrow pierced the target.", "expected": ["arrow"]},
        {"text": "He chopped wood with an axe.", "expected": ["axe"]},
        {"text": "She hid a dagger in her boot.", "expected": ["dagger"]},
        {"text": "The smith struck with a hammer.", "expected": ["hammer"]},
        {"text": "The wizard raised his staff.", "expected": ["staff"]},
        {"text": "A magic wand sparkled.", "expected": ["wand"]},
        {"text": "The helmet fits perfectly.", "expected": ["helmet"]},
        {"text": "Heavy armor protects him.", "expected": ["armor"]},
        {"text": "Leather boots walked quietly.", "expected": ["boots"]},
        
        # Creatures (15)
        {"text": "A massive dragon flew overhead.", "expected": ["dragon"]},
        {"text": "The horse galloped across the field.", "expected": ["horse"]},
        {"text": "A wolf howled in the dark.", "expected": ["wolf"]},
        {"text": "The dog barked at the stranger.", "expected": ["dog"]},
        {"text": "A cat slept on the table.", "expected": ["cat"]},
        {"text": "The bird sang in the branches.", "expected": ["bird"]},
        {"text": "A lion roared in the savannah.", "expected": ["lion"]},
        {"text": "The bear fished in the river.", "expected": ["bear"]},
        {"text": "A goblin snickered behind a rock.", "expected": ["goblin"]},
        {"text": "An orc charged with a battlecry.", "expected": ["orc"]},
        {"text": "The troll guarded the bridge.", "expected": ["troll"]},
        {"text": "A giant stepped over the hill.", "expected": ["giant"]},
        {"text": "A scary monster emerged from the lake.", "expected": ["monster"]},
        {"text": "The spider spun a web.", "expected": ["spider"]},
        {"text": "A green snake slithered by.", "expected": ["snake"]},
        
        # Characters (11)
        {"text": "The castle guard stood at attention.", "expected": ["castle guard"]},
        {"text": "A knight rode into battle.", "expected": ["knight"]},
        {"text": "The mage cast a fireball.", "expected": ["mage"]},
        {"text": "The king sat on his throne.", "expected": ["king"]},
        {"text": "The queen ruled with wisdom.", "expected": ["queen"]},
        {"text": "The young prince trained in the yard.", "expected": ["prince"]},
        {"text": "The princess waved from the tower.", "expected": ["princess"]},
        {"text": "A friendly villager helped us.", "expected": ["villager"]},
        {"text": "The merchant sold spices.", "expected": ["merchant"]},
        {"text": "The blacksmith forged steel.", "expected": ["blacksmith"]},
        {"text": "A soldier marched in line.", "expected": ["soldier"]},
        
        # Items (14)
        {"text": "A treasure chest was found.", "expected": ["chest"]},
        {"text": "She inserted the golden key.", "expected": ["key"]},
        {"text": "He drank a healing potion.", "expected": ["potion"]},
        {"text": "The scroll contained a map.", "expected": ["scroll"]},
        {"text": "A dusty book lay open.", "expected": ["book"]},
        {"text": "The ring glowed with power.", "expected": ["ring"]},
        {"text": "An ancient amulet hung on her neck.", "expected": ["amulet"]},
        {"text": "A shining gem caught the light.", "expected": ["gem"]},
        {"text": "He tossed a gold coin.", "expected": ["coin"]},
        {"text": "Piles of gold filled the vault.", "expected": ["gold"]},
        {"text": "The king wore a crown.", "expected": ["crown"]},
        {"text": "A torch lit the dark hallway.", "expected": ["torch"]},
        {"text": "The candle burned low.", "expected": ["candle"]},
        {"text": "A paper lantern swayed.", "expected": ["lantern"]},
        
        # Furniture & Vehicles (11)
        {"text": "He sat on a wooden chair.", "expected": ["chair"]},
        {"text": "Food was served on the table.", "expected": ["table"]},
        {"text": "She rested on the bed.", "expected": ["bed"]},
        {"text": "The grand throne was gold.", "expected": ["throne"]},
        {"text": "A barrel of water rolled.", "expected": ["barrel"]},
        {"text": "The wooden crate was empty.", "expected": ["crate"]},
        {"text": "A horse pulled the cart.", "expected": ["cart"]},
        {"text": "The royal carriage arrived.", "expected": ["carriage"]},
        {"text": "We rowed the boat.", "expected": ["boat"]},
        {"text": "A large ship sailed away.", "expected": ["ship"]},
        {"text": "A heavy wagon blocked the road.", "expected": ["wagon"]},
        
        # Nature & Buildings (14)
        {"text": "A tall tree stood nearby.", "expected": ["tree"]},
        {"text": "A giant rock blocked the path.", "expected": ["rock"]},
        {"text": "A smooth stone skipped on water.", "expected": ["stone"]},
        {"text": "A beautiful flower bloomed.", "expected": ["flower"]},
        {"text": "Green grass grew everywhere.", "expected": ["grass"]},
        {"text": "A strange plant grew in the cave.", "expected": ["plant"]},
        {"text": "He hid behind a bush.", "expected": ["bush"]},
        {"text": "The wood was dry and ready.", "expected": ["wood"]},
        {"text": "A fallen log lay across the trail.", "expected": ["log"]},
        {"text": "They gathered around the campfire.", "expected": ["campfire"]},
        {"text": "She pitched a tent.", "expected": ["tent"]},
        {"text": "They entered the old house.", "expected": ["house"]},
        {"text": "A log cabin stood in the woods.", "expected": ["cabin"]},
        {"text": "The stone castle loomed ahead.", "expected": ["castle"]},
        
        # Classes & Advanced Props (26)
        {"text": "A brave spearman held the line.", "expected": ["spearman"]},
        {"text": "A alert guard watched.", "expected": ["guard"]},
        {"text": "An archer shot an arrow.", "expected": ["archer", "arrow"]},
        {"text": "The warrior carried an axe.", "expected": ["warrior", "axe"]},
        {"text": "The priest prayed quietly.", "expected": ["priest"]},
        {"text": "A thief stole the key.", "expected": ["thief", "key"]},
        {"text": "An assassin held a dagger.", "expected": ["assassin", "dagger"]},
        {"text": "A ranger tracked the wolf.", "expected": ["ranger", "wolf"]},
        {"text": "The hunter set a trap.", "expected": ["hunter"]},
        {"text": "A druid spoke to trees.", "expected": ["druid"]},
        {"text": "The warlock cast a spell.", "expected": ["warlock"]},
        {"text": "A summoner summoned a monster.", "expected": ["summoner", "monster"]},
        {"text": "A heavy mace fell.", "expected": ["mace"]},
        {"text": "The guard held a halberd.", "expected": ["guard", "halberd"]},
        {"text": "The grim reaper held a scythe.", "expected": ["scythe"]},
        {"text": "A crossbow lay on the table.", "expected": ["crossbow", "table"]},
        {"text": "An archer carried a quiver.", "expected": ["archer", "quiver"]},
        {"text": "A buckler was strapped to his arm.", "expected": ["buckler"]},
        {"text": "He swung a greatsword.", "expected": ["greatsword"]},
        {"text": "A slender rapier gleamed.", "expected": ["rapier"]},
        {"text": "She drew a sharp katana.", "expected": ["katana"]},
        
        # Extra compound check sentences to make up to 100 cases
        {"text": "The king and queen sat down.", "expected": ["king", "queen"]},
        {"text": "A horse and cart traveled slowly.", "expected": ["horse", "cart"]},
        {"text": "A giant and troll fought.", "expected": ["giant", "troll"]},
        {"text": "The knight took the sword and shield.", "expected": ["knight", "sword", "shield"]},
        {"text": "The castle guard carried a spear.", "expected": ["castle guard", "spear"]}
    ]

    def setUp(self):
        self.director = AssetDirector()

    def test_noun_extraction_and_resolution(self):
        total_checks = 0
        passed_checks = 0
        
        for idx, tc in enumerate(self.TEST_CASES):
            text = tc["text"]
            expected = tc["expected"]
            
            extracted = self.director.extract_nouns(text)
            
            # Check noun extraction
            for exp in expected:
                total_checks += 1
                with self.subTest(text=text, expected_noun=exp):
                    self.assertIn(exp, extracted, f"Sentence '{text}' failed to extract noun '{exp}'")
                    passed_checks += 1
                    
            # Check asset resolution
            for noun in extracted:
                total_checks += 1
                res = self.director.resolve_asset(noun)
                with self.subTest(noun=noun):
                    self.assertEqual(res["noun"], noun)
                    # All assets except character humanoid.glb are missing on disk, so they must fallback
                    self.assertTrue(res["is_fallback"])
                    self.assertTrue(res["missing"])
                    self.assertIsNotNone(res["fallback"])
                    self.assertIsNotNone(res["scale"])
                    self.assertIsNotNone(res["placement"])
                    passed_checks += 1
                    
        print(f"\n[Asset Registry Test] Ran {len(self.TEST_CASES)} sentences. Verified {passed_checks}/{total_checks} assertions successfully.")

if __name__ == "__main__":
    unittest.main()
