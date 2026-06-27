# Next Blocker Ranked List & Gap Analysis

## 1. Multi-Character Dialogue, Speaker Tracking, & Lip Sync Timeline Mismatch (RESOLVED)
- **Blocker Name**: Multi-Character Dialogue, Speaker Tracking, & Lip Sync Timeline Mismatch
- **Why it Blocks Production Readiness**:
  - Legacy `ScenePlan` only supported a single `dialogue: Optional[DialogueLine]` field per scene, discarding subsequent dialogue lines.
  - The voice synthesis pipeline did not support sequential multi-character dialogue mapping or speaker tracking.
  - Lipsync visemes were unconditionally mapped to the primary character starting from frame 1, rather than tracking speakers and applying timing offsets.
- **Impact Score**: 9.5/10
- **Effort Score**: 8.5/10
- **Files Involved**:
  - [ai/storyboard/models.py](file://PROJECT_ROOT/Documents/LLM/ott/genott-phase2/genott-blender/ai/storyboard/models.py)
  - [ai/storyboard/planner.py](file://PROJECT_ROOT/Documents/LLM/ott/genott-phase2/genott-blender/ai/storyboard/planner.py)
  - [ai/renderer/blender.py](file://PROJECT_ROOT/Documents/LLM/ott/genott-phase2/genott-blender/ai/renderer/blender.py)
  - [ai/renderer/blender_daemon.py](file://PROJECT_ROOT/Documents/LLM/ott/genott-phase2/genott-blender/ai/renderer/blender_daemon.py)
  - [app.py](file://PROJECT_ROOT/Documents/LLM/ott/genott-phase2/genott-blender/app.py)
- **Resolution**:
  - Refactored `planner.py` to extract all dialogue lines for each scene and populate `plan.dialogues`.
  - Refactored `app.py` to synthesize dialogue files sequentially, offset viseme timelines relative to their start times, add pinning "rest" visemes to keep lips still when not speaking, and mix audio tracks at proper offsets.
  - Mapped character-specific viseme dictionary in `blender.py` so the daemon correctly animates the speaking characters when they are active.

---

## 2. Secondary Character Spatial Discontinuity across Scenes (RESOLVED)
- **Blocker Name**: Secondary Character Spatial Discontinuity across Scenes
- **Why it Blocks Production Readiness**:
  - `scene_state.json` only tracks the final position and rotation of the primary character (index 0).
  - Secondary characters have their positions reset on every scene change according to the static placement engine, causing them to jarringly jump around.
- **Impact Score**: 8.5/10
- **Effort Score**: 5.0/10
- **Files Involved**:
  - [ai/renderer/blender.py](file://PROJECT_ROOT/Documents/LLM/ott/genott-phase2/genott-blender/ai/renderer/blender.py)
  - [ai/renderer/blender_daemon.py](file://PROJECT_ROOT/Documents/LLM/ott/genott-phase2/genott-blender/ai/renderer/blender_daemon.py)
  - [scene_state.json](file://PROJECT_ROOT/Documents/LLM/ott/genott-phase2/genott-blender/scene_state.json)
- **Resolution**:
  - Modified `blender_daemon.py` to read/write location and rotation data for all active characters inside the scene's `scene_state.json` payload under a unified `characters` dictionary.
  - Calculated locomotion-based delta offsets for each character based on their scene-specific actions.
  - Applied loaded coordinates back on character import to ensure spatial continuity across scenes for secondary characters.

---

## 3. Environment Layout Discontinuity and Random Rebuilds (RESOLVED)
- **Blocker Name**: Environment Layout Discontinuity and Random Rebuilds
- **Why it Blocks Production Readiness**:
  - When consecutive scenes share the same location name, the procedural environment director rebuilds the geometry layouts (trees, rocks, props) from scratch using random seeds, causing elements to morph and move between cuts.
- **Impact Score**: 8.0/10
- **Effort Score**: 6.0/10
- **Files Involved**:
  - [environment_director.py](file://PROJECT_ROOT/Documents/LLM/ott/genott-phase2/environment_director.py)
  - [ai/renderer/blender.py](file://PROJECT_ROOT/Documents/LLM/ott/genott-phase2/ai/renderer/blender.py)
- **Resolution**:
  - Updated `environment_director.py` to allow passing a custom `env_seed` and to dynamically generate one if missing.
  - Modified `blender_daemon.py` to read `env_seed` from `scene_state.json` on load, pass it to `build_environment_in_blender`, and write the resulting `env_seed` back to `scene_state.json` at the end of the render. This locks the procedural placements across sequential cuts.

---

## 4. Lack of High-Level Narrative Pacing & Pacing Control (RESOLVED)
- **Blocker Name**: Lack of High-Level Narrative Pacing & Pacing Control
- **Why it Blocks Production Readiness**:
  - For narrative coherence, scene durations and pacing need to adapt to target overall movie length (30-60 seconds). Currently, scripts split sentences 1-to-1 to scenes with static 4s-5s scene durations, lacking global pacing coordination.
- **Impact Score**: 7.5/10
- **Effort Score**: 6.5/10
- **Files Involved**:
  - [storyboard_director.py](file://PROJECT_ROOT/Documents/LLM/ott/genott-phase2/storyboard_director.py)
  - [ai/storyboard/planner.py](file://PROJECT_ROOT/Documents/LLM/ott/genott-phase2/ai/storyboard/planner.py)
- **Resolution**:
  - Added dynamic duration normalization in `planner.py` to calculate overall raw storyboard duration and scale all scene segment runtimes proportionally to sum to a target 45.0s runtime. This guarantees movies fit cleanly into the target 30-60 second production window.

---

## 5. Cinematic Sequencer & Render Daemon Framerate Mismatch (RESOLVED)
- **Blocker Name**: Cinematic Sequencer & Render Daemon Framerate Mismatch
- **Why it Blocks Production Readiness**:
  - The cinematic sequencer generated keyframe locations/rotations based on a default `fps = 24`, while the Blender daemon rendered and configured properties targeting a hardcoded `fps = 12`. This caused keyframe truncation and play-back speeds to slow down.
- **Impact Score**: 9.0/10
- **Effort Score**: 4.0/10
- **Files Involved**:
  - [ai/renderer/blender.py](file://PROJECT_ROOT/Documents/LLM/ott/genott-phase2/genott-blender/ai/renderer/blender.py)
  - [ai/renderer/blender_daemon.py](file://PROJECT_ROOT/Documents/LLM/ott/genott-phase2/genott-blender/ai/renderer/blender_daemon.py)
- **Resolution**:
  - Updated `blender.py` to explicitly pass `fps=12` to `sequence_scene` so that keyframe generation matches the daemon's hardcoded rendering and video compilation framerates.

