# Architecture Decisions — Hollywood Challenge

This document lists the architectural updates and system configurations established during development.

## 🏛️ Architectural Updates

### ADR-01: Modular Engine Subsystems (Decoupled Layout)
* **Status**: Approved
* **Decision**: Decouple the monolithic pipeline handler into ten modular agent subsystems (`ai/asset_pipeline.py`, `ai/motion_intelligence.py`, `ai/physics_simulation.py`, etc.).
* **Consequences**: Eases parallel subsystem upgrades and enforces strict boundary checks.

### ADR-02: GPU Cycles OptiX Device Preferences
* **Status**: Approved
* **Decision**: Explicitly configure Cycles addon system preferences inside `blender_daemon.py` rather than letting Blender fall back to CPU.
* **Consequences**: Boosts frame generation speeds by leveraging local CUDA and OptiX kernels.

### ADR-03: Procedural Breathing and Micro-Expression Keyframing
* **Status**: Approved
* **Decision**: Inject sine-wave wiggles on shape keys and armature spine bones during dialogue rendering.
* **Consequences**: Removes rigid mannequin visual artifacts and elevates CGI realism.
