# ai/character/models.py
from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class OutfitDefinition:
    id: str
    description: str             # Visual prompt details (e.g. "wearing heavy silver armor and a flowing red cape")
    mesh_path: Optional[str] = None
    color_palette: List[str] = field(default_factory=list)

@dataclass
class WeaponDefinition:
    id: str
    description: str             # e.g., "holding a glowing Stormbreaker axe"
    model_path: Optional[str] = None

@dataclass
class CharacterProfile:
    name: str
    description: str             # Base look (e.g. "a muscular Nordic warrior with long blonde hair and blue eyes")
    face_reference_img: str      # Path to local facial reference
    voice_profile: str           # Edge-TTS voice identifier
    outfits: Dict[str, OutfitDefinition] = field(default_factory=dict)
    weapons: Dict[str, WeaponDefinition] = field(default_factory=dict)
    animations: List[str] = field(default_factory=list)
