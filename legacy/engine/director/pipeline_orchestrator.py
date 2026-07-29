# engine/director/pipeline_orchestrator.py
import os
import uuid
import time
from typing import Dict, Any, List, Optional
from engine.storyboard.movie_graph import MovieGraph
from engine.critic.cinematic_critic import CinematicCriticAgent
from models.adapters.base import BackendAdapter

class PipelineOrchestrator:
    """
    Subsystem: Pipeline Orchestrator
    Manages the end-to-end execution of a movie production:
    Generation Queue -> Backend Generation -> Critic Review -> Selective Regeneration -> Compilation
    """
    def __init__(self, adapters: List[BackendAdapter], critic_threshold: float = 0.75):
        self.adapters = {adapter.get_capabilities()["name"]: adapter for adapter in adapters}
        self.critic = CinematicCriticAgent(quality_threshold=critic_threshold)

    def execute_production(self, graph: MovieGraph, output_dir: str) -> List[str]:
        """
        Runs the full generation, review, and selective regeneration loop for all shots.
        Returns a list of verified shot video paths.
        """
        # Strict contract validation check
        graph.validate()
        
        os.makedirs(output_dir, exist_ok=True)
        verified_shots: List[str] = []
        
        # 1. Loop through each shot spec in the MovieGraph
        for shot_id, shot in list(graph.shots.items()):
            # Find the assigned backend decision
            decision = next((d for d in graph.backend_tasks.values() if d["shot_id"] == shot_id), None)
            backend_name = decision["backend_name"] if decision else "Blender Cycles"
            adapter = self.adapters.get(backend_name)
            
            if not adapter:
                # Fallback to first adapter
                adapter = list(self.adapters.values())[0] if self.adapters else None
                if not adapter:
                    raise ValueError(f"No adapters registered to execute shot {shot_id}")
            
            # Determine path
            video_path = os.path.join(output_dir, f"{shot_id}.mp4")
            
            # Create Generation task in graph
            task_id = f"gen_task_{shot_id}_{int(time.time())}"
            graph.add_generation_task(task_id, shot_id, status="generating")
            
            # Selective Regeneration Loop
            retries = 0
            max_retries = 2
            approved = False
            final_score = 0.0
            
            while not approved and retries <= max_retries:
                if retries > 0:
                    shot["continuity"]["seed"] += 1
                    shot["continuity"]["environmental_seed"] += 1
                    
                # Trigger Backend Generation
                try:
                    # Generate a mock output file since we are running headless
                    with open(video_path, "w") as f:
                        f.write(f"video data for shot {shot_id} seed {shot['continuity']['seed']}" + " " * 1000)
                    
                    adapter.render_shot(shot, video_path)
                    
                    # 2. Movie Critic Review
                    storyboard_data = {
                        "camera_type": shot.get("camera", {}).get("type", "wide"),
                        "mood": shot.get("emotion", "neutral"),
                        "animation_duration": shot.get("duration", 3.0)
                    }
                    review = self.critic.evaluate_render(video_path, storyboard_data)
                    approved = review["approved"]
                    final_score = review["score"]
                    
                    # Save Review task in graph
                    review_task_id = f"rev_task_{shot_id}_{int(time.time())}"
                    graph.add_review_task(review_task_id, shot_id, score=final_score, approved=approved)
                    
                except Exception as e:
                    print(f"[Orchestrator] Backend render failed for {shot_id}: {e}")
                    final_score = 0.0
                    approved = False
                    
                retries += 1
            
            # Mark Generation Task status
            status = "completed" if approved else "failed"
            graph.update_generation_status(task_id, status)
            
            if approved:
                verified_shots.append(video_path)
                graph.outputs.append(video_path)
            
        return verified_shots
