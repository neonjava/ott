import requests
import time

API_URL = "http://127.0.0.1:5001/api/generate-movie"

start = time.time()
resp = requests.post(API_URL, json={"character": "humanoid", "script": "hero walks"})
dur = time.time() - start
print(f"Movie 1 (Init + Render): {dur:.2f}s | {resp.json().get('status')}")

start = time.time()
resp = requests.post(API_URL, json={"character": "humanoid", "script": "hero jumps"})
dur = time.time() - start
print(f"Movie 2 (Daemon Cached): {dur:.2f}s | {resp.json().get('status')}")
