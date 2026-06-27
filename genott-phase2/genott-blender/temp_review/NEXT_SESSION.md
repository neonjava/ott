# Next Session Handoff — V14 OpenUSD Importer & Scene Reconstruction

## 🏛️ Current Architecture
* Decoupled modular engine subsystems (`ai/`) with persistent SQLite database schemas, non-destructive sequence timelines, and Cycles OPTIX/CUDA hardware preferences.
* Render Caching via MD5 hashing verification.
* Hierarchy tracking (Acts, Scenes, Shots, and Assets) via `MovieProjectManager` mapping UUID structures.
* OpenUSD exports and imports compiling/parsing USDA scene descriptions.

## 🛠️ Completed Work
1. **USD Importer**: Created `ai/usd/usd_importer.py` for parsing camera, lights, and node hierarchies.
2. **Verification**: Added `test_usd_importer_and_round_trip` inside `test_subsystems.py` asserting correct parsing of exported files (22/22 PASS).

## 🔮 Remaining Blockers
* **Fluid Simulation Caching**: Fluid and smoke dynamics are computed per frame without background serialization cache, slowing render cycles.

## 🎯 Exact Next Engineering Task
1. **Fluid Cache Manager**: Implement cache serialization managers for Blender fluid physics.

## 📋 Suggested Execution Order
1. Parse cache configurations from timeline triggers.
2. Write fluid cache descriptors to filesystem paths before rendering begins.
