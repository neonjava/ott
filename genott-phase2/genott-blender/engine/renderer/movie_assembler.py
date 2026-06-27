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

def get_best_h264_encoder():
    """Detect the best available H.264 encoder in FFmpeg."""
    try:
        result = subprocess.run(["ffmpeg", "-encoders"], capture_output=True, text=True, check=True)
        encoders = result.stdout
        # Order of preference
        for enc in ["libx264", "libopenh264", "h264_nvenc", "h264_amf", "h264_vaapi"]:
            if enc in encoders:
                return enc
    except Exception:
        pass
    return "h264"

def apply_fades_to_clip(filepath, fade_in_type, fade_out_type, output_filepath):
    """
    Applies FFmpeg video/audio fade filters to a clip.
    fade_in_type/fade_out_type: 'fade' (black), 'white' (white), or None.
    """
    valid, info = validate_scene(filepath)
    if not valid:
        return False
    
    duration = info.get("duration", 0.0) if isinstance(info, dict) else 0.0
    has_audio = info.get("has_audio", False) if isinstance(info, dict) else False
    
    if duration <= 0:
        return False
        
    fade_dur = min(0.5, duration / 4.0)
    if fade_dur <= 0.05:
        return False
        
    v_filters = []
    a_filters = []
    
    if fade_in_type:
        color = "white" if fade_in_type == "white" else "black"
        v_filters.append(f"fade=t=in:st=0:d={fade_dur}:color={color}")
        if has_audio:
            a_filters.append(f"afade=t=in:st=0:d={fade_dur}")
            
    if fade_out_type:
        color = "white" if fade_out_type == "white" else "black"
        start_time = max(0.0, duration - fade_dur)
        v_filters.append(f"fade=t=out:st={start_time}:d={fade_dur}:color={color}")
        if has_audio:
            a_filters.append(f"afade=t=out:st={start_time}:d={fade_dur}")
            
    if not v_filters and not a_filters:
        return False
        
    cmd = ["ffmpeg", "-y", "-i", filepath]
    
    if v_filters:
        cmd.extend(["-vf", ",".join(v_filters)])
    encoder = get_best_h264_encoder()
    cmd.extend(["-c:v", encoder, "-pix_fmt", "yuv420p"])
    if encoder == "libx264":
        cmd.extend(["-preset", "superfast"])
    
    if has_audio:
        if a_filters:
            cmd.extend(["-af", ",".join(a_filters)])
        cmd.extend(["-c:a", "aac"])
    else:
        cmd.extend(["-an"])
        
    cmd.append(output_filepath)
    
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to apply fades to {filepath}: {e.stderr.decode() if e.stderr else str(e)}")
        return False

def assemble_movie(generation_id, video_dir, output_filename="final_movie.mp4", scene_files=None, transitions=None):
    """
    Assemble scene clips into a single final movie, applying cross-scene transitions.
    
    Args:
        generation_id: Unique movie generation ID.
        video_dir: Directory containing scene videos.
        output_filename: Name for the final output file.
        scene_files: Optional explicit list of scene file paths. If None, auto-discovers.
        transitions: Optional list of transitions ('fade', 'white', 'cut') between scene clips.
    
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
    
    # 2.5 Apply transitions/fades if requested
    temp_fade_files = []
    processed_files = []
    
    for idx, filepath in enumerate(files):
        fade_in_type = None
        fade_out_type = None
        
        if transitions:
            # Transition before this scene
            if idx > 0 and idx - 1 < len(transitions):
                t_prev = transitions[idx - 1]
                if t_prev in ("fade", "white"):
                    fade_in_type = t_prev
            # Transition after this scene
            if idx < len(files) - 1 and idx < len(transitions):
                t_next = transitions[idx]
                if t_next in ("fade", "white"):
                    fade_out_type = t_next
                    
        if fade_in_type or fade_out_type:
            trans_filepath = filepath.replace(".mp4", f"_trans_{idx}.mp4")
            success = apply_fades_to_clip(filepath, fade_in_type, fade_out_type, trans_filepath)
            if success:
                temp_fade_files.append(trans_filepath)
                processed_files.append(trans_filepath)
            else:
                processed_files.append(filepath)
        else:
            processed_files.append(filepath)
            
    # 3. Generate concat manifest
    manifest_path = os.path.join(video_dir, f"manifest_{generation_id}.txt")
    with open(manifest_path, "w") as f:
        for filepath in processed_files:
            f.write(f"file '{filepath}'\n")

    final_filepath = os.path.join(video_dir, f"{generation_id}_{output_filename}")
    
    # 4. Merge scenes with FFmpeg
    # If we have faded clips, we force re-encoding to guarantee codec/stream alignment and smooth rendering.
    force_reencode = len(temp_fade_files) > 0
    encoder = get_best_h264_encoder()
    
    if force_reencode:
        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", manifest_path,
            "-c:v", encoder, "-c:a", "aac", "-pix_fmt", "yuv420p",
            final_filepath
        ]
        if encoder == "libx264":
            cmd.insert(-1, "-preset")
            cmd.insert(-1, "fast")
    else:
        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", manifest_path,
            "-c", "copy", final_filepath
        ]
        
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        # Fallback: re-encode if copy fails
        cmd_reencode = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", manifest_path,
            "-c:v", encoder, "-c:a", "aac", "-pix_fmt", "yuv420p",
            final_filepath
        ]
        if encoder == "libx264":
            cmd_reencode.insert(-1, "-preset")
            cmd_reencode.insert(-1, "fast")
        try:
            subprocess.run(cmd_reencode, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e2:
            # Clean up temp fade files before returning error
            for f in temp_fade_files:
                if os.path.exists(f):
                    os.remove(f)
            if os.path.exists(manifest_path):
                os.remove(manifest_path)
            return False, f"FFmpeg concat failed: {e2.stderr.decode()}", 0

    # Clean up temp fade files and manifest
    for f in temp_fade_files:
        if os.path.exists(f):
            try:
                os.remove(f)
            except:
                pass
    if os.path.exists(manifest_path):
        os.remove(manifest_path)

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
    
    if not has_video:
        return False, "Final movie missing video stream", 0
        
    return True, final_filepath, final_dur
