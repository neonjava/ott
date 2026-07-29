# tests/unit/test_contracts.py
import unittest
from engine.storyboard.movie_graph import (
    MovieGraph, MovieSpec, SceneSpec, ShotSpec,
    BackendTask, GenerationTask, ContractValidationError
)

class TestArchitectureContracts(unittest.TestCase):
    def test_movie_spec_validation(self):
        # Valid construction
        ms = MovieSpec("Dawn of AI", "Sci-Fi", "Suspenseful")
        self.assertEqual(ms.title, "Dawn of AI")
        
        # Invalid title
        with self.assertRaises(ContractValidationError):
            MovieSpec(" ", "Sci-Fi", "Suspenseful")
            
        # Invalid duration
        with self.assertRaises(ContractValidationError):
            MovieSpec("Title", "Sci-Fi", "Suspenseful", duration=-5.0)

    def test_shot_spec_validation(self):
        # Valid construction
        sh = ShotSpec("shot_01", "scene_01", "close_up", "Dolly")
        self.assertEqual(sh.continuity["seed"], 42)
        
        # Invalid duration
        with self.assertRaises(ContractValidationError):
            ShotSpec("shot_01", "scene_01", "close_up", "Dolly", duration=0.0)

        # Missing continuity fields
        with self.assertRaises(ContractValidationError):
            ShotSpec("shot_01", "scene_01", "close_up", "Dolly", continuity={"seed": 42})

    def test_movie_graph_strict_mode(self):
        graph = MovieGraph()
        # Initial empty graph is valid
        graph.validate()
        
        # Inject corrupt scene directly (bypassing add_scene verification check)
        graph.scenes["scene_corrupt"] = {
            "scene_id": "scene_corrupt",
            "purpose": "broken",
            "emotion": "broken",
            "location_id": "loc_01",
            "weather": "clear",
            "duration": -1.0 # Invalid duration!
        }
        
        # validate() must fail in strict mode
        with self.assertRaises(ContractValidationError):
            graph.validate()
