import requests
import time
print("Render 1")
requests.post("http://127.0.0.1:5005/render", json={"output_path": "/tmp/bench1.mp4", "action": "idle", "duration": 0.1})
print("Render 2")
requests.post("http://127.0.0.1:5005/render", json={"output_path": "/tmp/bench2.mp4", "action": "walk", "duration": 0.1})
