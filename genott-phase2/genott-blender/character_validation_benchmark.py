#!/usr/bin/env python3
"""
Character Validation Benchmark.
Generates 5 movies per required character and validates rendering, loading, voice, and audio/video outputs.
"""
import os
import time
import json
import requests
import subprocess

CHARACTERS_API = "http://127.0.0.1:5001/api/characters"
GENERATE_API = "http://127.0.0.1:5001/api/generate-movie"

# Required characters
REQUIRED_CHARACTERS = ["anime_girl", "anime_boy", "knight", "mage", "robot"]

# 5 scripts per character (placeholder replaced dynamically)
SCRIPT_TEMPLATES = [
    '{character} walks forward.',
    '{character} says: "Greetings traveler."',
    '{character} waves to the crowd.',
    '{character} jumps high and attacks.',
    '{character} runs and then says: "We must keep moving!"'
]

def get_video_info(filepath):
    try:
        cmd = [
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration:stream=codec_name,codec_type",
            "-of", "json", filepath
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except:
        return None

def main():
    print("=== Character Validation Benchmark ===\n")
    
    # 1. Fetch registry/characters to verify GET /api/characters
    try:
        resp = requests.get(CHARACTERS_API, timeout=10)
        resp.raise_for_status()
        characters_list = resp.json()
        registered_ids = [c["id"] for c in characters_list]
        print(f"Registered characters: {registered_ids}")
    except Exception as e:
        print(f"Failed to fetch characters metadata API: {e}")
        registered_ids = REQUIRED_CHARACTERS

    # Load character_registry.json to compare voice profiles
    project_dir = os.path.dirname(os.path.abspath(__file__))
    registry_path = os.path.join(project_dir, "character_registry.json")
    with open(registry_path, "r") as f:
        registry = json.load(f)

    results = []
    missing_assets = []
    render_failures = 0
    total_generated = 0
    total_succeeded = 0

    # Verify asset existence before rendering
    for char_id in REQUIRED_CHARACTERS:
        if char_id not in registry:
            missing_assets.append(f"Character {char_id} not in registry")
            continue
        char_info = registry[char_id]
        model_name = char_info.get("model")
        model_path = os.path.join(project_dir, "assets", "characters", model_name)
        if not os.path.exists(model_path) or os.path.getsize(model_path) < 100:
            missing_assets.append(f"Missing model asset {model_name} for {char_id}")
        
        face_path = os.path.join(project_dir, "static", "faces", f"{char_id}.png")
        if not os.path.exists(face_path):
            missing_assets.append(f"Missing face asset {char_id}.png")

    print(f"Asset existence verification: {'OK' if not missing_assets else 'FAIL'}")
    if missing_assets:
        print(f"Missing assets detail: {missing_assets}")

    for char_id in REQUIRED_CHARACTERS:
        if char_id not in registered_ids:
            print(f"Skipping {char_id} since it's not registered by API.")
            continue
            
        print(f"\n--- Testing Character: {char_id.upper()} ---")
        expected_voice = registry[char_id].get("voice")
        
        for idx, temp in enumerate(SCRIPT_TEMPLATES):
            script = temp.format(character=char_id.replace("_", " ").title())
            print(f"[Movie {idx+1}/5] Generating for {char_id} with script: \"{script}\"")
            
            t_start = time.time()
            total_generated += 1
            try:
                payload = {"character": char_id, "script": script}
                resp = requests.post(GENERATE_API, json=payload, timeout=900)
                t_dur = time.time() - t_start
                
                if resp.status_code != 200:
                    print(f"  -> HTTP ERROR {resp.status_code}: {resp.text}")
                    results.append({
                        "character": char_id,
                        "script": script,
                        "status": "FAIL",
                        "error": f"HTTP {resp.status_code}",
                        "time": t_dur
                    })
                    render_failures += 1
                    continue
                    
                data = resp.json()
                if data.get("status") != "success":
                    print(f"  -> RENDER FAIL: {data.get('error')}")
                    results.append({
                        "character": char_id,
                        "script": script,
                        "status": "FAIL",
                        "error": data.get("error"),
                        "time": t_dur
                    })
                    render_failures += 1
                    continue
                
                # Verify video file
                movie_path = data.get("movie", "").lstrip("/")
                movie_exists = os.path.exists(movie_path)
                
                playable = False
                has_video = False
                has_audio = False
                actual_duration = 0.0
                
                if movie_exists:
                    info = get_video_info(movie_path)
                    if info:
                        playable = True
                        streams = info.get("streams", [])
                        has_video = any(s.get("codec_type") == "video" for s in streams)
                        has_audio = any(s.get("codec_type") == "audio" for s in streams)
                        actual_duration = float(info.get("format", {}).get("duration", 0))
                
                # Verify voice assignment in scenes
                voice_correct = True
                scenes = data.get("scenes", [])
                dialogue_found = False
                for scene in scenes:
                    diag = scene.get("dialogue")
                    if diag:
                        dialogue_found = True
                        assigned_voice = diag.get("voice_profile")
                        if assigned_voice != expected_voice:
                            voice_correct = False
                            print(f"  -> VOICE MISMATCH: expected {expected_voice}, got {assigned_voice}")
                
                # Check if dialogue script actually had dialogue, and voice matched
                has_dialogue_in_script = '"' in script
                voice_status = "PASS"
                if has_dialogue_in_script and not dialogue_found:
                    voice_status = "FAIL (No dialogue parsed)"
                elif has_dialogue_in_script and not voice_correct:
                    voice_status = "FAIL (Voice mismatch)"
                
                all_pass = all([
                    movie_exists,
                    playable,
                    has_video,
                    has_audio,
                    voice_status == "PASS" if has_dialogue_in_script else True
                ])
                
                status = "PASS" if all_pass else "FAIL"
                if all_pass:
                    total_succeeded += 1
                    
                fail_reasons = []
                if not movie_exists: fail_reasons.append("no file")
                if not playable: fail_reasons.append("not playable")
                if not has_video: fail_reasons.append("no video")
                if not has_audio: fail_reasons.append("no audio")
                if voice_status != "PASS" if has_dialogue_in_script else False:
                    fail_reasons.append(voice_status)
                    
                suffix = f" | ISSUES: {', '.join(fail_reasons)}" if fail_reasons else ""
                print(f"  -> {status} in {t_dur:.2f}s | Duration: {actual_duration:.2f}s{suffix}")
                
                results.append({
                    "character": char_id,
                    "script": script,
                    "status": status,
                    "time": t_dur,
                    "duration": actual_duration,
                    "has_audio": has_audio,
                    "has_video": has_video,
                    "voice_assigned": expected_voice if dialogue_found else "N/A (Narration)",
                    "voice_status": voice_status,
                    "error": None
                })
                
            except Exception as e:
                t_dur = time.time() - t_start
                print(f"  -> EXCEPTION: {str(e)}")
                results.append({
                    "character": char_id,
                    "script": script,
                    "status": "FAIL",
                    "error": str(e),
                    "time": t_dur
                })
                render_failures += 1

    # Print summary
    success_rate = (total_succeeded / total_generated * 100) if total_generated > 0 else 0
    print("\n" + "=" * 60)
    print("      CHARACTER VALIDATION REPORT")
    print("=" * 60)
    print(f"Characters tested: {len(REQUIRED_CHARACTERS)}")
    print(f"Movies generated:  {total_generated}")
    print(f"Success rate:      {success_rate:.2f}%")
    print(f"Missing assets:    {len(missing_assets)}")
    print(f"Render failures:   {render_failures}")
    print("=" * 60)

    # Generate character_validation_report.md
    report_md = f"""# Character Validation Report

## Metrics
| Metric | Value |
|--------|-------|
| Characters Tested | {len(REQUIRED_CHARACTERS)} |
| Movies Generated | {total_generated} |
| Success Rate | {success_rate:.2f}% |
| Missing Assets | {len(missing_assets)} |
| Render Failures | {render_failures} |

### Missing Assets Detail
{chr(10).join(f"- {a}" for a in missing_assets) if missing_assets else "None"}

## Individual Character Test Results
| Character | Script | Status | Time | Duration | Audio | Video | Voice Status |
|-----------|--------|--------|------|----------|-------|-------|--------------|
"""

    for r in results:
        script_short = r.get("script", "")[:35] + ("..." if len(r.get("script", "")) > 35 else "")
        report_md += f"| {r['character']} | {script_short} | {r['status']} | {r.get('time', 0):.1f}s | {r.get('duration', 0):.1f}s | {'✅' if r.get('has_audio') else '❌'} | {'✅' if r.get('has_video') else '❌'} | {r.get('voice_status', 'N/A')} |\n"

    report_md += f"\n## Conclusion\n{'**All characters generate movies successfully and voices were mapped correctly.**' if success_rate == 100 else '**Validation failed. Some characters or scripts failed to generate properly.**'}\n"

    with open("character_validation_report.md", "w") as f:
        f.write(report_md)
    print("\nSaved character_validation_report.md")

if __name__ == "__main__":
    main()
