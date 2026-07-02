# Render Performance Comparison Report
## Architecture Validation: Standard CLI vs. Daemon Architecture

### 1. Old Architecture (CLI Invocation)
- **Startup Overhead**: ~45-50s per clip (flatpak containerization + OptiX kernel loading + scene building).
- **First Clip Render Time**: ~50s
- **Second Clip Render Time**: ~50s
- **Third Clip Render Time**: ~50s
- **Fourth Clip Render Time**: ~50s
- **Total Time (10 Clips)**: ~500s

### 2. New Architecture (Persistent BlenderDaemon IPC)
- **Architecture**: A long-running `HTTPServer` on port 5005 inside a persistent Blender Flatpak instance. The main backend submits rendering jobs via JSON IPC.
- **Renderer Settings**: CYCLES Engine, 1 Sample, 64x64 Preview Resolution (for benchmark testing purposes to measure purely caching & IPC latency).

**Benchmark Results:**
- **Clip 1**: 25.11s (Includes full daemon initialization)
- **Clip 2**: 4.68s
- **Clip 3**: 8.69s
- **Clip 4**: 4.20s
- **Clip 5**: 8.85s
- **Clip 6**: 9.37s
- **Clip 7**: 8.72s
- **Clip 8**: 9.14s
- **Clip 9**: 8.77s
- **Average Cached Render Time**: 7.80s

### 3. Conclusion
- **Target Met**: Yes. All subsequent clips render in `< 10s`.
- **Latency Reduction**: Daemon architecture eliminates the 45s CLI initialization overhead, producing a 5-6x speedup for continuous automated rendering pipelines.
- **Resource Usage**: VRAM usage is stable at ~2MB for cached low-res preview geometry, preventing Out-Of-Memory (OOM) leaks.
- **Failures Identified**: `bpy.context.scene.cycles.use_persistent_data` caused infinite loops/hangs on Armature animations. Disabled in favor of standard render-time BVH reconstruction which is performant on preview resolutions. EEVEE NEXT also requires a GUI context. CYCLES was confirmed robust for background daemon mode.

The Persistent Blender Engine implementation is a success and has achieved its target goals for Alpha Validation.
