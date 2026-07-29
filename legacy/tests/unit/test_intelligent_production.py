# tests/unit/test_intelligent_production.py
import unittest
from engine.storyboard.movie_graph import MovieGraph
from engine.director.director_pipeline import DirectorPipeline
from models.blender.blender_adapter import BlenderAdapter
from engine.director.story_ai import StoryAI
from engine.director.scene_ai import SceneAI
from engine.director.shot_ai import ShotAI
from engine.director.editor_ai import EditorAI
from engine.director.critic_ai import CriticAI

class TestIntelligentProductionEngine(unittest.TestCase):
    def setUp(self):
        self.adapter = BlenderAdapter()
        self.pipeline = DirectorPipeline([self.adapter])
        self.graph = MovieGraph()

    def test_modular_planners(self):
        # 1. Test Story AI
        story_ai = StoryAI()
        story_ai.plan_story(self.graph, "A child discovers a glowing robot in the forest.")
        self.assertEqual(self.graph.movie["title"], "Iron and Moss")
        self.assertIn("beginning", self.graph.movie["story_arc"])
        
        # 2. Test Scene AI
        scene_ai = SceneAI()
        scene_ai.plan_scenes(self.graph)
        self.assertEqual(len(self.graph.scenes), 3)
        self.assertEqual(self.graph.scenes["scene_01"]["weather"], "foggy")
        
        # 3. Test Shot AI
        shot_ai = ShotAI()
        shot_ai.plan_shots(self.graph)
        self.assertEqual(len(self.graph.shots), 6) # 2 shots per scene
        
        # Check Shot continuity properties
        for shot in self.graph.shots.values():
            self.assertIn("seed", shot["continuity"])
            self.assertIn("environmental_seed", shot["continuity"])

        # 4. Test Editor AI
        editor_ai = EditorAI()
        editor_ai.optimize_plan(self.graph)
        
        # Verify shot pacing and transition overrides
        for shot in self.graph.shots.values():
            self.assertLessEqual(shot["duration"], 5.0)

        # 5. Test Critic AI
        critic_ai = CriticAI()
        review = critic_ai.evaluate_production_plan(self.graph)
        self.assertTrue(review["score"] > 0.6)

    def test_run_intelligent_pipeline(self):
        res_graph = self.pipeline.run_intelligent_pipeline(self.graph, "Knight fights dragon in castle.")
        self.assertEqual(res_graph.movie["title"], "The Journey")
        self.assertEqual(len(res_graph.scenes), 3)
        self.assertEqual(len(res_graph.shots), 6)
        
        # Ensure validation passes
        res_graph.validate()
        
        # Ensure backend tasks are generated
        self.assertEqual(len(res_graph.backend_tasks), 6)
