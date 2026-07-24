# GenOTT V2 — Autonomous AI Production Studio

GenOTT V2 is an orchestration platform capable of planning, directing, generating, evaluating, and exporting professional cinematic short-form videos using interchangeable open-source AI generation models.

## Core Features
- **MovieGraph Orchestration**: Model-agnostic scene, shot, and character specification graph.
- **Interchangeable Backends**: Native support for open-source WAN backend (`engine/backends/wan/`), Blender 3D (`models/blender/`), and modular diffusion models (`third_party/`).
- **Model Manager**: Automated device detection, weight discovery, lazy loading, and hot unloading (`engine/model_manager/`).
- **Prompt Compiler**: Automatic compilation of canonical `MovieGraph` shot specs into model-tailored positive and negative prompts (`engine/prompt_compiler/`).
- **CLI & Local Execution**: Executable via `python3 run.py` or `./genott.py`.

## Quick Start
```bash
# Setup WAN environment & verify dependencies
python3 scripts/setup_wan.py

# Run diagnostic suite
python3 genott.py backend test wan

# Generate cinematic shot
python3 genott.py generate --prompt "A cyberpunk detective walking through neon rain" --output outputs/shot_01.mp4

# Run unit tests
python3 -m unittest discover -s tests/unit
```

## Structure
- `engine/`: Core planning, director pipeline, prompt compiler, model manager, and backend adapters.
- `third_party/`: Submodule/upstream integration directories for `wan/`, `hunyuanvideo/`, `cogvideox/`, `ltx-video/`, `mochi/`.
- `configs/`: Model configurations (`configs/models/wan.yaml`).
- `docs/`: Technical and backend documentation (`docs/backends/wan.md`).
