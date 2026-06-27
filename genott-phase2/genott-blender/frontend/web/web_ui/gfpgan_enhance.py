import os
import subprocess
import tempfile
import shutil

def enhance_video_with_gfpgan(src_mp4: str, dst_mp4: str) -> None:
    """Enhance a video using GFPGAN.

    Steps:
    1️⃣ Extract frames and audio from the source video.
    2️⃣ Run the SadTalker GFPGAN video script on the frames (up‑scale factor 2).
    3️⃣ Re‑encode the enhanced frames with the original audio.
    """
    # Create temporary workspace
    with tempfile.TemporaryDirectory() as tmpdir:
        frames_dir = os.path.join(tmpdir, "frames")
        enhanced_dir = os.path.join(tmpdir, "enhanced")
        os.makedirs(frames_dir, exist_ok=True)
        os.makedirs(enhanced_dir, exist_ok=True)

        # 1️⃣ Extract frames (25 fps) and keep original audio
        audio_path = os.path.join(tmpdir, "audio.aac")
        subprocess.run([
            "ffmpeg", "-y", "-i", src_mp4,
            "-vf", "fps=25", os.path.join(frames_dir, "frame_%04d.png"),
            "-vn", "-acodec", "copy", audio_path
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # 2️⃣ Run GFPGAN on each frame (module provided by SadTalker)
        # The entrypoint script lives at SadTalker/scripts/gfpgan_video.py
        subprocess.run([
            "python", "-m", "scripts.gfpgan_video",
            "-i", frames_dir,
            "-o", enhanced_dir,
            "-s", "2"  # upscale ×2 → ~1024 px final
        ], cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), "SadTalker")),
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # 3️⃣ Re‑assemble enhanced frames with original audio
        subprocess.run([
            "ffmpeg", "-y",
            "-r", "25", "-i", os.path.join(enhanced_dir, "frame_%04d.png"),
            "-i", audio_path,
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            dst_mp4
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
