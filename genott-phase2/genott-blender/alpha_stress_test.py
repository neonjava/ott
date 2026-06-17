import os
import sys
import time
import requests
import random
import subprocess

API_URL = "http://127.0.0.1:5001/api/generate-movie"
NUM_TESTS = 50

VERBS = ["walk", "run", "jump", "talk", "wave", "attack", "idle"]
DIALOGUES = ["'Greetings!'", "'Take cover!'", "'We must hurry.'", "'Look out!'", ""]

def get_random_script():
    num_actions = random.randint(1, 3)
    actions = random.sample(VERBS, num_actions)
    dialogue = random.choice(DIALOGUES)
    
    script_parts = []
    if dialogue:
        script_parts.append(f"hero says {dialogue} and")
    
    script_parts.append(f"hero {actions[0]}s")
    for i in range(1, len(actions)):
        script_parts.append(f"then {actions[i]}s")
        
    return " ".join(script_parts)

def get_system_metrics():
    # Memory
    mem_cmd = "free -m | awk 'NR==2{printf \"%.2f%%\", $3*100/$2 }'"
    mem_usage = subprocess.check_output(mem_cmd, shell=True).decode('utf-8').strip()
    
    # GPU
    try:
        gpu_cmd = "nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits"
        gpu_usage = subprocess.check_output(gpu_cmd, shell=True).decode('utf-8').strip() + "%"
    except:
        gpu_usage = "N/A"
        
    return mem_usage, gpu_usage

def run_test(test_id, script_text):
    payload = {"character": "humanoid", "script": script_text}
    start_time = time.time()
    mem_before, gpu_before = get_system_metrics()
    
    try:
        resp = requests.post(API_URL, json=payload, timeout=900)
        resp_data = resp.json()
    except Exception as e:
        return False, f"API Failure: {str(e)}", 0, 0
        
    duration = time.time() - start_time
    mem_after, gpu_after = get_system_metrics()
    print(f"    [Metrics] Mem: {mem_before}->{mem_after} | GPU: {gpu_before}->{gpu_after}")
    
    if resp.status_code != 200 or resp_data.get("status") != "success":
        error = resp_data.get("error", "Unknown error") if isinstance(resp_data, dict) else "Non-JSON response"
        return False, f"HTTP {resp.status_code}: {error}", duration, 0
        
    movie_url = resp_data.get("movie")
    movie_path = movie_url.lstrip("/")
    
    if not os.path.exists(movie_path):
        return False, f"Missing File: {movie_path}", duration, 0
        
    quality = resp_data.get("quality", {})
    if quality.get("score", 0) <= 0:
        return False, f"Quality failed: {quality}", duration, 0
        
    if not quality.get("has_audio") or not quality.get("has_video"):
        return False, f"Audio/Video failure: {quality}", duration, 0
        
    movie_duration = quality.get("duration", 0)
    
    return True, "Success", duration, movie_duration

if __name__ == "__main__":
    success_count = 0
    failure_count = 0
    total_render_duration = 0
    total_movie_duration = 0
    failures = []
    
    print(f"--- Starting Alpha Stress Testing ({NUM_TESTS} consecutive generations) ---")
    
    for i in range(NUM_TESTS):
        script = get_random_script()
        print(f"\\n[Test {i+1}/{NUM_TESTS}] Script: '{script}'")
        
        success, msg, duration, movie_dur = run_test(i+1, script)
        
        total_render_duration += duration
        
        if success:
            success_count += 1
            total_movie_duration += movie_dur
            print(f"  -> SUCCESS! (Render: {duration:.2f}s, Movie Dur: {movie_dur:.2f}s)")
        else:
            failure_count += 1
            failures.append(msg)
            print(f"  -> FAILED! (Render: {duration:.2f}s)\\n     Error: {msg}")
            print("  -> ABORTING STRESS TEST ON FIRST FAILURE to allow fixes.")
            break

    print("\\n==================================")
    print("      ALPHA STRESS TEST REPORT    ")
    print("==================================")
    print(f"Target Count:    {NUM_TESTS}")
    print(f"Success Count:   {success_count}")
    print(f"Failure Count:   {failure_count}")
    
    avg_render = total_render_duration / success_count if success_count > 0 else 0
    avg_movie = total_movie_duration / success_count if success_count > 0 else 0
    print(f"Avg Render Time: {avg_render:.2f}s")
    print(f"Avg Movie Dur:   {avg_movie:.2f}s")
    
    if failure_count > 0:
        print(f"Failure Reason:  {failures[-1]}")
        sys.exit(1)
    else:
        print("\\nSTATUS: ALPHA VALIDATION PASSED (50/50 CONSECUTIVE SUCCESS)")
        sys.exit(0)
