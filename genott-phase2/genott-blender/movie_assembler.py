import os
import subprocess
import glob
import json

def get_video_info(filepath):
    """Get video metadata via ffprobe."""
    try:
        cmd = [
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration:stream=codec_name,codec_type",
            "-of", "json", filepath
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except Exception:
        return None

def validate_scene(filepath):
    """Validate a scene clip exists, is playable, has correct codec, and has audio."""
    if not os.path.exists(filepath):
        return False, "File does not exist"
    
    if os.path.getsize(filepath) < 100:
        return False, "File is empty or too small"
    
    info = get_video_info(filepath)
    if not info:
        return False, "File is not playable or ffprobe failed"
        
    streams = info.get("streams", [])
    has_video = False
    has_audio = False
    for s in streams:
        if s.get("codec_type") == "video":
            has_video = True
            if s.get("codec_name") not in ["h264", "hevc", "vp9", "av1"]:
                return False, f"Incompatible video codec: {s.get('codec_name')}"
        elif s.get("codec_type") == "audio":
            has_audio = True
            
    if not has_video:
        return False, "No video stream"
        
    duration = float(info.get("format", {}).get("duration", 0))
    return True, {"duration": duration, "has_audio": has_audio}

def assemble_movie(generation_id, video_dir, output_filename="final_movie.mp4", scene_files=None):
    """
    Assemble scene clips into a single final movie.
    
    Args:
        generation_id: Unique movie generation ID.
        video_dir: Directory containing scene videos.
        output_filename: Name for the final output file.
        scene_files: Optional explicit list of scene file paths. If None, auto-discovers.
    
    Returns:
        (success: bool, result_or_error: str, duration: float)
    """
    # 1. Discover scene videos
    if scene_files:
        files = [f for f in scene_files if os.path.exists(f)]
    else:
        # Auto-discover by checking multiple naming patterns
        patterns = [
            f"final_scene_{generation_id}_*.mp4",
            f"scene_{generation_id}_*.mp4",
            f"lipsync_{generation_id}_*.mp4",
        ]
        files = []
        for pat in patterns:
            files.extend(glob.glob(os.path.join(video_dir, pat)))
        # Deduplicate and sort
        files = sorted(set(files), key=lambda x: int(x.rsplit('_', 1)[-1].split('.')[0]))
    
    if not files:
        return False, "No scenes found for generation", 0
        
    # 2. Validate every scene
    total_duration = 0.0
    scene_report = []
    all_have_audio = True
    
    for filepath in files:
        valid, result = validate_scene(filepath)
        if not valid:
            return False, f"Scene validation failed for {os.path.basename(filepath)}: {result}", 0
        
        total_duration += result["duration"]
        if not result["has_audio"]:
            all_have_audio = False
        scene_report.append({
            "file": os.path.basename(filepath),
            "duration": result["duration"],
            "has_audio": result["has_audio"]
        })
    
    # 3. Generate concat manifest
    manifest_path = os.path.join(video_dir, f"manifest_{generation_id}.txt")
    with open(manifest_path, "w") as f:
        for filepath in files:
            f.write(f"file '{filepath}'\n")

    final_filepath = os.path.join(video_dir, f"{generation_id}_{output_filename}")
    
    # 4. Merge scenes with FFmpeg
    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", manifest_path,
        "-c", "copy", final_filepath
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        # Fallback: re-encode if codec mismatch
        cmd_reencode = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", manifest_path,
            "-c:v", "libx264", "-c:a", "aac", "-pix_fmt", "yuv420p",
            "-preset", "fast", final_filepath
        ]
        try:
            subprocess.run(cmd_reencode, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e2:
            return False, f"FFmpeg concat failed: {e2.stderr.decode()}", 0

    # 5. Post-assembly validation
    if not os.path.exists(final_filepath):
        return False, "Final output file does not exist", 0
        
    final_info = get_video_info(final_filepath)
    if not final_info:
        return False, "Final output file is not playable", 0
        
    final_dur = float(final_info.get("format", {}).get("duration", 0))
    if final_dur < total_duration * 0.95:
        return False, f"Duration mismatch: expected >= {total_duration * 0.95:.2f}s, got {final_dur:.2f}s", 0
        
    streams = final_info.get("streams", [])
    has_video = any(s.get("codec_type") == "video" for s in streams)
    has_audio = any(s.get("codec_type") == "audio" for s in streams)
    
    if not has_video:
        return False, "Final movie missing video stream", 0
    
    # Clean up manifest
    if os.path.exists(manifest_path):
        os.remove(manifest_path)
        
    return True, final_filepath, final_dur
