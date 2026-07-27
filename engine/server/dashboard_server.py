# engine/server/dashboard_server.py
import os
import sys
import json
import time
import subprocess
from http.server import HTTPServer, SimpleHTTPRequestHandler
import logging

sys.path.insert(0, "PROJECT_ROOT/Documents/LLM/ott")
from engine.prompt_compiler.ollama_optimizer import OllamaPromptOptimizer

logger = logging.getLogger(__name__)

class StudioDashboardHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        if path == "/" or path == "/dashboard":
            return "PROJECT_ROOT/Documents/LLM/ott/frontend/dashboard.html"
        return super().translate_path(path)

    def do_GET(self):
        if self.path == "/api/metrics":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            
            gpu_info = {
                "gpu_model": "NVIDIA GeForce RTX 4060 Laptop GPU",
                "vram_used_mb": 735,
                "vram_total_mb": 8188,
                "gpu_utilization_pct": 0,
                "cpu_utilization_pct": 12,
                "ram_used_gb": 4.2,
                "ram_total_gb": 16.0,
                "is_active_generation": False,
                "latest_frame_url": "/outputs/debug/frame_0001.png"
            }

            # Check if movie generator or python inference is active
            try:
                ps_res = subprocess.run(["ps", "aux"], capture_output=True, text=True)
                if "movie_generator.py" in ps_res.stdout or "ltx" in ps_res.stdout.lower():
                    gpu_info["is_active_generation"] = True
            except Exception:
                pass

            # Query nvidia-smi for VRAM & GPU Utilization
            try:
                cmd = ["nvidia-smi", "--query-gpu=memory.used,memory.total,utilization.gpu,name", "--format=csv,noheader,nounits"]
                res = subprocess.run(cmd, capture_output=True, text=True)
                if res.returncode == 0:
                    parts = [p.strip() for p in res.stdout.strip().split(",")]
                    if len(parts) >= 4:
                        gpu_info["vram_used_mb"] = int(parts[0])
                        gpu_info["vram_total_mb"] = int(parts[1])
                        gpu_info["gpu_utilization_pct"] = int(parts[2])
                        gpu_info["gpu_model"] = parts[3]
                        if gpu_info["gpu_utilization_pct"] > 5:
                            gpu_info["is_active_generation"] = True
            except Exception:
                pass

            # Find latest generated debug frame
            debug_dir = "PROJECT_ROOT/Documents/LLM/ott/outputs/debug"
            if os.path.exists(debug_dir):
                frames = [f for f in os.listdir(debug_dir) if f.startswith("frame_") and f.endswith(".png")]
                if frames:
                    frames.sort()
                    gpu_info["latest_frame_url"] = f"/outputs/debug/{frames[-1]}?t={int(time.time())}"

            self.wfile.write(json.dumps(gpu_info).encode("utf-8"))
            return
        return super().do_GET()

    def do_POST(self):
        if self.path == "/api/generate":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                # Check GPU active generation lock
                ps_res = subprocess.run(["ps", "aux"], capture_output=True, text=True)
                if "movie_generator.py" in ps_res.stdout:
                    self.send_response(429)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    resp = {
                        "status": "LOCKED",
                        "message": "GPU is currently actively generating video clips! Please wait till this generation completes before submitting a new prompt."
                    }
                    self.wfile.write(json.dumps(resp).encode("utf-8"))
                    return

                data = json.loads(body.decode("utf-8"))
                user_prompt = data.get("prompt", "")
                duration = data.get("duration", "30s")

                optimizer = OllamaPromptOptimizer()
                decomp = optimizer.optimize_and_decompose(user_prompt, target_duration=duration)

                script_cmd = f"PYTHONPATH=. python3 engine/director/movie_generator.py --prompt '{user_prompt}' --duration {duration}"
                subprocess.Popen(script_cmd, shell=True, cwd="PROJECT_ROOT/Documents/LLM/ott")

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                resp = {
                    "status": "PROCESSING",
                    "message": f"Story decomposed into {decomp['num_shots']} scenes via Ollama Optimizer. Rendering clips on RTX 4060 GPU...",
                    "decomposition": decomp
                }
                self.wfile.write(json.dumps(resp).encode("utf-8"))
                return
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ERROR", "error": str(e)}).encode("utf-8"))
                return

        return super().do_POST()

def run_server(port: int = 8080):
    os.chdir("PROJECT_ROOT/Documents/LLM/ott")
    server_address = ("", port)
    httpd = HTTPServer(server_address, StudioDashboardHandler)
    logger.info(f"GenOTT Studio Dashboard Server running at http://localhost:{port}/")
    print(f"[✓] Dashboard Web Server active at http://localhost:{port}/")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
