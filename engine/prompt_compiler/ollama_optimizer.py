# engine/prompt_compiler/ollama_optimizer.py
import json
import logging
import subprocess

logger = logging.getLogger(__name__)

class OllamaPromptOptimizer:
    """
    Optimizes high-level user prompts into model-specific prompts for LTX-Video/Wan 2.1
    and decomposes a story into discrete scenes based on selected duration (15s, 30s, 60s).
    Falls back gracefully if Ollama service is offline.
    """

    def __init__(self, model_name: str = "llama3"):
        self.model_name = model_name

    def optimize_and_decompose(self, user_prompt: str, target_duration: str = "30s") -> dict:
        duration_map = {
            "15s": {"num_shots": 2, "shot_duration": 7.5},
            "30s": {"num_shots": 3, "shot_duration": 10.0},
            "60s": {"num_shots": 6, "shot_duration": 10.0}
        }
        config = duration_map.get(target_duration, duration_map["30s"])
        num_shots = config["num_shots"]

        # Attempt Ollama expansion
        ollama_prompt = (
            f"You are a Hollywood AI Film Director. Expand the following user prompt into a cinematic screenplay "
            f"with {num_shots} detailed scene descriptions for AI video diffusion generation.\n"
            f"User Prompt: '{user_prompt}'\n"
            f"Output exact JSON format with key 'scenes' containing a list of {num_shots} prompt strings."
        )

        enhanced_scenes = []
        try:
            cmd = ["ollama", "run", self.model_name, ollama_prompt]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=12)
            if res.returncode == 0 and "scenes" in res.stdout:
                parsed = json.loads(res.stdout)
                enhanced_scenes = parsed.get("scenes", [])
        except Exception:
            pass

        # Robust Fallback Prompt Expansion Engine if Ollama is uninstalled or offline
        if not enhanced_scenes or len(enhanced_scenes) < num_shots:
            angles = [
                "Establishing Wide Shot, high altitude view",
                "Medium Tracking Shot, side dolly camera movement",
                "Close-up Portrait Shot, shallow depth of field",
                "Reverse Over-the-Shoulder Angle",
                "Ground-Level Macro Insert Shot",
                "Climactic 360-Degree Sweeping Hero Exit Arc"
            ]
            enhanced_scenes = []
            for i in range(num_shots):
                angle = angles[i % len(angles)]
                scene_text = f"Cinematic {angle} of {user_prompt}. Detailed lighting, 8k resolution, volumetric fog, photorealistic masterpiece."
                enhanced_scenes.append(scene_text)

        return {
            "target_duration": target_duration,
            "num_shots": num_shots,
            "shot_duration_sec": config["shot_duration"],
            "optimized_scenes": enhanced_scenes
        }
