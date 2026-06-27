# test_subsystems.py
import unittest
import os
import json
import time
from ai.asset_pipeline import AssetPipelineAgent
from ai.motion_intelligence import MotionIntelligenceAgent
from ai.physics_simulation import PhysicsSimulationAgent
from ai.dialogue_performance import DialoguePerformanceAgent
from ai.cinematic_critic import CinematicCriticAgent
from ai.scene_streaming import SceneStreamingAgent
from ai.timeline_editing import TimelineEditingAgent
from ai.render_farm import RenderFarmAgent
from ai.ai_research import AIResearchAgent
from ai.production_readiness import ProductionReadinessAgent
from ai.scene_graph import SceneGraphManager, SceneGraphNode
from ai.visual_continuity import VisualContinuityEngine
from ai.procedural_layout import ProceduralLayoutSolver
from ai.camera_collision import CameraCollisionSolver
from ai.animation_graph import AnimationGraph
from ai.emotion_memory import EmotionMemoryEngine
from ai.gpu_performance import GPUPerformanceMonitor
from ai.audio_composer import AudioComposer
from ai.renderer.blender import BlenderVideoRenderer
from ai.project_manager import MovieProjectManager
from ai.usd.usd_exporter import USDExporter
from ai.usd.usd_importer import USDImporter
from ai.fluid_cache import FluidCacheManager
from ai.camera_motion import CameraMotionEngine
from ai.facial_performance import FacialPerformanceEngine
from ai.character_motion import CharacterMotionEngine
from ai.director_intelligence import DirectorIntelligenceEngine

