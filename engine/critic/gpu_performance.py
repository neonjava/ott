# ai/gpu_performance.py
import time
import subprocess
from typing import Dict, Any, List

class GPUPerformanceMonitor:
    """
    Subsystem: GPU Render Performance & CUDA Scheduler
    Monitors NVIDIA VRAM headroom, schedules CUDA/OptiX rendering configurations, and reports performance metrics.
    """
    def __init__(self):
        pass

    def detect_cuda_devices(self) -> List[Dict[str, Any]]:
        """Queries local system components to discover available CUDA devices."""
        devices = []
        try:
            # Query nvidia-smi for GPU names
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
            )
            for line in result.stdout.strip().split("\n"):
                if line:
                    parts = line.split(",")
                    devices.append({
                        "name": parts[0].strip(),
                        "total_vram_mb": float(parts[1].strip()),
                        "cuda_supported": True
                    })
        except Exception:
            # Fallback mock/CPU state if nvidia-smi is missing
            devices.append({
                "name": "Generic CPU Render Engine",
                "total_vram_mb": 8192.0,
                "cuda_supported": False
            })
        return devices

    def check_vram_headroom(self) -> Dict[str, Any]:
        """Calculates current VRAM capacity and returns memory bounds status."""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.used,memory.free", "--format=csv,noheader,nounits"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
            )
            parts = result.stdout.strip().split("\n")[0].split(",")
            used = float(parts[0].strip())
            free = float(parts[1].strip())
            total = used + free
            
            return {
                "status": "nominal" if (free / total) > 0.15 else "critical",
                "used_mb": used,
                "free_mb": free,
                "total_mb": total,
                "utilization_pct": round((used / total) * 100, 1)
            }
        except Exception:
            return {
                "status": "unknown",
                "used_mb": 0.0,
                "free_mb": 8192.0,
                "total_mb": 8192.0,
                "utilization_pct": 0.0
            }

    def calculate_render_metrics(self, start_time: float, frame_count: int) -> Dict[str, Any]:
        """Calculates render speed performance parameters."""
        elapsed = time.time() - start_time
        if elapsed <= 0:
            elapsed = 0.001
            
        fps = frame_count / elapsed
        sec_per_frame = elapsed / frame_count if frame_count > 0 else 0.0
        
        return {
            "elapsed_seconds": round(elapsed, 2),
            "frame_count": frame_count,
            "fps": round(fps, 2),
            "seconds_per_frame": round(sec_per_frame, 3)
        }
