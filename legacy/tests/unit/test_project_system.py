# tests/unit/test_project_system.py
import unittest
import os
import shutil
from engine.timeline.project_manager import MovieProjectManager
from models.blender.blender_adapter import BlenderAdapter

class TestProjectSystemAndAdapters(unittest.TestCase):
    def setUp(self):
        # Use a temporary root for sandbox safety
        self.test_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_studio_root")
        self.manager = MovieProjectManager(self.test_root)

    def tearDown(self):
        if os.path.exists(self.test_root):
            shutil.rmtree(self.test_root)

    def test_project_lifecycle(self):
        # Create
        path = self.manager.create_project("Epic Short Film", "Director X")
        self.assertTrue(os.path.exists(path))
        self.assertTrue(os.path.exists(os.path.join(path, "project.json")))
        
        # Verify folders exist
        self.assertTrue(os.path.exists(os.path.join(path, "script")))
        self.assertTrue(os.path.exists(os.path.join(path, "shots")))
        
        # Open
        opened = self.manager.open_project("Epic Short Film")
        self.assertTrue(opened)
        self.assertEqual(self.manager.project_data["author"], "Director X")
        self.assertEqual(self.manager.project_data["status"], "Draft")
        
        # Validate
        val_res = self.manager.validate_project()
        self.assertTrue(val_res["valid"])
        
        # Archive
        self.manager.archive_project()
        self.assertEqual(self.manager.project_data["status"], "Archived")
        
    def test_clone_and_backup(self):
        self.manager.create_project("Base Template", "System User")
        
        # Clone
        clone_path = self.manager.clone_project("Base Template", "Cloned Instance")
        self.assertTrue(os.path.exists(clone_path))
        
        self.manager.open_project("Cloned Instance")
        self.assertEqual(self.manager.project_data["name"], "Cloned Instance")

    def test_blender_adapter_capabilities(self):
        adapter = BlenderAdapter()
        caps = adapter.get_capabilities()
        self.assertEqual(caps["name"], "Blender Cycles")
        self.assertTrue(caps["supports_camera_control"])
        self.assertGreater(caps["max_duration"], 0)
