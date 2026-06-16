#!/usr/bin/env python3
"""
storyboard_director.py — Rule-based storyboard director.

Parses scripts into structured cinematic storyboards.
Detects scenes, locations, characters, actions, moods, and camera suggestions.
"""
import re
from typing import Dict, Any, List

# Map actions to camera suggestions
CAMERA_MAP = {
    "walk": "wide_shot",
    "run": "tracking_shot",
    "jump": "low_angle",
    "attack": "close_up",
    "wave": "medium_shot",
    "idle": "wide_shot",
    "enter": "tracking_shot",
    "discover": "medium_shot",
    "say": "close_up",
    "talk": "close_up",
    "stand": "wide_shot"
}

# Map keywords/locations/actions to moods
MOOD_MAP = {
    "dark": "mysterious",
    "forest": "mysterious",
    "castle": "mysterious",
    "ruins": "mysterious",
    "mountain": "epic",
    "storm": "epic",
    "lightning": "epic",
    "carefully": "tense",
    "quietly": "tense",
    "scared": "tense",
    "cautious": "tense",
    "attack": "aggressive",
    "fight": "aggressive",
    "battle": "aggressive",
    "smash": "aggressive",
    "wave": "cheerful",
    "victory": "triumphant",
    "triumph": "triumphant",
    "land": "dramatic",
    "impact": "dramatic"
}

# Prepositions and markers for location extraction
LOCATION_PREPOSITIONS = [
    "through", "into", "inside", "across", "along", "towards", 
    "around", "under", "above", "before", "near", 
    "in", "into", "at", "on", "to", "from"
]

# Verbs/actions that can precede location direct objects
LOCATION_VERBS = ["discovers", "enters", "approaches", "reaches", "explores", "sees", "visits"]

# Known characters in the system
KNOWN_CHARACTERS = ["anime_girl", "anime_boy", "knight", "mage", "robot", "humanoid", "fox", "thor", "tony stark", "hulk", "hero"]

def parse_script_to_storyboard(script: str, default_character: str = "humanoid") -> Dict[str, Any]:
    """
    Parse a raw script into a structured storyboard dictionary.
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
            
        # 3. Detect action
        detected_action = "idle"
        action_keywords = ["walk", "run", "jump", "attack", "wave", "duck", "enter", "discover", "stand", "say", "talk", "speak"]
        for act in action_keywords:
            if act in sentence_lower:
                # normalize common synonyms
                if act in ["say", "talk", "speak"]:
                    detected_action = "talk"
                elif act == "stand":
                    detected_action = "idle"
                else:
                    detected_action = act
                break
                
        # 4. Detect camera suggestion
        detected_camera = CAMERA_MAP.get(detected_action, "wide_shot")
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
            
        # 5. Detect mood
        detected_mood = "neutral"
        for kw, md in MOOD_MAP.items():
            if kw in sentence_lower:
                detected_mood = md
                break
                
        # Standardize naming to match character registration IDs
        char_id = current_character.lower().replace(" ", "_")
        
        scenes.append({
            "location": current_location,
            "character": char_id,
            "action": detected_action,
            "camera": detected_camera,
            "mood": detected_mood
        })
        
    return {"scenes": scenes}
