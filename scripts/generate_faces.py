"""
Generate high-quality character reference face images using the existing
Stable Diffusion pipeline (epiCRealism).
Run once to create faces, then SadTalker uses them for lip-synced videos.
"""

import os
import sys
import torch

FACES_DIR = os.path.join(os.path.dirname(__file__), "static", "faces")
os.makedirs(FACES_DIR, exist_ok=True)

# Character face prompts — highly detailed for photorealistic results
CHARACTER_FACES = {
    "tony_stark": {
        "prompt": (
            "portrait photo of Tony Stark, Robert Downey Jr face, "
            "dark goatee beard, brown eyes, confident smirk, "
            "wearing dark suit, arc reactor glowing blue on chest, "
            "high-tech lab background with holographic displays, "
            "masterpiece, photorealistic, 8k, sharp focus, "
            "studio lighting, face clearly visible, front facing"
        ),
        "negative": (
            "helmet, mask, iron man suit covering face, "
            "cartoon, anime, painting, blurry, deformed, "
            "bad anatomy, extra limbs, ugly, low quality"
        ),
    },
    "thor": {
        "prompt": (
            "portrait photo of Thor Odinson, Chris Hemsworth face, "
            "long blonde hair, blue eyes, strong jawline, short beard, "
            "wearing silver armor with red cape, "
            "stormy dark sky background with lightning, "
            "masterpiece, photorealistic, 8k, sharp focus, "
            "cinematic lighting, face clearly visible, front facing"
        ),
        "negative": (
            "helmet covering face, mask, "
            "cartoon, anime, painting, blurry, deformed, "
            "bad anatomy, extra limbs, ugly, low quality"
        ),
    },
    "hulk": {
        "prompt": (
            "portrait photo of Bruce Banner, Mark Ruffalo face, "
            "dark curly hair, brown eyes, serious expression, "
            "wearing torn purple shirt, slightly green tint to skin, "
            "ruined city background, "
            "masterpiece, photorealistic, 8k, sharp focus, "
            "cinematic lighting, face clearly visible, front facing"
        ),
        "negative": (
            "fully green skin, monster, "
            "cartoon, anime, painting, blurry, deformed, "
            "bad anatomy, extra limbs, ugly, low quality"
        ),
    },
}


def generate_face_image(avatar_key, pipeline=None):
    """Generate a single face image for a character."""
    if avatar_key not in CHARACTER_FACES:
        raise ValueError(f"Unknown avatar: {avatar_key}")

    char = CHARACTER_FACES[avatar_key]
    output_path = os.path.join(FACES_DIR, f"{avatar_key}.png")

    # Skip if already generated
    if os.path.exists(output_path):
        print(f"[FaceGen] {avatar_key} face already exists at {output_path}")
        return output_path

    if pipeline is None:
        from diffusers import StableDiffusionPipeline
        print("[FaceGen] Loading Stable Diffusion pipeline for face generation...")
        pipeline = StableDiffusionPipeline.from_pretrained(
            "emilianJR/epiCRealism",
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        )
        if torch.cuda.is_available():
            pipeline.enable_model_cpu_offload()
            try:
                pipeline.enable_vae_slicing()
            except Exception:
                pass

    print(f"[FaceGen] Generating {avatar_key} face portrait...")
    result = pipeline(
        prompt=char["prompt"],
        negative_prompt=char["negative"],
        width=512,
        height=512,
        num_inference_steps=30,
        guidance_scale=7.5,
        generator=torch.Generator(device="cpu").manual_seed(42),
    )

    image = result.images[0]
    image.save(output_path)
    print(f"[FaceGen] Saved {avatar_key} face to {output_path}")
    return output_path


def generate_all_faces():
    """Generate face images for all characters."""
    from diffusers import StableDiffusionPipeline

    print("[FaceGen] Loading Stable Diffusion pipeline...")
    pipeline = StableDiffusionPipeline.from_pretrained(
        "emilianJR/epiCRealism",
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    )
    if torch.cuda.is_available():
        pipeline.enable_model_cpu_offload()
        try:
            pipeline.enable_vae_slicing()
        except Exception:
            pass

    for key in CHARACTER_FACES:
        generate_face_image(key, pipeline=pipeline)

    # Free GPU memory
    del pipeline
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    print("[FaceGen] All character faces generated!")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        generate_face_image(sys.argv[1])
    else:
        generate_all_faces()
