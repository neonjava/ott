# ai/director_intelligence.py
"""
Director Intelligence Engine — The cinematic brain of the movie.

Generates context-aware, reasoning-backed DirectorDecision objects before rendering every shot
by analyzing the screenplay, previous/next shot contexts, character emotions, environment, and pacing.
"""
from typing import Dict, Any, List, Optional, Tuple

class DirectorDecision:
    def __init__(self, scene_id: str, decisions: Dict[str, Any], reasoning: str):
        self.scene_id = scene_id
        self.camera_profile = decisions.get("camera_profile", "steadicam")
        self.lens = decisions.get("lens", 35.0)
        self.composition = decisions.get("composition", "rule_of_thirds")
        self.character_blocking = decisions.get("character_blocking", {})
        self.character_movement = decisions.get("character_movement", {})
        self.eye_contact = decisions.get("eye_contact", True)
        self.walking_paths = decisions.get("walking_paths", [])
        self.pauses = decisions.get("pauses", [])
        self.head_movement = decisions.get("head_movement", "stabilized")
        self.emotion_intensity = decisions.get("emotion_intensity", 1.0)
        self.speaking_rhythm = decisions.get("speaking_rhythm", "standard")
        self.gesture_timing = decisions.get("gesture_timing", [])
        self.lighting_mood = decisions.get("lighting_mood", "neutral")
        self.shot_duration = decisions.get("shot_duration", 4.0)
        self.camera_transition = decisions.get("camera_transition", "cut")
        self.focus_target = decisions.get("focus_target", None)
        self.depth_of_field = decisions.get("depth_of_field", {"enabled": True, "fstop": 2.8})
        self.reasoning = reasoning

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scene_id": self.scene_id,
            "camera_profile": self.camera_profile,
            "lens": self.lens,
            "composition": self.composition,
            "character_blocking": self.character_blocking,
            "character_movement": self.character_movement,
            "eye_contact": self.eye_contact,
            "walking_paths": self.walking_paths,
            "pauses": self.pauses,
            "head_movement": self.head_movement,
            "emotion_intensity": self.emotion_intensity,
            "speaking_rhythm": self.speaking_rhythm,
            "gesture_timing": self.gesture_timing,
            "lighting_mood": self.lighting_mood,
            "shot_duration": self.shot_duration,
            "camera_transition": self.camera_transition,
            "focus_target": self.focus_target,
            "depth_of_field": self.depth_of_field,
            "reasoning": self.reasoning
        }

