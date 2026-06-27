# ai/character/consistency.py
"""
CharacterConsistencyEngine
Generates a master character sheet once and caches all reference assets.
Every render must reference the locked character sheet for identity preservation.
"""
import os
import json
import hashlib
import torch
from PIL import Image
from typing import Dict, Optional
from ai.character.models import CharacterProfile


class CharacterSheet:
    """A locked, cached set of reference assets for a single character."""
    def __init__(self, character_name: str, cache_dir: str):
        self.character_name = character_name
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

        self.face_reference: Optional[str] = None
        self.outfit_reference: Optional[str] = None
        self.weapon_reference: Optional[str] = None
        self.color_palette: list = []
        self.locked = False

    def lock(self):
        """Lock the character sheet — no more regeneration allowed."""
        self.locked = True
        manifest = {
            "character_name": self.character_name,
            "face_reference": self.face_reference,
            "outfit_reference": self.outfit_reference,
            "weapon_reference": self.weapon_reference,
            "color_palette": self.color_palette,
            "locked": True
        }
        with open(os.path.join(self.cache_dir, "manifest.json"), "w") as f:
            json.dump(manifest, f, indent=2)

    @classmethod
    def load_from_cache(cls, cache_dir: str) -> Optional["CharacterSheet"]:
        manifest_path = os.path.join(cache_dir, "manifest.json")
        if not os.path.exists(manifest_path):
            return None
        with open(manifest_path) as f:
            data = json.load(f)
        sheet = cls(data["character_name"], cache_dir)
        sheet.face_reference = data.get("face_reference")
        sheet.outfit_reference = data.get("outfit_reference")
        sheet.weapon_reference = data.get("weapon_reference")
        sheet.color_palette = data.get("color_palette", [])
        sheet.locked = data.get("locked", False)
        return sheet


class CharacterConsistencyEngine:
    """
    Manages character asset locking across all scenes.
    Generates master reference images once, caches them, and injects
    them into every render call via IP-Adapter FaceID conditioning.
    """
    def __init__(self, cache_root: str, faces_dir: str):
        self.cache_root = cache_root
        self.faces_dir = faces_dir
        os.makedirs(cache_root, exist_ok=True)
        self._sheets: Dict[str, CharacterSheet] = {}

    def get_or_create_sheet(self, profile: CharacterProfile, pipeline=None) -> CharacterSheet:
        """Get cached character sheet or generate a new one."""
        key = profile.name.lower().replace(" ", "_")
        cache_dir = os.path.join(self.cache_root, key)

        # Try loading from cache first
        cached = CharacterSheet.load_from_cache(cache_dir)
        if cached and cached.locked:
            self._sheets[key] = cached
            return cached

        # Create new sheet
        sheet = CharacterSheet(profile.name, cache_dir)

        # 1. Face reference — use the pre-generated photorealistic portrait
        face_src = profile.face_reference_img
        if os.path.exists(face_src):
            face_dst = os.path.join(cache_dir, "face_reference.png")
            if not os.path.exists(face_dst):
                img = Image.open(face_src).convert("RGB").resize((512, 512))
                img.save(face_dst)
            sheet.face_reference = face_dst
        
        # 2. Outfit reference — generate a full-body outfit snapshot
        outfit_path = os.path.join(cache_dir, "outfit_reference.png")
        if not os.path.exists(outfit_path) and pipeline is not None:
            outfit_desc = profile.description
            default_outfit = profile.outfits.get("default")
            if default_outfit:
                outfit_desc += f", {default_outfit.description}"
            self._generate_reference_image(
                pipeline, outfit_desc, outfit_path,
                prefix="Full body portrait of"
            )
        if os.path.exists(outfit_path):
            sheet.outfit_reference = outfit_path

        # 3. Weapon reference — generate a weapon close-up snapshot
        weapon_path = os.path.join(cache_dir, "weapon_reference.png")
        if not os.path.exists(weapon_path) and pipeline is not None:
            default_weapon = profile.weapons.get("default")
            if default_weapon:
                self._generate_reference_image(
                    pipeline, 
                    f"{profile.description}, {default_weapon.description}",
                    weapon_path,
                    prefix="Close-up cinematic shot of a warrior"
                )
        if os.path.exists(weapon_path):
            sheet.weapon_reference = weapon_path

        # 4. Extract color palette from face reference
        if sheet.face_reference:
            sheet.color_palette = self._extract_palette(sheet.face_reference)

        # Lock and persist
        sheet.lock()
        self._sheets[key] = sheet
        return sheet

    def _generate_reference_image(self, pipeline, description, output_path, prefix="A cinematic portrait of"):
        """Generate a single reference image using the AnimateDiff pipeline directly."""
        device = "cuda" if torch.cuda.is_available() else "cpu"
        generator = torch.Generator(device=device).manual_seed(42)  # Fixed seed for reproducibility

        prompt = (
            f"{prefix} {description}, "
            "masterpiece, photorealistic, 8k resolution, cinematic lighting, "
            "sharp focus, highly detailed, studio portrait"
        )
        neg_prompt = (
            "low quality, worst quality, blurry, deformed, disfigured, "
            "ugly, cartoon, anime, 3d render, CGI, painting, drawing"
        )

        # Load face reference if it was already saved to keep references consistent
        face_path = os.path.join(os.path.dirname(output_path), "face_reference.png")
        ip_adapter_image = None
        if os.path.exists(face_path):
            ip_adapter_image = Image.open(face_path).convert("RGB")

        # Run AnimateDiff with a few frames to generate the visual style reference
        kwargs = {
            "prompt": prompt,
            "negative_prompt": neg_prompt,
            "num_frames": 8,
            "width": 512,
            "height": 512,
            "num_inference_steps": 20,
            "guidance_scale": 7.5,
            "generator": generator
        }
        if ip_adapter_image is not None:
            kwargs["ip_adapter_image"] = ip_adapter_image

        print(f"[CharacterConsistency] Generating asset reference image to: {output_path}")
        output = pipeline(**kwargs)
        
        # Save the first frame of the generated clip as the reference image
        output.frames[0][0].save(output_path)
        torch.cuda.empty_cache()

    def _extract_palette(self, image_path: str, n_colors: int = 5) -> list:
        """Extract dominant color palette from a reference image."""
        import cv2
        import numpy as np
        
        img = cv2.imread(image_path)
        if img is None:
            return []
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pixels = img.reshape(-1, 3).astype(np.float32)
        
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        _, labels, centers = cv2.kmeans(pixels, n_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        palette = []
        for c in centers:
            hex_color = "#{:02x}{:02x}{:02x}".format(int(c[0]), int(c[1]), int(c[2]))
            palette.append(hex_color)
        return palette
