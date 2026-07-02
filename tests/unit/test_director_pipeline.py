# tests/unit/test_director_pipeline.py
import unittest
from engine.director.story_planner import StoryPlanner
from engine.director.scene_planner_v2 import ScenePlannerV2
from engine.director.shot_planner import ShotPlanner
from engine.director.shot_spec import ShotSpec
from engine.director.backend_router import BackendRouter
from engine.director.director_pipeline import DirectorPipeline
from models.blender.blender_adapter import BlenderAdapter

class TestDirectorPipeline(unittest.TestCase):
    def setUp(self):
        self.story_planner = StoryPlanner()
        self.scene_planner = ScenePlannerV2()
        self.shot_planner = ShotPlanner()
        self.blender_adapter = BlenderAdapter()
        self.router = BackendRouter([self.blender_adapter])
        self.pipeline = DirectorPipeline([self.blender_adapter])

    def test_story_planner(self):
        idea = "A lonely knight walks inside the forest and discovers a rusty robot"
        story = self.story_planner.plan_story(idea)
        self.assertEqual(story["title"], "Iron and Moss")
        self.assertEqual(story["genre"], "Sci-Fi")
        self.assertIn("forest", story["locations"])
        self.assertIn("knight", story["characters"])

    def test_shot_planner_and_spec(self):
        mock_scene = {
            "scene_number": 1,
            "character_name": "knight",
            "action": "walk",
            "duration": 5.0,
            "mood": "sad"
        }
        shots = self.shot_planner.plan_shots_for_scene(mock_scene)
        self.assertEqual(len(shots), 2)
        self.assertEqual(shots[0]["transition"], "Fade In")
        
        spec = ShotSpec({
            "shot_id": "shot_01",
            "scene_id": "scene_01",
            "purpose": shots[0]["camera_objective"]
        })
        spec_dict = spec.to_dict()
        self.assertEqual(spec_dict["shot_id"], "shot_01")
        self.assertEqual(spec_dict["composition"], "rule_of_thirds")

    def test_backend_router(self):
        mock_spec = {
            "shot_id": "shot_01",
            "backend_requirements": {"supports_multi_character": True},
            "characters": [{"name": "knight"}, {"name": "robot"}]
        }
        best = self.router.route_shot(mock_spec)
        self.assertEqual(best.get_capabilities()["name"], "Blender Cycles")

    def test_director_pipeline_e2e(self):
        idea = "A man discovers an abandoned robot in the forest."
        res = self.pipeline.run_pipeline(idea)
        self.assertIn("story", res)
        self.assertGreater(len(res["scenes"]), 0)
        self.assertGreater(len(res["shot_specs"]), 0)
        self.assertGreater(len(res["backend_decisions"]), 0)
