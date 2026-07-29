import unittest
import os
import shutil
from engine.backends.wan.backend import WANBackend
from engine.model_manager.manager import ModelManager
from engine.prompt_compiler.compiler import PromptCompiler

class TestWANBackendSuite(unittest.TestCase):
    def setUp(self):
        self.test_output_dir = "tests/tmp_outputs"
        os.makedirs(self.test_output_dir, exist_ok=True)
        self.backend = WANBackend()

    def tearDown(self):
        if os.path.exists(self.test_output_dir):
            shutil.rmtree(self.test_output_dir)

    def test_backend_lifecycle_and_health(self):
        self.assertTrue(self.backend.initialize())
        health = self.backend.health_check()
        self.assertEqual(health["status"], "healthy")
        self.assertEqual(health["version"], "2.1-open-source")

        # Load model test
        model_info = self.backend.load_model("wan-t2v-14b")
        self.assertIsNotNone(model_info)
        self.assertTrue(self.backend.health_check()["model_loaded"])

        # Unload model test
        self.assertTrue(self.backend.unload())
        self.assertFalse(self.backend.health_check()["model_loaded"])

    def test_prompt_compiler_wan(self):
        shot_spec = {
            "action": "A cyberpunk detective walking through neon-drenched rain",
            "characters": [{"name": "Detective V", "description": "leather coat, glowing cybernetic eye"}],
            "location": "Sector 7 Alley",
            "framing": "Wide",
            "camera_movement": "tracking forward",
            "lens": "35mm",
            "lighting": "Volumetric neon",
            "mood": "Noir moody"
        }
        pos, neg = PromptCompiler.compile_for_wan(shot_spec)
        self.assertIn("cyberpunk detective walking", pos)
        self.assertIn("Detective V", pos)
        self.assertIn("Sector 7 Alley", pos)
        self.assertIn("Wide shot", pos)
        self.assertIn("blurry", neg)

    def test_text_to_video_generation(self):
        output_path = os.path.join(self.test_output_dir, "test_wan.mp4")
        meta = self.backend.generate_from_text(
            prompt="A majestic dragon soaring over snow peaks",
            output_path=output_path,
            duration=3.0
        )
        self.assertTrue(os.path.exists(output_path))
        meta_path = os.path.join(self.test_output_dir, "test_wan_meta.json")
        self.assertTrue(os.path.exists(meta_path))
        self.assertEqual(meta["duration"], 3.0)

    def test_model_manager_discovery(self):
        mm = ModelManager()
        discovered = mm.discover_models()
        model_names = [d["name"] for d in discovered]
        self.assertIn("wan", model_names)
        self.assertIn("hunyuanvideo", model_names)
        self.assertIn("cogvideox", model_names)

    def test_render_shot_adapter_interface(self):
        shot_spec = {
            "description": "Astronaut standing on Mars looking at Earth in the sky",
            "duration": 4.0
        }
        output_path = os.path.join(self.test_output_dir, "mars_shot.mp4")
        result_path = self.backend.render_shot(shot_spec, output_path)
        self.assertTrue(os.path.exists(result_path))

if __name__ == "__main__":
    unittest.main()
