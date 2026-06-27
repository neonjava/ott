# GenOTT Project Issues Log

This file tracks technical issues, bottlenecks, and bugs found during the development and benchmark runs of the GenOTT AI Movie Generation platform.

---

## [Issue #1] Blender Flatpak Cold-Start Blocker (OptiX Shader Compilation)

- **Status**: RESOLVED
- **Date Found**: 2026-06-17
- **Severity**: HIGH (Blocker)
- **Description**: The first render request triggers bubblewrap/flatpak container initialization and OptiX GPU shader compilation in Blender. This initial load can exceed 120 seconds, causing the client API request to hit a timeout and fail.
- **Root Cause**: Cycles GPU rendering needs to build OptiX device kernels when initialized for the first time in a new environment session.
- **Resolution**: Implemented `prewarm_blender_daemon()` in [blender.py](file://PROJECT_ROOT/Documents/LLM/ott/genott-phase2/genott-blender/ai/renderer/blender.py). When the daemon starts up, it immediately triggers a background 1-frame mock render to compile kernels and warm up the container before any real client API requests are processed.
- **Resolution Commit**: fd7d6fb

---

## [Issue #2] String Formatting Typo in `movie_validation_benchmark.py`

- **Status**: RESOLVED
- **Date Found**: 2026-06-17
- **Severity**: LOW
- **Description**: The benchmark report file template failed to render the actual value of successful generations, printing the raw text `{passes}` inside the Markdown output.
- **Root Cause**: The conclusion formatting string `'**All {passes} movies passed validation.**'` was nested inside an f-string expression but lacked its own `f` prefix.
- **Resolution**: Added the `f` prefix to the single-quoted string inside the f-string evaluation statement in [movie_validation_benchmark.py](file://PROJECT_ROOT/Documents/LLM/ott/genott-phase2/genott-blender/movie_validation_benchmark.py#L158).
- **Resolution Commit**: fd7d6fb

---

## [Issue #3] Cinematic Camera Sequencer Mismatch & Regression

- **Status**: RESOLVED
- **Date Found**: 2026-06-17
- **Severity**: HIGH (Blocker)
- **Description**: The camera sequencer generated frame-by-frame 3D coordinates, but the Blender Daemon ignored them because it expected `camera_shot` and `loc_factor` metadata parameters, causing the camera to remain static on the first pass. Also, the Flask regeneration loop passed `"character_start"` as a string leading to Python `TypeError` and crash when regeneration was triggered. Finally, `ScenePlan` lacked a `camera_movement` field causing evaluator penalties.
- **Root Cause**: Lack of coordinate integration inside the daemon's camera setup loop and parameter mismatch between `cinematic_sequencer.py` and `blender_daemon.py`.
- **Resolution**:
  - Added `camera_movement` to `ScenePlan` in `models.py` and `planner.py`.
  - Updated `blender_daemon.py` to directly apply `location` and `rotation` tuples inside the keyframe payload if present.
  - Added safe fallback try-except logic for Blender 5.x Action curves.
  - Removed string-passing from `app.py` and auto-generated timeline in `blender.py` if missing.
- **Resolution Commit**: 7654434

---

## [Issue #4] Blender 5.1.2 Environment Primitive Radius Argument Bug

- **Status**: RESOLVED
- **Date Found**: 2026-06-17
- **Severity**: MEDIUM
- **Description**: Mountain, cave, forest, and village environments failed to build, logging: `Failed to build environment: Converting py args to operator properties:: keyword "radius" unrecognized`.
- **Root Cause**: In Blender 5.1.2, `bpy.ops.mesh.primitive_cone_add` was updated to use `radius1` and `radius2` instead of `radius`.
- **Resolution**: Updated `environment_director.py` to replace all `radius` parameter names with `radius1` inside `primitive_cone_add` calls.
- **Resolution Commit**: 7654434

