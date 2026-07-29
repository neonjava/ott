import unittest
import os
import json
import shutil
from engine.director.production_pipeline import RealProductionPipeline
from engine.backends.plugin_framework import BackendRegistry
from engine.voice.tts_engine import VoicePipeline
from engine.timeline.sequencer import TimelineSequencer
from engine.metrics.collector import MetricsCollector

class TestRealProductionPipelineSuite(unittest.TestCase):
    def setUp(self):
        self.tmp_output_dir = "outputs/test_real_prod"
        os.makedirs(self.tmp_output_dir, exist_ok=True)
        self.pipeline = RealProductionPipeline(backend_name="wan", output_dir=self.tmp_output_dir)

    def tearDown(self):
        if os.path.exists(self.tmp_output_dir):
            shutil.rmtree(self.tmp_output_dir)

    def test_backend_registry_plugin_resolution(self):
        registered = BackendRegistry.list_registered()
        self.assertIn("wan", registered)
        backend = BackendRegistry.get_backend("wan")
        self.assertIsNotNone(backend)
        self.assertTrue(backend.initialize())

    def test_hardware_metrics_collector(self):
        hw = MetricsCollector.get_hardware_info()
        self.assertIn("gpu_model", hw)
        self.assertIn("vram_allocated_gb", hw)
        self.assertIn("cpu_usage_percent", hw)
        self.assertIn("ram_used_gb", hw)

    def test_voice_pipeline_tts_and_subtitles(self):
        voice = VoicePipeline()
        lines = [
            {"duration": 3.0, "text": "Testing voice narration line one"},
            {"duration": 4.0, "text": "Testing voice narration line two"}
        ]
        audio_out = os.path.join(self.tmp_output_dir, "voice.wav")
        srt_out = os.path.join(self.tmp_output_dir, "sub.srt")
        res = voice.generate_narration(lines, audio_out, srt_out)
        self.assertTrue(os.path.exists(audio_out))
        self.assertTrue(os.path.exists(srt_out))
        self.assertEqual(res["total_duration_sec"], 7.0)

    def test_timeline_sequencer_frame_accuracy(self):
        seq = TimelineSequencer(fps=24)
        seq.add_shot(1, "shot_01.mp4", 5.0)
        seq.add_shot(2, "shot_02.mp4", 5.0)
        compiled = seq.compile_timeline(os.path.join(self.tmp_output_dir, "tl.json"))
        self.assertEqual(compiled["total_frames"], 240)
        self.assertEqual(compiled["total_duration_sec"], 10.0)

    def test_full_pipeline_execution(self):
        idea = "A lonely starship navigating the rings of Saturn"
        res = self.pipeline.execute_pipeline(idea_prompt=idea, target_duration_sec=10.0)
        
        self.assertEqual(res["total_shots"], 2)
        self.assertTrue(os.path.exists(res["exported_assets"]["screenplay"]))
        self.assertTrue(os.path.exists(res["exported_assets"]["movie_graph"]))
        self.assertTrue(os.path.exists(res["exported_assets"]["prompts"]))
        self.assertTrue(os.path.exists(res["exported_assets"]["narration_audio"]))
        self.assertTrue(os.path.exists(res["exported_assets"]["final_render"]))

if __name__ == "__main__":
    unittest.main()
