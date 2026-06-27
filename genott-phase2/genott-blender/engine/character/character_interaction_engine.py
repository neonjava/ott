#!/usr/bin/env python3
"""
character_interaction_engine.py
Detects character interactions in stories and generates interaction metadata.
Supported interactions: speaking, fighting, following, helping, greeting, looking at.
"""
import re
from typing import Dict, Any, List

# Lexicons for character names and interaction verbs
CHARACTERS_LEXICON = {
    "knight", "dragon", "mage", "robot", "queen", "king", "prince", "princess",
    "beast", "elf", "dwarf", "guard", "warrior", "hero", "villain", "humanoid",
    "fox", "thor", "tony stark", "hulk", "ironman", "girl", "boy", "anime_girl",
    "anime_boy", "child", "wizard", "monster", "creature", "traveler", "merchant",
    "shadow", "samurai", "ninja", "soldier", "captain", "alien", "ghost"
}

INTERACTION_LEXICONS = {
    "speaking": [
        "talk", "talks", "talking", "talked", "speak", "speaks", "speaking", "spoke",
        "say", "says", "saying", "said", "whisper", "whispers", "whispering", "whispered",
        "shout", "shouts", "shouting", "shouted", "tell", "tells", "telling", "told",
        "converse", "conversing", "conversed", "chat", "chats", "chatting", "chatted"
    ],
    "fighting": [
        "fight", "fights", "fighting", "fought", "attack", "attacks", "attacking", "attacked",
        "strike", "strikes", "striking", "struck", "slash", "slashes", "slashing", "slashed",
        "hit", "hits", "hitting", "smash", "smashes", "smashing", "smashed", "battle", "battles",
        "battling", "battled", "clash", "clashes", "clashing", "clashed", "slay", "slays", "slaying", "slew",
        "defeat", "defeats", "defeated", "defeating", "overcome", "overcomes", "overcoming", "overcame"
    ],
    "following": [
        "follow", "follows", "following", "followed", "chase", "chases", "chasing", "chased",
        "track", "tracks", "tracking", "tracked", "pursue", "pursues", "pursuing", "pursued",
        "run after", "runs after", "running after", "ran after", "chased after", "chases after"
    ],
    "helping": [
        "help", "helps", "helping", "helped", "rescue", "rescues", "rescuing", "rescued", "save", "saves",
        "saving", "saved", "guide", "guides", "guiding", "guided", "protect", "protects",
        "protecting", "protected", "support", "supports", "supporting", "supported", "comfort",
        "comforts", "comforting", "comforted"
    ],
    "greeting": [
        "greet", "greets", "greeting", "greeted", "wave", "waves", "waving", "waved",
        "salute", "salutes", "saluting", "saluted", "welcome", "welcomes", "welcoming", "welcomed",
        "bow", "bows", "bowed", "bowing"
    ],
    "looking at": [
        "look at", "looks at", "looking at", "looked at", "watch", "watches", "watching", "watched",
        "see", "sees", "seeing", "saw", "spot", "spots", "spotting", "spotted", "notice", "notices",
        "noticing", "noticed", "observe", "observes", "observing", "observed", "stare at", "stares at",
        "staring at", "stared at"
    ]
}

def clean_token(token: str) -> str:
    return re.sub(r'[^\w\s-]', '', token).lower().strip()

