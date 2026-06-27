# Story Understanding Gap Report

This report analyzes the ability of the current system to understand and visualize abstract, emotionally-driven, and complex script inputs such as:
> *"A lonely knight slowly loses faith while travelling through a frozen kingdom."*

---

## 1. Step-by-Step Failure Analysis

If this script is fed into the current pipeline, the following actions occur:

### A. Storyboard Parsing (`storyboard_director.py`)
1. **Character**: The word `"knight"` is detected and mapped to the standard ID `"knight"`.
2. **Location**: The preposition `"through"` matches `"frozen kingdom"`. With our Phase 1 updates, the keyword `"kingdom"` successfully classifies this environment as `"castle"`.
3. **Action**: The parser checks the script against the action keyword list (`walk`, `run`, `jump`, `attack`, `wave`, `duck`, `enter`, `discover`, `stand`, `say`, `talk`, `speak`). Since `"loses faith"` and `"travelling"` are not present, it defaults to `"idle"`.
4. **Camera/Mood**: The camera defaults to `"wide_shot"` and the mood defaults to `"neutral"`.

### B. Continuity Engine (`continuity_engine_v2.py`)
1. The location is set to `"castle"`.
2. The weather is set to `"snow"` because the word `"frozen"` in the location description is mapped to the `"mountain"` fallback or `"snow"` weather trigger.
3. No held items or outfits are modified since none are explicitly referenced as being equipped/drawn.

### C. Blender Scene Construction & Rendering (`blender_daemon.py`)
1. The daemon loads `humanoid.glb` and sets the action to `CharacterArmature|Idle` (standing still).
2. The environment is composed as a `"castle"` (spawns grey stone pillars on a dark plane under a dark grey sky).
3. The camera frames a static wide shot.
4. **Resulting Video**: A 4-second clip of a generic untextured mannequin standing completely motionless in a dark room with stone pillars, while a voiceover reads the sentence.

---

## 2. Identified Gaps and Missing Capabilities

| Gap Area | Missing Capability | Why it Failed |
|---|---|---|
| **Semantic Verbs** | Direct semantic mapping for abstract verb phrases like `"loses faith"` or `"travelling"`. | The rule-based keyword mapping falls back to `"idle"` because it cannot calculate semantic similarity. |
| **Emotional Expressiveness** | Applying body posture adjustments or facial expressions to match the actor's emotional state (e.g. `"lonely"`). | The system lacks an emotional pose database or keyframe deformers to slump shoulders or look downwards. |
| **Locomotion Mapping** | Trajectory and pathing for travelling actions. | The character walks or runs along a single straight line axis (`y`) without spatial pathfinding or steering. |
| **Environmental Detail** | Spawning weather effects like snow particles or frosting shaders on meshes. | The Blender scene builder only handles flat colors and static primitives, not dynamic weather particles or procedural snow cover. |

---

## 3. Required Systems

To bridge these gaps, the following four systems must be introduced:

1. **Semantic Action Mapper (NLP-to-Animation)**:
   - Uses local sentence embeddings (e.g. Sentence-Transformers) to map arbitrary verb phrases (e.g., *"loses faith"* -> *"slump_shoulders_head_down"*, *"travelling through"* -> *"walk_weary"*) to the closest contextually appropriate animation.
2. **Procedural Pose Modifiers (IK Director)**:
   - Uses Inverse Kinematics (IK) to modify base animations. For example, applying a head-down rotation constraint on the neck bone if the mood is `"sad"` or `"lonely"`.
3. **Procedural Particle Generator**:
   - A Blender module that spawns and simulates particle systems (like rain falling or snow drifting) in the environment based on the continuity weather state.
4. **LLM-Based Storyboard Planner**:
   - Shifting storyboard parsing from regular expressions to a local LLM (e.g. Llama 3.2 via Ollama) that can capture subtext, emotional arcs, and implicit scene directions.

---

## 4. Required Data Structures

The storyboard/scene plan data structure must be expanded as follows:

```json
{
  "scenes": [
    {
      "scene_number": 1,
      "location": "frozen kingdom",
      "environment_modifiers": ["snow", "ice", "fog"],
      "character_name": "knight",
      "action": "travel",
      "action_modifier": "weary",
      "actor_emotion": "depressed",
      "posture_modifiers": {
        "head_angle": -15.0,
        "shoulder_slump": 0.2
      },
      "held_item": null,
      "camera": "establishing_shot",
      "lighting_mood": "low_key_blue"
    }
  ]
}
```
