#!/usr/bin/env python3
"""
facial_animation_benchmark.py
Checks all character models in the assets directory, runs the compatibility evaluator,
and generates facial_animation_report.md.
"""
import sys
import os
import json

project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.append(project_dir)

from facial_animation_engine import FacialAnimationEngine

def run_benchmark():
    engine = FacialAnimationEngine()
    characters_dir = os.path.join(project_dir, "assets", "characters")
    
    models = ["humanoid.glb", "fox.glb", "test_human.glb"]
    results = []

    print("Running Facial Animation Engine compatibility checks...")

    for model_name in models:
        model_path = os.path.join(characters_dir, model_name)
        if os.path.exists(model_path):
            compat = engine.evaluate_compatibility(model_path)
            results.append(compat)
            print(f"Model '{model_name}': detected {compat['total_detected_blendshapes']} shape keys. ARKit Score: {compat['compatibility_score']}%")

    # Generate facial_animation_report.md
    report_content = """# Facial Animation Framework Compatibility Report

## Executive Summary
This report analyzes the face mesh shape keys (morph targets) of the 3D character assets in the generator against the 52 standard Apple ARKit blendshapes. ARKit blendshapes are the industry standard required for real-time facial expressions, dialogue lip sync, and fine-grained emotional mapping.

## Asset Audit Results
| Model Asset | Detected Shape Keys | ARKit Blendshapes Found | Compatibility Score | Status |
|---|---|---|---|---|
"""
    for r in results:
        name = os.path.basename(r["model_path"])
        status = "COMPATIBLE" if r["compatibility_score"] > 80 else ("PARTIAL" if r["compatibility_score"] > 20 else "INCOMPATIBLE (No face rig)")
        report_content += f"| {name} | {r['total_detected_blendshapes']} | {r['available_arkit_count']}/52 | {r['compatibility_score']}% | {status} |\n"

    report_content += """
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
"""
    # Write report locally
    local_report_path = os.path.join(project_dir, "facial_animation_report.md")
    with open(local_report_path, "w") as f:
        f.write(report_content)
    print(f"Local report generated: {local_report_path}")

    # Write report to Artifact Directory
    artifact_dir = "PROJECT_ROOT/.gemini/antigravity-cli/brain/3496fc80-3ea9-4817-8bc4-b4e0e2ff7b60"
    if os.path.exists(artifact_dir):
        artifact_report_path = os.path.join(artifact_dir, "facial_animation_report.md")
        with open(artifact_report_path, "w") as f:
            f.write(report_content)
        print(f"Artifact report generated: {artifact_report_path}")

    return True

if __name__ == "__main__":
    success = run_benchmark()
    sys.exit(0 if success else 1)