class CharacterInteractionEngine:
    def __init__(self):
        pass

    def detect_characters_in_text(self, text: str) -> List[str]:
        """Finds all characters present in the given text in order of appearance, preventing overlaps."""
        text_lower = text.lower()
        char_indices = []
        consumed_spans = []

        # Sort character lexicon by length descending to match longer ones first
        for char in sorted(CHARACTERS_LEXICON, key=len, reverse=True):
            char_spaced = char.replace("_", " ")
            # Find matches for both spaced and original string
            for pattern in (r'\b' + re.escape(char_spaced) + r'\b', r'\b' + re.escape(char) + r'\b'):
                for m in re.finditer(pattern, text_lower):
                    start, end = m.start(), m.end()
                    # Check if this overlaps with any already consumed span
                    overlap = False
                    for cs_start, cs_end in consumed_spans:
                        if not (end <= cs_start or start >= cs_end):
                            overlap = True
                            break
                    if not overlap:
                        char_indices.append((start, char.replace(" ", "_")))
                        consumed_spans.append((start, end))

        # Sort by start index to maintain narrative order
        char_indices.sort()
        found = []
        for _, cname in char_indices:
            if cname not in found:
                found.append(cname)
        return found

    def classify_interaction_type(self, text: str) -> str:
        """Classifies the interaction verb into one of the known interaction types."""
        text_lower = text.lower()
        matches = {itype: 0 for itype in INTERACTION_LEXICONS.keys()}

        for itype, keywords in INTERACTION_LEXICONS.items():
            for kw in keywords:
                pattern = r'\b' + re.escape(kw) + r'\b'
                if re.search(pattern, text_lower):
                    matches[itype] += len(kw.split())

        best_type = "none"
        max_score = 0
        # Priority order for disambiguation: helping, fighting, speaking, following, greeting, looking at
        priority = ["helping", "fighting", "speaking", "following", "greeting", "looking at"]
        for p in priority:
            score = matches.get(p, 0)
            if score > max_score:
                max_score = score
                best_type = p
        return best_type

    def detect_interactions(self, story_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Processes story understanding engine output and extracts interaction metadata.
        """
        events = story_data.get("events", [])
        interactions = []

        # Keep track of active characters for contextual carryover
        last_actor = "humanoid"
        last_target = None

        for idx, event in enumerate(events):
            desc = event.get("description", "")
            actor = event.get("actor", last_actor)
            target = event.get("target")

            # Extract actual characters mentioned in the description
            chars = self.detect_characters_in_text(desc)
            
            source_char = actor
            target_char = target

            # Pronoun detection for carryover
            contains_pronoun = re.search(r'\b(him|her|them|it)\b', desc.lower()) is not None

            # If description mentions multiple characters explicitly
            if len(chars) >= 2:
                source_char = chars[0]
                target_char = chars[1]
            elif len(chars) == 1:
                found_char = chars[0]
                # Determine if found character is subject or object
                # Simple check: does it appear before the verb?
                if found_char == actor:
                    source_char = found_char
                    if contains_pronoun and last_target:
                        target_char = last_target
                    elif contains_pronoun and last_actor and last_actor != source_char:
                        target_char = last_actor
                else:
                    target_char = found_char
            else:
                # No characters mentioned, but pronouns exist
                if contains_pronoun:
                    source_char = actor
                    if last_target and last_target != source_char:
                        target_char = last_target
                    elif last_actor and last_actor != source_char:
                        target_char = last_actor

            # If source_char and target_char are both known, check if they are different
            if source_char and target_char and source_char != target_char:
                interaction_type = self.classify_interaction_type(desc)
                if interaction_type != "none":
                    interactions.append({
                        "event_id": event.get("id"),
                        "source": source_char,
                        "target": target_char,
                        "type": interaction_type,
                        "description": desc.strip()
                    })

            # Update history
            last_actor = source_char
            if target_char:
                last_target = target_char

        return interactions

if __name__ == "__main__":
    import json
    engine = CharacterInteractionEngine()
    
    # Sample story data containing multi-character events
    sample_story_data = {
        "events": [
            {
                "id": "event_1",
                "actor": "knight",
                "target": "dragon",
                "location": "forest",
                "description": "A brave knight encounters a dragon in the forest."
            },
            {
                "id": "event_2",
                "actor": "knight",
                "target": "dragon",
                "description": "The knight speaks to the dragon, asking for peace."
            },
            {
                "id": "event_3",
                "actor": "dragon",
                "target": "knight",
                "description": "Suddenly, the dragon attacks the knight with fire."
            },
            {
                "id": "event_4",
                "actor": "mage",
                "target": "knight",
                "description": "A nearby mage saves the knight with a magical shield."
            }
        ]
    }
    
    results = engine.detect_interactions(sample_story_data)
    print(json.dumps(results, indent=2))
