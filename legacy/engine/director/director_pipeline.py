# engine/director/director_pipeline.py
from typing import Dict, Any, List
from engine.director.story_planner import StoryPlanner
from engine.director.scene_planner_v2 import ScenePlannerV2
from engine.director.shot_planner import ShotPlanner
from engine.director.shot_spec import ShotSpec
from engine.director.backend_router import BackendRouter
from models.adapters.base import BackendAdapter
from engine.storyboard.movie_graph import MovieGraph

class DirectorPipeline:
    """
    Subsystem: Director Pipeline Coordinator
    Orchestrates the entire GenOTT V2 film production planning sequence:
    Idea -> Story -> Scenes -> Shots -> ShotSpec -> Router -> Adapters
    """
    def __init__(self, adapters: List[BackendAdapter]):
        self.story_planner = StoryPlanner()
        self.scene_planner = ScenePlannerV2()
        self.shot_planner = ShotPlanner()
        self.router = BackendRouter(adapters)

    def run_pipeline(self, idea_text: str) -> Dict[str, Any]:
        """Runs the complete cinematic orchestration sequence from raw user prompt."""
        # 1. Story outline planning
        story = self.story_planner.plan_story(idea_text)
        
        # 2. Scene List breakdown
        # Format input for legacy ScenePlannerV2 compatibility
        events = []
        for idx, loc in enumerate(story["locations"]):
            events.append({
                "actor": story["characters"][0] if story["characters"] else "humanoid",
                "action": "walk" if idx == 0 else "discover",
                "location": loc,
                "emotion": "sad" if idx == 0 else "surprise",
                "description": f"Actor moves in the {loc}"
            })
            
        story_data = {
            "events": events,
            "characters": [{"name": c} for c in story["characters"]],
            "locations": [{"name": l} for l in story["locations"]]
        }
        scenes = self.scene_planner.plan_scenes(story_data)
        
        # 3. Shot breakdown
        shots = []
        for scene in scenes:
            scene_shots = self.shot_planner.plan_shots_for_scene(scene)
            shots.extend(scene_shots)
            
        # 4. Shot Spec Generation
        shot_specs = []
        backend_decisions = []
        
        for idx, shot in enumerate(shots):
            shot_id = f"shot_{idx+1:02d}"
            # Assemble custom ShotSpec map
            spec_data = {
                "shot_id": shot_id,
                "scene_id": shot["scene_id"],
                "purpose": shot["camera_objective"],
                "camera": {
                    "type": "close_up" if "Close" in shot["camera_objective"] else "wide",
                    "height": 1.5,
                    "target": "actor"
                },
                "movement": {
                    "camera_profile": "Steadicam",
                    "movement_speed": 1.0
                },
                "characters": [{
                    "name": story["characters"][0] if story["characters"] else "humanoid",
                    "action": "walk" if "walk" in shot["actor_objective"] else "idle",
                    "mood": shot["emotion"]
                }],
                "environment": {
                    "location": story["locations"][0] if story["locations"] else "forest",
                    "weather": "clear",
                    "environment_props": []
                },
                "emotion": shot["emotion"]
            }
            spec = ShotSpec(spec_data)
            spec_dict = spec.to_dict()
            shot_specs.append(spec_dict)
            
            # 5. Backend Routing Decision
            selected_adapter = self.router.route_shot(spec_dict)
            caps = selected_adapter.get_capabilities()
            backend_decisions.append({
                "shot_id": shot_id,
                "backend_name": caps["name"],
                "engine_version": caps["version"]
            })
            
        return {
            "story": story,
            "scenes": scenes,
            "shots": shots,
            "shot_specs": shot_specs,
            "backend_decisions": backend_decisions
        }

    def run_intelligent_pipeline(self, graph: MovieGraph, idea_text: str) -> MovieGraph:
        """
        Runs the complete intelligent planning sequence:
        StoryAI -> SceneAI -> ShotAI -> EditorAI -> CriticAI.
        Loops back to StoryAI if CriticAI rejects the plan.
        """
        from engine.director.story_ai import StoryAI
        from engine.director.scene_ai import SceneAI
        from engine.director.shot_ai import ShotAI
        from engine.director.editor_ai import EditorAI
        from engine.director.critic_ai import CriticAI

        story_ai = StoryAI()
        scene_ai = SceneAI()
        shot_ai = ShotAI()
        editor_ai = EditorAI()
        critic_ai = CriticAI()

        max_revisions = 3
        revision = 0
        approved = False

        while not approved and revision < max_revisions:
            # Clear previous plan
            graph.scenes = {}
            graph.shots = {}
            
            # Step 1: Story Planning
            revised_idea = idea_text if revision == 0 else f"{idea_text} with more visual variety"
            story_ai.plan_story(graph, revised_idea)
            
            # Step 2: Scene Planning
            scene_ai.plan_scenes(graph)
            
            # Step 3: Shot Planning
            shot_ai.plan_shots(graph)
            
            # Step 4: Editing / Pacing Optimizations
            editor_ai.optimize_plan(graph)
            
            # Step 5: Route Backends
            for shot_id, shot in graph.shots.items():
                selected_adapter = self.router.route_shot(shot)
                caps = selected_adapter.get_capabilities()
                graph.add_backend_task(f"task_{shot_id}", shot_id, caps["name"])
            
            # Step 6: Movie Critic Pre-Render Review
            review = critic_ai.evaluate_production_plan(graph)
            approved = review["approved"]
            
            # Record Review Task
            graph.add_review_task(f"critic_pre_{revision}", list(graph.shots.keys())[0], review["score"], approved)
            revision += 1
            
        graph.validate()
        return graph
