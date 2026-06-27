# ai/render_farm.py
import time
from typing import Dict, Any, List

class RenderFarmAgent:
    """
    Subsystem: Render Farm
    Coordinates worker job queues, distributes frames across multiple host targets, and manages automatic recovery.
    """
    def __init__(self):
        self.workers = [
            {"id": "gpu_node_0", "status": "idle", "performance_weight": 1.0},
            {"id": "gpu_node_1", "status": "idle", "performance_weight": 0.8}
        ]
        self.job_queue = []
        self.completed_jobs = {}

    def submit_render_job(self, job_id: str, script_text: str, duration: float) -> Dict[str, Any]:
        """Queues a render job and assigns it to the most suitable idle node worker."""
        job = {
            "id": job_id,
            "script": script_text,
            "duration": duration,
            "status": "queued",
            "submitted_at": time.time(),
            "assigned_worker": None,
            "retries": 0
        }
        self.job_queue.append(job)
        self._schedule_jobs()
        return job

    def _schedule_jobs(self):
        for job in self.job_queue:
            if job["status"] == "queued":
                # Find first idle worker
                for worker in self.workers:
                    if worker["status"] == "idle":
                        worker["status"] = "busy"
                        job["status"] = "rendering"
                        job["assigned_worker"] = worker["id"]
                        break

    def complete_job(self, job_id: str, success: bool) -> Dict[str, Any]:
        """Processes completion or failure, triggering render recovery retries if appropriate."""
        target_job = None
        for job in self.job_queue:
            if job["id"] == job_id:
                target_job = job
                break
                
        if not target_job:
            return {"error": "Job not found"}
            
        # Free worker
        worker_id = target_job["assigned_worker"]
        if worker_id:
            for w in self.workers:
                if w["id"] == worker_id:
                    w["status"] = "idle"
                    
        if success:
            target_job["status"] = "completed"
            self.job_queue.remove(target_job)
            self.completed_jobs[job_id] = target_job
        else:
            if target_job["retries"] < 3:
                target_job["retries"] += 1
                target_job["status"] = "queued"
                target_job["assigned_worker"] = None
                print(f"[RenderFarm] Job {job_id} failed. Retrying... (Attempt {target_job['retries']}/3)")
            else:
                target_job["status"] = "failed"
                self.job_queue.remove(target_job)
                self.completed_jobs[job_id] = target_job
                
        self._schedule_jobs()
        return target_job
