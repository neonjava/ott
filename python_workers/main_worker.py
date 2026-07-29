# python_workers/main_worker.py
import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../legacy")))
from engine.backends.ltx.backend import LTXVideoBackend

class AiWorkerPool:
    def __init__(self):
        print("[GenOTT V2 Python Worker] Initializing AI Worker Pool...")
        self.ltx_backend = LTXVideoBackend(
            debug_dir="PROJECT_ROOT/Documents/LLM/ott/outputs/debug",
            output_dir="PROJECT_ROOT/Documents/LLM/ott/outputs/productions"
        )

    def render_shot(self, shot_id: str, prompt: str, duration_sec: float = 5.0, seed: int = 42):
        print(f"[GenOTT V2 Python Worker] Executing render for {shot_id} via LTX-Video...")
        res = self.ltx_backend.generate_video(
            prompt=prompt,
            duration_sec=duration_sec,
            seed=seed,
            output_name=shot_id
        )
        return res

if __name__ == "__main__":
    worker = AiWorkerPool()
    print("[GenOTT V2 Python Worker] Ready for Rust Core IPC job requests.")
