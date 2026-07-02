# tests/unit/test_movie_graph.py
import unittest
import os
import shutil
from engine.storyboard.movie_graph import MovieGraph
from engine.storyboard.event_bus import EventBus
from engine.timeline.project_manager import MovieProjectManager

class TestMovieGraphSystem(unittest.TestCase):
    def setUp(self):
        self.bus = EventBus()
        self.graph = MovieGraph(self.bus)
        self.test_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_graph_root")
        self.manager = MovieProjectManager(self.test_root)

        # Track event publishes
        self.received_events = []
        self.bus.subscribe("MovieCreated", lambda data: self.received_events.append(("MovieCreated", data)))
        self.bus.subscribe("SceneGenerated", lambda data: self.received_events.append(("SceneGenerated", data)))

    def tearDown(self):
        if os.path.exists(self.test_root):
            shutil.rmtree(self.test_root)

    def test_graph_and_events(self):
        # Set Movie
        self.graph.set_movie("Robot Uprising", "Sci-Fi", "Dark")
        self.assertEqual(self.graph.movie["title"], "Robot Uprising")
        
        # Add Scene
        self.graph.add_scene("scene_01", "introduce characters", "tense", "loc_01")
        self.assertEqual(len(self.graph.scenes), 1)
        
        # Verify event bus triggers
        self.assertEqual(len(self.received_events), 2)
        self.assertEqual(self.received_events[0][0], "MovieCreated")
        self.assertEqual(self.received_events[1][0], "SceneGenerated")

    def test_serialization_reconstruction(self):
        self.graph.set_movie("Adventure Time", "Comedy", "Light")
        self.graph.add_scene("scene_01", "intro", "happy", "loc_01")
        self.graph.add_shot("shot_01", "scene_01", "medium", "Tripod")
        self.graph.add_character("char_01", "Humanoid")
        self.graph.add_location("loc_01", "Jungle")
        
        serialized = self.graph.serialize()
        
        # Reconstruct graph in a new instance
        new_graph = MovieGraph()
        new_graph.deserialize(serialized)
        
        self.assertEqual(new_graph.movie["title"], "Adventure Time")
        self.assertEqual(new_graph.scenes["scene_01"]["emotion"], "happy")
        self.assertEqual(new_graph.shots["shot_01"]["camera_profile"], "Tripod")
        self.assertEqual(new_graph.characters["char_01"]["name"], "Humanoid")
        self.assertEqual(new_graph.locations["loc_01"]["name"], "Jungle")

    def test_project_integration(self):
        # Create project
        self.manager.create_project("Project Graph Test", "Developer Y")
        
        # Configure its graph
        self.manager.movie_graph.set_movie("Project Movie", "Drama", "Serious")
        self.manager.movie_graph.add_scene("scene_01", "intro", "sad", "loc_01")
        self.manager.save_project()
        
        # Reload project
        new_manager = MovieProjectManager(self.test_root)
        new_manager.open_project("Project Graph Test")
        
        # Verify reconstructed graph
        self.assertEqual(new_manager.movie_graph.movie["title"], "Project Movie")
        self.assertEqual(new_manager.movie_graph.scenes["scene_01"]["emotion"], "sad")
