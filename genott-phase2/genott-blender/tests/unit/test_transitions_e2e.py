#!/usr/bin/env python3
import os
import requests
import json
import subprocess

API_URL = "http://127.0.0.1:5001/api/generate-movie"

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
        print(f"ffprobe failed for {filepath}: {e}")
        return None

def main():
    print("=== Transition Engine E2E Validation ===")
    
    # Script with transition keywords and different locations
    script = (
        "hero walks forward in the forest. "
        "FADE TO BLACK. "
        "hero jumps in the castle. "
        "FADE TO WHITE. "
        "hero attacks in the city."
    )
    
    payload = {
        "character": "humanoid",
        "script": script
    }
    
    print("Sending request to generate movie with transitions...")
    try:
        resp = requests.post(API_URL, json=payload, timeout=300)
    except Exception as e:
        print(f"Failed to connect to API: {e}")
        return
        
    print(f"Response status code: {resp.status_code}")
    if resp.status_code != 200:
        print(f"Error: {resp.text}")
        return
        
    data = resp.json()
    if data.get("status") != "success":
        print(f"Generation failed: {data.get('error')}")
        return
        
    movie_path = data.get("movie", "")
    print(f"Successfully generated movie: {movie_path}")
    
    # Remove leading slash if any
    local_path = movie_path.lstrip("/")
    
    # Validate movie file
    if not os.path.exists(local_path):
        print(f"FAIL: Movie file does not exist at local path: {local_path}")
        return
        
    info = get_video_info(local_path)
    if not info:
        print("FAIL: Movie is unplayable or ffprobe failed")
        return
        
    duration = float(info.get("format", {}).get("duration", 0.0))
    streams = info.get("streams", [])
    has_video = any(s.get("codec_type") == "video" for s in streams)
    
    print(f"Movie duration: {duration:.2f}s")
    print(f"Has video: {has_video}")
    
    # Verify we had 3 scenes
    scenes = data.get("scenes", [])
    print(f"Number of scenes in storyboard: {len(scenes)}")
    for i, s in enumerate(scenes):
        print(f"  Scene {i+1}: character={s.get('character_name')}, location={s.get('location')}, action={s.get('action')}, mood={s.get('mood')}")
        
    if len(scenes) == 3 and has_video and duration > 0:
        print("PASS: Transition E2E validation completed successfully!")
    else:
        print("FAIL: Expected 3 scenes and valid video stream.")

if __name__ == "__main__":
    main()
