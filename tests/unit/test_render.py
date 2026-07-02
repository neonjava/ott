# test_render.py
import os
import subprocess
import shutil

def run_test_render(output_mp4_path):
    project_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(project_dir, "test_render_script.py")
    output_mp4_path = os.path.abspath(output_mp4_path)

    # 1. Create a temp directory for raw image frames
    temp_frames_dir = os.path.join(project_dir, "temp_render_frames")
    os.makedirs(temp_frames_dir, exist_ok=True)

    # 2. Invoke Flatpak Blender CLI to render PNG frames
    cmd = [
        "flatpak", "run", "org.blender.Blender",
        "-b",
        "--python", script_path,
        "--", temp_frames_dir
    ]

    print(f"[TestRender] Running Blender Render cmd: {' '.join(cmd)}")
    process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if process.returncode != 0:
        if os.path.exists(temp_frames_dir):
            shutil.rmtree(temp_frames_dir)
        raise RuntimeError(f"Blender Test Render execution failed! Output:\n{process.stderr or process.stdout}")

    # 3. Assemble PNG frames into final browser-playable MP4 via system FFmpeg
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-framerate", "24",
        "-i", os.path.join(temp_frames_dir, "%04d.png"),
        "-c:v", "h264_nvenc",
        "-pix_fmt", "yuv420p",
        output_mp4_path
    ]
    
    print(f"[TestRender] Compiling frames with FFmpeg: {' '.join(ffmpeg_cmd)}")
    ffmpeg_process = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Cleanup temp frames
    if os.path.exists(temp_frames_dir):
        shutil.rmtree(temp_frames_dir)

    if ffmpeg_process.returncode != 0:
        raise RuntimeError("FFmpeg assembly of Blender frames failed!")

    print(f"[TestRender] Final video generated successfully at: {output_mp4_path}")
    return output_mp4_path

if __name__ == "__main__":
    run_test_render("./test.mp4")
