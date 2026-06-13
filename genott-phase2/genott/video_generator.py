"""
GenOTT — Local Video Generation Module
Uses LTX-Video via HuggingFace diffusers for text-to-video on RTX 4060 (8GB VRAM).
Falls back to AnimateDiff (lighter) if LTX-Video doesn't fit in VRAM.
"""

import os
import time
import uuid
import torch

# Directory to store generated video clips
VIDEO_DIR = os.path.join(os.path.dirname(__file__), "static", "videos")
os.makedirs(VIDEO_DIR, exist_ok=True)

# Global pipeline reference (lazy loaded)
_pipeline = None
_pipeline_type = None


def get_device():
    """Get the best available device."""
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def load_pipeline():
    """
    Lazy-load the video generation pipeline.
    Tries LTX-Video first, falls back to AnimateDiff if VRAM is insufficient.
    """
    global _pipeline, _pipeline_type

    if _pipeline is not None:
        return _pipeline, _pipeline_type

    device = get_device()
    print(f"\n[VideoGen] Loading pipeline on device: {device}")

    # Try AnimateDiff first (lighter, works on 8GB VRAM, only ~3GB download)
    try:
        from diffusers import AnimateDiffPipeline, MotionAdapter, DDIMScheduler

        print("[VideoGen] Loading AnimateDiff pipeline...")
        adapter = MotionAdapter.from_pretrained(
            "guoyww/animatediff-motion-adapter-v1-5-2",
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        )
        _pipeline = AnimateDiffPipeline.from_pretrained(
            "emilianJR/epiCRealism",
            motion_adapter=adapter,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        )
        _pipeline.scheduler = DDIMScheduler.from_config(
            _pipeline.scheduler.config,
            clip_sample=False,
            timestep_spacing="linspace",
            beta_schedule="linear",
            steps_offset=1,
        )

        if device == "cuda":
            _pipeline.enable_model_cpu_offload()
            try:
                _pipeline.enable_vae_slicing()
            except Exception:
                pass

        _pipeline_type = "animatediff"
        print("[VideoGen] AnimateDiff pipeline loaded successfully!")
        return _pipeline, _pipeline_type

    except Exception as e:
        print(f"[VideoGen] AnimateDiff failed to load: {e}")

    # Fallback: Try LTX-Video (Lightricks text-to-video, 28GB download)
    try:
        from diffusers import LTXPipeline
        print("[VideoGen] Falling back to LTX-Video pipeline...")
        _pipeline = LTXPipeline.from_pretrained(
            "Lightricks/LTX-Video",
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        )
        _pipeline.to(device)

        # Enable memory optimizations for 8GB VRAM
        if device == "cuda":
            _pipeline.enable_model_cpu_offload()
            try:
                _pipeline.enable_vae_slicing()
            except Exception:
                pass

        _pipeline_type = "ltx"
        print("[VideoGen] LTX-Video pipeline loaded successfully!")
        return _pipeline, _pipeline_type

    except Exception as e:
        print(f"[VideoGen] LTX-Video also failed: {e}")
        raise RuntimeError(
            "No video generation pipeline could be loaded. "
            "Ensure torch and diffusers are installed with CUDA support."
        )


def generate_video(prompt, num_frames=16, width=512, height=320, num_steps=25, seed=None):
    """
    Generate a video clip from a text prompt.

    Args:
        prompt: Text description for the video
        num_frames: Number of frames (16 = ~2 seconds at 8fps)
        width: Video width
        height: Video height
        num_steps: Inference steps (higher = better quality but slower)
        seed: Random seed for reproducibility

    Returns:
        dict with 'filename', 'path', 'url', 'duration_sec', 'gen_time_sec'
    """
    pipeline, ptype = load_pipeline()

    if seed is not None:
        generator = torch.Generator(device=get_device()).manual_seed(seed)
    else:
        generator = None

    video_id = str(uuid.uuid4())[:8]
    filename = f"scene_{video_id}.mp4"
    filepath = os.path.join(VIDEO_DIR, filename)

    print(f"\n[VideoGen] Generating video: {filename}")
    print(f"[VideoGen] Prompt: {prompt[:100]}...")
    print(f"[VideoGen] Settings: {num_frames} frames, {width}x{height}, {num_steps} steps")

    start_time = time.time()

    try:
        if ptype == "ltx":
            output = pipeline(
                prompt=prompt,
                negative_prompt="blurry, low quality, distorted, ugly, worst quality",
                num_frames=num_frames,
                width=width,
                height=height,
                num_inference_steps=num_steps,
                generator=generator,
            )
            # Export frames to video
            from diffusers.utils import export_to_video
            export_to_video(output.frames[0], filepath, fps=8)

        elif ptype == "animatediff":
            output = pipeline(
                prompt=prompt,
                negative_prompt="blurry, low quality, distorted, ugly, worst quality",
                num_frames=num_frames,
                width=width,
                height=height,
                num_inference_steps=num_steps,
                guidance_scale=7.5,
                generator=generator,
            )
            from diffusers.utils import export_to_video
            export_to_video(output.frames[0], filepath, fps=8)

        gen_time = round(time.time() - start_time, 1)
        duration_sec = round(num_frames / 8, 1)

        print(f"[VideoGen] Done! Generated in {gen_time}s -> {filepath}")

        return {
            "filename": filename,
            "path": filepath,
            "url": f"/static/videos/{filename}",
            "duration_sec": duration_sec,
            "gen_time_sec": gen_time,
        }

    except torch.cuda.OutOfMemoryError:
        torch.cuda.empty_cache()
        raise RuntimeError("GPU out of memory. Try reducing resolution or frame count.")

    except Exception as e:
        raise RuntimeError(f"Video generation failed: {str(e)}")


def get_pipeline_info():
    """Return info about the current pipeline status."""
    return {
        "loaded": _pipeline is not None,
        "type": _pipeline_type,
        "device": get_device(),
        "cuda_available": torch.cuda.is_available(),
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "vram_total_mb": round(torch.cuda.get_device_properties(0).total_mem / 1024**2) if torch.cuda.is_available() else 0,
    }
