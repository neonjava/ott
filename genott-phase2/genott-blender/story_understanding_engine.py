#!/usr/bin/env python3
"""
story_understanding_engine.py
Transforms natural language stories into structured movie plans.
Extracts characters, locations, objects, actions, emotions, scene transitions, and timeline order.
"""
import re
from typing import Dict, Any, List

# Lexicon definitions
CHARACTERS_LEXICON = {
    "knight", "dragon", "mage", "robot", "queen", "king", "prince", "princess",
    "beast", "elf", "dwarf", "guard", "warrior", "hero", "villain", "humanoid",
    "fox", "thor", "tony stark", "hulk", "ironman", "girl", "boy", "anime_girl",
    "anime_boy", "child", "wizard", "monster", "creature", "traveler", "merchant",
    "shadow", "samurai", "ninja", "soldier", "captain", "alien", "ghost"
}

LOCATIONS_LEXICON = {
    "forest", "kingdom", "castle", "cave", "ruins", "beach", "mountain", "city",
    "arena", "village", "tower", "hill", "desert", "swamp", "lake", "ocean",
    "space", "island", "dungeon", "temple", "room", "house", "glacier", "abyss",
    "woods", "shore", "sea", "sky", "volcano", "field", "bridge", "library", "dungeon"
}

OBJECTS_LEXICON = {
    "sword", "shield", "potion", "key", "crown", "relic", "stone", "artifact",
    "bow", "arrow", "treasure", "book", "staff", "amulet", "ring", "map", "coin",
    "gem", "faith", "purpose", "hope", "scroll", "orb", "mirror", "journal", "locket",
    "chalice", "dagger", "hammer", "chest"
}

EMOTIONS_LEXICON = {
    "sad": ["sad", "sadly", "lonely", "sorrowful", "depressed", "unhappy", "grief", "mournful", "faithless", "hopeless", "lose faith", "loses faith", "lost faith", "exhausted", "lose hope", "loses hope", "lost hope", "crying", "weeping", "tearful"],
    "angry": ["angry", "angrily", "furious", "furiously", "rage", "mad", "hostile", "vengeful", "resentful", "bitter", "enraged"],
    "happy": ["happy", "happily", "cheerful", "cheerfully", "joyful", "joyfully", "excited", "excitedly", "delighted", "glad", "proud", "proudly", "triumphant", "victorious", "celebrating", "gleeful"],
    "fear": ["scared", "fearful", "terrified", "frightened", "afraid", "tense", "tensely", "nervous", "cautious", "cautiously", "cowardly", "dread", "dreading", "panic", "panicked"],
    "hope": ["hope", "hopeful", "regain purpose", "regains purpose", "regaining purpose", "faith", "dream", "optimistic", "inspired", "inspired by", "reassure", "reassured"],
    "surprise": ["surprise", "surprised", "discover", "discovers", "discovered", "find", "finds", "found", "see", "sees", "saw", "notice", "notices", "noticed", "spot", "spots", "spotted", "shock", "shocked", "amazed", "astonished"],
    "determination": ["determination", "determined", "brave", "courage", "courageous", "focus", "resolve", "resolved", "persist", "persists", "valiant", "valiantly", "bold", "boldly", "steadfast", "firm"]
}

