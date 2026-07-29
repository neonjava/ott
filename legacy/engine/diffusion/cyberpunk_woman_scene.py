# engine/diffusion/cyberpunk_woman_scene.py
import os
import json
import time
import logging
import torch
import subprocess
from engine.backends.ltx.backend import LTXVideoBackend

logger = logging.getLogger(__name__)

def generate_cyberpunk_scene():
    prompt = (
        "A cinematic tracking shot of a futuristic woman walking through a rainy neon-lit cyberpunk city at night. "
        "Wet streets reflect colorful neon lights while soft rain falls. The camera slowly dollies forward with smooth motion. "
        "Ultra realistic face, natural walking animation, cinematic lighting, volumetric fog, detailed environment, Hollywood movie, masterpiece, high quality."
    )
    negative_prompt = "low quality, blurry, distorted, static, bad anatomy, deformed, glitch"

    print("==================================================")
    print("Executing Cyberpunk Woman LTX-Video Scene Generation")
    print(f"Prompt: {prompt}")
    print("==================================================")

    backend = LTXVideoBackend(output_dir="outputs/productions", debug_dir="outputs/debug")
    res = backend.generate_video(
        prompt=prompt,
        negative_prompt=negative_prompt,
        duration_sec=5.0,
        fps=16,
        resolution="704x384",
        seed=42
    )

    # Copy output to specific cyberpunk scene filenames
    src_mp4 = res["output_mp4"]
    cyber_mp4 = "outputs/productions/cyberpunk_woman_rainy_city.mp4"
    export_user_subfolder = "outputs/export_for_user/cyberpunk_woman_scene"
    export_user_mp4 = os.path.join(export_user_subfolder, "cyberpunk_woman_rainy_city.mp4")
    
    os.makedirs(export_user_subfolder, exist_ok=True)
    os.makedirs(os.path.join(export_user_subfolder, "images"), exist_ok=True)

    with open(src_mp4, "rb") as s, open(cyber_mp4, "wb") as d:
        d.write(s.read())
    with open(src_mp4, "rb") as s, open(export_user_mp4, "wb") as d:
        d.write(s.read())

    # Copy frame images to user subfolder
    for idx in range(1, res["frames_generated"] + 1):
        f_name = f"frame_{idx:04d}.png"
        src_img = os.path.join("outputs/debug", f_name)
        dst_img = os.path.join(export_user_subfolder, "images", f_name)
        if os.path.exists(src_img):
            with open(src_img, "rb") as s, open(dst_img, "wb") as d:
                d.write(s.read())

    print(f"[✓] Cyberpunk scene generated successfully! Exported to {export_user_mp4}")
    return res

if __name__ == "__main__":
    generate_cyberpunk_scene()
