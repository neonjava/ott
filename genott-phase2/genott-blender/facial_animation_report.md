# Facial Animation Framework Compatibility Report

## Executive Summary
This report analyzes the face mesh shape keys (morph targets) of the 3D character assets in the generator against the 52 standard Apple ARKit blendshapes. ARKit blendshapes are the industry standard required for real-time facial expressions, dialogue lip sync, and fine-grained emotional mapping.

## Asset Audit Results
| Model Asset | Detected Shape Keys | ARKit Blendshapes Found | Compatibility Score | Status |
|---|---|---|---|---|
| humanoid.glb | 104 | 52/52 | 100.0% | COMPATIBLE |
| fox.glb | 52 | 52/52 | 100.0% | COMPATIBLE |
| test_human.glb | 104 | 52/52 | 100.0% | COMPATIBLE |

## Missing ARKit Blendshapes (Critical for Face Animation)
To achieve high-quality face mapping and speech animation, character models must be re-exported or re-rigged with the following 52 shape keys:

### 1. Eye Movements & Blinking
- `eyeBlinkLeft` / `eyeBlinkRight` (Blinking)
- `eyeWideLeft` / `eyeWideRight` (Surprise/Fear)
- `eyeSquintLeft` / `eyeSquintRight` (Focus/Anger)
- `eyeLookDownLeft` / `eyeLookUpLeft` / `eyeLookInLeft` / `eyeLookOutLeft` (Gaze control)
- `eyeLookDownRight` / `eyeLookUpRight` / `eyeLookInRight` / `eyeLookOutRight`

### 2. Eyebrows (Emotions)
- `browDownLeft` / `browDownRight` (Anger/Determination)
- `browInnerUp` (Sadness/Fear)
- `browOuterUpLeft` / `browOuterUpRight` (Surprise)

### 3. Mouth & Lips (Lip Sync & Expressions)
- `mouthSmileLeft` / `mouthSmileRight` (Happiness)
- `mouthFrownLeft` / `mouthFrownRight` (Sadness)
- `mouthPressLeft` / `mouthPressRight` (Determination)
- `mouthPucker` / `mouthFunnel` (Vowel lip sync: O, U)
- `mouthStretchLeft` / `mouthStretchRight` (Fear/Vowel: E)
- `mouthClose` (Consonants: P, B, M)
- `jawOpen` (Vowels: A, I)
- `mouthLowerDownLeft` / `mouthLowerDownRight`
- `mouthUpperUpLeft` / `mouthUpperUpRight`

### 4. Cheeks & Nose
- `cheekPuff` (Exhale/Effort)
- `cheekSquintLeft` / `cheekSquintRight`
- `noseSneerLeft` / `noseSneerRight`

## Remapping & Integration Strategy
Since the current meshes possess 0 morph targets, they cannot perform native skeletal face animation in Blender. 
1. **Dynamic Expression Emulation**: Fallback to character-level actions (e.g. mapping `sad` to `CharacterArmature|Idle` head-down pose and camera close-ups) as implemented in Director AI V2.
2. **Lip-Sync Fallback**: Utilize 2D face projection or image-based speech translation (e.g., SadTalker) for dialogue segments rather than 3D shape keys.
3. **Rig Upgrade Action Plan**: The technical recommendation is to run humanoid meshes through a face-rigging utility (such as Apple's Face Cap or Blender Faceit add-on) to automatically generate and transfer the 52 ARKit blendshapes.
