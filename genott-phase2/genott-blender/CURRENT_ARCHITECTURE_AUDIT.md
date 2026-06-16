# Current Architecture Audit

This audit evaluates the reality of the current movie generation codebase. It identifies the operational logic (rule-based vs. AI-based), stubs, asset duplication, and failure modes when handling novel inputs.

---

## Part 1: Architecture Breakdown

### 1. Rule-Based Systems
* **Storyboard Parsing (`storyboard_director.py`)**: Uses regular expressions and predefined prepositional/keyword lists to split sentences and extract locations, characters, actions, camera types, and moods.
* **Dialogue & Timeline Extraction (`dialogue_engine.py`)**: Uses string patterns (e.g., checking for double quotes or matching `says:`) to isolate dialogue, narration lines, and map speakers to voice profiles.
* **Blender Action Resolution (`ai/renderer/blender.py`)**: Maps extracted storyboard actions to predefined action name keys in `character_registry.json` using exact string matches or keyword sub-searches (e.g., "charge" -> "run").
* **Scene Assembly & Stitching (`movie_assembler.py`)**: Utilizes FFmpeg to physically concatenate MP4 files and merge narration audio based on exact file paths and text-based concat manifests.

### 2. AI-Based Systems
* **Speech Synthesis (`VoiceSystem`)**: Relies on `edge-tts` (Microsoft's Cognitive Services TTS) to generate synthesized character dialogue and narration.
* **Lip-Sync (`SadTalkerProvider`)**: Uses deep learning neural network checkpoints for talking head generation from facial photos. *(Note: This module is currently disabled by default).*
* **Storyboard Planning Fallback (`planner.py`)**: Can query a local Ollama server running Llama 3.2, but this is bypassed in the active automated movie generation route (`plan_rule_based`).

### 3. Placeholders and Stubs
* **Unreal Engine Renderer (`ai/renderer/unreal.py`)**: Exists as an empty stub class with no implementation.
* **Diffusers AI Renderer (`ai/renderer/diffusers_ai.py`)**: Fully unimplemented stub that is bypassed in the active rendering pipeline.
* **Visual Modifiers (Outfits/Weapons)**: `OutfitDefinition` and `WeaponDefinition` classes exist in the character profile model but have no corresponding implementation in the Blender render script (no meshes are swapped, no textures are modified, and no weapons are attached).
* **Lip-Sync**: Bypassed by default (`Config.ENABLE_LIPSYNC = False`).

### 4. Duplicated Assets
* **Character Mesh**: All required characters (`anime_girl`, `anime_boy`, `knight`, `mage`, `robot`, `humanoid`) share the exact same 3D mesh model: `humanoid.glb`.
* **Face Reference Images**: `anime_girl.png`, `anime_boy.png`, `knight.png`, `mage.png`, `robot.png`, `humanoid.png`, and `fox.png` are copies of the identical 9KB `tony_stark.png` file to prevent file-not-found exceptions in the character library and validation scripts.

---

## Part 2: Novel Story Failure Analysis

### Example Input
> "A lonely knight slowly loses faith while travelling through a frozen kingdom."

### Will it produce a meaningful movie?
**No.**

### What happens step-by-step:
1. **Storyboard Parsing**:
   * The script is processed as a single sentence.
   * **Character**: The parser finds the keyword `"knight"`.
   * **Location**: Matches the preposition `"through"`. The parsed location becomes `"frozen kingdom"`.
   * **Action**: Checks the sentence against the keyword list (`walk`, `run`, `jump`, `attack`, `wave`, `duck`, `enter`, `discover`, `stand`, `say`, `talk`, `speak`). Since `"loses faith"` and `"travelling"` are not in the list, the action defaults to `"idle"`.
   * **Camera/Mood**: Defaults to `"wide_shot"` and `"neutral"`.
2. **Dialogue Engine**:
   * Detects no quotes or speech patterns. Generates a single narration block containing the input sentence.
3. **Blender Rendering**:
   * Resolves the character `"knight"` to `humanoid.glb`.
   * Maps `"idle"` to `CharacterArmature|Idle` in `character_registry.json`.
   * Loads `humanoid.glb` in Blender and runs the `Idle` animation block for 4.0 seconds.
   * **Environment**: Renders in the static default Blender project template (a plain grey grid/surface with basic lighting). The `"frozen kingdom"` location description is ignored by the renderer.
4. **Audio Synthesis**:
   * Synthesizes the narrator voice (`en-US-GuyNeural`) speaking: *"A lonely knight slowly loses faith while travelling through a frozen kingdom."*
5. **Output**:
   * Stitches the single 4-second clip containing the generic untextured humanoid model standing still on a flat grey plane, with a male voice-over reading the text.
   * **Failure reasons**: No knight armor or visual indicators exist, no frozen environment is generated, and the abstract action of "losing faith" is rendered as standing completely still.

---

## Part 3: System Audit Metrics

### Implemented Systems
* **Blender Daemon & IPC Render Queue**: *Complete (95%)*. Handles background rendering processes via Flatpak and processes scene payloads using IPC.
* **Movie Assembly & Audio Merger**: *Complete (95%)*. Concatenates clips and merges voices using FFmpeg with verification checks.
* **Rule-Based Script Dialogue Parser**: *Complete (90%)*. Splitting and classifying text segments into dialogues and narration.
* **Metadata APIs**: *Complete (90%)*. Returns lists of characters and status objects.

### Partially Implemented Systems
* **Storyboard Director (Parsing)**: *Partial (85%)*. Rule-based, works well for predefined templates but lacks semantic parsing of complex or abstract sentences.
* **Action Mapping**: *Partial (40%)*. Maps descriptive action words to a fixed array of 6-10 rigid character animations. Cannot proceduralize or blend movements.
* **Visual Continuity Manager**: *Partial (50%)*. Saves character coordinates across scenes in `scene_state.json`, but does not maintain dynamic item attachments or visual damage states.
* **Lip-Sync Integration**: *Partial (30%)*. SadTalker module exists but is disabled by default due to high setup/inference latency.

### Missing Systems
* **Visual Character Differentiation (Swapping Outfits/Weapons)**: *Missing (5%)*. All humanoid characters look visually identical inside the rendered output.
* **Dynamic Environment Generator**: *Missing (0%)*. Renderer is incapable of generating/styling environments (e.g. castles, forests, skybox) from the storyboard location string.
* **Procedural Animation/Action Synthesis**: *Missing (0%)*. Lacks any ability to compile or synthesize animations for novel action descriptions outside the predefined set.

### Technical Debt
* **Lack of Asset Variety**: The engine depends on a single humanoid mesh and a single animal mesh (`fox`).
* **Hardcoded Camera Presets**: Camera shots map directly to a static preset list of movements instead of dynamically composing shots based on scene elements.

### Production Risks
* **Lack of Visual Variety**: Users receive identical visual assets regardless of the selected character.
* **Static Environment**: Renders take place in the same empty template, causing all movies to look visually identical apart from the animation track.

---

## Part 4: Classification

### Is the project currently:
**A) Blender Animation Generator**

### Justification:
The system is unable to dynamically compose, construct, or style visual components from semantic story script inputs. It reads text parameters to locate hardcoded animation indices, applies those indices to a single static 3D model, and launches a command-line Blender render using a static background template. It behaves as an automated pipeline renderer for pre-existing animations rather than a generative movie engine.
