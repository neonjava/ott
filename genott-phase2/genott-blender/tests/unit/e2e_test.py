import os
import sys
import time
import requests
import json
import sqlite3

API_URL = "http://127.0.0.1:5001/api/generate-movie"
DB_PATH = "sqlite.db"
NUM_TESTS = 5

SCRIPTS = [
    "hero says 'For Asgard!' and leaps",
    "hero stands still and looks around",
    "hero walks slowly, waves, then attacks",
    "hero says 'Let's fly' and jumps into the air",
    "hero raises weapon and strikes"
]

def reset_db():
    print("[E2E] Resetting database...")
    if os.path.exists(DB_PATH):
        try:
            # Let's not delete the DB outright as Flask holds a lock, but we can clear tables if needed
            # For a true fresh state, the API endpoints just create new generations so it shouldn't conflict.
            pass
        except Exception as e:
            print(f"[E2E] Error resetting DB: {e}")

def run_test(test_id, script_text):
    payload = {
        "character": "humanoid",
        "script": script_text
    }
    
    start_time = time.time()
    try:
        resp = requests.post(API_URL, json=payload, timeout=600)
        resp_data = resp.json()
    except Exception as e:
        return False, str(e), 0
        
    duration = time.time() - start_time
    
    if resp.status_code != 200 or resp_data.get("status") != "success":
        error = resp_data.get("error", "Unknown error") if isinstance(resp_data, dict) else "Non-JSON response"
        return False, f"HTTP {resp.status_code}: {error}", duration
        
    movie_url = resp_data.get("movie")
    movie_path = movie_url.lstrip("/")  # Relative path to check existence
    
    if not os.path.exists(movie_path):
        return False, f"Movie file missing: {movie_path}", duration
        
    quality = resp_data.get("quality", {})
    if quality.get("score", 0) <= 0:
        return False, f"Quality score failed or 0: {quality}", duration
        
    storyboards = resp_data.get("storyboard", [])
    if not storyboards:
        return False, "Storyboard missing", duration
        
    for sb in storyboards:
        sb_path = sb.lstrip("/")
        if not os.path.exists(sb_path):
            return False, f"Storyboard file missing: {sb_path}", duration
            
    return True, "Success", duration

if __name__ == "__main__":
    reset_db()
    
    success_count = 0
    failure_count = 0
    total_duration = 0
    
    print(f"--- Starting E2E Pipeline Testing ({NUM_TESTS} consecutive generations) ---")
    
    for i in range(NUM_TESTS):
        print(f"\\n[Test {i+1}/{NUM_TESTS}] Generating movie: '{SCRIPTS[i]}'")
        success, msg, duration = run_test(i+1, SCRIPTS[i])
        
        total_duration += duration
        
        if success:
            success_count += 1
            print(f"  -> SUCCESS! (Took {duration:.2f}s)")
        else:
            failure_count += 1
            print(f"  -> FAILED! (Took {duration:.2f}s)\\n     Error: {msg}")
            break

    print("\\n==================================")
    print("        E2E TEST REPORT           ")
    print("==================================")
    print(f"Test Count:      {i+1}")
    print(f"Success Count:   {success_count}")
    print(f"Failure Count:   {failure_count}")
    avg_render = total_duration / (i+1) if (i+1) > 0 else 0
    print(f"Avg Render Time: {avg_render:.2f}s")
    
    if failure_count > 0:
        print("\\nSTATUS: FAILED")
        sys.exit(1)
    else:
        print("\\nSTATUS: MVP PASSED (5/5 CONSECUTIVE SUCCESS)")
        sys.exit(0)