class DirectorIntelligenceEngine:
    """
    Analyzes storyboard context to generate a structured DirectorDecision plan for each shot.
    """
    def __init__(self):
        pass

    def direct_shot(
        self,
        scene: Dict[str, Any],
        prev_scene: Optional[Dict[str, Any]] = None,
        next_scene: Optional[Dict[str, Any]] = None,
        env_config: Optional[Dict[str, Any]] = None
    ) -> DirectorDecision:
        """
        Generates a DirectorDecision for a single shot based on screenplay context.
        """
        scene_id = str(scene.get("scene_number", scene.get("id", "0")))
        action = scene.get("action", "idle").lower()
        mood = scene.get("mood", "neutral").lower()
        dialogue = scene.get("dialogue", scene.get("line", ""))
        
        env = env_config or {}
        env_type = env.get("environment_type", "forest").lower()
        weather = env.get("weather", "clear").lower()
        
        decisions: Dict[str, Any] = {}
        reasoning_steps: List[str] = []

        # --- 1. Camera Profile & Movement ---
        if "attack" in action or "run" in action:
            decisions["camera_profile"] = "steadicam"
            decisions["camera_movement"] = "orbit"
            reasoning_steps.append("High action demands dynamic tracking and orbit movements.")
        elif mood in ("fear", "tense", "panic"):
            decisions["camera_profile"] = "handheld"
            decisions["camera_movement"] = "push_in"
            reasoning_steps.append("Anxiety/Fear is enhanced by unstable handheld camera pushing in.")
        else:
            decisions["camera_profile"] = "tripod"
            decisions["camera_movement"] = "static"
            reasoning_steps.append("Stable scene supports static tripod framing.")

        # --- 2. Lens & Composition ---
        if dialogue:
            decisions["lens"] = 50.0  # Portrait lens
            decisions["composition"] = "over_shoulder"
            decisions["focus_target"] = scene.get("character_name", "character")
            reasoning_steps.append("Dialogue prompts portrait lens with over-shoulder composition.")
        elif "attack" in action:
            decisions["lens"] = 28.0  # Wide angle
            decisions["composition"] = "low_angle"
            reasoning_steps.append("Action framing uses wide lens at low angle for scale.")
        else:
            decisions["lens"] = 35.0  # standard storytelling
            decisions["composition"] = "rule_of_thirds"
            reasoning_steps.append("Standard narrative defaults to 35mm lens with rule of thirds.")

        # --- 3. Depth of Field ---
        if mood in ("sad", "fear", "tense"):
            decisions["depth_of_field"] = {"enabled": True, "fstop": 1.8}
            reasoning_steps.append("Shallow depth of field (f/1.8) isolates character's intense emotion.")
        else:
            decisions["depth_of_field"] = {"enabled": True, "fstop": 4.0}
            reasoning_steps.append("Moderate depth of field (f/4.0) maintains environmental details.")

        # --- 4. Character Blocking & Movement ---
        blocking: Dict[str, Any] = {}
        char_move: Dict[str, Any] = {}
        if mood in ("fear", "tense"):
            blocking["stance"] = "defensive"
            if prev_scene:
                char_move["step"] = "backwards"
            decisions["eye_contact"] = False
            reasoning_steps.append("Defensive stance, stepping back, and broken eye contact highlight threat.")
        elif "attack" in action:
            blocking["stance"] = "combat"
            char_move["step"] = "forwards"
            decisions["eye_contact"] = True
            reasoning_steps.append("Aggressive stance, stepping forward, and steady eye contact indicate combat.")
        else:
            blocking["stance"] = "relaxed"
            char_move["step"] = "none"
            decisions["eye_contact"] = True
            reasoning_steps.append("Relaxed stance and direct eye contact.")

        decisions["character_blocking"] = blocking
        decisions["character_movement"] = char_move

        # --- 5. Speech Rhythm & Pacing ---
        if mood in ("fear", "tense"):
            decisions["speaking_rhythm"] = "slow_anxious"
            decisions["pauses"] = [1.2]
            reasoning_steps.append("Slow, anxious speech rhythm with pauses builds tension.")
        elif mood in ("sad",):
            decisions["speaking_rhythm"] = "slow_melancholic"
            decisions["pauses"] = [0.8]
            reasoning_steps.append("Melancholic delivery matches slow speaking rhythm.")
        else:
            decisions["speaking_rhythm"] = "standard"
            decisions["pauses"] = []
            reasoning_steps.append("Standard speech rhythm.")

        # --- 6. Lighting Mood ---
        if mood in ("fear", "tense", "sad"):
            decisions["lighting_mood"] = "colder" if weather != "foggy" else "mysterious"
            reasoning_steps.append("Cold/mysterious lighting matches emotional tone.")
        elif mood in ("happy", "cheerful", "hope"):
            decisions["lighting_mood"] = "cheerful"
            reasoning_steps.append("Cheerful warm lighting aligns with positive mood.")
        else:
            decisions["lighting_mood"] = "neutral"
            reasoning_steps.append("Neutral lighting preset.")

        # --- 7. Shot Duration & Transitions ---
        duration = 4.0
        if "attack" in action or "run" in action:
            duration = 3.0
            decisions["camera_transition"] = "cut"
            reasoning_steps.append("Fast action demands shorter 3.0s shot duration.")
        elif mood in ("sad", "hope"):
            duration = 5.5
            decisions["camera_transition"] = "fade"
            reasoning_steps.append("Slow emotional moment warrants longer 5.5s shot duration and fade transition.")
        else:
            decisions["camera_transition"] = "cut"
            reasoning_steps.append("Standard shot duration.")
            
        # Location change fade
        if prev_scene and prev_scene.get("location") != scene.get("location"):
            decisions["camera_transition"] = "fade"
            reasoning_steps.append("Fade transition handles location changes smoothly.")

        decisions["shot_duration"] = duration

        # Combine reasoning steps into a cohesive statement
        reasoning = " -> ".join(reasoning_steps)
        return DirectorDecision(scene_id, decisions, reasoning)
