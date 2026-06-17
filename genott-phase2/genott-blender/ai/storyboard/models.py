# ai/storyboard/models.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class DialogueLine:
    speaker: str
    text: str
    voice_profile: str

@dataclass
class ScenePlan:
    scene_number: int
    character_name: Optional[str]
    location: str
    action: str
    camera_shot: str
    duration: float
    dialogue: Optional[DialogueLine] = None
    narration: Optional[str] = None
    visual_description: str = ""
    mood: Optional[str] = "neutral"
    characters: Optional[list] = None
    character_placements: Optional[dict] = None
    camera_movement: Optional[str] = 'static'



