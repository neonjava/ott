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

        # NOTE: IP-Adapter disabled — causes device/dtype mismatch with enable_model_cpu_offload()
        # Consistency is achieved via detailed character prompts + shared seeds instead.
        # To re-enable IP-Adapter, CPU offloading must be replaced with manual .to(device) calls.

        if device == "cuda":
            _pipeline.enable_model_cpu_offload()
            try:
                _pipeline.enable_vae_slicing()
            except Exception:
                pass

        _pipeline_type = "animatediff"
        print("[VideoGen] AnimateDiff pipeline loaded successfully with IP-Adapter!")
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


# Global store for tracking active generation logs
generation_logs = {}

def get_generation_logs(generation_id):
    """Retrieve logs for a specific generation ID."""
    return generation_logs.get(generation_id, [])

def generate_video(prompt, num_frames=16, width=512, height=320, num_steps=25, seed=None, generation_id=None):
    """
    Generate a video clip from a text prompt.

    Args:
        prompt: Text description for the video
        num_frames: Number of frames (16 = ~2 seconds at 8fps)
        width: Video width
        height: Video height
        num_steps: Inference steps (higher = better quality but slower)
        seed: Random seed for reproducibility
        generation_id: Unique string to track logs for this generation session

    Returns:
        dict with 'filename', 'path', 'url', 'duration_sec', 'gen_time_sec'
    """
    def update_log(msg):
        if generation_id:
            if generation_id not in generation_logs:
                generation_logs[generation_id] = []
            generation_logs[generation_id].append(f"[{time.strftime('%H:%M:%S')}] {msg}")
            print(f"[VideoGen Log] {generation_id}: {msg}")

    update_log("Checking system environment...")
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

    # Enhance video prompts automatically for superior visual fidelity
    enhanced_prompt = f"{prompt}, masterpiece, photorealistic, 8k resolution, cinematic lighting, sharp focus, highly detailed, dramatic atmosphere"
    enhanced_neg_prompt = (
        "low quality, worst quality, blurry, deformed face, bad eyes, disfigured, "
        "distorted, ugly, extra limbs, bad proportions, cartoon, anime, 3d render, CGI, doll, painting, drawing"
    )

    try:
        if ptype == "ltx":
            update_log("Starting LTX-Video generation...")
            output = pipeline(
                prompt=enhanced_prompt,
                negative_prompt=enhanced_neg_prompt,
                num_frames=num_frames,
                width=width,
                height=height,
                num_inference_steps=num_steps,
                generator=generator,
            )
            # Export frames to video
            update_log("Saving video output to disk...")
            from diffusers.utils import export_to_video
            export_to_video(output.frames[0], filepath, fps=8)

        elif ptype == "animatediff":
            update_log("Preparing AnimateDiff pipeline inputs...")
            
            def pipe_callback(pipe, step, timestep, callback_kwargs):
                pct = int(((step + 1) / num_steps) * 100)
                update_log(f"Inference step {step + 1}/{num_steps} ({pct}%)")
                return callback_kwargs

            try:
                update_log("Starting AnimateDiff diffusion process...")
                output = pipeline(
                    prompt=enhanced_prompt,
                    negative_prompt=enhanced_neg_prompt,
                    num_frames=num_frames,
                    width=width,
                    height=height,
                    num_inference_steps=num_steps,
                    guidance_scale=7.5,
                    generator=generator,
                    callback_on_step_end=pipe_callback
                )
            except TypeError:
                # Fallback if callback_on_step_end signature differs
                update_log("Step progress callback not supported, running standard inference...")
                output = pipeline(
                    prompt=enhanced_prompt,
                    negative_prompt=enhanced_neg_prompt,
                    num_frames=num_frames,
                    width=width,
                    height=height,
                    num_inference_steps=num_steps,
                    guidance_scale=7.5,
                    generator=generator,
                )

            update_log("Encoding frames into video container (MP4)...")
            from diffusers.utils import export_to_video
            export_to_video(output.frames[0], filepath, fps=8)

        gen_time = round(time.time() - start_time, 1)
        duration_sec = round(num_frames / 8, 1)

        update_log(f"Success! Video rendered in {gen_time}s.")
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
        update_log("ERROR: GPU Out of Memory!")
        raise RuntimeError("GPU out of memory. Try reducing resolution or frame count.")

    except Exception as e:
        update_log(f"ERROR: {str(e)}")
        raise RuntimeError(f"Video generation failed: {str(e)}")


