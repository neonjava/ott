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

    @classmethod
    def compile_for_wan(cls, shot_spec: Dict[str, Any]) -> Tuple[str, str]:
        action = shot_spec.get("action", "")
        cam_spec = shot_spec.get("cinematic_camera_spec", "Cinematic 8k masterwork shot.")
        style = shot_spec.get("style_notes", "photorealistic cinematic lighting, volumetric atmosphere")
        lighting = shot_spec.get("lighting", "dramatic rim lighting")
        location = shot_spec.get("location", "")
        framing = shot_spec.get("framing", "")

        char_desc = ""
        chars = shot_spec.get("characters", [])
        if chars and isinstance(chars[0], dict):
            char_desc = f"Featuring {chars[0].get('name', 'hero')} ({chars[0].get('description', '')}). "

        framing_str = f"{framing} shot. " if framing else ""
        location_str = f"Set in {location}. " if location else ""

        positive_prompt = f"{char_desc}{action}. {framing_str}{location_str}{cam_spec} {lighting}, {style}. Masterpiece, hyper-detailed, photorealistic, 8k resolution, fluid motion."
        negative_prompt = "blurry, low quality, deformed faces, static image, flickering, jittery, artifacting, text, watermark, bad lighting."
        return positive_prompt, negative_prompt

    @classmethod
    def compile_for_backend(cls, backend_name: str, shot_spec: Dict[str, Any]) -> Tuple[str, str]:
        b = backend_name.lower()
        if b == "cogvideox":
            pos, neg = cls.compile_for_wan(shot_spec)
            return f"[CogVideoX Optimized] {pos}", neg
        elif b == "hunyuanvideo":
            pos, neg = cls.compile_for_wan(shot_spec)
            return f"[Hunyuan 1.0] {pos}", neg
        return cls.compile_for_wan(shot_spec)
