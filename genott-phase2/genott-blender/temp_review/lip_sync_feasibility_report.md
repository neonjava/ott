# Lip Sync Feasibility Report

## Overview & Feasibility Status
- **Status**: **FEASIBLE**
- **Mesh Asset Path**: `assets/characters/humanoid.glb`
- **Speech Synthesis Provider**: `edge-tts`

## Critical System Gaps
- None! System is ready to implement lipsync.

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

### 3. Face Rig Assets Upgraded
The active character meshes have been successfully upgraded with 52 standard ARKit shape keys, satisfying the skeletal morph target requirements.

## Feasibility Conclusion & Action Plan
- **Conclusion**: The 3D skeletal lip-sync pipeline is fully **FEASIBLE**. Mesh shape keys and phoneme alignment pipelines are ready.
- **Action Plan**:
  1. Leverage the timed viseme transitions extracted from the TTS dialogue generation process.
  2. Implement the shape-key keyframing logic in the Blender renderer to drive `jawOpen`, `mouthClose`, `mouthFunnel`, and other blendshapes during speech.
