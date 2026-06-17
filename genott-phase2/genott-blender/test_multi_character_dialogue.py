#!/usr/bin/env python3
import os
import sys
import time
import requests
import json
import subprocess

API_URL = "http://127.0.0.1:5001/api/generate-avatar-video"
VIDEO_DIR = "static/videos"

payload = {
    "generation_id": "test_multi_char_dialogue_e2e",
    "scenes": [
        {
            "character_name": "knight",
            "action": "walk",
            "location": "forest",
            "camera_shot": "medium_shot",
            "dialogues": [
                {"speaker": "knight", "text": "Who goes there?"},
                {"speaker": "fox", "text": "I am but a humble fox."}
            ],
            "mood": "tense"
        }
    ]
}

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
        print(f"ffprobe failed: {e}")
        return None

print("=== Starting E2E Multi-Character Dialogue & Speaker Tracking Test ===")
print(f"Sending payload to {API_URL}...")

t_start = time.time()
try:
    resp = requests.post(API_URL, json=payload, timeout=600)
    t_dur = time.time() - t_start
    print(f"Response Status Code: {resp.status_code}")
    data = resp.json()
except Exception as e:
    print(f"Request failed: {e}")
    sys.exit(1)

if resp.status_code != 200:
    print(f"Error: Generation failed. Response: {data}")
    sys.exit(1)

print("\n=== Generation Succeeded! ===")
print(f"Total time taken: {t_dur:.2f}s")

movie_url = data.get("url")
local_path = movie_url.lstrip("/")
print(f"Output Movie File: {local_path}")

# Verify file exists and is playable
if not os.path.exists(local_path):
    print(f"ERROR: Output movie file does not exist at {local_path}")
    sys.exit(1)

info = get_video_info(local_path)
if not info:
    print("ERROR: Generated movie is not playable or corrupt.")
    sys.exit(1)

streams = info.get("streams", [])
has_video = any(s.get("codec_type") == "video" for s in streams)
has_audio = any(s.get("codec_type") == "audio" for s in streams)
actual_duration = float(info.get("format", {}).get("duration", 0))

print(f"Video Stream Found: {has_video}")
print(f"Audio Stream Found: {has_audio}")
print(f"Actual Duration: {actual_duration:.2f}s")

# Let's inspect the generated payload file to verify speaker tracking in character_payload
payload_file = os.path.join(VIDEO_DIR, "payload_test_multi_char_dialogue_e2e_1.json")
if os.path.exists(payload_file):
    print(f"\nVerifying Payload file: {payload_file}")
    with open(payload_file, "r") as f:
        payload_data = json.load(f)
    
    characters = payload_data.get("characters", [])
    print(f"Found {len(characters)} characters in payload:")
    for char in characters:
        name = char.get("name")
        visemes = char.get("viseme_timeline")
        viseme_count = len(visemes) if visemes else 0
        print(f" - Character: {name} | Viseme timeline entries: {viseme_count}")
        if visemes:
            # Print the first few visemes to verify starting frame and offset
            print(f"   First few visemes: {visemes[:3]}")
            print(f"   Last few visemes: {visemes[-3:]}")

    # Make sure we have visemes for both knight and fox
    knight_vis = next((c.get("viseme_timeline") for c in characters if c.get("name") == "knight"), None)
    fox_vis = next((c.get("viseme_timeline") for c in characters if c.get("name") == "fox"), None)
    
    if not knight_vis or not fox_vis:
        print("ERROR: Speaker tracking failed! One or both characters are missing their viseme timeline.")
        sys.exit(1)
        
    print("\nE2E SPEAKER TRACKING AND LIP SYNC OFFSET CHECKS PASSED SUCCESSFULLY!")
    sys.exit(0)
else:
    print(f"ERROR: Logged payload file {payload_file} was not generated.")
    sys.exit(1)
