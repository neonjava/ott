# test_subsystems.py
import unittest
import os
import json
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

if __name__ == "__main__":
    unittest.main()
