# WAN Backend Adapter Specification

## Overview
The WAN Backend integration provides official open-source WAN model capabilities (Text-to-Video, Image-to-Video, Video-to-Video) to GenOTT V2 as a pluggable execution backend under `engine/backends/wan/`.

## Architecture & Integration
- **Backend Adapter**: `WANBackend` implements `BackendAdapter` (`models/adapters/base.py`).
- **Model Manager**: Managed via `ModelManager` (`engine/model_manager/`) supporting lazy loading, device detection, and hot unloading.
- **Prompt Compiler**: Translates `MovieGraph` / `ShotSpec` descriptions into rich WAN positive/negative prompts.
- **CLI Commands**: Accessible via `./genott.py` and `run.py`.

## Operations & Usage
```bash
# Diagnostic health check
python3 genott.py backend test wan

# Model discovery & info
python3 genott.py models info

# Text-to-Video generation
python3 genott.py generate --prompt "Cinematic wide shot of a medieval castle at dusk" --backend wan --output outputs/castle.mp4 --duration 5.0

# Benchmark performance
python3 genott.py benchmark wan
```

## Sidecar Metadata Storage
Every generation automatically outputs a companion metadata JSON file alongside the video (`outputs/<filename>_meta.json`) capturing:
- Text prompt & negative prompt
- Seed & step parameters
- Framerate & resolution
- Model version
- VRAM usage and generation latency