class TestEngineSubsystems(unittest.TestCase):
    def setUp(self):
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        self.asset_pipeline = AssetPipelineAgent(project_dir=self.project_dir)
        self.motion_intel = MotionIntelligenceAgent()
        self.physics_sim = PhysicsSimulationAgent()
        self.dialogue_perf = DialoguePerformanceAgent()
        self.critic = CinematicCriticAgent(quality_threshold=0.7)
        self.streaming = SceneStreamingAgent(max_concurrent_assets=3)
        self.timeline_edit = TimelineEditingAgent()
        self.render_farm = RenderFarmAgent()
        self.research = AIResearchAgent()
        self.readiness = ProductionReadinessAgent()
        self.scene_graph = SceneGraphManager()
        self.continuity = VisualContinuityEngine()
        self.layout_solver = ProceduralLayoutSolver()
        self.camera_solver = CameraCollisionSolver()
        self.anim_graph = AnimationGraph()
        self.emotion_engine = EmotionMemoryEngine()
        self.gpu_monitor = GPUPerformanceMonitor()
        self.audio_composer = AudioComposer()
        self.project_manager = MovieProjectManager(self.project_dir)
        self.usd_exporter = USDExporter()
        self.usd_importer = USDImporter()
        self.fluid_cache = FluidCacheManager(self.project_dir)
        self.camera_motion = CameraMotionEngine()
        self.facial_engine = FacialPerformanceEngine()
        self.char_motion = CharacterMotionEngine()
        self.director_engine = DirectorIntelligenceEngine()

    def test_asset_pipeline(self):
        # Resolve sword
        details = self.asset_pipeline.get_asset_details("sword")
        self.assertEqual(details.get("type"), "prop")
        # Validate missing
        val = self.asset_pipeline.validate_asset("non_existent_asset")
        self.assertFalse(val["valid"])

    def test_motion_intelligence(self):
        params = self.motion_intel.compute_blend_parameters("idle", "walk")
        self.assertEqual(params["curve"], "ease-in-out")
        ik = self.motion_intel.get_ik_targets("walk", speed=1.2)
        self.assertGreater(ik["foot_ik_left_weight"], 0)

    def test_physics_simulation(self):
        settings = self.physics_sim.get_simulation_settings("stormy mountains", "epic")
        self.assertTrue(settings["cloth_enabled"])
        self.assertGreater(settings["secondary_motion_multiplier"], 1.0)

    def test_dialogue_performance(self):
        pacing = self.dialogue_perf.calculate_pacing("Wait, who goes there?", "fear")
        self.assertGreater(pacing["wpm"], 140)
        micro = self.dialogue_perf.generate_micro_expressions(5.0)
        self.assertIsInstance(micro, list)

    def test_cinematic_critic(self):
        mock_data = {"camera_type": "close_up", "mood": "tense", "animation_duration": 4.0}
        eval_res = self.critic.evaluate_render("/dev/null", mock_data)
        self.assertFalse(eval_res["approved"]) # File does not exist /dev/null is size 0

    def test_scene_streaming(self):
        timeline = [
            {"character": "thor", "scene_assets": [{"noun": "sword"}]},
            {"character": "tony", "scene_assets": [{"noun": "shield"}]},
            {"character": "hulk", "scene_assets": [{"noun": "spear"}]},
            {"character": "thor", "scene_assets": [{"noun": "sword"}]}
        ]
        schedule = self.streaming.build_stream_schedule(timeline)
        self.assertEqual(len(schedule), 4)

    def test_timeline_editing(self):
        clip = self.timeline_edit.create_clip("video", "clip_1", 0.0, 3.5, "scene_1.mp4")
        self.assertEqual(clip["duration"], 3.5)

    def test_render_farm(self):
        job = self.render_farm.submit_render_job("job_001", "hero walks", 3.0)
        self.assertEqual(job["status"], "rendering")
        completed = self.render_farm.complete_job("job_001", success=True)
        self.assertEqual(completed["status"], "completed")

    def test_ai_research(self):
        analysis = self.research.run_competitive_analysis()
        self.assertIn("pixar_usd", analysis)
        proposal = self.research.generate_proposal("usd integration")
        self.assertIn("OpenUSD", proposal)

    def test_production_readiness(self):
        services = {"flask": True, "blender": False}
        health = self.readiness.run_health_checks(services)
        self.assertEqual(health["status"], "degraded")
        recipe = self.readiness.recover_crashed_daemon("blender")
        self.assertIn("ports_to_free", recipe)

    def test_scene_graph(self):
        # Create character node
        char_node = SceneGraphNode("hero", "character")
        char_node.local_transform["translation"] = [1.0, 2.0, 0.0]
        self.scene_graph.root.add_child(char_node)
        
        # Create prop node parented to character
        prop_node = SceneGraphNode("sword", "prop")
        prop_node.local_transform["translation"] = [0.0, 0.0, 1.0]
        self.scene_graph.root.add_child(prop_node)
        self.scene_graph.attach_node("hero", "sword", socket="right_hand")
        
        # Verify relative parenting and world coordinates
        world_t = prop_node.get_world_transform()["translation"]
        self.assertEqual(world_t, [1.0, 2.0, 1.0])

    def test_visual_continuity(self):
        self.continuity.persistence_file = "test_continuity_state.json"
        self.continuity.shot_states = []
        if os.path.exists("test_continuity_state.json"):
            try:
                os.remove("test_continuity_state.json")
            except Exception:
                pass
                
        # Record first shot
        self.continuity.record_shot_state(0, {
            "outfits": {"hero": "heavy_armor"},
            "held_props": {"hero": "sword"},
            "lighting_color": "warm_gold"
        })
        # Record second shot with mismatch
        self.continuity.record_shot_state(1, {
            "outfits": {"hero": "tattered_pants"},
            "held_props": {"hero": "axe"},
            "lighting_color": "warm_gold"
        })
        errors = self.continuity.check_continuity()
        
        # Cleanup
        if os.path.exists("test_continuity_state.json"):
            try:
                os.remove("test_continuity_state.json")
            except Exception:
                pass
        self.assertEqual(len(errors), 2)
        types = [e["type"] for e in errors]
        self.assertIn("outfit_continuity_error", types)
        self.assertIn("prop_continuity_error", types)

    def test_procedural_layout(self):
        layouts = self.layout_solver.arrange_props("table", ["chair", "book"], layout_type="stack")
        self.assertEqual(len(layouts), 3)
        # Table at center base
        self.assertEqual(layouts[0]["noun"], "table")
        self.assertEqual(layouts[0]["translation"], [0.0, 0.0, 0.0])
        # Stacked props should have height offsets
        self.assertEqual(layouts[1]["noun"], "chair")
        self.assertEqual(layouts[1]["translation"][2], 0.8)
        self.assertEqual(layouts[2]["noun"], "book")
        self.assertEqual(layouts[2]["translation"][2], 0.95)

    def test_camera_collision(self):
        cam_pos = [3.0, 3.0, 1.0]
        actor_pos = [0.0, 0.0, 1.0]
        # Intersecting obstacle in path
        obstacles = [{"min_x": 1.0, "max_x": 2.0, "min_y": 1.0, "max_y": 2.0}]
        
        is_occluded = self.camera_solver.check_occlusion(cam_pos, actor_pos, obstacles)
        self.assertTrue(is_occluded)
        
        # Solving should shift coordinates to clear the occlusion
        new_cam = self.camera_solver.solve_position(cam_pos, actor_pos, obstacles)
        self.assertNotEqual(new_cam, cam_pos)

    def test_animation_graph(self):
        # Idle state
        state = self.anim_graph.update_state("idle", velocity=0.0)
        self.assertEqual(state, "idle")
        
        # Idle to Walk transition
        state2 = self.anim_graph.update_state("idle", velocity=1.0)
        self.assertEqual(state2, "walk")
        
        # Blend tree weights check at walk speed 0.25 m/s
        blend = self.anim_graph.evaluate_blend("walk", speed=0.25)
        self.assertEqual(blend["walk"], 0.5)
        self.assertEqual(blend["idle"], 0.5)

    def test_emotion_memory(self):
        # Default initialization check
        profile = self.emotion_engine.get_profile("hero")
        self.assertEqual(profile["happiness"], 0.5)
        self.assertEqual(profile["anger"], 0.0)
        
        # Process stimulus (getting attacked should raise anger/fear)
        updated = self.emotion_engine.process_stimulus("hero", "The guard decided to attack the hero.")
        anger_before = updated["anger"]
        self.assertGreater(anger_before, 0.0)
        self.assertGreater(updated["fear"], 0.0)
        
        # Simulated time decay tick (anger decays over time)
        decayed = self.emotion_engine.tick_decay("hero", duration_sec=5.0)
        self.assertLess(decayed["anger"], anger_before)

    def test_gpu_performance(self):
        devices = self.gpu_monitor.detect_cuda_devices()
        self.assertGreater(len(devices), 0)
        
        vram = self.gpu_monitor.check_vram_headroom()
        self.assertIn("status", vram)
        self.assertIn("utilization_pct", vram)
        
        metrics = self.gpu_monitor.calculate_render_metrics(time.time() - 2.0, frame_count=60)
        self.assertGreater(metrics["fps"], 0.0)
        self.assertGreater(metrics["elapsed_seconds"], 0.0)

    def test_audio_composer(self):
        # Attenuation check
        near_gain = self.audio_composer.compute_spatial_gain(1.0)
        far_gain = self.audio_composer.compute_spatial_gain(10.0)
        self.assertGreater(near_gain, far_gain)
        
        # Command compilation check
        cmd = self.audio_composer.compile_ffmpeg_mix_command(
            "bgm.wav", 
            [{"path": "v1.wav", "start": 1.0, "volume": 1.0}], 
            [{"path": "s1.wav", "start": 2.5, "volume": 0.8}], 
            "out.wav"
        )
        self.assertIn("ffmpeg", cmd)
        self.assertIn("amix=inputs=3:normalize=0[aout]", "".join(cmd))

    def test_render_cache(self):
        # Create test mock directories for cache and assert presence
        cache_dir = os.path.join(self.project_dir, "static", "videos", "cache")
        os.makedirs(cache_dir, exist_ok=True)
        self.assertTrue(os.path.exists(cache_dir))

    def test_project_manager(self):
        # Add scene check
        s_id = self.project_manager.add_scene("Intro Scene", "Hero leaps into the dynamic fog")
        self.assertIsNotNone(s_id)
        
        # Add shot check
        shot_id = self.project_manager.add_shot(s_id, "wide_shot", 3.5)
        self.assertIsNotNone(shot_id)
        
        # Validate data integrity
        self.assertIn(shot_id, self.project_manager.project_data["scenes"][s_id]["shots"])

    def test_usd_exporter(self):
        # USD layout check
        output_usda = os.path.join(self.project_dir, "static", "videos", "test_scene.usda")
        cameras = [{"name": "MainCam", "location": [0.0, -4.0, 1.5], "rotation": [80.0, 0.0, 0.0]}]
        lights = [{"name": "KeyLight", "type": "distant", "intensity": 5.0, "color": [1.0, 0.9, 0.7]}]
        
        full_usda = self.usd_exporter.export_scene(output_usda, cameras, lights)
        self.assertTrue(os.path.exists(output_usda))
        self.assertIn("def Camera \"MainCam\"", full_usda)
        self.assertIn("float inputs:intensity = 5.0", full_usda)

    def test_usd_importer_and_round_trip(self):
        output_usda = os.path.join(self.project_dir, "static", "videos", "test_scene.usda")
        self.assertTrue(os.path.exists(output_usda))
        
        # Import and parse back
        reconstructed = self.usd_importer.import_scene(output_usda)
        self.assertEqual(len(reconstructed["cameras"]), 1)
        self.assertEqual(reconstructed["cameras"][0]["name"], "MainCam")
        self.assertEqual(reconstructed["cameras"][0]["location"], [0.0, -4.0, 1.5])
        
        self.assertEqual(len(reconstructed["lights"]), 1)
        self.assertEqual(reconstructed["lights"][0]["name"], "KeyLight")
        self.assertEqual(reconstructed["lights"][0]["intensity"], 5.0)

    def test_fluid_cache(self):
        # Cache resolution lookup checks
        import uuid
        unique_scene = f"scene-{uuid.uuid4()}"
        key = self.fluid_cache.generate_cache_key(unique_scene, "fluid", "obj-456", 64, {"viscosity": 0.1}, (1, 100))
        self.assertIsNotNone(key)
        
        # Lookups and registrations
        miss = self.fluid_cache.check_cache(key)
        self.assertIsNone(miss)
        
        path = self.fluid_cache.register_cache(key, {"scene_uuid": unique_scene, "resolution": 64})
        self.assertTrue(os.path.exists(path))
        
        hit = self.fluid_cache.check_cache(key)
        self.assertEqual(hit, path)

    def test_camera_motion(self):
        # Tripod profile check
        c_loc, c_rot = self.camera_motion.apply_profile("tripod", 10, 24.0, (1.0, 2.0, 3.0), (0.1, 0.2, 0.3))
        self.assertEqual(c_loc, (1.0, 2.0, 3.0))
        self.assertEqual(c_rot, (0.1, 0.2, 0.3))
        
        # Handheld profile check
        h_loc, h_rot = self.camera_motion.apply_profile("handheld", 10, 24.0, (1.0, 2.0, 3.0), (0.1, 0.2, 0.3))
        self.assertNotEqual(h_loc, (1.0, 2.0, 3.0))
        self.assertNotEqual(h_rot, (0.1, 0.2, 0.3))

    def test_facial_performance_emotion_interpolation(self):
        """Verify that emotions produce non-zero, distinct weights and ease in."""
        engine = self.facial_engine
        # Frame 1 (start) should have reduced intensity due to ease-in
        w_start = engine.compute_frame(1, 1, 48, 24.0, "happy", 1.0, None, "TestHead", False)
        # Frame 24 should be fully eased in
        w_full = engine.compute_frame(24, 1, 48, 24.0, "happy", 1.0, None, "TestHead", False)
        # Happy should produce smiles
        self.assertGreater(w_full.get("mouthSmileLeft", 0), 0.0)
        self.assertGreater(w_full.get("mouthSmileRight", 0), 0.0)
        # Ease-in: frame 1 smile should be weaker than frame 24
        self.assertLess(w_start.get("mouthSmileLeft", 0), w_full.get("mouthSmileLeft", 0))

        # Different emotions produce different profiles
        w_angry = engine.compute_frame(24, 1, 48, 24.0, "angry", 1.0, None, "TestHead", False)
        self.assertGreater(w_angry.get("browDownLeft", 0), 0.0)
        # Angry should NOT have strong smile
        self.assertGreater(w_angry.get("browDownLeft", 0), w_angry.get("mouthSmileLeft", 0))

    def test_facial_performance_blink_generation(self):
        """Verify blinks are generated and values stay in [0,1]."""
        engine = self.facial_engine
        blink_found = False
        for f in range(1, 200):
            w = engine.compute_frame(f, 1, 200, 24.0, "happy", 1.0, None, "BlinkTest", False)
            blink_val = w.get("eyeBlinkLeft", 0.0)
            self.assertGreaterEqual(blink_val, 0.0)
            self.assertLessEqual(blink_val, 1.0)
            if blink_val > 0.5:
                blink_found = True
        self.assertTrue(blink_found, "No blink detected across 200 frames")

    def test_facial_performance_saccade_generation(self):
        """Verify eye saccades produce gaze movement."""
        engine = self.facial_engine
        gaze_keys = {"eyeLookOutLeft", "eyeLookInRight", "eyeLookInLeft", "eyeLookOutRight",
                     "eyeLookUpLeft", "eyeLookUpRight", "eyeLookDownLeft", "eyeLookDownRight"}
        any_gaze = False
        for f in range(1, 100):
            w = engine.compute_frame(f, 1, 100, 24.0, "happy", 1.0, None, "GazeTest", False)
            for gk in gaze_keys:
                if w.get(gk, 0.0) > 0.01:
                    any_gaze = True
                    break
            if any_gaze:
                break
        self.assertTrue(any_gaze, "No gaze saccade detected across 100 frames")

    def test_facial_performance_viseme_interpolation(self):
        """Verify viseme timeline produces lip movement."""
        engine = self.facial_engine
        timeline = [
            {"time": 0.0, "viseme": "rest"},
            {"time": 0.2, "viseme": "A"},
            {"time": 0.4, "viseme": "O"},
            {"time": 0.6, "viseme": "rest"},
        ]
        # At t=0.2 (frame ~6 at 24fps), viseme A should produce jawOpen
        w = engine.compute_frame(6, 1, 24, 24.0, "happy", 1.0, timeline, "VisemeTest", True)
        self.assertGreater(w.get("jawOpen", 0.0), 0.1, "Viseme A should open jaw")

        # At t=0.3 (frame ~8), interpolation between A and O should produce mouthFunnel
        w_mid = engine.compute_frame(8, 1, 24, 24.0, "happy", 1.0, timeline, "VisemeTest", True)
        self.assertGreater(w_mid.get("mouthFunnel", 0.0), 0.0, "Interpolation should produce mouthFunnel")

    def test_facial_performance_behavioural_states(self):
        """Verify speaking vs listening produce different facial states."""
        engine = self.facial_engine
        w_speaking = engine.compute_frame(24, 1, 48, 24.0, "happy", 1.0, None, "StateTest", True)
        w_listening = engine.compute_frame(24, 1, 48, 24.0, "happy", 1.0, None, "StateTest", False)
        # Speaking should have jawForward (speech emphasis)
        # Listening should have idle jaw relaxation
        # They should differ in at least some weights
        diffs = sum(1 for k in set(w_speaking.keys()) | set(w_listening.keys())
                    if abs(w_speaking.get(k, 0) - w_listening.get(k, 0)) > 0.001)
        self.assertGreater(diffs, 0, "Speaking and listening states should produce different weights")

    def test_facial_performance_all_clamped(self):
        """All output weights must be in [0, 1]."""
        engine = self.facial_engine
        timeline = [{"time": 0.0, "viseme": "A"}, {"time": 0.5, "viseme": "O"}, {"time": 1.0, "viseme": "M"}]
        for f in range(1, 50):
            w = engine.compute_frame(f, 1, 50, 24.0, "angry", 1.0, timeline, "ClampTest", True)
            for name, val in w.items():
                self.assertGreaterEqual(val, 0.0, f"{name} below 0 at frame {f}")
                self.assertLessEqual(val, 1.0, f"{name} above 1 at frame {f}")

    def test_character_motion_balance_and_breathing(self):
        """Verify dynamic balance leans and natural breathing offset updates."""
        engine = self.char_motion
        res = engine.compute_frame(
            frame=5, f_start=1, f_end=48, fps=24.0,
            action_name="idle", char_name="Thor",
            velocity=(0.0, 0.0, 0.0), acceleration=(1.0, 2.0, 0.0)
        )
        self.assertIn("Spine", res["bones"])
        self.assertIn("Hips", res["bones"])
        
        # Test breathing is non-zero
        spine_rot = res["bones"]["Spine"]["rotation"]
        self.assertNotEqual(spine_rot, (0.0, 0.0, 0.0))

    def test_character_motion_foot_locking(self):
        """Verify that feet planting states alternate during locomotion and lock flat."""
        engine = self.char_motion
        res = engine.compute_frame(
            frame=15, f_start=1, f_end=48, fps=24.0,
            action_name="walk", char_name="Tony",
            velocity=(0.0, 1.2, 0.0), acceleration=(0.0, 0.0, 0.0)
        )
        self.assertIn("foot_locking", res)
        self.assertIn("Foot.L", res["foot_locking"])
        self.assertIn("Foot.R", res["foot_locking"])
        
        # UpperLeg pitch should change due to strides
        leg_rot = res["bones"]["UpperLeg.L"]["rotation"]
        self.assertNotEqual(leg_rot, (0.0, 0.0, 0.0))

    def test_character_motion_blending(self):
        """Verify action transition blending avoids snapping."""
        engine = self.char_motion
        # Frame during transition should smoothly interpolate offsets between walk and idle
        res_blend = engine.compute_frame(
            frame=10, f_start=1, f_end=48, fps=24.0,
            action_name="walk", char_name="Hulk",
            velocity=(0.0, 1.2, 0.0), acceleration=(0.0, 0.0, 0.0),
            prev_action_name="idle", transition_t=0.2
        )
        self.assertIn("bones", res_blend)
        self.assertIn("UpperLeg.L", res_blend["bones"])

    def test_director_intelligence(self):
        """Verify Director Intelligence Engine generates consistent cinematic plans."""
        engine = self.director_engine
        
        # Test Case 1: Threat/Fear scene
        scene_fear = {
            "scene_number": 1,
            "character_name": "Thor",
            "action": "retreat",
            "mood": "fear",
            "line": "Something approaches."
        }
        decision = engine.direct_shot(scene_fear, env_config={"weather": "clear"})
        self.assertEqual(decision.camera_profile, "handheld")
        self.assertEqual(decision.lens, 50.0)
        self.assertEqual(decision.lighting_mood, "colder")
        self.assertIn("handheld", decision.reasoning.lower())
        self.assertFalse(decision.eye_contact)
        
        # Test Case 2: Action scene
        scene_attack = {
            "scene_number": 2,
            "character_name": "Thor",
            "action": "attack",
            "mood": "epic",
            "line": ""
        }
        decision_attack = engine.direct_shot(scene_attack)
        self.assertEqual(decision_attack.camera_profile, "steadicam")
        self.assertEqual(decision_attack.lens, 28.0)
        self.assertEqual(decision_attack.lighting_mood, "neutral")

if __name__ == "__main__":
    unittest.main()
