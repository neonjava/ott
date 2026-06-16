#!/usr/bin/env python3
"""
storyboard_director.py — Rule-based storyboard director.

Parses scripts into structured cinematic storyboards.
Detects scenes, locations, characters, actions, moods, and camera suggestions.
"""
import re
from typing import Dict, Any, List

# Expanded synonym mapping from verbs to standard animation action keys
ACTION_SYNONYMS = {
    "walk": ["walk", "walks", "walking", "travel", "travels", "travelling", "traveling", "wander", "wandering", "wanders", "march", "marching", "marches", "journey", "journeying", "stroll", "strolling", "strolls", "move", "moving", "moves", "approach", "approaches", "approaching", "trek", "treks", "trekking"],
    "run": ["run", "runs", "running", "sprint", "sprints", "sprinting", "charge", "charges", "charging", "rush", "rushes", "rushing", "dash", "dashing", "dashes", "flee", "fleeing", "flees", "escape", "escaping", "escapes"],
    "jump": ["jump", "jumps", "jumping", "leap", "leaps", "leaping", "bound", "bounding", "bounds", "vault", "vaulting", "hop", "hopping", "hops"],
    "attack": ["attack", "attacks", "attacking", "fight", "fights", "fighting", "strike", "strikes", "striking", "slash", "slashes", "slashing", "swing", "swings", "swinging", "hit", "hits", "hitting", "smash", "smashes", "smashing", "punch", "punches", "punching", "kick", "kicks", "kicking", "battle", "battles", "battling"],
    "wave": ["wave", "waves", "waving", "greet", "greets", "greeting", "salute", "saluting", "salutes", "gesture", "gesturing", "gestures"],
    "duck": ["duck", "ducks", "ducking", "crouch", "crouching", "crouches", "dodge", "dodging", "dodges", "cower", "cowering", "cowers", "hide", "hiding", "hides"],
    "enter": ["enter", "enters", "entering", "penetrate", "penetrating", "go inside", "goes inside", "cross", "crosses", "crossing"],
    "discover": ["discover", "discovers", "discovering", "find", "finds", "finding", "see", "sees", "seeing", "spot", "spots", "spotting", "notice", "notices", "noticing", "locate", "locating", "locates"],
    "idle": ["idle", "idles", "idling", "stand", "stands", "standing", "wait", "waits", "waiting", "pause", "pauses", "pausing", "stop", "stops", "stopping", "stay", "stays", "staying", "rest", "rests", "resting", "sit", "sits", "sitting"],
    "talk": ["talk", "talks", "talking", "say", "says", "saying", "speak", "speaks", "speaking", "tell", "tells", "telling", "whisper", "whispers", "whispering", "shout", "shouts", "shouting", "yell", "yells", "yelling", "scream", "screams", "screaming", "converse", "conversing", "chat", "chats", "chatting"]
}

# Rich emotional state mapping to storyboard moods
EMOTION_MAP = {
    "sad": ["sad", "sadly", "lonely", "sorrowful", "depressed", "unhappy", "grief", "mournful", "faith"],
    "aggressive": ["angry", "angrily", "furious", "furiously", "rage", "mad", "attack", "fight", "battle", "smash"],
    "cheerful": ["happy", "happily", "cheerful", "cheerfully", "joyful", "joyfully", "excited", "excitedly", "wave", "greet"],
    "tense": ["scared", "fearful", "terrified", "frightened", "afraid", "tense", "tensely", "nervous", "carefully", "quietly", "cautious", "cautiously"],
    "triumphant": ["proud", "proudly", "triumphant", "triumphant", "victory", "victorious", "triumph"],
    "mysterious": ["dark", "forest", "castle", "ruins", "shadow", "shadowy", "ancient"],
    "epic": ["mountain", "storm", "lightning", "glacier", "abyss"]
}

# Prepositions and markers for location extraction
LOCATION_PREPOSITIONS = [
    "through", "into", "inside", "across", "along", "towards", 
    "around", "under", "above", "before", "near", 
    "in", "into", "at", "on", "to", "from"
]

# Verbs/actions that can precede location direct objects
LOCATION_VERBS = ["discovers", "enters", "approaches", "reaches", "explores", "sees", "visits"]

import json
import os

def load_known_characters() -> List[str]:
    # Hardcoded defaults
    chars = ["anime_girl", "anime_boy", "knight", "mage", "robot", "humanoid", "fox", "thor", "tony stark", "hulk", "hero"]
    
    # Try loading from character_registry.json
    project_dir = os.path.dirname(os.path.abspath(__file__))
    char_reg_path = os.path.join(project_dir, "character_registry.json")
    if os.path.exists(char_reg_path):
        try:
            with open(char_reg_path, "r") as f:
                data = json.load(f)
                for key in data.keys():
                    if key not in chars:
                        chars.append(key)
        except: pass
        
    # Try loading from asset_registry.json
    asset_reg_path = os.path.join(project_dir, "asset_registry.json")
    if os.path.exists(asset_reg_path):
        try:
            with open(asset_reg_path, "r") as f:
                data = json.load(f)
                for key, val in data.items():
                    if val.get("type") == "character" and key not in chars:
                        chars.append(key)
        except: pass
        
    return chars

KNOWN_CHARACTERS = load_known_characters()

