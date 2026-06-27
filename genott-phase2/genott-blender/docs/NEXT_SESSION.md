# Next Session Handoff — V20 Clean Production Repository Layout

## 🏛️ Current Architecture
* **Frontend**: Decoupled template and static assets located under `frontend/templates/` and `frontend/static/` directories.
* **Backend**: Flask endpoints and services located under `backend/api/` and `backend/services/`.
* **Engine**: Main modules categorized logically under `engine/` subfolders (director, character, camera, interaction, physics, audio, usd, cache, renderer, environment).
* **Pipeline**: Timelines and validation suites placed in `pipeline/` subfolders (storyboard, timeline, validation).
* **Compatibility Wrapper Layers**: Re-export wrappers present in the original locations (root and `ai/`) to provide 100% backwards-compatibility and prevent breaking existing external scripts.

## 🛠️ Completed Work
1. **Refactoring**: Category-sorted all Python modules and assets into target directories (e.g. `engine/director/director_intelligence.py`, `pipeline/validation/cinematic_critic.py`, etc.).
2. **Path Updates**: Updated Flask static/template path parameters and the character registry resolution paths to dynamically compute directories relative to the project root.
3. **Blender Path Registration**: Added the engine and pipeline subdirectories to the Blender daemon's `sys.path` to enable correct resolution under independent python execution contexts.
4. **Verification**: 35/35 unit tests pass, and character validation benchmarks generated successfully.

## 🔮 Remaining Blockers
* **Secondary Physics**: Hair/Clothing dynamics could be enhanced with responsive procedural solver layers.

## 🎯 Exact Next Engineering Task
1. **Continue auditing** the renderer for the next weakest production-quality implementation.

## 📋 Suggested Execution Order
1. Audit secondary dynamics, light probes, or camera obstacle detection.
2. Replace with production-grade solver layer.
