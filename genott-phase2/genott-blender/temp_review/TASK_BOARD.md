# TASK BOARD — AI Movie Production Platform V2.0

This task board coordinates the multi-role autonomous workflow to transition the platform from prototype to production-grade.

## 📋 Milestone Overview

| Milestone | Objective | Owner | Status | Target Files |
|-----------|-----------|-------|--------|--------------|
| **M1: Task Board & Audit** | Establish TASK_BOARD.md, AUDIT reports & VISUAL_QUALITY_PLAN.md | Coordinator / Architecture | ✅ Completed | `TASK_BOARD.md`, `VISUAL_QUALITY_PLAN.md` |
| **M2: Configurable Render Profiles** | Remove hardcoded resolutions & sample counts; implement development/production profiles | Rendering / Visual Quality | ✅ Completed | `ai/config.py`, `ai/renderer/blender_daemon.py` |
| **M3: Character Memory & State Manager** | Implement Character State Manager tracking persistent IDs, clothing, and styles | Character Agent | ✅ Completed | `ai/character/library.py`, `character_state_manager.py` |
| **M4: Visual Realism Upgrades** | Improve lighting, shadow settings, HDRI environment skyboxes, and anti-aliasing | Visual Quality / Env | ✅ Completed | `environment_director.py`, `ai/renderer/blender_daemon.py` |
| **M5: 30s Showcase Generation & Validation** | Compile 30-second HD movie, run E2E checks, and update AI_HISTORY.md | QA / Documentation | ✅ Completed | `app.py`, `AI_HISTORY.md` |
| **M6: Scene Graph & Continuity** | Implement scene graph hierarchy, absolute coordinate solver, and visual checks | Scene Graph / Continuity | ✅ Completed | `ai/scene_graph.py`, `ai/visual_continuity.py` |
| **M7: Procedural Layout Solver** | Implement circle and stack furniture placement algorithms | Layout Agent | ✅ Completed | `ai/procedural_layout.py` |
| **M8: Camera Collision Solver** | Implement collision raycasts and camera occlusion shifts | Camera Agent | ✅ Completed | `ai/camera_collision.py` |
| **M9: Animation Graph** | Implement walk/run transition graphs and blend trees | Animation Agent | ✅ Completed | `ai/animation_graph.py` |
| **M10: Emotion Memory** | Implement emotional baselines and time decay functions | Character / Emotion Agent | ✅ Completed | `ai/emotion_memory.py` |

---

## 🛠️ Task Backlog

### Milestone 1: Initialization & Planning
- [x] Create `TASK_BOARD.md` containing milestones, ownership, and conflicts mappings (Architecture/Coordinator)
- [ ] Perform rendering and visual audit; produce `VISUAL_QUALITY_PLAN.md` (Visual Quality Agent)
- [ ] Audit character consistency; design character state manager schema (Character Agent)

### Milestone 2: Configurable Render Engine
- [ ] Move `resolution_x`, `resolution_y`, and `cycles.samples` to runtime config parameters (Rendering Agent)
- [ ] Implement profiles (`development`, `testing`, `preview`, `production`, `ultra`) in `ai/config.py` (Rendering Agent)
- [ ] Update daemon request handler to read and apply active profile parameters dynamically (Rendering Agent)

### Milestone 3: Character State & Memory
- [ ] Define character identity tracking schema with persistent IDs (`hero_001` etc.) (Character Agent)
- [ ] Create `CharacterStateManager` to store look/outfit parameters to prevent regeneration (Character Agent)

---

## ⚠️ Avoid File Conflicts (Ownership Matrix)
To prevent concurrent writes, the following ownership limits apply:
- **`blender_daemon.py`:** Rendering Agent (M2) → Visual Quality Agent (M4)
- **`ai/config.py`:** Rendering Agent (M2)
- **`environment_director.py`:** Environment Agent / Visual Quality Agent (M4)
