# ai/renderer/blender.py
"""
Blender-based video renderer for the movie pipeline.
Invokes Blender CLI with render_script.py to produce real rendered MP4 videos.
"""
import os
import json
import subprocess
from ai.renderer.base import VideoRenderer
from ai.storyboard.models import ScenePlan
from ai.renderer.action_mapper import ActionMapper

# Map character names to their GLB files and embedded action names
CHARACTER_REGISTRY = {
    "thor": {
        "glb": "humanoid.glb",
        "action_map": {
            "idle": "CharacterArmature|Idle",
            "walk": "CharacterArmature|Run", 
            "run": "CharacterArmature|Run",
            "attack": "CharacterArmature|Punch",
            "punch": "CharacterArmature|Punch",
            "jump": "CharacterArmature|Jump",
            "death": "CharacterArmature|Death",
            "wave": "CharacterArmature|Wave",
            "duck": "CharacterArmature|Duck",
            "landing": "CharacterArmature|Jump_Land",
            "standing": "CharacterArmature|Idle",
            "talk": "CharacterArmature|Idle",
            "raise_weapon": "CharacterArmature|Punch",
            "fly": "CharacterArmature|Jump",
            "victory": "CharacterArmature|Wave",
        }
    },
    "tony_stark": {
        "glb": "humanoid.glb",
        "action_map": {
            "idle": "CharacterArmature|Idle",
            "walk": "CharacterArmature|Run",
            "run": "CharacterArmature|Run",
            "attack": "CharacterArmature|Punch",
            "fly": "CharacterArmature|Jump",
            "landing": "CharacterArmature|Jump_Land",
            "standing": "CharacterArmature|Idle",
            "talk": "CharacterArmature|Idle",
            "victory": "CharacterArmature|Wave",
        }
    },
    "hulk": {
        "glb": "humanoid.glb",
        "action_map": {
            "idle": "CharacterArmature|Idle",
            "walk": "CharacterArmature|Run",
            "run": "CharacterArmature|Run",
            "attack": "CharacterArmature|Punch",
            "smash": "CharacterArmature|Punch",
            "jump": "CharacterArmature|Jump",
            "landing": "CharacterArmature|Jump_Land",
            "standing": "CharacterArmature|Idle",
            "roar": "CharacterArmature|HitReact",
            "talk": "CharacterArmature|Idle",
        }
    },
    "humanoid": {
        "glb": "humanoid.glb",
        "action_map": {
            "idle": "CharacterArmature|Idle",
            "walk": "CharacterArmature|Run",
            "run": "CharacterArmature|Run",
            "attack": "CharacterArmature|Punch",
            "jump": "CharacterArmature|Jump",
            "death": "CharacterArmature|Death",
            "wave": "CharacterArmature|Wave",
            "duck": "CharacterArmature|Duck",
            "landing": "CharacterArmature|Jump_Land",
            "standing": "CharacterArmature|Idle",
            "talk": "CharacterArmature|Idle",
        }
    },
    "fox": {
        "glb": "fox.glb",
        "action_map": {
            "walk": "Walk",
            "run": "Run",
            "survey": "Survey",
            "idle": "Survey",
            "standing": "Survey",
            "talk": "Survey",
        }
    }
}


