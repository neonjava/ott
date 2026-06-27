# Roadmap to Vision

This roadmap outlines the 10 major milestones required to transition the codebase from a static **Blender Animation Generator** to a complete, autonomous **Movie Generation Engine** capable of converting arbitrary user scripts into coherent cinematic outputs.

---

## 1. Dynamic Character Customization & Asset Swapping
* **Problem**: All characters share the exact same untextured mannequin model (`humanoid.glb`).
* **Milestone**: Refactor the Blender render script to dynamically swap character meshes, apply color/texture materials, and bind auxiliary assets (weapons, shields, garments) at render-time according to properties defined in the character registry.

## 2. Dynamic Environment Composition Engine
* **Problem**: The renderer uses a static background template, resulting in identical visual environments regardless of location.
* **Milestone**: Build a procedural composition module that dynamically loads 3D asset packs (e.g., trees for forests, walls for castles, ground textures) and arranges them based on parsed locations, rather than relying on a static grid template.

## 3. Semantic/NLP Action-to-Animation Mapping
* **Problem**: Action resolution relies on rigid string/keyword matches. A novel verb phrase (like "loses faith") defaults to "idle".
* **Milestone**: Integrate a local vector embeddings model (e.g., Sentence-Transformers) to calculate semantic similarity between the script action description and the index of available animation tracks, selecting the closest contextual match.

## 4. Procedural Animation Synthesis & IK Retargeting
* **Problem**: Characters are locked into rigid pre-baked FBX animations and cannot interact with varying scene locations.
* **Milestone**: Implement Inverse Kinematics (IK) and procedural joint rotation within Blender to modify base animations dynamically (e.g., adjusting feet to uneven terrain, turning head towards camera target, or grabbing specific 3D coordinates).

## 5. LLM-Based Storyboard Structuring
* **Problem**: Rule-based script parsing (`storyboard_director.py`) fails on complex, multi-clause sentences or metaphorical/abstract script writing.
* **Milestone**: Shift storyboard parsing from regex to a structured local LLM (via Ollama/Llama) that outputs formal storyboard JSON containing scene boundaries, characters, actions, spatial constraints, and emotional context.

## 6. Procedural Camera Composition & Lighting
* **Problem**: Camera positions are mapped to static spatial presets.
* **Milestone**: Implement a dynamic camera director inside the Blender script that calculates camera distance, height, angle, and focal length dynamically using character bounding boxes. Adjust scene lighting (colors, angles, intensity) to match parsed mood values (e.g. low-key dramatic lighting for "mysterious").

## 7. Dynamic Asset Pipeline & Retrieval
* **Problem**: Unrecognized nouns (e.g. "dragon") cannot be visualized because the assets do not exist.
* **Milestone**: Implement an asset search and downloading manager that queries local model directories or public APIs (e.g., Sketchfab, Poly Haven) to dynamically fetch and cache 3D meshes, materials, and textures for unrecognized visual entities.

## 8. Visual State Continuity Manager
* **Problem**: Scene states (`scene_state.json`) only carry coordinates and do not maintain visual state consistency (e.g. a sword drawn in scene 1 is missing in scene 2).
* **Milestone**: Upgrade the state system to write and read dynamic visual states (e.g. held items, visible wounds, outfit state, environmental weather particles) between subsequent scenes.

## 9. Local GPU Lip-Sync Acceleration
* **Problem**: Lip-sync is disabled by default due to high setup overhead and execution latency.
* **Milestone**: Package a lightweight lip-sync engine (e.g., Wav2Lip) into a pre-compiled Python wheel using local CUDA libraries to perform sub-second lip-sync post-processing on generated face clips without external dependencies.

## 10. Generative Sound Effects (SFX) & Ambience Placement
* **Problem**: The audio output only consists of the voice synthesis track.
* **Milestone**: Build a sound design module that automatically queries sound libraries, extracts environmental ambience (e.g. wind howling, birds chirping), and synthesizes/aligns sound effects (e.g., footsteps, clashing steel) based on action keywords and storyboard timestamps.