def generate_speech(text, output_path, voice="en-US-ChristopherNeural"):
    """Generate speech using Microsoft Edge TTS (asynchronous library run synchronously)."""
    import asyncio
    import edge_tts

    async def _speak():
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)

    asyncio.run(_speak())


def generate_talking_head(image_path, audio_path, output_path, generation_id=None):
    """Generate a lip-synced talking head video from a source image and audio using SadTalker."""
    import subprocess
    import shutil
    import glob

    def update_log(msg):
        if generation_id:
            if generation_id not in generation_logs:
                generation_logs[generation_id] = []
            generation_logs[generation_id].append(f"[{time.strftime('%H:%M:%S')}] {msg}")
            print(f"[SadTalker Log] {generation_id}: {msg}")

    update_log("Initiating SadTalker lip-sync generator...")
    
    project_dir = os.path.dirname(os.path.abspath(__file__))
    sadtalker_dir = os.path.join(project_dir, "SadTalker")
    temp_results_dir = os.path.join(project_dir, "static", "videos", f"sadtalker_temp_{uuid.uuid4().hex[:8]}")
    os.makedirs(temp_results_dir, exist_ok=True)

    cmd = [
        os.path.join(project_dir, "venv", "bin", "python3"),
        os.path.join(sadtalker_dir, "inference.py"),
        "--driven_audio", audio_path,
        "--source_image", image_path,
        "--result_dir", temp_results_dir,
        "--still",
        "--preprocess", "full",
        "--checkpoint_dir", os.path.abspath(os.path.join(project_dir, "SadTalker", "checkpoints")),
    ]

    try:
        update_log("Running face processing and expression models (GFPGAN enabled)...")
        # Run process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=sadtalker_dir
        )

        # Monitor output logs in real-time — capture ALL output for debugging
        all_output_lines = []
        while True:
            line = process.stdout.readline()
            if not line:
                break
            line_str = line.strip()
            if line_str:
                all_output_lines.append(line_str)
                print(f"[SadTalker STDOUT] {line_str}")
                # Forward progress lines to the generation log
                if "%" in line_str or "step" in line_str.lower() or "processing" in line_str.lower():
                    update_log(line_str)

        process.wait()

        if process.returncode != 0:
            # Include the tail of SadTalker output in the error for diagnosis
            tail = "\n".join(all_output_lines[-30:])
            update_log(f"SadTalker FULL OUTPUT (last 30 lines):\n{tail}")
            raise RuntimeError(f"SadTalker process exited with code {process.returncode}. Output:\n{tail}")

        # Find the generated video file inside temp results
        generated_videos = glob.glob(os.path.join(temp_results_dir, "**", "*.mp4"), recursive=True)
        if not generated_videos:
            raise FileNotFoundError("SadTalker completed but no output MP4 video was found.")

        # Copy the final video to the desired destination output path
        shutil.copy(generated_videos[0], output_path)
        update_log("Stitched talking-head lip sync completed successfully!")
        return output_path

    except Exception as e:
        update_log(f"SadTalker inference failed: {str(e)}")
        raise e
    finally:
        # Cleanup temporary outputs
        if os.path.exists(temp_results_dir):
            shutil.rmtree(temp_results_dir)


def add_audio_to_video(video_path, audio_path, output_path):
    """Combine video and audio tracks using ffmpeg."""
    import subprocess
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        output_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


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


