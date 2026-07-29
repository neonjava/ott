# engine/metrics/collector.py
import os
import sys
import time
import psutil
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class MetricsCollector:
    """
    Collects real hardware runtime statistics: GPU model, CUDA version, VRAM allocated,
    peak VRAM, CPU utilization, system RAM, inference latency, loading duration, FPS, and resolution.
    """

    @staticmethod
    def get_hardware_info() -> Dict[str, Any]:
        gpu_model = "CPU Fallback"
        cuda_version = "None"
        vram_allocated_gb = 0.0
        peak_vram_gb = 0.0

        try:
            import torch
            if torch.cuda.is_available():
                gpu_model = torch.cuda.get_device_name(0)
                cuda_version = torch.version.cuda or "Available"
                vram_allocated_gb = round(torch.cuda.memory_allocated(0) / (1024 ** 3), 3)
                peak_vram_gb = round(torch.cuda.max_memory_allocated(0) / (1024 ** 3), 3)
        except ImportError:
            pass

        cpu_percent = psutil.cpu_percent(interval=None)
        mem_info = psutil.virtual_memory()
        ram_used_gb = round(mem_info.used / (1024 ** 3), 2)
        ram_total_gb = round(mem_info.total / (1024 ** 3), 2)

        return {
            "gpu_model": gpu_model,
            "cuda_version": cuda_version,
            "vram_allocated_gb": vram_allocated_gb,
            "peak_vram_gb": peak_vram_gb,
            "cpu_usage_percent": cpu_percent,
            "ram_used_gb": ram_used_gb,
            "ram_total_gb": ram_total_gb
        }

    @classmethod
    def record_inference_metrics(
        cls, 
        model_name: str, 
        model_version: str, 
        duration_sec: float, 
        inference_time_sec: float, 
        load_time_sec: float,
        fps: int, 
        resolution: str, 
        seed: int
    ) -> Dict[str, Any]:
        hw = cls.get_hardware_info()
        calculated_fps = round((duration_sec * fps) / max(0.001, inference_time_sec), 2)

        return {
            "model_name": model_name,
            "model_version": model_version,
            "inference_duration_sec": round(inference_time_sec, 3),
            "model_loading_duration_sec": round(load_time_sec, 3),
            "fps": fps,
            "effective_fps": calculated_fps,
            "output_resolution": resolution,
            "generation_seed": seed,
            **hw
        }