class BlenderVideoRenderer(VideoRenderer):
    def __init__(self, assets_dir: str = None):
        project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Use the consolidated assets directory (with real models)
        self.assets_dir = assets_dir or os.path.join(project_dir, "assets")
        self.project_dir = project_dir
        
        # Ensure directories exist
        os.makedirs(os.path.join(self.assets_dir, "characters"), exist_ok=True)
        os.makedirs(os.path.join(self.assets_dir, "animations"), exist_ok=True)

    def _resolve_character(self, character_name: str):
        """Resolve character name to GLB path and action map."""
        key = character_name.lower().replace(" ", "_")
        
        if key in CHARACTER_REGISTRY:
            reg = CHARACTER_REGISTRY[key]
        else:
            # Default to humanoid for unknown characters
            reg = CHARACTER_REGISTRY["humanoid"]
        
        glb_path = os.path.join(self.assets_dir, "characters", reg["glb"])
        return glb_path, reg["action_map"]

    def _resolve_action(self, action_description: str, action_map: dict) -> tuple:
        """Map a storyboard action description to an animation action name.
        Returns (blender_action_name, fbx_path_or_None)."""
        desc_lower = action_description.lower()
        
        # Try exact match first
        if desc_lower in action_map:
            return action_map[desc_lower], None
        
        # Try keyword matching
        action_keywords = [
            ("fly", "fly"), ("flying", "fly"), ("launch", "fly"), ("blast", "fly"),
            ("land", "landing"), ("impact", "landing"), ("descend", "landing"),
            ("walk", "walk"), ("approach", "walk"), ("moving", "walk"),
            ("run", "run"), ("charge", "run"), ("sprint", "run"), ("rushing", "run"),
            ("attack", "attack"), ("fight", "attack"), ("swing", "attack"), ("smash", "attack"),
            ("punch", "punch"), ("hit", "punch"), ("strike", "punch"),
            ("jump", "jump"), ("leap", "jump"), ("leaping", "jump"),
            ("stand", "standing"), ("standing", "standing"), ("guard", "standing"),
            ("talk", "talk"), ("speak", "talk"), ("say", "talk"),
            ("raise", "raise_weapon"), ("summon", "raise_weapon"), ("raising", "raise_weapon"),
            ("wave", "wave"), ("victory", "victory"), ("triumph", "victory"),
            ("roar", "roar"), ("shout", "roar"),
            ("die", "death"), ("dead", "death"), ("fall", "death"),
            ("duck", "duck"), ("dodge", "duck"), ("crouch", "duck"),
        ]
        
        for keyword, action_key in action_keywords:
            if keyword in desc_lower:
                if action_key in action_map:
                    return action_map[action_key], None
        
        # Default to idle
        return action_map.get("idle", action_map.get("standing", list(action_map.values())[0])), None

    def _find_blender(self) -> str:
        """Find Blender executable."""
        # Try flatpak first
        try:
            result = subprocess.run(
                ["flatpak", "run", "org.blender.Blender", "--version"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10
            )
            if result.returncode == 0:
                return "flatpak"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        # Try system blender
        try:
            result = subprocess.run(
                ["blender", "--version"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10
            )
            if result.returncode == 0:
                return "system"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        return None

    def render_scene(self, plan: ScenePlan, seed: int, output_path: str, generation_id: str = None) -> str:
        """Render a scene using real Blender CLI."""
        # Resolve character and action
        char_path, action_map = self._resolve_character(plan.character_name or "humanoid")
        blender_action, fbx_path = self._resolve_action(plan.action or "idle", action_map)

        print(f"[BlenderRenderer] Scene {plan.scene_number}: {plan.character_name} -> {blender_action}")
        print(f"[BlenderRenderer] Character: {char_path} (exists: {os.path.exists(char_path)})")

        # Verify character file is real (not a placeholder)
        if not os.path.exists(char_path) or os.path.getsize(char_path) < 100:
            raise FileNotFoundError(
                f"Character GLB not found or is a placeholder: {char_path}. "
                f"Please add a real GLB model to assets/characters/"
            )

        # Build render payload
        render_payload = {
            "character_name": (plan.character_name or "humanoid").lower().replace(" ", "_"),
            "action": blender_action,
            "action_file": fbx_path or "",
            "character_file": os.path.abspath(char_path),
            "location": plan.location or "environment",
            "camera_shot": plan.camera_shot or "cinematic wide",
            "duration": plan.duration or 4.0,
            "output_path": os.path.abspath(output_path)
        }

        # Write payload JSON
        payload_path = os.path.abspath(os.path.join(
            self.project_dir, "static", "videos",
            f"payload_{generation_id or 'scene'}_{plan.scene_number}.json"
        ))
        os.makedirs(os.path.dirname(payload_path), exist_ok=True)
        with open(payload_path, "w") as f:
            json.dump(render_payload, f)

        # Find render script
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "blender_render_script.py"))

        # Find Blender
        blender_mode = self._find_blender()

        if blender_mode == "flatpak":
            cmd = [
                "flatpak", "run", "org.blender.Blender",
                "-b", "--python", script_path,
                "--", payload_path
            ]
        elif blender_mode == "system":
            cmd = [
                "blender", "-b",
                "--python", script_path,
                "--", payload_path
            ]
        else:
            raise RuntimeError(
                "Blender not found. Install via: flatpak install org.blender.Blender "
                "or install blender system package."
            )

        print(f"[BlenderRenderer] Executing Blender CLI ({blender_mode})...")
        process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=300)
        
        if process.returncode != 0:
            error_msg = process.stderr or process.stdout
            print(f"[BlenderRenderer] STDERR: {error_msg[-500:]}")
            raise RuntimeError(f"Blender render failed (exit {process.returncode}): {error_msg[-300:]}")

        # Verify output exists
        if not os.path.exists(output_path):
            raise RuntimeError(f"Blender completed but output file missing: {output_path}")

        # Cleanup payload
        if os.path.exists(payload_path):
            os.remove(payload_path)

        print(f"[BlenderRenderer] Scene {plan.scene_number} rendered: {output_path} ({os.path.getsize(output_path)} bytes)")
        return output_path
