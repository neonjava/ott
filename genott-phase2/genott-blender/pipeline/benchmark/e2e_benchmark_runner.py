#!/usr/bin/env python3
import os
import time
import requests
import json

API_URL = "http://127.0.0.1:5001/api/generate-movie"
NUM_MOVIES = 100

# 100 diverse scripts across 5 genres (20 each)
SCRIPTS = []

GENRES = ["fantasy", "anime", "action", "adventure", "mystery"]

# Template blocks to expand to 100
FANTASY_TEMPLATES = [
    "knight walks through the forest. FADE TO BLACK. knight attacks inside the cave.",
    "mage says 'behold the fire magic' in the castle.",
    "queen waves from the castle wall. FADE TO BLACK. queen walks into the throne room.",
    "hero runs fast through the forest.",
    "dragon attacks in the ruins. FADE TO BLACK. hero ducks behind a stone.",
    "elf walks slowly in the forest. FADE TO BLACK. elf shoots an arrow.",
    "king says 'welcome to our kingdom' in the castle.",
    "knight stands victorious on the mountain. FADE TO BLACK. knight walks into the castle.",
    "orc runs quickly in the cave.",
    "wizard stands idle in the library."
]

ANIME_TEMPLATES = [
    "anime_girl waves cheerfully on the beach. FADE TO BLACK. anime_girl jumps into the cave.",
    "anime_boy says 'we must defeat them' in the city.",
    "ninja runs on the rooftops. FADE TO BLACK. ninja attacks the enemy.",
    "samurai jumps high in the field.",
    "school_girl walks home in the city. FADE TO BLACK. school_girl waves goodbye.",
    "spirit floats in the forest. FADE TO BLACK. spirit disappears.",
    "sensei says 'focus your energy' in the dojo.",
    "fighter punches the air in the arena. FADE TO BLACK. fighter stands victorious.",
    "robot walks slowly in the desert.",
    "anime_girl stands still in the village."
]

ACTION_TEMPLATES = [
    "soldier runs through the ruins. FADE TO BLACK. soldier fires a weapon.",
    "commander says 'move out now' in the base.",
    "cyborg jumps off the building. FADE TO BLACK. cyborg attacks in the city.",
    "spy runs fast in the alley.",
    "assassin walks silently in the shadows. FADE TO BLACK. assassin strikes.",
    "rebel throws a grenade in the arena. FADE TO BLACK. rebel runs to safety.",
    "agent says 'the package is secure' in the warehouse.",
    "fighter kicks the target in the gym. FADE TO BLACK. fighter waves to coach.",
    "hero jumps over the fire in the factory.",
    "cop stands guard in the city."
]

ADVENTURE_TEMPLATES = [
    "explorer walks in the jungle. FADE TO BLACK. explorer climbs the cliff.",
    "guide says 'follow the path' in the mountains.",
    "archaeologist finds the relic in the cave. FADE TO BLACK. archaeologist runs away.",
    "scout runs from the boulder in the ruins.",
    "pirate waves from the ship. FADE TO BLACK. pirate digs for treasure.",
    "traveler walks on the beach. FADE TO BLACK. traveler watches the sunset.",
    "captain says 'steer west' in the sea.",
    "adventurer jumps across the canyon. FADE TO BLACK. adventurer stands proud.",
    "boy runs through the village.",
    "hiker stands on the mountain peak."
]

MYSTERY_TEMPLATES = [
    "detective walks in the rain. FADE TO BLACK. detective examines the clue.",
    "suspect says 'it wasn't me' in the parlor.",
    "thief runs from the museum. FADE TO BLACK. thief hides in the alley.",
    "witness runs in panic in the street.",
    "sleuth finds the secret door. FADE TO BLACK. sleuth walks inside.",
    "informant whispers in the park. FADE TO BLACK. informant runs away.",
    "butler says 'dinner is served' in the manor.",
    "shadowy_figure walks in the fog. FADE TO BLACK. shadowy_figure attacks.",
    "detective jumps into the car.",
    "stranger stands idle in the library."
]