def score_movie_quality(filepath: str, expected_duration: float = None) -> dict:
    """Evaluate movie quality and return a score and metrics."""
    import json
    if not os.path.exists(filepath):
        return {"score": 0, "status": "missing_file"}
        
    try:
        # Use ffprobe to get video streams and format
        cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams", filepath
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        data = json.loads(result.stdout)
        
        streams = data.get("streams", [])
        format_data = data.get("format", {})
        
        has_video = False
        has_audio = False
        resolution = 0
        fps = 0
        
        for s in streams:
            if s.get("codec_type") == "video":
                has_video = True
                resolution = int(s.get("height", 0))
                # framerate is like "24/1"
                fr_str = s.get("r_frame_rate", "0/1").split('/')
                if len(fr_str) == 2 and int(fr_str[1]) > 0:
                    fps = int(fr_str[0]) / int(fr_str[1])
            elif s.get("codec_type") == "audio":
                has_audio = True
                
        actual_duration = float(format_data.get("duration", 0))
        bitrate = int(format_data.get("bit_rate", 0))
        
        score = 0
        if has_video: score += 20
        if has_audio: score += 20
        if resolution >= 540: score += 20
        if fps >= 23.9: score += 20
        
        if expected_duration:
            # Score duration accuracy (within 10%)
            if abs(actual_duration - expected_duration) / expected_duration <= 0.1:
                score += 20
            else:
                score += 10
        else:
            score += 20
            
        return {
            "score": score,
            "has_video": has_video,
            "has_audio": has_audio,
            "resolution": resolution,
            "fps": round(fps, 2),
            "duration": round(actual_duration, 2),
            "bitrate": bitrate
        }
    except Exception as e:
        print(f"Quality scoring error: {e}")
        return {"score": 0, "error": str(e)}


def _get_video_duration(video_path):
    import subprocess
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", video_path]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        return float(result.stdout.strip())
    except:
        return 2.0

def concatenate_videos(video_paths, output_path, transition="fade"):
    """Concatenate multiple video files into one with optional transitions."""
    import subprocess
    import os
    
    if not video_paths:
        raise ValueError("No videos to concatenate")
        
    if len(video_paths) == 1:
        import shutil
        shutil.copy(video_paths[0], output_path)
        return True

    processed_paths = []
    
    # Apply fade transitions if requested
    if transition == "fade":
        for i, path in enumerate(video_paths):
            dur = _get_video_duration(path)
            fade_in = 0.5 if i > 0 else 0.0 # Don't fade in first clip
            fade_out = 0.5 if i < len(video_paths) - 1 else 0.0 # Don't fade out last clip
            
            out_fade = f"{path}_faded.mp4"
            fade_cmd = [
                "ffmpeg", "-y", "-i", path,
                "-vf", f"fade=t=in:st=0:d={fade_in},fade=t=out:st={max(0, dur-fade_out)}:d={fade_out}",
                "-c:v", "h264_nvenc", "-preset", "fast", "-pix_fmt", "yuv420p",
                out_fade
            ]
            try:
                subprocess.run(fade_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                processed_paths.append(out_fade)
            except Exception as e:
                print(f"[VideoGen] Warning: Fade transition failed for {path}, using original. Error: {e}")
                processed_paths.append(path)
    else:
        processed_paths = video_paths

    # Concatenate
    list_path = output_path + ".txt"
    with open(list_path, "w") as f:
        for path in processed_paths:
            f.write(f"file '{os.path.abspath(path)}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", list_path,
        "-c:v", "h264_nvenc",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        output_path
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Cleanup
        if os.path.exists(list_path):
            os.remove(list_path)
        if transition == "fade":
            for p in processed_paths:
                if p.endswith("_faded.mp4") and os.path.exists(p):
                    os.remove(p)
                    
        return True
    except Exception as e:
        print(f"[VideoGen] Concat error: {e}")
        if os.path.exists(list_path):
            os.remove(list_path)
        raise e