def parse_script_to_storyboard(script: str, default_character: str = "humanoid") -> Dict[str, Any]:
    """
    Parse a raw script into a structured storyboard dictionary with semantic understanding.
    """
    sentences = []
    # Split by sentence endings (. ! ?)
    raw_sentences = re.split(r'(?<=[.!?])\s+', script.strip())
    for s in raw_sentences:
        s_clean = s.strip()
        if s_clean:
            sentences.append(s_clean)
            
    if not sentences:
        sentences = [script.strip()]

    scenes = []
    current_character = default_character
    current_location = "environment"
    
    for idx, sentence in enumerate(sentences):
        sentence_lower = sentence.lower()
        
        # 1. Detect characters
        detected_char = None
        for char in KNOWN_CHARACTERS:
            # Replace underscore with space for keyword matching
            char_spaced = char.replace("_", " ")
            if re.search(r'\b' + re.escape(char_spaced) + r'\b', sentence_lower) or re.search(r'\b' + re.escape(char) + r'\b', sentence_lower):
                detected_char = char
                break
                
        if detected_char:
            current_character = detected_char
        else:
            # Resolve pronouns to current active character
            if sentence_lower.startswith(("he ", "she ", "it ", "they ")):
                pass # keep current_character
                
        # 2. Detect location
        detected_loc = None
        
        # A. Check transitive location verbs first (e.g. "discovers an abandoned castle")
        for verb in LOCATION_VERBS:
            pattern = r'\b' + re.escape(verb) + r'\s+(?:a|an|the)?\s*([a-zA-Z0-9\s_]+?)(?:\.|\b(?:and|but|he|she|it|says|walks|runs|jumps|attacks|waves|stands|enters|carefully)\b|$)'
            match = re.search(pattern, sentence_lower)
            if match:
                loc_cand = match.group(1).strip()
                words = loc_cand.split()
                clean_words = []
                for w in words[:4]:
                    if w in ["says", "walks", "runs", "jumps", "attacks", "waves", "enters", "stands", "and", "but", "carefully", "with"]:
                        break
                    clean_words.append(w)
                if clean_words:
                    detected_loc = " ".join(clean_words)
                    break
        
        # B. Check prepositional phrases if no location verb matched (e.g. "through a snowy forest")
        if not detected_loc:
            for prep in LOCATION_PREPOSITIONS:
                pattern = r'\b' + re.escape(prep) + r'\s+(?:a|an|the)?\s*([a-zA-Z0-9\s_]+?)(?:\.|\b(?:and|but|he|she|it|says|walks|runs|jumps|attacks|waves|stands|enters|carefully)\b|$)'
                match = re.search(pattern, sentence_lower)
                if match:
                    loc_cand = match.group(1).strip()
                    words = loc_cand.split()
                    clean_words = []
                    for w in words[:4]:
                        if w in ["says", "walks", "runs", "jumps", "attacks", "waves", "enters", "stands", "and", "but", "carefully", "with"]:
                            break
                        clean_words.append(w)
                    if clean_words:
                        detected_loc = " ".join(clean_words)
                        break
                        
        if detected_loc:
            current_location = detected_loc
            
        # 3. Detect action using priority-based synonym mapping
        detected_action = "idle"
        words_in_sentence = re.findall(r'\b[a-z]+\b', sentence_lower)
        
        # Priority order: combat/gestures -> interaction -> locomotion -> resting
        action_priority = ["attack", "jump", "duck", "wave", "enter", "discover", "talk", "run", "walk", "idle"]
        
        found_action = False
        for action_key in action_priority:
            synonyms = ACTION_SYNONYMS[action_key]
            for syn in synonyms:
                if syn in words_in_sentence:
                    detected_action = action_key
                    found_action = True
                    break
            if found_action:
                break
                
        # 4. Detect camera suggestion
        detected_camera = "wide_shot"
        if "close-up" in sentence_lower or "closeup" in sentence_lower or "close up" in sentence_lower or "face" in sentence_lower or "expression" in sentence_lower:
            detected_camera = "close_up"
        elif "establishing" in sentence_lower or "panorama" in sentence_lower:
            detected_camera = "establishing_shot"
        elif "over the shoulder" in sentence_lower or "over shoulder" in sentence_lower or "looking at" in sentence_lower:
            detected_camera = "over_shoulder"
        elif "wide" in sentence_lower or "distant" in sentence_lower or "far away" in sentence_lower:
            detected_camera = "wide_shot"
        elif "tracking" in sentence_lower or "track" in sentence_lower or "follow" in sentence_lower:
            detected_camera = "tracking_shot"
        else:
            # Action fallback
            if detected_action in ["walk", "idle"]:
                detected_camera = "wide_shot"
            elif detected_action in ["run", "enter"]:
                detected_camera = "tracking_shot"
            elif detected_action in ["attack", "talk"]:
                detected_camera = "close_up"
            elif detected_action in ["wave", "discover"]:
                detected_camera = "medium_shot"
            
        # 5. Detect mood/emotion
        detected_mood = "neutral"
        
        def is_mood_match(kw: str, word: str) -> bool:
            if kw == word:
                return True
            if word == kw + "s" or word == kw + "es" or word == kw + "ly":
                return True
            if kw == word + "s" or kw == word + "es" or kw == word + "ly":
                return True
            return False

        for mood_key, keywords in EMOTION_MAP.items():
            for kw in keywords:
                if any(is_mood_match(kw, w) for w in words_in_sentence):
                    detected_mood = mood_key
                    break
            if detected_mood != "neutral":
                break
                
        # 6. Adverb/Speed Modifiers detection
        speed_modifier = "normal"
        if "slowly" in sentence_lower or "calmly" in sentence_lower or "leisurely" in sentence_lower:
            speed_modifier = "slow"
        elif "quickly" in sentence_lower or "rapidly" in sentence_lower or "hastily" in sentence_lower or "hurriedly" in sentence_lower:
            speed_modifier = "fast"
            
        # Standardize naming to match character registration IDs
        char_id = current_character.lower().replace(" ", "_")
        
        scenes.append({
            "location": current_location,
            "character": char_id,
            "action": detected_action,
            "camera": detected_camera,
            "mood": detected_mood,
            "speed": speed_modifier
        })
        
    return {"scenes": scenes}
