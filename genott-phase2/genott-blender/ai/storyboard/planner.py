# ai/storyboard/planner.py
import json
import requests
from typing import List
from ai.storyboard.models import ScenePlan, DialogueLine
from ai.character.library import CharacterLibrary

# Built-in cinematic story templates (6 scenes each for 30-second clips)
HERO_STORIES = {
    "thor": {
        "title": "Thor: Wrath of the Storm",
        "scenes": [
            {
                "scene_number": 1,
                "character_name": "Thor",
                "location": "dark storm clouds above a shattered mountain peak",
                "action": "descending from the sky with lightning trailing behind",
                "camera_shot": "low-angle dramatic wide shot",
                "duration": 5.0,
                "dialogue": "Asgard's fury arrives!",
                "narration": "From the raging skies, a god descends upon the broken world."
            },
            {
                "scene_number": 2,
                "character_name": "Thor",
                "location": "ancient battlefield littered with debris and burning ruins",
                "action": "landing with a thunderous ground-shaking impact",
                "camera_shot": "close-up tracking shot with dust explosion",
                "duration": 5.0,
                "dialogue": "You dare threaten this realm?",
                "narration": "The ground cracks beneath divine power."
            },
            {
                "scene_number": 3,
                "character_name": "Thor",
                "location": "center of a burning village surrounded by dark creatures",
                "action": "raising the Stormbreaker battleaxe overhead summoning lightning",
                "camera_shot": "rotating orbit shot around the character",
                "duration": 5.0,
                "dialogue": "Feel the storm's wrath!",
                "narration": "Lightning arcs from the clouds into the weapon, illuminating the darkness."
            },
            {
                "scene_number": 4,
                "character_name": "Thor",
                "location": "a rain-soaked crumbling stone bridge over a chasm",
                "action": "charging forward swinging the Stormbreaker through enemies",
                "camera_shot": "side-tracking action shot with motion blur",
                "duration": 5.0,
                "dialogue": "For Asgard!",
                "narration": "Each swing of the axe sends shockwaves through the battlefield."
            },
            {
                "scene_number": 5,
                "character_name": "Thor",
                "location": "a vast open plain under clearing storm clouds with sunlight breaking through",
                "action": "slamming the Stormbreaker into the ground creating a massive lightning explosion",
                "camera_shot": "wide epic aerial shot pulling back",
                "duration": 5.0,
                "dialogue": "This ends now!",
                "narration": "A column of lightning erupts from the earth to the heavens."
            },
            {
                "scene_number": 6,
                "character_name": "Thor",
                "location": "golden sunset over a peaceful restored village",
                "action": "standing tall with cape billowing in the wind looking at the horizon",
                "camera_shot": "cinematic silhouette wide shot at golden hour",
                "duration": 5.0,
                "dialogue": "",
                "narration": "The storm passes. A god watches over the world he saved."
            }
        ]
    },
    "tony_stark": {
        "title": "Iron Man: Arc of Power",
        "scenes": [
            {
                "scene_number": 1,
                "character_name": "Tony Stark",
                "location": "high-tech underground workshop with holographic displays",
                "action": "standing before holographic armor blueprints, touching interface panels",
                "camera_shot": "medium shot with blue holographic reflections",
                "duration": 5.0,
                "dialogue": "Time to upgrade.",
                "narration": "In the depths of his lab, a genius prepares for war."
            },
            {
                "scene_number": 2,
                "character_name": "Tony Stark",
                "location": "armoring chamber with robotic arms assembling the suit",
                "action": "suiting up as armor plates attach to his body piece by piece",
                "camera_shot": "tight tracking shot following armor assembly",
                "duration": 5.0,
                "dialogue": "JARVIS, full power.",
                "narration": "Metal meets flesh as the Iron Man is born once more."
            },
            {
                "scene_number": 3,
                "character_name": "Tony Stark",
                "location": "launchpad on top of Stark Tower under a night sky",
                "action": "blasting off from the tower with repulsor jets firing",
                "camera_shot": "upward tracking shot following the launch",
                "duration": 5.0,
                "dialogue": "Let's fly.",
                "narration": "A streak of light cuts through the Manhattan skyline."
            },
            {
                "scene_number": 4,
                "character_name": "Tony Stark",
                "location": "above the clouds with the sun gleaming off the armor",
                "action": "flying at high speed through cloud formations",
                "camera_shot": "close-up helmet shot with cloud reflections",
                "duration": 5.0,
                "dialogue": "",
                "narration": "Above the world, iron meets the sky."
            },
            {
                "scene_number": 5,
                "character_name": "Tony Stark",
                "location": "destroyed city street with fires and overturned vehicles",
                "action": "landing hard and firing repulsor beams at incoming threats",
                "camera_shot": "dynamic low-angle action shot",
                "duration": 5.0,
                "dialogue": "You picked the wrong city.",
                "narration": "Repulsor fire illuminates the wreckage with deadly precision."
            },
            {
                "scene_number": 6,
                "character_name": "Tony Stark",
                "location": "rooftop overlooking a saved city at dawn",
                "action": "standing with faceplate up, arc reactor glowing softly",
                "camera_shot": "wide cinematic shot with sunrise behind",
                "duration": 5.0,
                "dialogue": "I am Iron Man.",
                "narration": "The city sleeps safe. The man in the machine stands guard."
            }
        ]
    },
    "hulk": {
        "title": "Hulk: Rage Unleashed",
        "scenes": [
            {
                "scene_number": 1,
                "character_name": "Hulk",
                "location": "dark military containment facility with flashing red alarm lights",
                "action": "transformation sequence, muscles expanding, skin turning green",
                "camera_shot": "extreme close-up on eyes turning green, pulling to wide",
                "duration": 5.0,
                "dialogue": "HULK... SMASH!",
                "narration": "Behind reinforced walls, something unstoppable awakens."
            },
            {
                "scene_number": 2,
                "character_name": "Hulk",
                "location": "collapsing concrete bunker with steel walls bending",
                "action": "smashing through reinforced walls with bare fists",
                "camera_shot": "tracking shot following destruction path",
                "duration": 5.0,
                "dialogue": "",
                "narration": "Concrete and steel are nothing against pure rage."
            },
            {
                "scene_number": 3,
                "character_name": "Hulk",
                "location": "city intersection with abandoned cars and cracked asphalt",
                "action": "leaping high into the air over skyscrapers",
                "camera_shot": "dramatic upward tracking shot following the leap",
                "duration": 5.0,
                "dialogue": "RAAAAAH!",
                "narration": "The green giant launches skyward, leaving craters in his wake."
            },
            {
                "scene_number": 4,
                "character_name": "Hulk",
                "location": "demolished building rooftop with dust and rubble everywhere",
                "action": "grabbing a massive piece of debris and hurling it at enemies",
                "camera_shot": "wide action shot with slow-motion debris",
                "duration": 5.0,
                "dialogue": "",
                "narration": "Buildings become weapons in the hands of a titan."
            },
            {
                "scene_number": 5,
                "character_name": "Hulk",
                "location": "rain-soaked crater in the middle of a destroyed street",
                "action": "pounding both fists into the ground creating a massive shockwave",
                "camera_shot": "low-angle shot with shockwave rippling outward",
                "duration": 5.0,
                "dialogue": "HULK STRONGEST THERE IS!",
                "narration": "The earth itself trembles under the fury of the Hulk."
            },
            {
                "scene_number": 6,
                "character_name": "Hulk",
                "location": "quiet forest clearing at twilight with soft green light",
                "action": "standing still, breathing heavily, slowly calming down",
                "camera_shot": "wide cinematic shot with soft backlighting",
                "duration": 5.0,
                "dialogue": "",
                "narration": "The rage subsides. The beast rests. For now."
            }
        ]
    }
}


