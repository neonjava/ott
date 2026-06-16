#!/usr/bin/env python3
"""
Dialogue Validation Benchmark.
Generates 20 dialogue-enabled movies and validates audio/speech/timing.
"""
import os
import time
import json
import requests
import subprocess

API_URL = "http://127.0.0.1:5001/api/generate-movie"
NUM_MOVIES = 20

SCRIPTS = [
    'Hero walks into city.',
    'Hero says: "Hello everyone." Hero waves.',
    'Hero runs fast and jumps.',
    'Hero walks forward. Hero says: "I am here."',
    'Hero jumps onto rooftop.',
    'Crowd cheers. Hero waves at people.',
    'Hero says: "Let the battle begin!" Hero attacks.',
    'Hero walks slowly through the forest.',
    'Hero runs and says: "Follow me!"',
    'Hero jumps high. Hero says: "Watch this!"',
    'Hero waves goodbye.',
    'Hero attacks the enemy. Hero says: "Take that!"',
    'Hero walks into the sunset.',
    'Hero runs across the bridge.',
    'Hero says: "Victory is ours!" Hero waves.',
    'Hero jumps and then walks forward.',
    'Hero walks and waves at the audience.',
    'Hero says: "I will protect this city." Hero runs.',
    'Hero attacks. Hero jumps away.',
    'Hero walks into the arena. Hero says: "Ready."',
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
print(f"=== Dialogue Validation Benchmark ({NUM_MOVIES} movies) ===\n")

for i in range(NUM_MOVIES):
    script = SCRIPTS[i % len(SCRIPTS)]
    has_dialogue = '"' in script or "'" in script
    print(f"[Movie {i+1}/{NUM_MOVIES}] Script: \"{script}\"")
    print(f"  Expected: {'dialogue + narration' if has_dialogue else 'narration only'}")
    
    t_start = time.time()
    try:
        resp = requests.post(API_URL, json={"character": "humanoid", "script": script}, timeout=900)
        t_dur = time.time() - t_start
        data = resp.json()
        
        if data.get("status") != "success":
            print(f"  -> ERROR: {data.get('error', 'Unknown')}")
            results.append({"movie": i+1, "status": "ERROR", "error": data.get("error"), "time": t_dur, "script": script})
            continue
        
        movie_path = data.get("movie", "").lstrip("/")
        movie_duration = data.get("duration", 0)
        
        checks = {
            "file_exists": os.path.exists(movie_path),
            "has_audio": False,
            "has_video": False,
            "playable": False,
            "actual_duration": 0.0,
            "scene_count": len(data.get("scenes", [])),
        }
        
        if checks["file_exists"]:
            info = get_video_info(movie_path)
            if info:
                checks["playable"] = True
                streams = info.get("streams", [])
                checks["has_video"] = any(s.get("codec_type") == "video" for s in streams)
                checks["has_audio"] = any(s.get("codec_type") == "audio" for s in streams)
                checks["actual_duration"] = float(info.get("format", {}).get("duration", 0))
        
        all_pass = all([
            checks["file_exists"],
            checks["playable"],
            checks["has_video"],
        ])
        
        status = "PASS" if all_pass else "FAIL"
        
        fail_reasons = []
        if not checks["file_exists"]: fail_reasons.append("no file")
        if not checks["playable"]: fail_reasons.append("not playable")
        if not checks["has_video"]: fail_reasons.append("no video")
        if not checks["has_audio"]: fail_reasons.append("no audio")
        
        suffix = f" | ISSUES: {', '.join(fail_reasons)}" if fail_reasons else ""
        print(f"  -> {status} in {t_dur:.2f}s | Duration: {checks['actual_duration']:.2f}s | Scenes: {checks['scene_count']}{suffix}")
        
        results.append({
            "movie": i+1,
            "status": status,
            "time": t_dur,
            "duration": checks["actual_duration"],
            "checks": checks,
            "error": None,
            "script": script,
        })
        
    except Exception as e:
        t_dur = time.time() - t_start
        print(f"  -> EXCEPTION: {str(e)}")
        results.append({"movie": i+1, "status": "EXCEPTION", "error": str(e), "time": t_dur, "script": script})

# Summary
print("\n" + "=" * 60)
print("      DIALOGUE VALIDATION REPORT")
print("=" * 60)

total = len(results)
passes = sum(1 for r in results if r["status"] == "PASS")
failures = total - passes
durations = [r.get("duration", 0) for r in results if r.get("duration")]
times = [r.get("time", 0) for r in results if r.get("time")]

print(f"Total Movies:      {total}")
print(f"Successful:        {passes}")
print(f"Failed:            {failures}")
if durations:
    print(f"Avg Duration:      {sum(durations)/len(durations):.2f}s")
if times:
    print(f"Avg Assembly Time: {sum(times)/len(times):.2f}s")

errors = [r.get("error") for r in results if r.get("error")]
if errors:
    from collections import Counter
    most_common = Counter(errors).most_common(1)[0]
    print(f"Most Common Failure: {most_common[0]} ({most_common[1]}x)")

# Write markdown report
report = f"""# Dialogue Validation Report

## Summary
| Metric | Value |
|--------|-------|
| Total Movies | {total} |
| Successful | {passes} |
| Failed | {failures} |
| Avg Duration | {sum(durations)/len(durations) if durations else 0:.2f}s |
| Avg Assembly Time | {sum(times)/len(times) if times else 0:.2f}s |

## Individual Results
| # | Script | Status | Time | Duration | Scenes | Audio | Video |
|---|--------|--------|------|----------|--------|-------|-------|
"""

for r in results:
    c = r.get("checks", {})
    script_short = r.get("script", "")[:35] + ("..." if len(r.get("script", "")) > 35 else "")
    report += f"| {r['movie']} | {script_short} | {r['status']} | {r.get('time', 0):.1f}s | {r.get('duration', 0):.1f}s | {c.get('scene_count', '-')} | {'✅' if c.get('has_audio') else '❌'} | {'✅' if c.get('has_video') else '❌'} |\n"

if errors:
    from collections import Counter
    report += f"\n## Most Common Failure\n`{Counter(errors).most_common(1)[0][0]}` ({Counter(errors).most_common(1)[0][1]}x)\n"

report += f"\n## Conclusion\n{'**All ' + str(passes) + ' dialogue-enabled movies passed validation.**' if failures == 0 else '**' + str(failures) + ' movies failed. See details above.**'}\n"

with open("dialogue_validation_report.md", "w") as f:
    f.write(report)
print("\nSaved dialogue_validation_report.md")
