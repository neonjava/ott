import unittest
import os
import json
import shutil
from engine.director.demo_orchestrator import DemoOrchestrator

class Test30sDemoMilestoneSuite(unittest.TestCase):
    def setUp(self):
        self.tmp_demo_dir = "outputs/demo_test_30s"
        os.makedirs(self.tmp_demo_dir, exist_ok=True)
        self.orchestrator = DemoOrchestrator(output_dir=self.tmp_demo_dir)

    def tearDown(self):
        if os.path.exists(self.tmp_demo_dir):
            shutil.rmtree(self.tmp_demo_dir)

    def test_30s_cinematic_demo_milestone_production(self):
        meta = self.orchestrator.run_30s_cinematic_production()

        # 1. Total duration and shot counts
        self.assertEqual(meta["total_duration_sec"], 30.0)
        self.assertEqual(meta["number_of_shots"], 6)

        # 2. Verify all asset files exist
        assets = meta["assets"]
        self.assertTrue(os.path.exists(assets["screenplay_script"]))
        self.assertTrue(os.path.exists(assets["shot_prompts"]))
        self.assertTrue(os.path.exists(assets["narration_audio"]))
        self.assertTrue(os.path.exists(assets["final_export"]))

if __name__ == "__main__":
    unittest.main()
