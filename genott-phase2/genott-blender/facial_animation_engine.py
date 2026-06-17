#!/usr/bin/env python3
"""
facial_animation_engine.py
Maps emotional states to face mesh blendshapes. Inspections GLB files to extract
target shape keys, performs compatibility analysis against 52 standard ARKit blendshapes,
and outputs mapping and compatibility reports.
"""
import os
import struct
import json
from typing import Dict, Any, List, Tuple

# The 52 standard ARKit blendshape keys
ARKIT_BLENDSHAPES = [
    "eyeBlinkLeft", "eyeLookDownLeft", "eyeLookInLeft", "eyeLookOutLeft", "eyeLookUpLeft", "eyeSquintLeft", "eyeWideLeft",
    "eyeBlinkRight", "eyeLookDownRight", "eyeLookInRight", "eyeLookOutRight", "eyeLookUpRight", "eyeSquintRight", "eyeWideRight",
    "jawForward", "jawLeft", "jawRight", "jawOpen", "mouthClose", "mouthFunnel", "mouthPucker", "mouthLeft", "mouthRight",
    "mouthSmileLeft", "mouthSmileRight", "mouthFrownLeft", "mouthFrownRight", "mouthDimpleLeft", "mouthDimpleRight",
    "mouthStretchLeft", "mouthStretchRight", "mouthRollLower", "mouthRollUpper", "mouthShrugLower", "mouthShrugUpper",
    "mouthPressLeft", "mouthPressRight", "mouthLowerDownLeft", "mouthLowerDownRight", "mouthUpperUpLeft", "mouthUpperUpRight",
    "browDownLeft", "browDownRight", "browInnerUp", "browOuterUpLeft", "browOuterUpRight", "cheekPuff", "cheekSquintLeft",
    "cheekSquintRight", "noseSneerLeft", "noseSneerRight", "tongueOut"
]

# Standard mapping from emotions to blendshape intensity profiles
EMOTION_TO_BLENDSHAPES = {
    "happy": {
        "mouthSmileLeft": 0.8,
        "mouthSmileRight": 0.8,
        "browInnerUp": 0.3,
        "cheekSquintLeft": 0.4,
        "cheekSquintRight": 0.4
    },
    "sad": {
        "mouthFrownLeft": 0.9,
        "mouthFrownRight": 0.9,
        "browOuterUpLeft": 0.5,
        "browOuterUpRight": 0.5,
        "eyeSquintLeft": 0.3,
        "eyeSquintRight": 0.3
    },
    "angry": {
        "browDownLeft": 1.0,
        "browDownRight": 1.0,
        "mouthPressLeft": 0.6,
        "mouthPressRight": 0.6,
        "eyeSquintLeft": 0.5,
        "eyeSquintRight": 0.5
    },
    "fear": {
        "jawOpen": 0.5,
        "mouthStretchLeft": 0.7,
        "mouthStretchRight": 0.7,
        "browInnerUp": 0.8,
        "eyeWideLeft": 0.6,
        "eyeWideRight": 0.6
    },
    "surprise": {
        "jawOpen": 0.8,
        "eyeWideLeft": 0.9,
        "eyeWideRight": 0.9,
        "browInnerUp": 0.9
    },
    "hope": {
        "mouthSmileLeft": 0.4,
        "mouthSmileRight": 0.4,
        "browInnerUp": 0.2
    },
    "determination": {
        "browDownLeft": 0.4,
        "browDownRight": 0.4,
        "mouthClose": 0.5,
        "mouthPressLeft": 0.5,
        "mouthPressRight": 0.5
    }
}

class FacialAnimationEngine:
    def __init__(self):
        pass

    def extract_blendshape_names_from_glb(self, glb_path: str) -> List[str]:
        """
        Parses a GLB file's binary structure and extracts target morph names (shape keys)
        from mesh primitive extras.
        """
        if not os.path.exists(glb_path):
            return []

        try:
            with open(glb_path, "rb") as f:
                header = f.read(12)
                if len(header) < 12:
                    return []

                magic, version, length = struct.unpack("<4sII", header)
                if magic != b"glTF":
                    return []

                # Read chunk 0 (JSON Chunk)
                chunk_header = f.read(8)
                if len(chunk_header) < 8:
                    return []

                chunk_length, chunk_type = struct.unpack("<II", chunk_header)
                # Chunk Type 0x4E4F534A is JSON
                if chunk_type != 0x4E4F534A:
                    return []

                json_bytes = f.read(chunk_length)
                gltf_json = json.loads(json_bytes.decode("utf-8", errors="ignore"))

                # Traverse meshes to look for shape key target names
                target_names = []
                meshes = gltf_json.get("meshes", [])
                for mesh in meshes:
                    primitives = mesh.get("primitives", [])
                    for prim in primitives:
                        extras = prim.get("extras", {})
                        names = extras.get("targetNames", [])
                        for name in names:
                            if name not in target_names:
                                target_names.append(name)

                return target_names
        except Exception as e:
            print(f"[FacialAnimationEngine] Error reading GLB {glb_path}: {e}")
            return []

    def evaluate_compatibility(self, glb_path: str) -> Dict[str, Any]:
        """
        Evaluates a character model's facial shape key compatibility against ARKit standards.
        """
        detected = self.extract_blendshape_names_from_glb(glb_path)
        
        # Calculate intersection
        available_arkit = [b for b in ARKIT_BLENDSHAPES if b in detected]
        missing_arkit = [b for b in ARKIT_BLENDSHAPES if b not in detected]
        
        compatibility_score = (len(available_arkit) / len(ARKIT_BLENDSHAPES)) * 100

        # remap recommendations
        remappings = {}
        for missing in missing_arkit:
            # Check if there is a similar case-insensitive name or simple substring match
            for det in detected:
                if det.lower() == missing.lower() or det.lower().replace("_", "") == missing.lower():
                    remappings[missing] = det
                    break

        return {
            "model_path": glb_path,
            "total_detected_blendshapes": len(detected),
            "available_arkit_count": len(available_arkit),
            "missing_arkit_count": len(missing_arkit),
            "compatibility_score": round(compatibility_score, 1),
            "available_blendshapes": detected,
            "missing_arkit_blendshapes": missing_arkit,
            "suggested_remappings": remappings
        }

    def generate_facial_pose(self, emotion: str, available_blendshapes: List[str]) -> Dict[str, float]:
        """
        Generates shape key weights for the given emotion, filtering or remapping based
        on what the mesh supports.
        """
        target_profile = EMOTION_TO_BLENDSHAPES.get(emotion.lower(), {})
        active_weights = {}

        for bshape, weight in target_profile.items():
            if bshape in available_blendshapes:
                active_weights[bshape] = weight
            else:
                # Try simple case-insensitive mapping
                matched = False
                for av in available_blendshapes:
                    if av.lower() == bshape.lower():
                        active_weights[av] = weight
                        matched = True
                        break
                if not matched:
                    # Log missing target
                    pass
        return active_weights

if __name__ == "__main__":
    engine = FacialAnimationEngine()
    glb_test_path = "assets/characters/humanoid.glb"
    report = engine.evaluate_compatibility(glb_test_path)
    print(json.dumps(report, indent=2))
