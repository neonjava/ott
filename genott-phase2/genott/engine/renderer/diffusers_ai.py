# ai/renderer/diffusers_ai.py
import os
import torch
import uuid
import time
from PIL import Image
from ai.renderer.base import VideoRenderer
from ai.storyboard.models import ScenePlan
from ai.character.library import CharacterLibrary
from ai.config import Config

class DiffusersAIVideoRenderer(VideoRenderer):
    def __init__(self, char_library: CharacterLibrary, load_pipeline_fn):
        self.char_library = char_library
        self.load_pipeline_fn = load_pipeline_fn

    def render_scene(self, plan: ScenePlan, seed: int, output_path: str, generation_id: str = None) -> str:
        pipeline, ptype = self.load_pipeline_fn()
        device = "cuda" if torch.cuda.is_available() else "cpu"
        generator = torch.Generator(device=device).manual_seed(seed)

        # Build a detailed, consistent character prompt from the library
        prompt_parts = []
        char_profile = None

        # Action camera composition description
        prompt_parts.append(f"A cinematic {plan.camera_shot} scene of")

        # Build consistent character styling from the library
        if plan.character_name:
            char_profile = self.char_library.get_character(plan.character_name)

        if char_profile:
            prompt_parts.append(f"{char_profile.name}, {char_profile.description},")

            # Determine correct outfit mapping
            outfit_key = "default"
            if char_profile.name.lower() == "tony_stark" or char_profile.name.lower() == "tony stark":
                outfit_key = "ironman" if any(kw in plan.action.lower() for kw in ["armor", "combat", "fight", "fly"]) else "suit"

            outfit = char_profile.outfits.get(outfit_key) or char_profile.outfits.get("default")
            if outfit:
                prompt_parts.append(f"{outfit.description},")

            # Inject weapon description
            weapon = char_profile.weapons.get("default") or char_profile.weapons.get("repulsor")
            if weapon:
                prompt_parts.append(f"{weapon.description},")
        elif plan.character_name:
            prompt_parts.append(plan.character_name)
        else:
            prompt_parts.append("an epic scene")

        # Map environment and background
        prompt_parts.append(f"on location: {plan.location}.")

        # Add visual actions
        prompt_parts.append(f"The character is actively {plan.action}.")

        # Combine into complete prompt
        final_prompt = " ".join(prompt_parts)
        enhanced_prompt = f"{final_prompt}, masterpiece, photorealistic, 8k resolution, cinematic lighting, sharp focus, highly detailed, dramatic atmosphere"
        enhanced_neg_prompt = (
            "low quality, worst quality, blurry, deformed face, bad eyes, disfigured, "
            "distorted, ugly, extra limbs, bad proportions, cartoon, anime, 3d render, CGI, doll, painting, drawing"
        )

        num_frames = 16
        num_steps = 25
        width = 512
        height = 320

        print(f"[DiffusersRenderer] Rendering Scene {plan.scene_number} | Seed: {seed}")
        print(f"[DiffusersRenderer] Prompt: '{enhanced_prompt[:150]}...'")

        # Run pipeline inference (no IP-Adapter — disabled due to CPU offload conflicts)
        kwargs = {
            "prompt": enhanced_prompt,
            "negative_prompt": enhanced_neg_prompt,
            "num_frames": num_frames,
            "width": width,
            "height": height,
            "num_inference_steps": num_steps,
            "generator": generator
        }

        if ptype == "ltx":
            output = pipeline(**kwargs)
            from diffusers.utils import export_to_video
            export_to_video(output.frames[0], output_path, fps=8)
        else:
            # Default to AnimateDiff
            kwargs["guidance_scale"] = 7.5
            output = pipeline(**kwargs)
            from diffusers.utils import export_to_video
            export_to_video(output.frames[0], output_path, fps=8)

        print(f"[DiffusersRenderer] Scene {plan.scene_number} saved to {output_path}")
        return output_path
