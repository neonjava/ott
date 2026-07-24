import unittest
import os
import json
import shutil
from engine.backends.wan.backend import WANBackend

class TestWANE2EIntegrationSuite(unittest.TestCase):
    def setUp(self):
        self.demo_dir = "outputs/demo_test"
        os.makedirs(self.demo_dir, exist_ok=True)
        self.backend = WANBackend()

    def tearDown(self):
        if os.path.exists(self.demo_dir):
            shutil.rmtree(self.demo_dir)

    def test_e2e_real_wan_generation_and_metadata_recording(self):
        output_video_path = os.path.join(self.demo_dir, "test_e2e_wan.mp4")
        prompt = "Cinematic drone shot over glowing cybernetic metropolis"
        seed = 1337
        
        self.backend.initialize()
        meta = self.backend.generate_from_text(
            prompt=prompt,
            output_path=output_video_path,
            seed=seed,
            duration=5.0
        )

        # 1. Verify video output file created
        self.assertTrue(os.path.exists(output_video_path))
        self.assertGreater(os.path.getsize(output_video_path), 0)

        # 2. Verify metadata sidecar JSON created
        meta_sidecar = os.path.join(self.demo_dir, "test_e2e_wan_meta.json")
        self.assertTrue(os.path.exists(meta_sidecar))

        with open(meta_sidecar, "r") as f:
            sidecar_data = json.load(f)

        # 3. Confirm all required recorded fields
        self.assertEqual(sidecar_data["model_version"], "2.1-open-source")
        self.assertIn("generation_time_sec", sidecar_data)
        self.assertIn("vram_gb", sidecar_data)
        self.assertEqual(sidecar_data["prompt"], prompt)
        self.assertEqual(sidecar_data["seed"], seed)
        self.assertEqual(sidecar_data["output_path"], output_video_path)

if __name__ == "__main__":
    unittest.main()
