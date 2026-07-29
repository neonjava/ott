# run_humanoid_validation.py
import os
import subprocess
import shutil
import glob
import math

def calculate_image_diff(img1_path, img2_path):
    """Simple pixel-difference check using OpenCV to verify visual pose movement."""
    try:
        import cv2
        img1 = cv2.imread(img1_path)
        img2 = cv2.imread(img2_path)
        if img1 is None or img2 is None:
            return 0.0
        # Compute absolute difference
        diff = cv2.absdiff(img1, img2)
        # Normalized mean difference percentage
        return float(diff.mean() / 255.0 * 100.0)
    except Exception as e:
        print(f"[DiffError] Could not calculate visual diff: {e}")
        return 0.0

def run_validation():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(project_dir, "test_humanoid_render.py")
    
    char_path = os.path.join(project_dir, "assets", "characters", "fox.glb")
    action_name = "Walk"
    
    output_mp4_path = os.path.join(project_dir, "static", "videos", "character_animation_test.mp4")
    report_path = os.path.join(project_dir, "character_animation_validation.md")
    
    # Target frames
    screenshot_001 = os.path.join(project_dir, "static", "videos", "frame_001.png")
    screenshot_060 = os.path.join(project_dir, "static", "videos", "frame_060.png")
    screenshot_120 = os.path.join(project_dir, "static", "videos", "frame_120.png")

    temp_frames_dir = os.path.join(project_dir, "temp_humanoid_frames")
    os.makedirs(temp_frames_dir, exist_ok=True)
    os.makedirs(os.path.dirname(output_mp4_path), exist_ok=True)

    # 1. Execute Blender render script
    cmd = [
        "flatpak", "run", "org.blender.Blender",
        "-b",
        "--python", script_path,
        "--", char_path, action_name, temp_frames_dir
    ]

    print(f"[Validation] Running Blender command: {' '.join(cmd)}")
    process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Parse print output tags for validation metrics
    stdout = process.stdout or ""
    stderr = process.stderr or ""
    
    mesh_count = 0
    armature_count = 0
    selected_action = ""
    frame_count = 0
    objects = []
    actions = []

    for line in stdout.split("\n"):
        if "VERIFICATION_MESH_COUNT:" in line:
            mesh_count = int(line.split(":")[-1].strip())
        elif "VERIFICATION_ARMATURE_COUNT:" in line:
            armature_count = int(line.split(":")[-1].strip())
        elif "VERIFICATION_SELECTED_ACTION:" in line:
            selected_action = line.split(":")[-1].strip()
        elif "VERIFICATION_FRAME_COUNT:" in line:
            frame_count = int(line.split(":")[-1].strip())
        elif "VERIFICATION_OBJECT:" in line:
            objects.append(line.split(":")[-1].strip())
        elif "VERIFICATION_ACTION:" in line:
            actions.append(line.split(":")[-1].strip())

    print(f"[Validation] Blender exited with code: {process.returncode}")

    if process.returncode != 0:
        if os.path.exists(temp_frames_dir):
            shutil.rmtree(temp_frames_dir)
        raise RuntimeError(f"Blender validation render failed! Stderr:\n{stderr}")

    # Copy target screenshots
    png_files = sorted(glob.glob(os.path.join(temp_frames_dir, "*.png")))
    if len(png_files) >= 120:
        shutil.copy(png_files[0], screenshot_001)
        shutil.copy(png_files[59], screenshot_060)
        shutil.copy(png_files[119], screenshot_120)
        print("[Validation] Screenshots frame_001.png, frame_060.png, and frame_120.png generated.")
    else:
        if os.path.exists(temp_frames_dir):
            shutil.rmtree(temp_frames_dir)
        raise FileNotFoundError(f"FAIL: Rendered only {len(png_files)} frames instead of 120!")

    # Verify visual pose difference (pose must change)
    diff_60 = calculate_image_diff(screenshot_001, screenshot_060)
    diff_120 = calculate_image_diff(screenshot_060, screenshot_120)
    
    print(f"[Validation] Frame 1 vs 60 Pixel Diff: {diff_60:.2f}%")
    print(f"[Validation] Frame 60 vs 120 Pixel Diff: {diff_120:.2f}%")

    passed_checks = True
    fail_reasons = []

    if mesh_count == 0:
        passed_checks = False
        fail_reasons.append("FAIL: No meshes found.")
    if armature_count == 0:
        passed_checks = False
        fail_reasons.append("FAIL: No armature found.")
    if not selected_action:
        passed_checks = False
        fail_reasons.append("FAIL: Animation action missing.")
    if diff_60 < 0.5 and diff_120 < 0.5:
        passed_checks = False
        fail_reasons.append("FAIL: Pose did not change across frames (Character is static).")

    # Assemble final MP4
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-framerate", "24",
        "-i", os.path.join(temp_frames_dir, "%04d.png"),
        "-c:v", "h264_nvenc",
        "-pix_fmt", "yuv420p",
        output_mp4_path
    ]
    subprocess.run(ffmpeg_cmd, check=True)

    # Cleanup temp directory
    if os.path.exists(temp_frames_dir):
        shutil.rmtree(temp_frames_dir)

    # Generate Markdown validation report
    status_str = "SUCCESS" if passed_checks else "FAILED"
    report_content = f"""# Character Animation Pipeline Validation Report

## Execution Status: {status_str}

{"".join([f"*   {r}\n" for r in fail_reasons])}

### Imported Assets
*   **Humanoid Character Model:** `assets/characters/fox.glb` (Real rigged glTF sample asset)
*   **Animation Action Mapped:** `{selected_action}`

### Scene Structure Verified
*   **Meshes Found Count:** {mesh_count}
*   **Armatures Found Count:** {armature_count}
*   **Total Keyframes In Action:** {frame_count}

### Object Hierarchy
{"".join([f"*   {obj}\n" for obj in objects])}

### Animation Actions Registry
{"".join([f"*   {act}\n" for act in actions])}

### Visual Movement Benchmarking
*   **Frame 1 vs 60 Frame Pose Diff:** {diff_60:.2f}%
*   **Frame 60 vs 120 Frame Pose Diff:** {diff_120:.2f}%

### Output Assets
*   **Rendered Movie MP4 Output:** [character_animation_test.mp4](file://{output_mp4_path})
*   **Frame 1 Screenshot:** [frame_001.png](file://{screenshot_001})
*   **Frame 60 Screenshot:** [frame_060.png](file://{screenshot_060})
*   **Frame 120 Screenshot:** [frame_120.png](file://{screenshot_120})
"""
    with open(report_path, "w") as f:
        f.write(report_content)
    print(f"[Validation] Verification report written to: {report_path}")
    
    if not passed_checks:
        raise ValueError(f"Pipeline validation failed: {', '.join(fail_reasons)}")
    
    return output_mp4_path

if __name__ == "__main__":
    run_validation()
