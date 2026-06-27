import requests
import json
import time
import sys

URL = "http://localhost:5000"

def test_avatar_pipeline(avatar_choice="tony_stark"):
    print(f"\n🚀 Starting test pipeline for avatar: {avatar_choice}...")
    
    # 1. Generate Storyboard Script
    print("[*] Generating storyboard script from Ollama...")
    res = requests.post(f"{URL}/api/generate-avatar-script", json={"avatar": avatar_choice})
    if res.status_code != 200:
        print(f"❌ Script generation failed: {res.text}")
        return
        
    script_data = res.json()
    print(f"✓ Storyboard generated: \"{script_data.get('title')}\"")
    print(json.dumps(script_data, indent=2))
    
    # 2. Render and Stitch 30-Second Video
    print("\n[*] Sending storyboard to render engine (rendering 6 segments)...")
    gen_id = f"test_run_{int(time.time())}"
    
    # Start background polling thread or simulate polling in a loop
    payload = {
        "scenes": script_data.get("scenes", []),
        "generation_id": gen_id
    }
    
    # Trigger generation
    video_res = requests.post(f"{URL}/api/generate-avatar-video", json=payload)
    if video_res.status_code != 200:
        print(f"❌ Video rendering failed: {video_res.text}")
        return
        
    video_data = video_res.json()
    print("\n🎉 VIDEO RENDERED SUCCESSFUL!")
    print(f"🎬 Video Duration: {video_data.get('duration_sec')} seconds")
    print(f"🔗 Access the final stitched video here: {URL}{video_data.get('url')}")
    print(f"💾 File saved on disk as: {video_data.get('filename')}")

if __name__ == "__main__":
    choice = "tony_stark"
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    test_avatar_pipeline(choice)
