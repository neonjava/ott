# engine/prompt_compiler/compiler.py
from typing import Dict, Any, Tuple

class PromptCompiler:
    """
    Transforms MovieGraph shot specifications, cinematic framing, camera paths, 
    actors, lighting, and action descriptions into target prompts for video generation models.
    """

    @staticmethod
    def compile_for_wan(shot_spec: Dict[str, Any]) -> Tuple[str, str]:
        """
        Compiles ShotSpec into (positive_prompt, negative_prompt) tailored for the WAN video diffusion model.
        """
        prompt_parts = []
        
        # 1. Visual summary & action
        action = shot_spec.get("action", shot_spec.get("description", shot_spec.get("visual_summary", "")))
        if action:
            prompt_parts.append(action.strip())

        # 2. Characters & Subject details
        characters = shot_spec.get("characters", shot_spec.get("actors", []))
        if isinstance(characters, list) and characters:
            char_descs = [f"{c.get('name', 'person')}: {c.get('description', '')}" if isinstance(c, dict) else str(c) for c in characters]
            prompt_parts.append("Featuring " + ", ".join(char_descs))

        # 3. Environment & Location
        location = shot_spec.get("location", shot_spec.get("environment", ""))
        if location:
            prompt_parts.append(f"Setting: {location}")

        # 4. Cinematic framing & Camera Movement
        framing = shot_spec.get("framing", shot_spec.get("shot_type", ""))
        camera_move = shot_spec.get("camera_movement", shot_spec.get("camera_path", ""))
        lens = shot_spec.get("lens", shot_spec.get("focal_length", ""))
        
        camera_specs = []
        if framing:
            camera_specs.append(f"{framing} shot")
        if camera_move:
            camera_specs.append(f"camera moving {camera_move}")
        if lens:
            camera_specs.append(f"{lens} lens")
            
        if camera_specs:
            prompt_parts.append(", ".join(camera_specs))

        # 5. Lighting & Atmospheric style
        lighting = shot_spec.get("lighting", shot_spec.get("light_setup", ""))
        mood = shot_spec.get("mood", shot_spec.get("atmosphere", ""))
        style_notes = shot_spec.get("style_notes", "hyperrealistic, 8k resolution, cinematic lighting, masterwork")
        
        if lighting:
            prompt_parts.append(f"{lighting} lighting")
        if mood:
            prompt_parts.append(f"{mood} atmosphere")
        if style_notes:
            prompt_parts.append(style_notes)

        positive_prompt = ". ".join(filter(None, prompt_parts))
        
        # Construct negative prompt
        user_neg = shot_spec.get("negative_prompt", "")
        default_neg = "blurry, low quality, distorted anatomy, morphing artifacts, bad motion, low resolution, text watermark, flickering"
        if user_neg:
            negative_prompt = f"{default_neg}, {user_neg}"
        else:
            negative_prompt = default_neg

        return positive_prompt, negative_prompt
