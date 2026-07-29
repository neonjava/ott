# engine/server/dashboard_server.py
import os
import sys
import json
import time
import subprocess
import logging
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn

sys.path.insert(0, "PROJECT_ROOT/Documents/LLM/ott")
from engine.prompt_compiler.ollama_optimizer import OllamaPromptOptimizer

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)

OTT_ROOT = "PROJECT_ROOT/Documents/LLM/ott"

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """Threaded HTTP server so polling + POST don't block each other."""
    daemon_threads = True

class StudioDashboardHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress noisy frame polling logs, only show important ones
        msg = format % args
        if "/api/metrics" not in msg and "frame_" not in msg:
            logger.info("HTTP %s", msg)

    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def translate_path(self, path):
        # Route root → dashboard HTML
        if path in ("/", "/dashboard"):
            return os.path.join(OTT_ROOT, "frontend/dashboard.html")
        # Serve static files from OTT_ROOT
        rel = path.lstrip("/")
        return os.path.join(OTT_ROOT, rel)

    def do_GET(self):
        if self.path == "/api/metrics":
            self._handle_metrics()
            return
        return super().do_GET()

    def _handle_metrics(self):
        gpu_info = {
            "gpu_model": "NVIDIA GeForce RTX 4060 Laptop GPU",
            "vram_used_mb": 735,
            "vram_total_mb": 8188,
            "gpu_utilization_pct": 0,
            "cpu_utilization_pct": 12,
            "ram_used_gb": 4.2,
            "ram_total_gb": 16.0,
            "is_active_generation": False,
            "latest_frame_url": None  # No default — only set when a real frame exists
        }

        # Check active generation via process list — only match actual Python generation scripts
        try:
            ps_res = subprocess.run(["ps", "aux"], capture_output=True, text=True, timeout=3)
            generation_scripts = [
                "movie_generator.py",
                "wo0021_human_story_runner.py",
                "wo0020_nature_film_runner.py",
                "wo0019_continuity_runner.py",
            ]
            for script in generation_scripts:
                if script in ps_res.stdout:
                    gpu_info["is_active_generation"] = True
                    break
        except Exception:
            pass

        # Real GPU stats via nvidia-smi
        try:
            cmd = ["nvidia-smi", "--query-gpu=memory.used,memory.total,utilization.gpu,name",
                   "--format=csv,noheader,nounits"]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=4)
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

        # Real CPU / RAM via psutil if available
        try:
            import psutil
            gpu_info["cpu_utilization_pct"] = psutil.cpu_percent(interval=0.2)
            vm = psutil.virtual_memory()
            gpu_info["ram_used_gb"] = round(vm.used / (1024**3), 1)
            gpu_info["ram_total_gb"] = round(vm.total / (1024**3), 1)
        except Exception:
            pass

        # Latest generated debug frame
        debug_dir = os.path.join(OTT_ROOT, "outputs/debug")
        if os.path.exists(debug_dir):
            frames = sorted(
                f for f in os.listdir(debug_dir)
                if f.startswith("frame_") and f.endswith(".png")
            )
            if frames:
                gpu_info["latest_frame_url"] = f"/outputs/debug/{frames[-1]}?t={int(time.time())}"

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self._send_cors_headers()
        self.end_headers()
        try:
            self.wfile.write(json.dumps(gpu_info).encode("utf-8"))
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_POST(self):
        if self.path == "/api/generate":
            self._handle_generate()
            return
        return super().do_POST()

    def _handle_generate(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        try:
            # GPU active generation lock
            try:
                ps_res = subprocess.run(["ps", "aux"], capture_output=True, text=True, timeout=3)
                if "movie_generator.py" in ps_res.stdout:
                    self.send_response(429)
                    self.send_header("Content-Type", "application/json")
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "status": "LOCKED",
                        "message": "⚠️ GPU is currently generating! Please wait until the current generation finishes before submitting a new prompt."
                    }).encode("utf-8"))
                    return
            except Exception:
                pass

            data = json.loads(body.decode("utf-8"))
            user_prompt = data.get("prompt", "").strip()
            duration = data.get("duration", "30s")

            if not user_prompt:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ERROR", "error": "Empty prompt"}).encode("utf-8"))
                return

            logger.info("[Web UI Request] Optimizing prompt via Ollama for %s...", duration)

            optimizer = OllamaPromptOptimizer()
            decomp = optimizer.optimize_and_decompose(user_prompt, target_duration=duration)

            # Launch movie_generator.py in background (non-blocking)
            safe_prompt = user_prompt.replace("'", "\\'")
            script_cmd = (
                f"PYTHONPATH={OTT_ROOT} python3 {OTT_ROOT}/engine/director/movie_generator.py "
                f"--prompt '{safe_prompt}' --duration {duration}"
            )
            subprocess.Popen(script_cmd, shell=True, cwd=OTT_ROOT,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            logger.info("[Web UI] Generation started: %d scenes @ %s", decomp["num_shots"], duration)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._send_cors_headers()
            self.end_headers()
            resp = {
                "status": "PROCESSING",
                "message": (
                    f"Story decomposed into {decomp['num_shots']} scenes. "
                    f"Rendering on RTX 4060 GPU — watch the frame preview below!"
                ),
                "decomposition": decomp
            }
            self.wfile.write(json.dumps(resp).encode("utf-8"))

        except Exception as e:
            logger.error("[Web UI Error] %s", str(e))
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ERROR", "error": str(e)}).encode("utf-8"))


def run_server(port: int = 8080):
    os.chdir(OTT_ROOT)
    server = ThreadingHTTPServer(("", port), StudioDashboardHandler)
    logger.info("GenOTT Studio Dashboard running at http://localhost:%d/", port)
    print(f"[✓] Dashboard Web Server active at http://localhost:{port}/")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
