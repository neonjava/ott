#!/usr/bin/env python3
"""
emotion_engine.py
Classifies story events and phrases into fine-grained emotional states:
happy, sad, angry, fear, hope, surprise, determination.
Exposes emotion data to Director AI, the Camera system, and the Character system.
"""
import re
from typing import Dict, Any, List

# Lexicon definitions for the 7 key emotional states
EMOTIONS_LEXICON = {
    "happy": [
        "happy", "happily", "cheerful", "cheerfully", "joyful", "joyfully",
        "excited", "excitedly", "delighted", "glad", "proud", "proudly",
        "triumphant", "victorious", "celebrating", "gleeful", "gleefully", "laugh", "laughing",
        "smile", "smiling", "smiled", "rejoice", "rejoicing", "joy", "pleased", "delight", "delightful",
        "delightedly", "warmly", "warmth", "celebrates", "celebrated"
    ],
    "sad": [
        "sad", "sadly", "lonely", "sorrowful", "depressed", "unhappy", "unhappiness", "grief",
        "mournful", "mournfully", "faithless", "hopeless", "lose faith", "loses faith", "lost faith",
        "losing faith", "lose all faith", "loses all faith", "lost all faith", "exhausted",
        "lose hope", "loses hope", "lost hope", "losing hope", "lose all hope", "loses all hope",
        "lost all hope", "crying", "weeping", "tearful", "mourn", "mourning", "regret", "regretful",
        "brokenhearted", "wept", "bitterly", "tragic", "loss", "sigh", "sighed", "sighs", "tears", "tear"
    ],
    "angry": [
        "angry", "angrily", "furious", "furiously", "rage", "mad", "hostile", "hostility",
        "vengeful", "resentful", "bitter", "enraged", "fury", "irritated", "annoyed",
        "hate", "hateful", "spiteful", "aggressively", "fought"
    ],
    "fear": [
        "scared", "fearful", "terrified", "frightened", "afraid", "tense", "tensely",
        "nervous", "cautious", "cautiously", "cowardly", "dread", "dreading",
        "panic", "panicked", "terror", "spooked", "horror", "haunted", "graveyard",
        "spooky"
    ],
    "hope": [
        "hope", "hopeful", "regain purpose", "regains purpose", "regaining purpose",
        "regain hope", "regains hope", "regained hope",
        "faith", "dream", "optimistic", "inspired", "inspired by", "reassure", "reassured",
        "trust", "trusting", "trustful", "trusts", "relieved", "relief", "peaceful", "peacefully"
    ],
    "surprise": [
        "surprise", "surprised", "discover", "discovers", "discovered", "find",
        "finds", "found", "see", "sees", "saw", "notice", "notices", "noticed",
        "spot", "spots", "spotted", "shock", "shocked", "amazed", "astonished",
        "unexpected", "sudden", "suddenly"
    ],
    "determination": [
        "determination", "determined", "brave", "courage", "courageous", "focus",
        "focused", "resolve", "resolved", "persist", "persists", "valiant", "valiantly",
        "bold", "boldly", "steadfast", "firm", "unstoppable", "defiant", "defiantly"
    ]
}

