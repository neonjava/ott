# Lip Sync Feasibility Report

## Overview & Feasibility Status
- **Status**: **BLOCKED**
- **Mesh Asset Path**: `assets/characters/humanoid.glb`
- **Speech Synthesis Provider**: `edge-tts`

## Critical System Gaps
- [ ] **GAP**: Character rig has 0 morph targets. Skeletal lip movements are impossible without shape keys.
- [ ] **GAP**: TTS pipeline produces raw audio streams without viseme/phoneme alignment metadata.

## Architectural Requirements for 3D Lip Sync

To implement true 3D skeletal lip-syncing without faking it (e.g. scaling mouths randomly), the pipeline must resolve two sides: the **Viseme Timeline** and the **Face Morph Targets**.

### 1. The Speech Viseme Timeline (Input)
We must extract exactly *when* each speech sound occurs in the generated audio.
- **Rhubarb Lip Sync Integration (Recommended)**: An offline, open-source command-line tool that parses `.wav` or `.ogg` audio files, runs automatic speech recognition, and outputs a clean JSON timeline of Preston Blair viseme keys (A, B, C, D, E, F, G, H, X) and timings.
- **Phoneme-aware TTS**: Upgrading to a TTS service (e.g., Azure or Google TTS) that outputs SSML Speech Marks containing viseme index mappings directly.

### 2. Viseme to ARKit Blendshape Mapping
The 3D mesh must expose shape keys corresponding to viseme configurations. Below is the blueprint of how visemes map to the mesh:
- **Viseme 'A'**: `jawOpen` = 0.8, `mouthFunnel` = 0.2
- **Viseme 'E'**: `mouthStretchLeft` = 0.6, `mouthStretchRight` = 0.6, `jawOpen` = 0.2
- **Viseme 'F'**: `mouthShrugLower` = 0.5, `mouthClose` = 0.3
- **Viseme 'L'**: `jawOpen` = 0.4, `mouthPressLeft` = 0.2
- **Viseme 'M'**: `mouthClose` = 1.0
- **Viseme 'O'**: `mouthFunnel` = 0.8, `jawOpen` = 0.4
- **Viseme 'rest'**: `mouthClose` = 0.5

### 3. Missing Face Rig Assets
The current humanoid meshes possess **0 shape keys**. 
**Required Rig Upgrades**:
1. Add `mouthClose` (close lips completely for consonants M, B, P).
2. Add `jawOpen` (depress jaw for open vowels A, I).
3. Add `mouthFunnel` / `mouthPucker` (pucker lips for rounded vowels O, U).
4. Add `mouthStretchLeft` / `mouthStretchRight` (stretch lips horizontally for E).

## Feasibility Conclusion & Action Plan
- **Conclusion**: Implementing 3D skeletal lip sync is currently blocked by character asset limitations.
- **Action Plan**:
  1. Continue using 2D SadTalker facial projection endpoints for high-fidelity dialogue videos where lip sync is required (since SadTalker generates lip sync by warping face textures directly).
  2. Procure updated `humanoid_rigged.glb` assets with the 4 basic viseme blendshapes listed above before initiating skeletal Blender Lip Sync features.