ACTIONS_LEXICON = {
    "walk": ["walk", "walks", "walking", "walked", "travel", "travels", "travelling", "travelled", "traveling", "wander", "wandering", "wandered", "wanders", "march", "marching", "marched", "marches", "journey", "journeying", "stroll", "strolling", "strolled", "strolls", "move", "moving", "moved", "moves", "approach", "approaches", "approaching", "approached", "trek", "treks", "trekking", "trekked"],
    "run": ["run", "runs", "running", "ran", "sprint", "sprints", "sprinting", "sprinted", "charge", "charges", "charging", "charged", "rush", "rushes", "rushing", "rushed", "dash", "dashing", "dashed", "dashes", "flee", "fleeing", "fled", "flees", "escape", "escaping", "escaped", "escapes"],
    "jump": ["jump", "jumps", "jumping", "jumped", "leap", "leaps", "leaping", "leaped", "leapt", "bound", "bounding", "bounded", "bounds", "vault", "vaulting", "vaulted", "hop", "hopping", "hopped", "hops"],
    "attack": ["attack", "attacks", "attacking", "attacked", "fight", "fights", "fighting", "fought", "strike", "strikes", "striking", "struck", "slash", "slashes", "slashing", "slashed", "swing", "swings", "swinging", "swung", "hit", "hits", "hitting", "smash", "smashes", "smashing", "smashed", "punch", "punches", "punching", "punched", "kick", "kicks", "kicking", "kicked", "battle", "battles", "battling", "battled", "slay", "slays", "slaying", "slew", "defeat", "defeats", "defeating", "defeated"],
    "wave": ["wave", "waves", "waving", "waved", "greet", "greets", "greeting", "greeted", "salute", "saluting", "salutes", "saluted", "gesture", "gesturing", "gestured", "gestures"],
    "duck": ["duck", "ducks", "ducking", "ducked", "crouch", "crouching", "crouched", "crouches", "dodge", "dodging", "dodged", "dodges", "cower", "cowering", "cowered", "cowers", "hide", "hiding", "hid", "hides"],
    "enter": ["enter", "enters", "entering", "entered", "penetrate", "penetrating", "penetrated", "cross", "crosses", "crossing", "crossed"],
    "discover": ["discover", "discovers", "discovering", "discovered", "find", "finds", "finding", "found", "see", "sees", "seeing", "saw", "spot", "spots", "spotting", "spotted", "notice", "notices", "noticing", "noticed", "locate", "locating", "located", "locates"],
    "idle": ["idle", "idles", "idling", "idled", "stand", "stands", "standing", "stood", "wait", "waits", "waiting", "waited", "pause", "pauses", "pausing", "paused", "stop", "stops", "stopping", "stopped", "stay", "stays", "staying", "stayed", "rest", "rests", "resting", "rested", "sit", "sits", "sitting", "sat"],
    "talk": ["talk", "talks", "talking", "talked", "say", "says", "saying", "said", "speak", "speaks", "speaking", "spoke", "tell", "tells", "telling", "told", "whisper", "whispers", "whispering", "whispered", "shout", "shouts", "shouting", "shouted", "yell", "yells", "yelling", "yelled", "scream", "screams", "screaming", "screamed", "converse", "conversing", "conversed", "chats", "chatting", "chatted"],
    "follow": ["follow", "follows", "following", "followed", "track", "tracking", "tracked", "chase", "chasing", "chased"],
    "help": ["help", "helps", "helping", "helped", "rescue", "rescuing", "rescued", "save", "saving", "saved", "guide", "guiding", "guided", "comfort", "comforting", "comforted", "protect", "protecting", "protected", "support", "supporting", "supported"]
}

PREPOSITIONS = {"in", "at", "through", "inside", "into", "on", "onto", "to", "towards", "from", "near", "by", "beside"}
ADVERBS_MODIFIERS = {
    "slowly": "slow", "calmly": "slow", "leisurely": "slow", "quietly": "slow", "cautiously": "slow", "gradually": "slow",
    "quickly": "fast", "rapidly": "fast", "hastily": "fast", "hurriedly": "fast", "aggressively": "fast", "violently": "fast", "swiftly": "fast", "boldly": "fast"
}

def clean_token(token: str) -> str:
    return re.sub(r'[^\w\s-]', '', token).lower().strip()

def split_story_into_clauses(story: str) -> List[str]:
    """Splits a story into clauses based on punctuation and conjunctions."""
    # First split by sentence end punctuation
    sentences = re.split(r'(?<=[.!?])\s+', story.strip())
    clauses = []
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        # Split by conjunctions: "and", "but", "while", "then", "then,", "so", commas (if separating actions)
        parts = re.split(r'\b(?:and|but|while|then|so)\b|,\s*', s)
        for p in parts:
            p = p.strip()
            # Clean trailing punctuation
            p = re.sub(r'[.!?]+$', '', p).strip()
            if p:
                clauses.append(p)
    return clauses