# Create 100 entries by slightly modifying templates to ensure uniqueness
for i in range(20):
    idx = i % len(FANTASY_TEMPLATES)
    SCRIPTS.append({"genre": "fantasy", "script": FANTASY_TEMPLATES[idx].replace("knight", f"knight_{i+1}").replace("mage", f"mage_{i+1}")})
    SCRIPTS.append({"genre": "anime", "script": ANIME_TEMPLATES[idx].replace("anime_girl", f"anime_girl_{i+1}").replace("anime_boy", f"anime_boy_{i+1}")})
    SCRIPTS.append({"genre": "action", "script": ACTION_TEMPLATES[idx].replace("soldier", f"soldier_{i+1}").replace("spy", f"spy_{i+1}")})
    SCRIPTS.append({"genre": "adventure", "script": ADVENTURE_TEMPLATES[idx].replace("explorer", f"explorer_{i+1}").replace("traveler", f"traveler_{i+1}")})
    SCRIPTS.append({"genre": "mystery", "script": MYSTERY_TEMPLATES[idx].replace("detective", f"detective_{i+1}").replace("thief", f"thief_{i+1}")})

def main():
    print(f"=== End-to-End Movie Test Benchmark ({NUM_MOVIES} movies) ===\n")
    results = []
    
    # Trackers for failure categories
    failures = {
        "render": 0,
        "blender": 0,
        "ffmpeg": 0,
        "audio": 0,
        "transition": 0,
        "continuity": 0
    }
    
    t_start_all = time.time()
    
    for i in range(NUM_MOVIES):
        item = SCRIPTS[i]
        script = item["script"]
        genre = item["genre"]
        print(f"[Movie {i+1}/{NUM_MOVIES}] Genre: {genre.upper()} | Script: \"{script}\"")
        
        t_start = time.time()
        try:
            resp = requests.post(API_URL, json={"character": "humanoid", "script": script}, timeout=350)
            t_dur = time.time() - t_start
            
            if resp.status_code != 200:
                print(f"  -> ERROR: HTTP {resp.status_code}")
                # Analyze failure type
                if resp.status_code == 500:
                    failures["blender"] += 1
                    err_type = "blender"
                else:
                    failures["render"] += 1
                    err_type = "render"
                results.append({"id": i+1, "genre": genre, "script": script, "status": "FAIL", "error": f"HTTP {resp.status_code}", "err_type": err_type, "time": t_dur})
                continue
                
            data = resp.json()
            if data.get("status") != "success":
                err_msg = data.get("error", "")
                print(f"  -> ERROR: {err_msg}")
                # Categorize API error
                if "Assembly" in err_msg or "concat" in err_msg:
                    failures["ffmpeg"] += 1
                    err_type = "ffmpeg"
                elif "Voice" in err_msg or "Audio" in err_msg:
                    failures["audio"] += 1
                    err_type = "audio"
                elif "transition" in err_msg:
                    failures["transition"] += 1
                    err_type = "transition"
                else:
                    failures["blender"] += 1
                    err_type = "blender"
                results.append({"id": i+1, "genre": genre, "script": script, "status": "FAIL", "error": err_msg, "err_type": err_type, "time": t_dur})
                continue
                
            duration = data.get("duration", 0)
            quality = data.get("quality", {})
            score = quality.get("score", 0)
            status = quality.get("status", "rejected")
            metrics = quality.get("metrics", {})
            reasons = quality.get("reasons", [])
            
            # Check for continuity warnings in reasons
            has_continuity_issue = any("continuity" in r.lower() for r in reasons)
            if has_continuity_issue:
                failures["continuity"] += 1
                
            print(f"  -> PASS in {t_dur:.2f}s | Quality Score: {score}/100 ({status.upper()})")
            results.append({
                "id": i+1,
                "genre": genre,
                "script": script,
                "status": "PASS" if status == "passed" else "REJECT",
                "score": score,
                "time": t_dur,
                "duration": duration,
                "metrics": metrics,
                "reasons": reasons
            })
            
        except Exception as e:
            t_dur = time.time() - t_start
            print(f"  -> EXCEPTION: {e}")
            failures["render"] += 1
            results.append({"id": i+1, "genre": genre, "script": script, "status": "FAIL", "error": str(e), "err_type": "render", "time": t_dur})
            
    total_dur = time.time() - t_start_all
    
    # Calculate Metrics
    total = len(results)
    passes = sum(1 for r in results if r["status"] == "PASS")
    pipeline_failures = sum(1 for r in results if r["status"] == "FAIL")
    rejects = sum(1 for r in results if r["status"] == "REJECT")
    
    success_rate = (passes / total) * 100 if total > 0 else 0
    avg_duration = sum(r.get("duration", 0) for r in results if "duration" in r) / passes if passes > 0 else 0
    avg_render_time = sum(r.get("time", 0) for r in results) / total if total > 0 else 0
    avg_quality_score = sum(r.get("score", 0) for r in results if "score" in r) / total if total > 0 else 0
    
    # Identify most common failure
    failure_counts = {k: v for k, v in failures.items() if v > 0}
    if failure_counts:
        most_common_failure = max(failure_counts, key=failure_counts.get)
    else:
        most_common_failure = "None"
        
    # Generate final_benchmark_report.md
    report_content = f"""# Final Benchmark Report (100 Movies E2E Test)

## Core Metrics
| Metric | Value |
|--------|-------|
| Success Rate | {success_rate:.1f}% |
| Total Movies Run | {total} |
| Successful Generations | {passes} |
| Quality Engine Rejections | {rejects} |
| Pipeline Failures | {pipeline_failures} |
| Average Movie Duration | {avg_duration:.2f}s |
| Average Render Time | {avg_render_time:.2f}s |
| Average Quality Score | {avg_quality_score:.1f}/100 |
| Most Common Failure | {most_common_failure.upper()} |
| Total Benchmark Time | {total_dur:.2f}s |

## Failure Category Breakdown
| Category | Failures Tracked | Description |
|----------|------------------|-------------|
| Render Failures | {failures['render']} | General exceptions, network timeouts, unhandled crashes |
| Blender Failures | {failures['blender']} | Blender daemon crashes, scene building errors |
| FFmpeg Failures | {failures['ffmpeg']} | Stitching / concatenation / audio merge failures |
| Audio Failures | {failures['audio']} | Edge-TTS speech generation problems |
| Transition Failures | {failures['transition']} | Invalid transition processing between scenes |
| Continuity Failures | {failures['continuity']} | Scene continuity or character matching discrepancies |

## Genre Analysis
| Genre | Runs | Success Rate | Average Score | Avg Render Time |
|-------|------|--------------|---------------|-----------------|
"""
    for g in GENRES:
        g_res = [r for r in results if r["genre"] == g]
        if g_res:
            g_total = len(g_res)
            g_passes = sum(1 for r in g_res if r["status"] == "PASS")
            g_avg = sum(r.get("score", 0) for r in g_res if "score" in r) / g_total
            g_render = sum(r.get("time", 0) for r in g_res) / g_total
            g_rate = (g_passes / g_total) * 100
            report_content += f"| {g.upper()} | {g_total} | {g_rate:.1f}% | {g_avg:.1f}/100 | {g_render:.2f}s |\n"

    report_content += """
## Detailed Logs (First 30 runs shown)
| ID | Genre | Status | Quality Score | Duration | Render Time | Error / Failure Type |
|----|-------|--------|---------------|----------|-------------|----------------------|
"""
    for r in results[:30]:
        err = r.get("error") or r.get("err_type") or "None"
        report_content += f"| {r['id']} | {r['genre'].upper()} | {r['status']} | {r.get('score', 'N/A')} | {r.get('duration', 0.0):.2f}s | {r['time']:.2f}s | {err} |\n"
        
    with open("final_benchmark_report.md", "w") as f:
        f.write(report_content)
    print("\nSaved final_benchmark_report.md")
    
    # Sync to Documents/md
    md_dir = "PROJECT_ROOT/Documents/md"
    os.makedirs(md_dir, exist_ok=True)
    with open(os.path.join(md_dir, "final_benchmark_report.md"), "w") as f:
        f.write(report_content)
        
    # Sync to brain artifact directory
    artifact_dir = "PROJECT_ROOT/.gemini/antigravity-cli/brain/3496fc80-3ea9-4817-8bc4-b4e0e2ff7b60"
    with open(os.path.join(artifact_dir, "final_benchmark_report.md"), "w") as f:
        f.write(report_content)
    print("Reports successfully synchronized across directories.")

if __name__ == "__main__":
    main()
