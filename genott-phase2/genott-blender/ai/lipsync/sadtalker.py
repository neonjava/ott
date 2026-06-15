# ai/lipsync/sadtalker.py
import os
import subprocess
import shutil
import glob
import uuid
from ai.lipsync.base import LipSyncProvider

class SadTalkerProvider(LipSyncProvider):
    def __init__(self, python_venv_path: str, sadtalker_dir: str, checkpoints_dir: str):
        self.python_venv_path = python_venv_path
        self.sadtalker_dir = sadtalker_dir
        self.checkpoints_dir = checkpoints_dir

    def run_lipsync(self, image_path: str, audio_path: str, output_path: str, generation_id: str = None) -> str:
        temp_dir = os.path.join(os.path.dirname(output_path), f"sadtalker_run_{uuid.uuid4().hex[:8]}")
        os.makedirs(temp_dir, exist_ok=True)

        cmd = [
            self.python_venv_path,
            os.path.join(self.sadtalker_dir, "inference.py"),
            "--driven_audio", audio_path,
            "--source_image", image_path,
            "--result_dir", temp_dir,
            "--still",
            "--preprocess", "full",
            "--checkpoint_dir", self.checkpoints_dir
        ]

        try:
            print(f"[SadTalkerProvider] Starting lip-sync inference for {generation_id}...")
            process = subprocess.run(cmd, cwd=self.sadtalker_dir, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            generated_videos = glob.glob(os.path.join(temp_dir, "**", "*.mp4"), recursive=True)
            if not generated_videos:
                raise FileNotFoundError("SadTalker executed successfully but generated no video file outputs.")
            
            shutil.copy(generated_videos[0], output_path)
            return output_path
        except Exception as e:
            print(f"[SadTalkerProvider] Error: {e}")
            raise e
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
