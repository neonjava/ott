# engine/server/dashboard_server.py
import os
import json
import subprocess
from http.server import HTTPServer, SimpleHTTPRequestHandler
import logging
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
            
            gpu_info = {"gpu_model": "NVIDIA GeForce RTX 4060 Laptop GPU", "vram_used_mb": 735, "vram_total_mb": 8188, "encoder": "h264_nvenc"}
            try:
                cmd = ["nvidia-smi", "--query-gpu=memory.used,memory.total,name", "--format=csv,noheader,nounits"]
                res = subprocess.run(cmd, capture_output=True, text=True)
                if res.returncode == 0:
                    parts = [p.strip() for p in res.stdout.strip().split(",")]
                    if len(parts) >= 3:
                        gpu_info["vram_used_mb"] = int(parts[0])
                        gpu_info["vram_total_mb"] = int(parts[1])
                        gpu_info["gpu_model"] = parts[2]
            except Exception:
                pass

            self.wfile.write(json.dumps(gpu_info).encode("utf-8"))
            return
        return super().do_GET()

    def do_POST(self):
        if self.path == "/api/generate":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode("utf-8"))
                user_prompt = data.get("prompt", "")
                duration = data.get("duration", "30s")

                optimizer = OllamaPromptOptimizer()
                decomp = optimizer.optimize_and_decompose(user_prompt, target_duration=duration)

                # Trigger background generation script
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
