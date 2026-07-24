# engine/prompt_compiler/compiler.py
import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

class PromptCompiler:
    """
    Prompt Intelligence Engine for GenOTT V2.
    Rewrites and optimizes prompts for motion, realism, visual continuity, lighting, emotions,
    and backend-specific strengths (WAN 2.1, CogVideoX, HunyuanVideo, LTX-Video, Mochi).
    """

    def compile_for_wan(self, shot_spec: Dict[str, Any]) -> Tuple[str, str]:
        action = shot_spec.get("action", "")
        cam_spec = shot_spec.get("cinematic_camera_spec", "Cinematic 8k masterwork shot.")
        style = shot_spec.get("style_notes", "photorealistic cinematic lighting, volumetric atmosphere")
        lighting = shot_spec.get("lighting", "dramatic rim lighting")

        char_desc = ""
        chars = shot_spec.get("characters", [])
        if chars and isinstance(chars[0], dict):
            char_desc = f"Featuring {chars[0].get('name', 'hero')} ({chars[0].get('description', '')}). "

        positive_prompt = f"{char_desc}{action}. {cam_spec} {lighting}, {style}. Masterpiece, hyper-detailed, photorealistic, 8k resolution, fluid motion."
        negative_prompt = "blurry, low quality, deformed faces, static image, flickering, jittery, artifacting, text, watermark, bad lighting."
        return positive_prompt, negative_prompt

    def compile_for_backend(self, backend_name: str, shot_spec: Dict[str, Any]) -> Tuple[str, str]:
        b = backend_name.lower()
        if b == "cogvideox":
            pos, neg = self.compile_for_wan(shot_spec)
            return f"[CogVideoX Optimized] {pos}", neg
        elif b == "hunyuanvideo":
            pos, neg = self.compile_for_wan(shot_spec)
            return f"[Hunyuan 1.0] {pos}", neg
        return self.compile_for_wan(shot_spec)
