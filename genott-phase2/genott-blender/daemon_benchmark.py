import os
import time
import requests
import subprocess

API_URL = "http://127.0.0.1:5001/api/generate-movie"
NUM_MOVIES = 10

def get_system_metrics():
    try:
        mem_cmd = "free -m | awk 'NR==2{printf \"%.2f%%\", $3*100/$2 }'"
        mem_usage = subprocess.check_output(mem_cmd, shell=True).decode('utf-8').strip()
    except: mem_usage = "N/A"
    
    try:
        gpu_cmd = "nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader,nounits"
        out = subprocess.check_output(gpu_cmd, shell=True).decode('utf-8').strip().split(',')
        gpu_usage = f"{out[0].strip()}%"
        vram_usage = f"{out[1].strip()} MB"
    except:
        gpu_usage = "N/A"
        vram_usage = "N/A"
        
    return mem_usage, gpu_usage, vram_usage

print(f"--- Starting Daemon Architecture Benchmark ({NUM_MOVIES} iterations) ---")
time.sleep(2)

results = []
for i in range(1, NUM_MOVIES + 1):
    print(f"\\n[Movie {i}/{NUM_MOVIES}] Sending request...")
    
    action = "walk" if i % 2 == 0 else "jump"
    payload = {"character": "humanoid", "script": f"hero {action}s"}
    
    mem_before, gpu_before, vram_before = get_system_metrics()
    
    start_time = time.time()
    try:
        resp = requests.post(API_URL, json=payload, timeout=900)
        dur = time.time() - start_time
        data = resp.json()
        status = data.get("status", "error")
        error_msg = data.get("error", "Unknown error")
        
        mem_after, gpu_after, vram_after = get_system_metrics()
        
        if status == "success":
            print(f"  -> SUCCESS in {dur:.2f}s | Mem: {mem_after} | GPU: {gpu_after} | VRAM: {vram_after}")
            results.append(dur)
        else:
            print(f"  -> ERROR: {error_msg}")
            results.append(-1)
    except Exception as e:
        print(f"  -> FAILED: {str(e)}")
        results.append(-1)

print("\\n==================================")
print("      DAEMON ARCHITECTURE REPORT  ")
print("==================================")
for i, d in enumerate(results):
    print(f"Clip {i+1}: {d:.2f}s")

successes = [r for r in results if r > 0]
if len(successes) > 1:
    avg_cached = sum(successes[1:]) / len(successes[1:])
    print(f"\\nAverage Cached Render Time: {avg_cached:.2f}s")
    
    if avg_cached < 10.0:
        print("STATUS: TARGET MET (< 10s per cached render)")
    else:
        print("STATUS: CACHE FAILED OR TOO SLOW")
