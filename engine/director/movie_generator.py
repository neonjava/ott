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
    Production-Grade Multi-Shot AI Movie Generator with Dynamic Scene Diversity.
    Passes unique shot output filenames to LTXVideoBackend so each shot is saved in its own permanent subfolder.
    """

    def __init__(self, debug_dir: str = "outputs/debug", output_dir: str = "outputs/productions"):
        self.debug_dir = os.path.abspath(debug_dir)
        self.output_dir = os.path.abspath(output_dir)
        
        self.backend = LTXVideoBackend(debug_dir=self.debug_dir, output_dir=self.output_dir)
        self.continuity = SceneContinuityState()
        self.qa_engine = ShotQualityAssurance(debug_dir=self.debug_dir)
        self.assembler = AutomaticMovieAssembler(output_dir=self.output_dir)

    def build_dynamic_shot_list(self) -> List[Dict[str, Any]]:
        return [
            {
                "shot_id": "shot_01_establishing_wide",
                "shot_type": "Wide Drone Establishing Shot",
                "duration_sec": 10.0,
                "fps": 16,
                "resolution": "704x384",
                "steps": 30,
                "guidance_scale": 4.0,
                "seed": 1010,
                "prompt": (
                    "A high-altitude wide drone shot looking down at a cybernetic woman standing on a high-tech skyscraper helipad. "
                    "Massive glowing holographic billboards and flying vehicles pass across a rainy cyberpunk city skyline at night. "
                    "Futuristic cybernetic explorer woman with silver hair, wearing black leather tactical coat with cyan glowing seams. "
                    "Volumetric neon fog, cinematic lighting, 8k resolution, masterpiece."
                )
            },
            {
                "shot_id": "shot_02_medium_tracking",
                "shot_type": "Side Tracking Low-Angle Action Shot",
                "duration_sec": 10.0,
                "fps": 16,
                "resolution": "704x384",
                "steps": 30,
                "guidance_scale": 4.0,
                "seed": 2020,
                "prompt": (
                    "A low-angle fast tracking camera following a cybernetic woman sprinting down a narrow rain-slicked alleyway. "
                    "Steam rises from manholes while vibrant pink and purple neon signs reflect off wet pavement. "
                    "Futuristic cybernetic explorer woman with silver hair, wearing black leather coat. High motion, dynamic action shot, "
                    "cinematic motion blur, 8k, Hollywood masterpiece."
                )
            },
            {
                "shot_id": "shot_03_closeup_portrait",
                "shot_type": "Extreme Close-Up Face & Eye Detail",
                "duration_sec": 10.0,
                "fps": 16,
                "resolution": "704x384",
                "steps": 30,
                "guidance_scale": 4.0,
                "seed": 3030,
                "prompt": (
                    "Extreme close-up shot of a cybernetic woman's face and glowing cyan cybernetic eye. "
                    "Raindrops run down her face as her silver hair sways in the wind. Soft out-of-focus background neon lights. "
                    "Photorealistic skin texture, ultra detailed face, glowing cyan eye HUD display, cinematic depth of field, 8k masterpiece."
                )
            },
            {
                "shot_id": "shot_04_reverse_angle",
                "shot_type": "Over-the-Shoulder Reverse Action Shot",
                "duration_sec": 10.0,
                "fps": 16,
                "resolution": "704x384",
                "steps": 30,
                "guidance_scale": 4.0,
                "seed": 4040,
                "prompt": (
                    "Over-the-shoulder reverse shot looking over a cybernetic woman's leather jacket toward an approaching glowing hover vehicle. "
                    "Bright headlights cut through the dark rainy night fog. Her silver hair blows across her shoulders. "
                    "Dramatic lens flare, volumetric headlight beam, intense atmosphere, cinematic lighting, 8k."
                )
            },
            {
                "shot_id": "shot_05_environment_insert",
                "shot_type": "Macro Footstep Reflection Insert",
                "duration_sec": 10.0,
                "fps": 16,
                "resolution": "704x384",
                "steps": 30,
                "guidance_scale": 4.0,
                "seed": 5050,
                "prompt": (
                    "Macro ground-level shot of armored tactical boots splashing into a deep neon puddle on dark wet asphalt. "
                    "Water droplets spray outward in slow motion reflecting vibrant cyan and magenta city neon lights. "
                    "Slow motion fluid dynamics, high contrast, crisp detail, cinematic 8k."
                )
            },
            {
                "shot_id": "shot_06_action_tracking",
                "shot_type": "Sweeping Hero Exit Shot",
                "duration_sec": 10.0,
                "fps": 16,
                "resolution": "704x384",
                "steps": 30,
                "guidance_scale": 4.0,
                "seed": 6060,
                "prompt": (
                    "Full-body cinematic 360 sweeping camera arc around a cybernetic woman turning sharply as sparks fly from an overhead power line. "
                    "Her leather coat billows violently in the wind. Futuristic cybernetic explorer woman with silver hair, "
                    "epic hero pose, dramatic lighting, movie climax, 8k resolution masterpiece."
                )
            }
        ]

    def generate_full_movie(self) -> Dict[str, Any]:
        logger.info("==================================================")
        logger.info("Starting Dynamic Multi-Shot AI Movie Generation (~60s)")
        logger.info("==================================================")

        shots = self.build_dynamic_shot_list()
        approved_shots = []
        anchor_histogram = None

        for shot_info in shots:
            s_id = shot_info["shot_id"]
            prompt = shot_info["prompt"]
            negative_prompt = self.continuity.get_negative_prompt()

            logger.info(f"\n--- Processing {s_id} ({shot_info['shot_type']}) ---")
            logger.info(f"Prompt: {prompt}")

            shot_approved = False
            max_attempts = 3
            current_seed = shot_info["seed"]

            for attempt in range(1, max_attempts + 1):
                logger.info(f"[Shot Generation] {s_id} - Attempt {attempt}/{max_attempts} (Seed: {current_seed})...")
                
                render_res = self.backend.generate_video(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    duration_sec=shot_info["duration_sec"],
                    fps=shot_info["fps"],
                    resolution=shot_info["resolution"],
                    seed=current_seed,
                    output_name=s_id
                )

                num_frames = render_res["frames_generated"]
                frame_paths = [os.path.join(self.debug_dir, f"frame_{idx:04d}.png") for idx in range(1, num_frames + 1)]

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
                        "shot_subfolder": render_res["shot_subfolder"],
                        "qa_result": qa_res
                    }
                    approved_shots.append(shot_record)
                    
                    if anchor_histogram is None and "mean_histogram" in qa_res:
                        anchor_histogram = np.array(qa_res["mean_histogram"])
                    
                    shot_approved = True
                    break
                else:
                    logger.warning(f"[!] {s_id} failed QA on attempt {attempt}: {qa_res['reason']}. Regenerating with seed {current_seed + 15}...")
                    current_seed += 15

            if not shot_approved:
                logger.error(f"[X] {s_id} failed to pass QA after {max_attempts} attempts. Halting pipeline.")
                return {"status": "FAILED_QA", "failed_shot": s_id}

        movie_manifest = self.assembler.assemble_movie(approved_shots)
        return movie_manifest

if __name__ == "__main__":
    generator = AIMovieGeneratorEngine()
    generator.generate_full_movie()
