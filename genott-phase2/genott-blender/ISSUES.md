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
- **Resolution Commit**: (To be committed)

---

## [Issue #2] String Formatting Typo in `movie_validation_benchmark.py`

- **Status**: RESOLVED
- **Date Found**: 2026-06-17
- **Severity**: LOW
- **Description**: The benchmark report file template failed to render the actual value of successful generations, printing the raw text `{passes}` inside the Markdown output.
- **Root Cause**: The conclusion formatting string `'**All {passes} movies passed validation.**'` was nested inside an f-string expression but lacked its own `f` prefix.
- **Resolution**: Added the `f` prefix to the single-quoted string inside the f-string evaluation statement in [movie_validation_benchmark.py](file://PROJECT_ROOT/Documents/LLM/ott/genott-phase2/genott-blender/movie_validation_benchmark.py#L158).
- **Resolution Commit**: (To be committed)
