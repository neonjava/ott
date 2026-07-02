# GPU Performance & CUDA Scheduler Subsystem Design

## Purpose
Optimize Blender rendering pipelines to leverage hardware-accelerated NVIDIA CUDA and OptiX cycles, tracking memory usage, CPU fallback overrides, and scheduling GPU tasks.

## Responsibilities
* **Device Detection**: Detect local GPU CUDA and OptiX availability.
* **VRAM Allocator and Cache Scheduler**: Monitor memory headroom to prevent VRAM overflow.
* **Performance Benchmarks**: Calculate render latency, frame rate (FPS), and VRAM utilization metrics.

## Public Interfaces
```python
class GPUPerformanceMonitor:
    def detect_cuda_devices(self) -> List[Dict[str, Any]]
    def check_vram_headroom(self) -> Dict[str, Any]
    def calculate_render_metrics(self, start_time: float, frame_count: int) -> Dict[str, Any]
```

## Dependencies
* `ai/config.py`: Imports rendering resolution scales.
* `ai/renderer/blender_daemon.py`: Dispatches render calls and binds cycles render settings.

## Data Flow
```
[Render Queue Dispatch] -> [check_vram_headroom] -> [OptiX/CUDA Enabled] -> [Blender Cycles Render] -> [calculate_render_metrics] -> [Performance Log]
```

## Testing Strategy
* Mock NVIDIA System Management Interface (nvidia-smi) readings to verify failover thresholds.
* Benchmark render metric formulas using elapsed delta ranges.