class EmotionEngine:
    def __init__(self):
        pass

    def classify_emotion(self, text: str) -> str:
        """
        Classifies a given text string into one of the 7 emotional states,
        or returns 'neutral' if no emotion is matched.
        """
        text_lower = text.lower()
        
        # Track word matches to find the strongest match, weighting by word count
        matches = {emo: 0 for emo in EMOTIONS_LEXICON.keys()}
        
        for emo, keywords in EMOTIONS_LEXICON.items():
            for kw in keywords:
                pattern = r'\b' + re.escape(kw) + r'\b'
                if re.search(pattern, text_lower):
                    matches[emo] += len(kw.split())
                    
        # Find the emotion with the highest number of keyword matches, using priority to resolve ties
        priority = ["determination", "hope", "fear", "angry", "sad", "surprise", "happy"]
        best_emo = "neutral"
        max_matches = 0
        for emo in priority:
            count = matches.get(emo, 0)
            if count > max_matches:
                max_matches = count
                best_emo = emo
                
        return best_emo

    def map_emotion_to_director_config(self, emotion: str) -> Dict[str, Any]:
        """
        Returns cinematic preferences for Director AI based on emotion.
        """
        configs = {
            "happy": {
                "camera_shot": "medium_shot",
                "camera_movement": "pan",
                "pacing": "standard",
                "duration": 4.0
            },
            "sad": {
                "camera_shot": "close_up",
                "camera_movement": "static",
                "pacing": "slow",
                "duration": 6.0
            },
            "angry": {
                "camera_shot": "low_angle",
                "camera_movement": "orbit_shot",
                "pacing": "fast",
                "duration": 3.0
            },
            "fear": {
                "camera_shot": "close_up",
                "camera_movement": "tracking",
                "pacing": "fast",
                "duration": 3.5
            },
            "hope": {
                "camera_shot": "wide_shot",
                "camera_movement": "zoom",
                "pacing": "slow",
                "duration": 5.0
            },
            "surprise": {
                "camera_shot": "medium_shot",
                "camera_movement": "tilt",
                "pacing": "standard",
                "duration": 4.0
            },
            "determination": {
                "camera_shot": "low_angle",
                "camera_movement": "static",
                "pacing": "standard",
                "duration": 4.5
            },
            "neutral": {
                "camera_shot": "wide_shot",
                "camera_movement": "static",
                "pacing": "standard",
                "duration": 4.0
            }
        }
        return configs.get(emotion, configs["neutral"])

    def map_emotion_to_camera_settings(self, emotion: str) -> Dict[str, Any]:
        """
        Returns focal length, depth of field, and shake settings for Blender Camera system.
        """
        settings = {
            "happy": {
                "focal_length": 35.0, # Wider, cheerful perspective
                "dof_distance": 5.0,
                "dof_aperture": 2.8,
                "shake_amplitude": 0.05
            },
            "sad": {
                "focal_length": 85.0, # Telephoto, intimate portrait
                "dof_distance": 2.5,
                "dof_aperture": 1.4,  # Shallow depth of field for isolation
                "shake_amplitude": 0.01
            },
            "angry": {
                "focal_length": 50.0,
                "dof_distance": 4.0,
                "dof_aperture": 4.0,
                "shake_amplitude": 0.25 # High shake for tension/rage
            },
            "fear": {
                "focal_length": 75.0,
                "dof_distance": 3.0,
                "dof_aperture": 1.8,
                "shake_amplitude": 0.40 # Extreme camera shake/panic
            },
            "hope": {
                "focal_length": 24.0, # Ultrawide, grand scale
                "dof_distance": 10.0,
                "dof_aperture": 8.0,  # Deep depth of field to see the world
                "shake_amplitude": 0.02
            },
            "surprise": {
                "focal_length": 50.0,
                "dof_distance": 3.5,
                "dof_aperture": 2.0,
                "shake_amplitude": 0.15 # Quick jolt
            },
            "determination": {
                "focal_length": 50.0,
                "dof_distance": 3.0,
                "dof_aperture": 2.0,
                "shake_amplitude": 0.05
            },
            "neutral": {
                "focal_length": 50.0,
                "dof_distance": 5.0,
                "dof_aperture": 5.6,
                "shake_amplitude": 0.0
            }
        }
        return settings.get(emotion, settings["neutral"])

    def map_emotion_to_character_settings(self, emotion: str) -> Dict[str, Any]:
        """
        Returns facial expression identifiers and locomotion animation overrides for Character System.
        """
        settings = {
            "happy": {
                "facial_expression": "smile",
                "animation_override": "CharacterArmature|Wave",
                "facial_parameters": {"eyebrow_raise": 0.3, "mouth_smile": 1.0}
            },
            "sad": {
                "facial_expression": "frown",
                "animation_override": "CharacterArmature|Idle",
                "facial_parameters": {"eyebrow_raise": -0.2, "mouth_frown": 1.0}
            },
            "angry": {
                "facial_expression": "rage",
                "animation_override": "CharacterArmature|Punch",
                "facial_parameters": {"eyebrows_down": 1.0, "mouth_open": 0.5, "eyes_narrow": 0.8}
            },
            "fear": {
                "facial_expression": "scared",
                "animation_override": "CharacterArmature|Duck",
                "facial_parameters": {"eyes_wide": 1.0, "mouth_open": 0.6, "eyebrow_raise": 0.8}
            },
            "hope": {
                "facial_expression": "serene",
                "animation_override": "CharacterArmature|Idle",
                "facial_parameters": {"eyebrow_raise": 0.1, "mouth_smile": 0.3}
            },
            "surprise": {
                "facial_expression": "shocked",
                "animation_override": "CharacterArmature|Jump",
                "facial_parameters": {"eyes_wide": 1.0, "mouth_open": 1.0}
            },
            "determination": {
                "facial_expression": "focused",
                "animation_override": "CharacterArmature|Sword_Slash",
                "facial_parameters": {"eyebrows_down": 0.5, "mouth_closed": 1.0, "eyes_narrow": 0.4}
            },
            "neutral": {
                "facial_expression": "neutral",
                "animation_override": "CharacterArmature|Idle",
                "facial_parameters": {}
            }
        }
        return settings.get(emotion, settings["neutral"])

if __name__ == "__main__":
    import json
    engine = EmotionEngine()
    test_phrases = [
        "A lonely knight weeping in the dark forest.",
        "The brave hero stands victorious and celebrates happily.",
        "A terrified villager screams and flees in panic!",
        "The angry giant roared and smashed the table in fury."
    ]
    for p in test_phrases:
        emo = engine.classify_emotion(p)
        print(f"Phrase: '{p}' => classified as: {emo}")
        print(f"  Camera settings: {engine.map_emotion_to_camera_settings(emo)}")
        print(f"  Character expression: {engine.map_emotion_to_character_settings(emo)}")
