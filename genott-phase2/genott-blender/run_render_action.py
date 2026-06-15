# run_render_action.py
import os
import sys
import subprocess
import shutil
import glob

# ActionMapper registry
ACTION_MAPPER = {
    "walk": "Walk",
    "run": "Run",
    "survey": "Survey",
    "fly": "assets/animations/fly.fbx",
    "land": "assets/animations/land.fbx",
    "attack": "assets/animations/attack.fbx"
}

def render_action(character_name="fox", action_input="Walk"):
    project_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(project_dir, "render_action_blender.py")
    
    # Locate character GLB
    char_filename = f"{character_name}.glb"
    char_path = os.path.join(project_dir, "assets", "characters", char_filename)
    if not os.path.exists(char_path):
        # Try fallback or exact check
        raise FileNotFoundError(f"Character model not found: {char_path}")
        
    # Map action input based on character
    action_key = action_input.lower()
    if character_name == "fox":
        fox_map = {
            "walk": "Walk",
            "run": "Run",
            "survey": "Survey"
        }
        mapped_action = fox_map.get(action_key, action_input)
    elif character_name in ["humanoid", "human"]:
        human_map = {
            "idle": "CharacterArmature|Idle",
            "walk": "CharacterArmature|Run",
            "attack": "CharacterArmature|Punch",
            "run": "CharacterArmature|Run"
        }
        mapped_action = human_map.get(action_key, action_input)
    else:
        mapped_action = ACTION_MAPPER.get(action_key, action_input)
    
    # If mapped action is a path inside assets, resolve full path
    if isinstance(mapped_action, str) and mapped_action.startswith("assets/"):
        mapped_action_path = os.path.join(project_dir, mapped_action)
    else:
        mapped_action_path = mapped_action

    temp_frames_dir = os.path.join(project_dir, "temp_action_frames")
    if os.path.exists(temp_frames_dir):
        shutil.rmtree(temp_frames_dir)
    os.makedirs(temp_frames_dir, exist_ok=True)
    
    # Run Blender
    cmd = [
        "flatpak", "run", "org.blender.Blender",
        "-b",
        "--python", script_path,
        "--", char_path, mapped_action_path, temp_frames_dir
    ]
    
    print(f"[Wrapper] Executing command: {' '.join(cmd)}")
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    stdout = result.stdout or ""
    stderr = result.stderr or ""
    
    if result.returncode != 0:
        if os.path.exists(temp_frames_dir):
            shutil.rmtree(temp_frames_dir)
        raise RuntimeError(f"Blender render script failed! Stderr:\n{stderr}\nStdout:\n{stdout}")

    # Parse stdout for start/end frames
    f_start = 1
    f_end = 17
    for line in stdout.split("\n"):
        if "VERIFICATION_FRAME_START:" in line:
            f_start = int(line.split(":")[-1].strip())
        elif "VERIFICATION_FRAME_END:" in line:
            f_end = int(line.split(":")[-1].strip())
            
    print(f"[Wrapper] Animation frame range: {f_start} to {f_end}")

    # Save walk screenshots if target action is Walk
    png_files = sorted(glob.glob(os.path.join(temp_frames_dir, "*.png")))
    print(f"[Wrapper] Rendered {len(png_files)} PNG frames.")
    
    output_dir = os.path.join(project_dir, "static", "videos")
    os.makedirs(output_dir, exist_ok=True)

    if action_input.lower() == "walk" and len(png_files) >= 17:
        # Save specific frames as requested
        # First frame is index 0, 8th is index 7, 17th is index 16
        shutil.copy(png_files[0], os.path.join(output_dir, "frame_001.png"))
        shutil.copy(png_files[7], os.path.join(output_dir, "frame_008.png"))
        shutil.copy(png_files[16], os.path.join(output_dir, "frame_017.png"))
        print("[Wrapper] Saved Walk screenshots: frame_001.png, frame_008.png, frame_017.png")

    # Compile video
    output_mp4_path = os.path.join(output_dir, f"{action_input.lower()}_preview.mp4")
    
    # Construct ffmpeg pattern
    # Since files are padded e.g. 0000.png or 0001.png, we can find the pattern or start number
    start_number = str(f_start)
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-framerate", "24",
        "-start_number", start_number,
        "-i", os.path.join(temp_frames_dir, "%04d.png"),
        "-c:v", "h264_nvenc",
        "-pix_fmt", "yuv420p",
        output_mp4_path
    ]
    
    print(f"[Wrapper] Compiling video with FFmpeg: {' '.join(ffmpeg_cmd)}")
    subprocess.run(ffmpeg_cmd, check=True)
    
    # Clean up temp frames
    if os.path.exists(temp_frames_dir):
        shutil.rmtree(temp_frames_dir)
        
    print(f"[Wrapper] Success! Created video: {output_mp4_path}")
    return output_mp4_path

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--character", default="fox")
    parser.add_argument("--action", default="Walk")
    args = parser.parse_args()
    
    render_action(args.character, args.action)
