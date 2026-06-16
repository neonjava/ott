import os
import subprocess
import glob
import json

def get_video_info(filepath):
    try:
        cmd = [
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration:stream=codec_name,codec_type",
            "-of", "json", filepath
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        return None

def validate_scene(filepath):
    if not os.path.exists(filepath):
        return False, "File does not exist"
    
    info = get_video_info(filepath)
    if not info:
        return False, "File is not playable or ffprobe failed"
        
    streams = info.get("streams", [])
    has_video = False
    has_audio = False
    for s in streams:
        if s.get("codec_type") == "video":
            has_video = True
            if s.get("codec_name") not in ["h264", "hevc", "vp9"]:
                return False, f"Incompatible video codec: {s.get('codec_name')}"
        elif s.get("codec_type") == "audio":
            has_audio = True
            
    if not has_video:
        return False, "No video stream"
    if not has_audio:
        return False, "No audio stream"
        
    return True, float(info.get("format", {}).get("duration", 0))

def assemble_movie(generation_id, video_dir, output_filename="final_movie.mp4"):
    # 1. Discover all generated scene videos
    pattern = os.path.join(video_dir, f"final_scene_{generation_id}_*.mp4")
    files = glob.glob(pattern)
    
    # 2. Order scenes correctly
    files.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))
    
    if not files:
        return False, "No scenes found for generation", 0
        
    total_duration = 0.0
    manifest_path = os.path.join(video_dir, f"manifest_{generation_id}.txt")
    
    try:
        with open(manifest_path, "w") as f:
            for filepath in files:
                # 3, 4, 5. Validate scene, playability, codec, audio
                valid, result = validate_scene(filepath)
                if not valid:
                    return False, f"Scene validation failed for {os.path.basename(filepath)}: {result}", 0
                
                total_duration += result
                f.write(f"file '{filepath}'\\n")
    except Exception as e:
        return False, f"Failed to generate manifest: {str(e)}", 0

    final_filepath = os.path.join(video_dir, f"{generation_id}_{output_filename}")
    
    # Merge scenes with FFmpeg
    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", manifest_path,
        "-c", "copy", final_filepath
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        return False, f"FFmpeg concat failed: {e.stderr.decode()}", 0

    # Validation: After assembly
    if not os.path.exists(final_filepath):
        return False, "Final output file does not exist", 0
        
    final_info = get_video_info(final_filepath)
    if not final_info:
        return False, "Final output file is not playable", 0
        
    final_dur = float(final_info.get("format", {}).get("duration", 0))
    if final_dur < total_duration * 0.95:
        return False, f"Duration mismatch: expected {total_duration}, got {final_dur}", 0
        
    streams = final_info.get("streams", [])
    has_video = any(s.get("codec_type") == "video" for s in streams)
    has_audio = any(s.get("codec_type") == "audio" for s in streams)
    
    if not has_video:
        return False, "Final movie missing video stream", 0
    if not has_audio:
        return False, "Final movie missing audio stream", 0
        
    return True, final_filepath, final_dur
