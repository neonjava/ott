import unittest
import os
import shutil
from engine.model_manager.registry import ModelRegistry, OFFICIAL_MODEL_SPECS
from engine.model_manager.installer import ModelInstaller

class TestModelInstallerRegistrySuite(unittest.TestCase):
    def setUp(self):
        self.tmp_models_dir = "tests/tmp_models"
        self.tmp_third_party_dir = "tests/tmp_third_party"
        self.tmp_registry_file = "tests/tmp_configs/registry.json"

        os.makedirs(self.tmp_models_dir, exist_ok=True)
        os.makedirs(self.tmp_third_party_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.tmp_registry_file), exist_ok=True)

        self.installer = ModelInstaller(
            base_models_dir=self.tmp_models_dir,
            third_party_dir=self.tmp_third_party_dir
        )
        self.installer.registry.registry_file = os.path.abspath(self.tmp_registry_file)

    def tearDown(self):
        for p in [self.tmp_models_dir, self.tmp_third_party_dir, "tests/tmp_configs"]:
            if os.path.exists(p):
                shutil.rmtree(p)

    def test_system_resource_detection(self):
        res = self.installer.detect_system_resources()
        self.assertIn("free_disk_gb", res)
        self.assertIn("gpu_vram_gb", res)
        self.assertIn("cuda_version", res)
        self.assertIn("python_version", res)

    def test_registry_initialization_and_saving(self):
        reg = self.installer.registry
        models = reg.list_all()
        self.assertIn("wan", models)
        self.assertIn("hunyuanvideo", models)
        self.assertIn("cogvideox", models)
        self.assertIn("ltx-video", models)
        self.assertIn("mochi", models)

    def test_model_directory_preparation(self):
        subdirs = self.installer.prepare_model_directory_structure("wan")
        self.assertTrue(os.path.exists(subdirs["weights"]))
        self.assertTrue(os.path.exists(subdirs["configs"]))
        self.assertTrue(os.path.exists(subdirs["tokenizers"]))
        self.assertTrue(os.path.exists(subdirs["cache"]))

    def test_model_install_verify_remove_lifecycle(self):
        # Install
        success = self.installer.install_model("wan")
        self.assertTrue(success)

        # Verify
        verification = self.installer.verify_model("wan")
        self.assertEqual(verification["status"], "healthy")
        self.assertTrue(verification["weights_exist"])

        # Remove
        removed = self.installer.remove_model("wan")
        self.assertTrue(removed)
        verification_after = self.installer.verify_model("wan")
        self.assertFalse(verification_after["weights_exist"])

if __name__ == "__main__":
    unittest.main()
