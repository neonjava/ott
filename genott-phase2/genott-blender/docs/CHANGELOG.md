# Changelog — GenOTT Movie Engine

All notable changes to this project will be documented in this file.

## [1.0.0-rc1] — 2026-06-27

### Added
* **Cycles GPU Preference Auto-Discovery**: Programmatic CUDA/OptiX preference setups inside Blender daemon, preventing CPU falling backs.
* **Procedural Torso Breathing Rotation**: Sine-wave armature keyframing wiggles to eliminate rigid mannequins during speech.
* **Spatial Audio Mixer & SFX Composer**: Attenuates dialogue gain based on camera distances and compiles layered voice/BGM/SFX tracks using FFmpeg filters.
* **Volumetric Atmospheric Scattering**: Renders volumetric fog density using Blender World nodes.
