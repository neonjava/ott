# tests/unit/test_pipeline_orchestrator.py
import unittest
import os
import shutil
from engine.storyboard.movie_graph import MovieGraph
from engine.director.pipeline_orchestrator import PipelineOrchestrator
from models.blender.blender_adapter import BlenderAdapter

class TestPipelineOrchestrator(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_orchestrator_output")
        self.adapter = BlenderAdapter()
        self.orchestrator = PipelineOrchestrator([self.adapter], critic_threshold=0.7)
        self.graph = MovieGraph()

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_pipeline_execution(self):
        # Configure test graph
        self.graph.set_movie("Orchestrator Test", "Sci-Fi", "Dark")
        self.graph.add_scene("scene_01", "intro", "tense", "loc_01")
        self.graph.add_shot("shot_01", "scene_01", "close_up", "Tripod")
        
        # Manually register the backend decision
        self.graph.add_backend_task("task_01", "shot_01", "Blender Cycles")
        
        # Execute production
        verified = self.orchestrator.execute_production(self.graph, self.test_dir)
        self.assertEqual(len(verified), 1)
        self.assertTrue(os.path.exists(verified[0]))
        
        # Verify tasks registered in graph
        self.assertEqual(len(self.graph.generation_tasks), 1)
        self.assertEqual(len(self.graph.review_tasks), 1)
        
        task_id = list(self.graph.generation_tasks.keys())[0]
        self.assertEqual(self.graph.generation_tasks[task_id]["status"], "completed")