class StoryUnderstandingEngine:
    def __init__(self):
        pass

    def extract_characters(self, text: str) -> List[Dict[str, Any]]:
        """Extracts characters and their adjectives from text."""
        words = text.split()
        extracted = []
        found_names = set()

        # Check multi-word characters first (e.g. tony stark, anime girl, anime boy)
        text_lower = text.lower()
        for char in sorted(CHARACTERS_LEXICON, key=len, reverse=True):
            if re.search(r'\b' + re.escape(char) + r'\b', text_lower):
                char_key = char.replace(" ", "_")
                if char_key not in found_names:
                    # Find modifiers/adjectives preceding it
                    modifiers = []
                    # Simple regex to look for adjectives before character
                    # e.g., "lonely knight", "ancient dragon"
                    words_before = re.findall(r'(\b\w+\b)\s+(?:' + re.escape(char) + r')\b', text_lower)
                    for wb in words_before:
                        if wb not in {"a", "an", "the", "and", "or", "to", "of", "in", "on", "at", "with"}:
                            modifiers.append(wb)
                    
                    extracted.append({
                        "name": char_key,
                        "modifiers": modifiers
                    })
                    found_names.add(char_key)

        return extracted

    def extract_locations(self, text: str) -> List[Dict[str, Any]]:
        """Extracts locations and their adjectives from text."""
        text_lower = text.lower()
        extracted = []
        found_names = set()

        # 1. Search for prepositional phrases: prepositions followed by optional article/adjective and location noun
        # e.g., "through a frozen forest", "in the dark cave", "to the kingdom"
        for prep in PREPOSITIONS:
            # Match: prep + optionally (a/an/the) + optionally (word like frozen/dark) + location
            for loc in LOCATIONS_LEXICON:
                pattern = r'\b' + re.escape(prep) + r'\s+(?:a|an|the|ancient|old|dark|snowy|frozen|dusty|lonely)?\s*(\b\w+\b\s+)?' + re.escape(loc) + r'\b'
                match = re.search(pattern, text_lower)
                if match:
                    # Capture full matched phrase as location, or just the location name
                    # Let's extract the modifiers
                    modifiers = []
                    # Let's see what was between prep and loc
                    phrase = match.group(0)
                    words_in_phrase = phrase.split()
                    for w in words_in_phrase[1:-1]: # skip prep and loc
                        w_clean = clean_token(w)
                        if w_clean not in {"a", "an", "the", ""}:
                            modifiers.append(w_clean)
                    
                    loc_name = loc
                    if loc_name not in found_names:
                        extracted.append({
                            "name": loc_name,
                            "modifiers": modifiers
                        })
                        found_names.add(loc_name)

        # 2. General scan fallback
        for loc in LOCATIONS_LEXICON:
            if loc not in found_names and re.search(r'\b' + re.escape(loc) + r'\b', text_lower):
                # Search for adjective right before it
                words_before = re.findall(r'(\b\w+\b)\s+' + re.escape(loc) + r'\b', text_lower)
                modifiers = []
                for wb in words_before:
                    wb_clean = clean_token(wb)
                    if wb_clean not in {"a", "an", "the", "and", "or", "in", "to", "on", "at", "from"}:
                        modifiers.append(wb_clean)
                extracted.append({
                    "name": loc,
                    "modifiers": modifiers
                })
                found_names.add(loc)

        return extracted

    def extract_objects(self, text: str) -> List[Dict[str, Any]]:
        """Extracts objects from text."""
        text_lower = text.lower()
        extracted = []
        found_names = set()

        for obj in OBJECTS_LEXICON:
            if re.search(r'\b' + re.escape(obj) + r'\b', text_lower):
                # Find modifiers preceding the object
                words_before = re.findall(r'(\b\w+\b)\s+' + re.escape(obj) + r'\b', text_lower)
                modifiers = []
                for wb in words_before:
                    wb_clean = clean_token(wb)
                    if wb_clean not in {"a", "an", "the", "and", "or", "of", "to"}:
                        modifiers.append(wb_clean)

                extracted.append({
                    "name": obj,
                    "modifiers": modifiers
                })
                found_names.add(obj)
        return extracted

    def extract_emotions(self, text: str) -> List[Dict[str, Any]]:
        """Extracts emotions and their source phrases from text."""
        text_lower = text.lower()
        extracted = []
        found_emotions = set()

        for emotion_name, keywords in EMOTIONS_LEXICON.items():
            for kw in keywords:
                if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                    extracted.append({
                        "emotion": emotion_name,
                        "phrase": kw
                    })
                    found_emotions.add(emotion_name)
                    break # Only add once per emotion class in a sentence/clause
        return extracted

    def extract_actions(self, text: str) -> List[Dict[str, Any]]:
        """Extracts action types and verb phrases from text."""
        text_lower = text.lower()
        extracted = []
        found_actions = set()

        # Detect speed modifier
        speed = "normal"
        for adv, val in ADVERBS_MODIFIERS.items():
            if re.search(r'\b' + re.escape(adv) + r'\b', text_lower):
                speed = val
                break

        for action_name, keywords in ACTIONS_LEXICON.items():
            for kw in keywords:
                if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                    extracted.append({
                        "action": action_name,
                        "verb": kw,
                        "speed": speed
                    })
                    found_actions.add(action_name)
                    break
        return extracted

    def understand_story(self, story: str) -> Dict[str, Any]:
        """
        Parses a story into characters, locations, emotions, events, and a timeline.
        """
        clauses = split_story_into_clauses(story)
        
        all_characters = []
        all_locations = []
        all_objects = []
        all_emotions = []
        events = []
        timeline = []
        transitions = []

        # Track active character and location across clauses
        current_character = "humanoid"
        current_location = "environment"

        # Global entities tracking to populate root level
        global_chars_map = {}
        global_locs_map = {}
        global_objs_map = {}
        global_emotions_map = {}

        # Collect all verbs across actions lexicon to split clauses
        all_verbs = set()
        for verbs in ACTIONS_LEXICON.values():
            all_verbs.update(verbs)
        # Add other common verbs
        all_verbs.update({"loses", "lost", "lose", "regains", "regained", "regain", "finds", "found", "find", "has", "had", "have", "is", "was", "are", "were", "becomes", "became"})

        for idx, clause in enumerate(clauses):
            clause_lower = clause.lower()

            # Find the first verb in the clause to split into Subject and Object parts
            words = clause_lower.split()
            first_verb_idx = -1
            found_verb = None
            for w_idx, w in enumerate(words):
                w_clean = clean_token(w)
                if w_clean in all_verbs:
                    first_verb_idx = w_idx
                    found_verb = w_clean
                    break

            if first_verb_idx != -1:
                subject_part = " ".join(words[:first_verb_idx])
                object_part = " ".join(words[first_verb_idx:])
            else:
                subject_part = clause_lower
                object_part = ""

            # Extract entities from the whole clause for global maps
            clause_chars = self.extract_characters(clause)
            clause_locs = self.extract_locations(clause)
            clause_objs = self.extract_objects(clause)
            clause_emotions = self.extract_emotions(clause)
            clause_actions = self.extract_actions(clause)

            # Store in global maps
            for c in clause_chars:
                name = c["name"]
                if name not in global_chars_map:
                    global_chars_map[name] = set(c["modifiers"])
                else:
                    global_chars_map[name].update(c["modifiers"])

            for l in clause_locs:
                name = l["name"]
                if name not in global_locs_map:
                    global_locs_map[name] = set(l["modifiers"])
                else:
                    global_locs_map[name].update(l["modifiers"])

            for o in clause_objs:
                name = o["name"]
                if name not in global_objs_map:
                    global_objs_map[name] = set(o["modifiers"])
                else:
                    global_objs_map[name].update(o["modifiers"])

            for emo in clause_emotions:
                emo_name = emo["emotion"]
                phrase = emo["phrase"]
                if emo_name not in global_emotions_map:
                    global_emotions_map[emo_name] = set([phrase])
                else:
                    global_emotions_map[emo_name].add(phrase)

            # SVO resolution for the current event
            # Extract characters present in subject part vs object part
            subj_chars = self.extract_characters(subject_part)
            obj_chars = self.extract_characters(object_part)
            
            # If subject has character(s), the actor is the first subject character
            if subj_chars:
                current_character = subj_chars[0]["name"]
            # Otherwise, actor carries over (implicit subject)

            # Target is the first character in the object part, or first object in object part
            target = None
            if obj_chars:
                target = obj_chars[0]["name"]
            else:
                obj_objs = self.extract_objects(object_part)
                if obj_objs:
                    target = obj_objs[0]["name"]

            # Update location if any is explicitly mentioned in the clause
            if clause_locs:
                current_location = clause_locs[0]["name"]

            # Determine Action and Speed
            action_val = "idle"
            speed_val = "normal"
            if clause_actions:
                action_val = clause_actions[0]["action"]
                speed_val = clause_actions[0]["speed"]

            # Determine Emotion
            emotion_val = "neutral"
            if clause_emotions:
                emotion_val = clause_emotions[0]["emotion"]
            else:
                # Infer emotion
                if action_val == "attack":
                    emotion_val = "angry"
                elif action_val in ["run", "duck"]:
                    emotion_val = "fear"
                elif action_val in ["discover", "wave"]:
                    emotion_val = "surprise"

            # Form Event
            event_id = f"event_{idx + 1}"
            event = {
                "id": event_id,
                "actor": current_character,
                "action": action_val,
                "target": target,
                "location": current_location,
                "emotion": emotion_val,
                "speed": speed_val,
                "description": clause.strip()
            }
            events.append(event)
            timeline.append(event_id)

            # Determine transition from previous event
            if idx > 0:
                prev_event = events[idx - 1]
                if prev_event["location"] != current_location:
                    transitions.append("fade")
                else:
                    transitions.append("cut")

        # Format global lists for output
        all_characters = [{"name": name, "modifiers": list(mods)} for name, mods in global_chars_map.items()]
        all_locations = [{"name": name, "modifiers": list(mods)} for name, mods in global_locs_map.items()]
        all_objects = [{"name": name, "modifiers": list(mods)} for name, mods in global_objs_map.items()]
        all_emotions = [{"emotion": name, "triggers": list(triggers)} for name, triggers in global_emotions_map.items()]

        # Fallbacks
        if not all_characters:
            all_characters = [{"name": "humanoid", "modifiers": []}]
        if not all_locations:
            all_locations = [{"name": "environment", "modifiers": []}]

        return {
            "characters": all_characters,
            "locations": all_locations,
            "objects": all_objects,
            "emotions": all_emotions,
            "events": events,
            "timeline": timeline,
            "transitions": transitions
        }

if __name__ == "__main__":
    import json
    engine = StoryUnderstandingEngine()
    test_story = "A lonely knight loses faith, discovers an ancient dragon, and regains purpose."
    result = engine.understand_story(test_story)
    print(json.dumps(result, indent=2))
