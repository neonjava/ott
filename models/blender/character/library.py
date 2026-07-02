# ai/character/library.py
import os
from typing import Dict, Optional
from models.blender.character.models import CharacterProfile, OutfitDefinition, WeaponDefinition

class CharacterLibrary:
    def __init__(self, faces_dir: str):
        self.faces_dir = faces_dir
        self._characters: Dict[str, CharacterProfile] = {}
        
        from engine.characters.character_state_manager import CharacterStateManager
        self.state_manager = CharacterStateManager()
        
        self._initialize_default_library()

    def _initialize_default_library(self):
        # 1. Thor Profile
        thor = CharacterProfile(
            name="Thor",
            description="a muscular Nordic warrior with long blonde hair, blue eyes, and a light beard",
            face_reference_img=os.path.join(self.faces_dir, "thor.png"),
            voice_profile="en-GB-RyanNeural"
        )
        thor.outfits["default"] = OutfitDefinition(
            id="default",
            description="wearing heavy silver chest armor plate and a flowing bright red cape"
        )
        thor.weapons["default"] = WeaponDefinition(
            id="default",
            description="holding the Stormbreaker battleaxe reflecting lightning streaks"
        )
        thor.animations = ["landing", "fight", "standing", "walk", "raise_weapon"]
        self._characters["thor"] = thor

        # 2. Tony Stark Profile
        tony = CharacterProfile(
            name="Tony Stark",
            description="an intelligent man with dark hair, a clean-cut goatee beard, and intense eyes",
            face_reference_img=os.path.join(self.faces_dir, "tony_stark.png"),
            voice_profile="en-US-ChristopherNeural"
        )
        tony.outfits["suit"] = OutfitDefinition(
            id="suit",
            description="dressed in a premium black three-piece suit with a glowing blue arc reactor showing from the chest"
        )
        tony.outfits["ironman"] = OutfitDefinition(
            id="ironman",
            description="fully encased in the crimson and gold metallic Iron Man armor with glowing eye slits"
        )
        tony.weapons["repulsor"] = WeaponDefinition(
            id="repulsor",
            description="raising glowing repulsor gauntlets preparing to fire energy blasts"
        )
        tony.animations = ["walk", "gesture", "fly", "combat"]
        self._characters["tony_stark"] = tony

        # 3. Hulk Profile
        hulk = CharacterProfile(
            name="Hulk",
            description="a giant, green-skinned, muscular superhero with dark messy hair and angry expression",
            face_reference_img=os.path.join(self.faces_dir, "hulk.png"),
            voice_profile="en-US-GuyNeural"
        )
        hulk.outfits["default"] = OutfitDefinition(
            id="default",
            description="wearing torn tattered purple pants and bare green chest"
        )
        hulk.weapons["default"] = WeaponDefinition(
            id="default",
            description="smashing with massive green fists"
        )
        hulk.animations = ["landing", "fight", "standing", "walk", "raise_weapon"]
        self._characters["hulk"] = hulk

        # Load dynamic characters from character_registry.json
        import json
        project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        registry_path = os.path.join(project_dir, "character_registry.json")
        if os.path.exists(registry_path):
            try:
                with open(registry_path, "r") as f:
                    registry = json.load(f)
                for key, val in registry.items():
                    # Handle face image reference
                    face_filename = f"{key}.png"
                    face_path = os.path.join(self.faces_dir, face_filename)
                    if not os.path.exists(face_path):
                        default_face = os.path.join(self.faces_dir, "tony_stark.png")
                        if os.path.exists(default_face):
                            import shutil
                            try:
                                shutil.copy(default_face, face_path)
                                print(f"[CharacterLibrary] Copied default face reference to {face_path}")
                            except Exception as e:
                                print(f"[CharacterLibrary] Failed to copy face for {key}: {e}")
                        else:
                            # Write empty file if default doesn't exist
                            try:
                                with open(face_path, "wb") as dummy:
                                    dummy.write(b"")
                            except Exception:
                                pass
                    
                    profile = CharacterProfile(
                        name=val.get("name", key.title()),
                        description=val.get("description", ""),
                        face_reference_img=face_path,
                        voice_profile=val.get("voice", "en-US-ChristopherNeural"),
                        animations=list(val.get("action_map", {}).keys())
                    )
                    self._characters[key] = profile
            except Exception as e:
                print(f"[CharacterLibrary] Error loading character registry: {e}")

    def get_character(self, name: str) -> Optional[CharacterProfile]:
        key = name.lower().replace(" ", "_")
        return self._characters.get(key)

