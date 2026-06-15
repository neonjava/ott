# ai/renderer/action_mapper.py
import os
from typing import Dict, List, Optional

class ActionMapper:
    def __init__(self, animations_dir: str):
        self.animations_dir = animations_dir
        # Maps generic storyboard phrases/actions to specific animations
        self._action_map: Dict[str, str] = {
            "fly": "fly.fbx",
            "land": "land.fbx",
            "walk": "walk.fbx",
            "run": "run.fbx",
            "talk": "talk.fbx",
            "attack": "attack.fbx",
            "raise_weapon": "raise_weapon.fbx",
            "victory_pose": "victory_pose.fbx",
            "standing": "talk.fbx" # Fallback
        }

    def get_animation_path(self, action_name: str) -> Optional[str]:
        """Resolve an action term to its corresponding anim asset path."""
        action_key = action_name.lower().strip()
        filename = self._action_map.get(action_key)
        if filename:
            path = os.path.join(self.animations_dir, filename)
            # Create a placeholder on the fly if it doesn't exist for demo safety
            if not os.path.exists(path):
                os.makedirs(self.animations_dir, exist_ok=True)
                with open(path, "w") as f:
                    f.write("MOCK FBX CONTENT")
            return path
        
        # Default fallback to talk/idle fbx
        fallback_path = os.path.join(self.animations_dir, "talk.fbx")
        if not os.path.exists(fallback_path):
            os.makedirs(self.animations_dir, exist_ok=True)
            with open(fallback_path, "w") as f:
                f.write("MOCK FBX CONTENT")
        return fallback_path

    def extract_actions(self, visual_description: str) -> List[str]:
        """Scan a description and extract known animation tags."""
        desc_lower = visual_description.lower()
        extracted = []
        for key in self._action_map.keys():
            if key in desc_lower:
                extracted.append(key)
        
        if not extracted:
            # Fallback to talk animation
            extracted.append("talk")
        return extracted
