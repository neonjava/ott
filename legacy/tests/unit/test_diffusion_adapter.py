# tests/unit/test_diffusion_adapter.py
import unittest
import os
import shutil
from models.adapters.diffusion import DiffusionAdapter

class TestDiffusionAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = DiffusionAdapter("HunyuanVideo")
        self.test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_diffusion_output")
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_capabilities_and_prompt(self):
        caps = self.adapter.get_capabilities()
        self.assertEqual(caps["name"], "HunyuanVideo")
        self.assertTrue(caps["supports_image_reference"])
        
        # Build mock spec
        shot_spec = {
            "shot_id": "shot_01",
            "scene_id": "scene_01",
            "camera_type": "close_up",
            "camera_profile": "handheld",
            "camera_movement": "push_in",
            "composition": "rule_of_thirds",
            "emotion": "sad",
            "actor_focus": "knight",
            "duration": 4.0,
            "continuity": {"seed": 42, "environmental_seed": 100}
        }
        
        output_path = os.path.join(self.test_dir, "shot_01.mp4")
        self.adapter.render_shot(shot_spec, output_path)
        
        self.assertTrue(os.path.exists(output_path))
        with open(output_path, "r") as f:
            content = f.read()
        self.assertIn("HunyuanVideo", content)
        self.assertIn("knight", content)
        self.assertIn("push_in", content)
