# Facial Micro-Expressions & Breathing Automation Design

## Purpose
Eliminate the robotic, static look of CGI characters during speech by programmatically inserting blinking keyframes, subtle eye/neck saccades, and rhythmic breathing posture wiggles.

## Responsibilities
* **Blinking Shape Keys**: Programmatically drive the character's eye closure shape keys at random intervals (every 2.5 - 4.0 seconds).
* **Bone Saccades**: Inject minor neck and head rotation noise to simulate gaze shifts.
* **Torso Breathing**: Apply a low-frequency sinus loop rotation to the spine/chest bone to simulate chest expansion during respiration.

## Public Interfaces
To be integrated directly into the Blender rendering loops inside `blender_daemon.py`.

## Data Flow
```
[Dialogue Timeline] -> [Calculate Blink Frames] -> [Inject Shape Key Values] -> [Sine Wave Spine Rotations] -> [Fitted Armature Render]
```

## Testing Strategy
* Verify that the Blender daemon does not crash when applying shape key properties to armatures.
* Validate keyframe tracks are properly generated in the animation action curves.
