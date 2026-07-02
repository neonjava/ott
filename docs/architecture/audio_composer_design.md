# Spatial Audio Mixer & SFX Composer Design

## Purpose
Simulate a professional audio mixing studio by combining voice, background music (BGM), and contextual sound effects (SFX) using spatial sound fields, distance attenuation, and time-aligned triggers.

## Responsibilities
* **Procedural SFX Generation**: Dynamically maps narrative verbs (e.g., "strike", "walk", "jump") to specific audio tracks (e.g., clashing swords, rustling footsteps).
* **Multi-Channel Mixing & Levels**: Integrates voice, BGM, and environmental ambience with adjustable decibel volumes to prevent clipping.
* **Spatial Attenuation**: Adjusts audio gains based on camera-to-actor distance metrics.

## Public Interfaces
```python
class AudioComposer:
    def mix_tracks(self, bgm_path: str, vocal_segments: List[Dict[str, Any]], sfx_triggers: List[Dict[str, Any]], output_path: str) -> str
    def compute_spatial_gain(self, camera_distance: float) -> float
```

## Dependencies
* `ai/timeline_editing.py`: Provides shot duration boundaries.
* `movie_assembler.py`: Invoked during final stitching to mix movie master tracks.

## Data Flow
```
[Timeline Cues] -> [Procedural SFX Triggers] -> [Spatial Attenuation Gain] -> [FFmpeg Audio Mixer Compiler] -> [Master Export Track]
```

## Testing Strategy
* Unit test distance attenuation outputs for near (1.0m) and far (15.0m) coordinates.
* Verify FFmpeg command mapping structures compiled for track mixes.
