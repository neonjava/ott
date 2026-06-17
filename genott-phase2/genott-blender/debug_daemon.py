import requests
resp = requests.post("http://127.0.0.1:5005/render", json={"output_path": "/tmp/bench_daemon.mp4", "action": "jump", "duration": 2.0})
print(resp.json())
