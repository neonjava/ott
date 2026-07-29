#!/usr/bin/env python3
"""
test_environment.py — Unit tests and regression tests verifying 100 environment classifications.
"""
import unittest
import sys
import os

project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.append(project_dir)

from engine.director.environment_director import get_environment_for_location

class TestEnvironmentClassification(unittest.TestCase):
    # 100 unique environment classification test cases
    TEST_CASES = [
        # Forest (12)
        {"location": "snowy forest", "expected": "forest"},
        {"location": "deep pine woods", "expected": "forest"},
        {"location": "shadowy jungle", "expected": "forest"},
        {"location": "green grove", "expected": "forest"},
        {"location": "dark woodland", "expected": "forest"},
        {"location": "thick leaf canopy", "expected": "forest"},
        {"location": "rainforest", "expected": "forest"},
        {"location": "mystic woods", "expected": "forest"},
        {"location": "autumn grove", "expected": "forest"},
        {"location": "birch forest", "expected": "forest"},
        {"location": "ancient jungle", "expected": "forest"},
        {"location": "pine trees", "expected": "forest"},
        
        # Castle (13)
        {"location": "abandoned castle", "expected": "castle"},
        {"location": "royal palace", "expected": "castle"},
        {"location": "stone keep", "expected": "castle"},
        {"location": "ancient fortress", "expected": "castle"},
        {"location": "dark dungeon", "expected": "castle"},
        {"location": "high tower", "expected": "castle"},
        {"location": "throne chamber", "expected": "castle"},
        {"location": "castle ruins", "expected": "castle"},
        {"location": "wizard tower", "expected": "castle"},
        {"location": "palace gardens", "expected": "castle"},
        {"location": "stone walls", "expected": "castle"},
        {"location": "royal court", "expected": "castle"},
        {"location": "golden kingdom", "expected": "castle"},
        
        # Village (13)
        {"location": "peaceful village", "expected": "village"},
        {"location": "market town", "expected": "village"},
        {"location": "cozy house", "expected": "village"},
        {"location": "village street", "expected": "village"},
        {"location": "farm cottage", "expected": "village"},
        {"location": "school yard", "expected": "village"},
        {"location": "classroom", "expected": "village"},
        {"location": "quiet library", "expected": "village"},
        {"location": "village square", "expected": "village"},
        {"location": "wooden cabin", "expected": "village"},
        {"location": "blacksmith shop", "expected": "village"},
        {"location": "old tavern", "expected": "village"},
        {"location": "crowded market", "expected": "village"},
        
        # Cave (12)
        {"location": "dark cave", "expected": "cave"},
        {"location": "crystal cavern", "expected": "cave"},
        {"location": "underground tunnel", "expected": "cave"},
        {"location": "gold mine", "expected": "cave"},
        {"location": "pitch black abyss", "expected": "cave"},
        {"location": "deep underground cavern", "expected": "cave"},
        {"location": "ice cave", "expected": "cave"},
        {"location": "lava cavern", "expected": "cave"},
        {"location": "shadow cave", "expected": "cave"},
        {"location": "secret passage", "expected": "cave"},
        {"location": "subterranean tunnel", "expected": "cave"},
        {"location": "dark abyss", "expected": "cave"},
        
        # Beach (12)
        {"location": "sunny beach", "expected": "beach"},
        {"location": "rocky coast", "expected": "beach"},
        {"location": "sandy shore", "expected": "beach"},
        {"location": "wide ocean", "expected": "beach"},
        {"location": "deep blue sea", "expected": "beach"},
        {"location": "tropical island", "expected": "beach"},
        {"location": "beachfront", "expected": "beach"},
        {"location": "shallow water", "expected": "beach"},
        {"location": "sunny lake", "expected": "beach"},
        {"location": "ocean waves", "expected": "beach"},
        {"location": "coral reef", "expected": "beach"},
        {"location": "sandy beachside", "expected": "beach"},
        
        # Mountain (12)
        {"location": "mountain peak", "expected": "mountain"},
        {"location": "snowy hill", "expected": "mountain"},
        {"location": "rocky cliff", "expected": "mountain"},
        {"location": "cold mountain pass", "expected": "mountain"},
        {"location": "frozen slopes", "expected": "mountain"},
        {"location": "high peak", "expected": "mountain"},
        {"location": "mountain pass", "expected": "mountain"},
        {"location": "windy slopes", "expected": "mountain"},
        {"location": "snowy ridge", "expected": "mountain"},
        {"location": "rocky mountains", "expected": "mountain"},
        {"location": "glacier slopes", "expected": "mountain"},
        {"location": "snowy heights", "expected": "mountain"},
        
        # City (13)
        {"location": "busy street", "expected": "city"},
        {"location": "industrial factory", "expected": "city"},
        {"location": "large warehouse", "expected": "city"},
        {"location": "high-tech laboratory", "expected": "city"},
        {"location": "train station", "expected": "city"},
        {"location": "gaming cafe", "expected": "city"},
        {"location": "classroom hallway", "expected": "city"},
        {"location": "asphalt road", "expected": "city"},
        {"location": "city streets", "expected": "city"},
        {"location": "highway bridge", "expected": "city"},
        {"location": "science lab", "expected": "city"},
        {"location": "subway station", "expected": "city"},
        {"location": "office hallway", "expected": "city"},
        
        # Arena (13)
        {"location": "fighting arena", "expected": "arena"},
        {"location": "sports stadium", "expected": "arena"},
        {"location": "circular ring", "expected": "arena"},
        {"location": "elevated platform", "expected": "arena"},
        {"location": "conveyor belt", "expected": "arena"},
        {"location": "training field", "expected": "arena"},
        {"location": "default environment", "expected": "arena"},
        {"location": "empty grid", "expected": "arena"},
        {"location": "battle ring", "expected": "arena"},
        {"location": "combat arena", "expected": "arena"},
        {"location": "practice field", "expected": "arena"},
        {"location": "gladiator arena", "expected": "arena"},
        {"location": "empty environment", "expected": "arena"}
    ]
    
    def test_classifications(self):
        passed = 0
        failed_cases = []
        for idx, tc in enumerate(self.TEST_CASES):
            loc = tc["location"]
            expected = tc["expected"]
            config = get_environment_for_location(loc)
            actual = config.get("environment_type")
            
            with self.subTest(location=loc, expected=expected):
                if actual == expected:
                    passed += 1
                else:
                    failed_cases.append((loc, expected, actual))
                self.assertEqual(actual, expected, f"Location '{loc}' expected '{expected}', got '{actual}'")
        
        print(f"\n[Environment Regression Test] Classified {passed}/{len(self.TEST_CASES)} locations successfully.")
        if failed_cases:
            print("Failures:")
            for fc in failed_cases:
                print(f"  - '{fc[0]}': expected '{fc[1]}', got '{fc[2]}'")

    def test_weather_volumetrics(self):
        """Verify build_environment_in_blender completes or skips gracefully on environment configs."""
        from engine.director.environment_director import build_environment_in_blender
        env_config = {"environment_type": "forest", "weather": "rainy"}
        # Ensure it runs without exception in both Blender and mock contexts
        seed = build_environment_in_blender(env_config, (0, 0, 0), "rainy")
        self.assertTrue(seed is None or isinstance(seed, int))

if __name__ == "__main__":
    unittest.main()
