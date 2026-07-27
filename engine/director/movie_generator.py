# engine/director/movie_generator.py
import os
import sys
import json
import time
import logging
import torch
import numpy as np
from typing import Dict, Any, List

from engine.backends.ltx.backend import LTXVideoBackend
from engine.characters.continuity_state import SceneContinuityState
from engine.critic.shot_qa import ShotQualityAssurance
from engine.timeline.movie_assembler import AutomaticMovieAssembler

logger = logging.getLogger(__name__)

class AIMovieGeneratorEngine:
    """
    Production-Grade Multi-Shot AI Movie Generator.
    1. Compiles high-level screenplay into a 6-shot sequence (~60 seconds total).
    2. Maintains character memory and scene continuity across all shots.
    3. Runs per-shot frame verification & QA (detects flicker, noise, and identity drift).
    4. Automatically regenerates failed shots up to 3 attempts.
    5. Assembles all approved shots into a single 60s cinematic MP4 with clean cuts.
    """

    def __init__(self, debug_dir: str = "outputs/debug", output_dir: str = "outputs/productions"):
        self.debug_dir = os.path.abspath(debug_dir)
        self.output_dir = os.path.abspath(output_dir)
        
        self.backend = LTXVideoBackend(debug_dir=self.debug_dir, output_dir=self.output_dir)
        self.continuity = SceneContinuityState()
        self.qa_engine = ShotQualityAssurance(debug_dir=self.debug_dir)
        self.assembler = AutomaticMovieAssembler(output_dir=self.output_dir)

    def build_shot_list(self) -> List[Dict[str, Any]]:
        """
        Builds a 6-shot cinematic screenplay sequence (~60 seconds total duration).
        """
        return [
            {
                "shot_id": "shot_01_establishing_wide",
                "shot_type": "Establishing Wide Shot",
                "duration_sec": 10.0,
                "fps": 16,
                "resolution": "704x384",
                "steps": 30,
                "guidance_scale": 4.0,
                "seed": 101,
                "action": "standing on a rain-soaked rooftop overlooking the glowing skyline",
                "camera": "The camera slowly pans out establishing the massive scale of the neon city"
            },
            {
                "shot_id": "shot_02_medium_tracking",
                "shot_type": "Medium Tracking Shot",
                "duration_sec": 10.0,
                "fps": 16,
                "resolution": "704x384",
                "steps": 30,
                "guidance_scale": 4.0,
                "seed": 102,
                "action": "walking purposefully along the wet reflective sidewalk past glowing shopfronts",
                "camera": "The camera dollies smoothly alongside her tracking her natural walking motion"
            },
            {
                "shot_id": "shot_03_closeup_portrait",
                "shot_type": "Close-up Portrait Shot",
                "duration_sec": 10.0,
                "fps": 16,
                "resolution": "704x384",
                "steps": 30,
                "guidance_scale": 4.0,
                "seed": 103,
                "action": "looking up with subtle determination as rain droplets glisten on her face",
                "camera": "Intimate close-up tracking shot with shallow depth of field and soft background blur"
            },
            {
                "shot_id": "shot_04_reverse_angle",
                "shot_type": "Reverse Over-the-Shoulder Angle",
                "duration_sec": 10.0,
                "fps": 16,
                "resolution": "704x384",
                "steps": 30,
                "guidance_scale": 4.0,
                "seed": 104,
                "action": "gazing ahead into a dark alleyway filled with cyan volumetric fog and glowing neon signs",
                "camera": "Over-the-shoulder reverse angle camera framing her back and silhouette"
            },
            {
                "shot_id": "shot_05_environment_insert",
                "shot_type": "Environmental Detail Insert",
                "duration_sec": 10.0,
                "fps": 16,
                "resolution": "704x384",
                "steps": 30,
                "guidance_scale": 4.0,
                "seed": 105,
                "action": "her boots stepping into a glowing neon puddle causing ripples on the wet asphalt",
                "camera": "Low-angle macro tracking camera following her steps"
            },
            {
                "shot_id": "shot_06_action_tracking",
                "shot_type": "Climactic Action Tracking Shot",
                "duration_sec": 10.0,
                "fps": 16,
                "resolution": "704x384",
                "steps": 30,
                "guidance_scale": 4.0,
                "seed": 106,
                "action": "turning sharply into the rain with her coat blowing in the wind as a hover vehicle speeds overhead",
                "camera": "Dynamic cinematic tracking shot with sweeping motion"
            }
        ]

    def generate_full_movie(self) -> Dict[str, Any]:
        logger.info("==================================================")
        logger.info("Starting Production 60-Second Multi-Shot AI Movie Generation")
        logger.info("==================================================")

        shots = self.build_shot_list()
        approved_shots = []
        anchor_histogram = None

        for shot_info in shots:
            s_id = shot_info["shot_id"]
            prompt = self.continuity.get_shot_prompt(
                shot_num=len(approved_shots) + 1,
                shot_type=shot_info["shot_type"],
                action_description=shot_info["action"],
                camera_movement=shot_info["camera"]
            )
            negative_prompt = self.continuity.get_negative_prompt()

            logger.info(f"\n--- Processing {s_id} ({shot_info['shot_type']}) ---")
            logger.info(f"Prompt: {prompt}")

            shot_approved = False
            max_attempts = 3
            current_seed = shot_info["seed"]

            for attempt in range(1, max_attempts + 1):
                logger.info(f"[Shot Generation] {s_id} - Attempt {attempt}/{max_attempts} (Seed: {current_seed})...")
                
                # Render Shot via LTX-Video Backend
                render_res = self.backend.generate_video(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    duration_sec=shot_info["duration_sec"],
                    fps=shot_info["fps"],
                    resolution=shot_info["resolution"],
                    seed=current_seed
                )

                # Collect frame paths for QA
                num_frames = render_res["frames_generated"]
                frame_paths = [os.path.join(self.debug_dir, f"frame_{idx:04d}.png") for idx in range(1, num_frames + 1)]

                # Run QA Evaluation
                qa_res = self.qa_engine.evaluate_shot(frame_paths, s_id, anchor_hist=anchor_histogram)

                if qa_res["passed"]:
                    logger.info(f"[✓] {s_id} PASSED Quality Assurance on attempt {attempt}!")
                    shot_record = {
                        "shot_id": s_id,
                        "shot_type": shot_info["shot_type"],
                        "prompt": prompt,
                        "duration_sec": shot_info["duration_sec"],
                        "fps": shot_info["fps"],
                        "num_frames": num_frames,
                        "output_mp4": render_res["output_mp4"],
                        "qa_result": qa_res
                    }
                    approved_shots.append(shot_record)
                    
                    # Set Shot 01 histogram as continuity anchor for subsequent shots
                    if anchor_histogram is None and "mean_histogram" in qa_res:
                        anchor_histogram = np.array(qa_res["mean_histogram"])
                    
                    shot_approved = True
                    break
                else:
                    logger.warning(f"[!] {s_id} failed QA on attempt {attempt}: {qa_res['reason']}. Regenerating with seed {current_seed + 10}...")
                    current_seed += 10

            if not shot_approved:
                logger.error(f"[X] {s_id} failed to pass QA after {max_attempts} attempts. Halting pipeline.")
                return {"status": "FAILED_QA", "failed_shot": s_id}

        # Assemble all approved shots into final ~60s movie
        movie_manifest = self.assembler.assemble_movie(approved_shots)
        return movie_manifest

if __name__ == "__main__":
    generator = AIMovieGeneratorEngine()
    generator.generate_full_movie()
