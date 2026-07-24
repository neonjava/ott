import unittest
import os
import json
import shutil
from engine.director.director_agent import DirectorAgent
from engine.characters.memory import CharacterMemory
from engine.critic.continuity_guard import VisualContinuityGuard
from engine.storyboard.camera_planner import CameraPlanner
from engine.critic.shot_reviewer import ShotReviewer
from engine.routing.backend_router import BackendRouter
from engine.memory.production_db import ProductionDatabase
from engine.memory.self_improvement import SelfImprovementEngine
from engine.director.production_pipeline import RealProductionPipeline

class TestAIDirectorProductionIntelligenceSuite(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = "outputs/test_ai_director"
        os.makedirs(self.tmp_dir, exist_ok=True)
        self.pipeline = RealProductionPipeline(output_dir=self.tmp_dir)

    def tearDown(self):
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

    def test_director_agent_pacing_and_review(self):
        agent = DirectorAgent()
        screenplay = {"shots": [{"duration": 5.0}, {"duration": 5.0}]}
        mg = {"shots": [{"action": "Short action", "framing": ""}]}
        pacing = agent.analyze_screenplay_pacing(screenplay)
        review = agent.review_movie_graph(mg)
        self.assertEqual(pacing["pacing_score"], 0.90)
        self.assertGreater(len(review["improvement_suggestions"]), 0)

    def test_character_memory_persistence(self):
        mem = CharacterMemory(memory_file=os.path.join(self.tmp_dir, "char_mem.json"))
        char = mem.register_character("Nova", "glowing cybernetic eyes", age=28)
        self.assertEqual(char["name"], "Nova")
        self.assertIn("Nova", mem.get_prompt_description("Nova"))

    def test_visual_continuity_guard(self):
        guard = VisualContinuityGuard()
        shots = [
            {"location": "Bridge", "lighting": "Neon blue"},
            {"location": "Bridge", "lighting": "Golden dawn"}  # Lighting mismatch
        ]
        audit = guard.audit_scene_continuity(shots)
        self.assertFalse(audit["is_continuous"])
        self.assertGreater(len(audit["continuity_flags"]), 0)

    def test_camera_planner(self):
        planner = CameraPlanner()
        shot = planner.plan_camera_for_shot({"action": "Starship hyper-jump core ignites"})
        self.assertEqual(shot["cinematography_preset"], "dramatic")
        self.assertIn("Macro", shot["framing"])

    def test_shot_reviewer_quality_evaluation(self):
        reviewer = ShotReviewer()
        shot_spec = {"duration": 5.0}
        gen_res = {"prompt": "Wide tracking shot of starship with cinematic volumetric lighting", "duration": 5.0}
        score, eval_dict, needs_regen = reviewer.evaluate_shot(shot_spec, gen_res)
        self.assertGreaterEqual(score, 0.80)
        self.assertFalse(needs_regen)

    def test_backend_router_selection(self):
        router = BackendRouter()
        backend = router.select_backend(intent="cinematic", resolution="1080p")
        self.assertIsNotNone(backend)
        self.assertEqual(backend.get_capabilities()["name"], "WAN")

    def test_full_ai_director_single_command_execution(self):
        prompt = "Create a 30 second sci-fi short film"
        meta = self.pipeline.execute_pipeline(idea_prompt=prompt, target_duration_sec=10.0)
        self.assertIn("director_intelligence", meta)
        self.assertTrue(os.path.exists(meta["exported_assets"]["final_render"]))

if __name__ == "__main__":
    unittest.main()