class ScenePlanner:
    def __init__(self, char_library: CharacterLibrary, ollama_url: str = "http://localhost:11434/api/chat", model: str = "llama3.2"):
        self.char_library = char_library
        self.ollama_url = ollama_url
        self.model = model

    def plan_rule_based(self, script: str, character: str) -> List[ScenePlan]:
        import re
        script_lower = script.lower()
        
        # Rule-based verb extraction
        verbs = ["walk", "wave", "jump", "idle", "attack", "run"]
        found_actions = []
        
        # Extract verbs in order they appear in text
        words = re.findall(r'\b[a-z]+\b', script_lower)
        for word in words:
            for verb in verbs:
                if verb in word and verb not in [a["action"] for a in found_actions]:
                    # Default duration mappings
                    duration = 4.0
                    if verb == "walk": duration = 5.0
                    elif verb == "wave": duration = 3.0
                    elif verb == "jump": duration = 4.0
                    elif verb == "attack": duration = 4.0
                    
                    found_actions.append({"action": verb, "duration": duration})
                    
        # Fallback if no verbs found
        if not found_actions:
            found_actions.append({"action": "idle", "duration": 4.0})
            
        # Extract potential dialogue from quotes
        dialogue_match = re.search(r'\"([^\"]+)\"|\'([^\']+)\'', script)
        dialogue_text = dialogue_match.group(1) or dialogue_match.group(2) if dialogue_match else None

        plans = []
        for i, act in enumerate(found_actions):
            # Only assign dialogue to the first scene to avoid repeating it
            scene_diag = None
            if i == 0 and dialogue_text:
                char_profile = self.char_library.get_character(character)
                voice = char_profile.voice_profile if char_profile else "en-US-ChristopherNeural"
                scene_diag = DialogueLine(speaker=character, text=dialogue_text, voice_profile=voice)
                
            plan = ScenePlan(
                scene_number=i + 1,
                character_name=character,
                location="environment",
                action=act["action"],
                camera_shot="cinematic wide",
                duration=act["duration"],
                dialogue=scene_diag,
                narration=None
            )
            plans.append(plan)
            
        return plans

    def plan_story(self, user_prompt: str, scene_count: int = 3) -> List[ScenePlan]:
        # First try to detect if this is a known hero and use built-in stories
        prompt_lower = user_prompt.lower()
        for hero_key, story in HERO_STORIES.items():
            if hero_key in prompt_lower or hero_key.replace("_", " ") in prompt_lower:
                print(f"[ScenePlanner] Using built-in story template for: {hero_key}")
                return self._parse_scenes(story["scenes"][:scene_count])

        # Try Ollama for custom prompts
        try:
            return self._query_ollama(user_prompt, scene_count)
        except Exception as e:
            print(f"[ScenePlanner Error, using Thor fallback]: {e}")
            # Fallback to Thor story
            return self._parse_scenes(HERO_STORIES["thor"]["scenes"][:scene_count])

    def _parse_scenes(self, raw_scenes: list) -> List[ScenePlan]:
        plans = []
        for item in raw_scenes:
            char_name = item.get("character_name")
            char_profile = self.char_library.get_character(char_name) if char_name else None

            dialogue = None
            diag_text = item.get("dialogue", "").strip()
            if diag_text and char_name:
                voice = char_profile.voice_profile if char_profile else "en-US-ChristopherNeural"
                dialogue = DialogueLine(speaker=char_name, text=diag_text, voice_profile=voice)

            plan = ScenePlan(
                scene_number=int(item.get("scene_number", 1)),
                character_name=char_name,
                location=item.get("location", "unknown area"),
                action=item.get("action", "standing"),
                camera_shot=item.get("camera_shot", "cinematic wide"),
                duration=float(item.get("duration", 5.0)),
                dialogue=dialogue,
                narration=item.get("narration")
            )
            plans.append(plan)
        return plans

    def _query_ollama(self, user_prompt: str, scene_count: int) -> List[ScenePlan]:
        system_prompt = """You are a film script supervisor. Break the story down into sequential, structured cinematic scenes.
For each scene, output ONLY valid JSON using this format structure:
{
  "title": "Short film title",
  "scenes": [
    {
      "scene_number": 1,
      "character_name": "Thor",
      "location": "shattered battlefield during a lightning storm",
      "action": "landing",
      "camera_shot": "low-angle wide cinematic tracking shot",
      "duration": 5.0,
      "dialogue": "I have arrived, villains!",
      "narration": "The sky darkens as a legendary hero returns."
    }
  ]
}
Ensure character names match known heroes ('Thor', 'Tony Stark', 'Hulk') if present."""

        query_prompt = f"Break down this story into exactly {scene_count} scenes:\n{user_prompt}\nReturn JSON strictly matching the format."

        response = requests.post(
            self.ollama_url,
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query_prompt}
                ],
                "format": "json",
                "stream": False
            },
            timeout=90
        )
        raw = response.json().get("message", {}).get("content", "{}")
        parsed = json.loads(raw)
        raw_scenes = parsed.get("scenes", [])

        if not raw_scenes:
            raise ValueError("Ollama returned empty scenes")

        return self._parse_scenes(raw_scenes)
