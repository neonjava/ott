# 30-Second Cinematic Video Production Demo Specification

## Overview
GenOTT V2 features an autonomous 30-second cinematic video production pipeline (`engine/director/demo_orchestrator.py`).
It orchestrates narrative screenplay planning, WAN prompt compilation, narration audio synthesis, shot-by-shot video rendering, and final assembly into `outputs/demo/`.

## Multi-Workstream Ownership Layout
- **Workstream 1 (Architecture & Brain)**: `brain/`, `ARCHITECTURE.md`, `ROADMAP.md`, `STATE.json`
- **Workstream 2 (Model Manager)**: `engine/model_manager/`
- **Workstream 3 (Backend Adapters)**: `engine/backends/wan/`, `models/adapters/`
- **Workstream 4 (WAN Integration)**: `third_party/wan/`
- **Workstream 5 (CLI & Production Pipeline)**: `genott.py`, `run.py`, `engine/director/demo_orchestrator.py`
- **Workstream 6 (Prompt Compiler)**: `engine/prompt_compiler/`
- **Workstream 7 (Testing & Validation)**: `tests/unit/`, `tests/integration/`
- **Workstream 8 (Documentation)**: `docs/`, `README.md`
- **Workstream 9 (Benchmarking)**: `genott benchmark`

## Generating the 30-Second Production Demo
Run the CLI command:
```bash
python3 genott.py generate --demo
```

## Generated Production Artifacts in `outputs/demo/`
1. `screenplay_script.json` — 6-shot screenplay narrative breakdown.
2. `shot_prompts.json` — Model-agnostic & WAN compiled positive/negative prompt pairs per shot.
3. `narration_audio.wav` — 30-second synchronized narration audio track.
4. `shot_01.mp4` to `shot_06.mp4` — Rendered individual visual scenes (5.0s duration each).
5. `30s_cinematic_production.mp4` — Final exported 30-second production video.
6. `production_metadata.json` — Comprehensive metadata recording total duration, latency, model versions, seeds, VRAM usage, and compute settings.
