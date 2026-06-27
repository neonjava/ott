#!/usr/bin/env python3
"""
Movie Assembly Validation Benchmark.
Generates 10 movies and validates final_movie.mp4 assembly for each.
"""
import os
import time
import json
import requests
import subprocess

API_URL = "http://127.0.0.1:5001/api/generate-movie"
VIDEO_DIR = "static/videos"
NUM_MOVIES = 10

SCRIPTS = [
    "hero walks forward",
    "hero jumps over obstacle",
    "hero walks and then waves",
    "hero runs fast",
    "hero jumps and then walks",
    "hero waves at crowd",
    "hero walks slowly",
    "hero jumps high",
    "hero runs and waves",
    "hero walks and jumps",
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

results = []
print(f"=== Movie Assembly Validation Benchmark ({NUM_MOVIES} movies) ===\n")

for i in range(NUM_MOVIES):
    script = SCRIPTS[i % len(SCRIPTS)]
    print(f"[Movie {i+1}/{NUM_MOVIES}] Script: \"{script}\"")
    
    t_start = time.time()
    try:
        resp = requests.post(API_URL, json={"character": "humanoid", "script": script}, timeout=900)
        t_dur = time.time() - t_start
        data = resp.json()
        
        if data.get("status") != "success":
            print(f"  -> ERROR: {data.get('error', 'Unknown')}")
            results.append({"movie": i+1, "status": "ERROR", "error": data.get("error", "Unknown"), "time": t_dur})
            continue
        
        movie_path = data.get("movie", "")
        movie_duration = data.get("duration", 0)
        local_path = movie_path.lstrip("/")  # Remove leading /
        
        # Validation checks
        checks = {
            "file_exists": os.path.exists(local_path),
            "duration_reported": movie_duration > 0,
            "video_stream": False,
            "audio_stream": False,
            "playable": False,
            "scene_count": len(data.get("scenes", [])),
        }
        
        if checks["file_exists"]:
            info = get_video_info(local_path)
            if info:
                checks["playable"] = True
                streams = info.get("streams", [])
                checks["video_stream"] = any(s.get("codec_type") == "video" for s in streams)
                checks["audio_stream"] = any(s.get("codec_type") == "audio" for s in streams)
                checks["actual_duration"] = float(info.get("format", {}).get("duration", 0))
        
        all_pass = all([
            checks["file_exists"],
            checks["playable"],
            checks["video_stream"],
        ])
        
        status = "PASS" if all_pass else "FAIL"
        print(f"  -> {status} in {t_dur:.2f}s | Duration: {movie_duration:.2f}s | Scenes: {checks['scene_count']}")
        for k, v in checks.items():
            if not v and k not in ("audio_stream", "actual_duration", "scene_count", "duration_reported"):
                print(f"     FAILED CHECK: {k}")
        
        results.append({
            "movie": i+1,
            "status": status,
            "time": t_dur,
            "duration": movie_duration,
            "checks": checks,
            "error": None
        })
        
    except Exception as e:
        t_dur = time.time() - t_start
        print(f"  -> EXCEPTION: {str(e)}")
        results.append({"movie": i+1, "status": "EXCEPTION", "error": str(e), "time": t_dur})

# Generate Report
print("\n" + "=" * 50)
print("      MOVIE VALIDATION REPORT")
print("=" * 50)

total = len(results)
passes = sum(1 for r in results if r["status"] == "PASS")
failures = total - passes
durations = [r.get("duration", 0) for r in results if r.get("duration")]
times = [r.get("time", 0) for r in results if r.get("time")]

print(f"Total Movies:     {total}")
print(f"Successful:       {passes}")
print(f"Failed:           {failures}")
if durations:
    print(f"Avg Duration:     {sum(durations)/len(durations):.2f}s")
if times:
    print(f"Avg Assembly Time: {sum(times)/len(times):.2f}s")

# Most common failure
errors = [r.get("error") for r in results if r.get("error")]
if errors:
    from collections import Counter
    most_common = Counter(errors).most_common(1)[0]
    print(f"Most Common Failure: {most_common[0]} ({most_common[1]}x)")

# Write markdown report
report = f"""# Movie Validation Report

## Summary
| Metric | Value |
|--------|-------|
| Total Movies | {total} |
| Successful | {passes} |
| Failed | {failures} |
| Avg Duration | {sum(durations)/len(durations) if durations else 0:.2f}s |
| Avg Assembly Time | {sum(times)/len(times) if times else 0:.2f}s |

## Individual Results
| Movie | Status | Time | Duration | Scenes | File | Video | Audio | Playable |
|-------|--------|------|----------|--------|------|-------|-------|----------|
"""

for r in results:
    c = r.get("checks", {})
    report += f"| {r['movie']} | {r['status']} | {r.get('time', 0):.1f}s | {r.get('duration', 0):.1f}s | {c.get('scene_count', '-')} | {'✅' if c.get('file_exists') else '❌'} | {'✅' if c.get('video_stream') else '❌'} | {'✅' if c.get('audio_stream') else '❌'} | {'✅' if c.get('playable') else '❌'} |\n"

if errors:
    report += f"\n## Most Common Failure\n`{Counter(errors).most_common(1)[0][0]}` ({Counter(errors).most_common(1)[0][1]}x)\n"

report += f"\n## Conclusion\n{f'**All {passes} movies passed validation.**' if failures == 0 else f'**{failures} movies failed validation. See details above.**'}\n"

with open("movie_validation_report.md", "w") as f:
    f.write(report)
print("\nSaved movie_validation_report.md")
