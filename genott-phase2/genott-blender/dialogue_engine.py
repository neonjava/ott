"""
dialogue_engine.py — Rule-based dialogue and narration extraction engine.

Parses raw scripts into structured dialogue timelines without using LLMs.
Detects narration lines, spoken dialogue, and generates structured output
for the voice generation pipeline.
"""
import re
from typing import List, Dict, Any


# Voice profiles for different speaker types
VOICE_PROFILES = {
    "narrator": "en-US-GuyNeural",
    "hero": "en-US-ChristopherNeural",
    "villain": "en-US-EricNeural",
    "crowd": "en-US-JennyNeural",
    "default": "en-US-ChristopherNeural",
}

# Action verbs that indicate narration (not spoken dialogue)
ACTION_VERBS = [
    "walks", "runs", "jumps", "attacks", "waves", "flies",
    "lands", "stands", "enters", "exits", "charges", "smashes",
    "leaps", "punches", "kicks", "dodges", "blocks", "falls",
    "rises", "turns", "looks", "grabs", "throws", "slams",
    "crashes", "explodes", "appears", "disappears", "arrives",
    "cheers", "claps", "roars", "screams",
]


def parse_script(script: str) -> List[Dict[str, Any]]:
    """
    Parse a raw script into a structured dialogue timeline.

    Detects:
      - Spoken dialogue: lines containing quotes or "says:" patterns
      - Narration: action descriptions, stage directions

    Returns a list of timeline entries:
      [
        {"type": "narration", "text": "...", "speaker": None},
        {"type": "dialogue", "text": "...", "speaker": "Hero"},
        ...
      ]
    """
    timeline = []
    lines = [line.strip() for line in script.strip().split("\n") if line.strip()]

    # If no newlines, try splitting on periods/sentences
    if len(lines) == 1:
        lines = _split_into_sentences(lines[0])

    for line in lines:
        entry = _classify_line(line)
        if entry:
            timeline.append(entry)

    # Fallback: if nothing was parsed, treat entire script as narration
    if not timeline:
        timeline.append({
            "type": "narration",
            "text": script.strip(),
            "speaker": None,
        })

    return timeline


def _split_into_sentences(text: str) -> List[str]:
    """Split a single block of text into individual sentences."""
    # Split on period, exclamation, question mark followed by space or end
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    return [p.strip() for p in parts if p.strip()]


def _classify_line(line: str) -> Dict[str, Any]:
    """Classify a single script line as dialogue or narration."""

    # Pattern 1: "Speaker says: 'text'" or 'Speaker says: "text"'
    says_match = re.match(
        r'^(.+?)\s+says?\s*:\s*["\'](.+?)["\']\.?$', line, re.IGNORECASE
    )
    if says_match:
        return {
            "type": "dialogue",
            "speaker": says_match.group(1).strip(),
            "text": says_match.group(2).strip(),
        }

    # Pattern 2: "Speaker: 'text'" or 'Speaker: "text"'
    colon_match = re.match(
        r'^([A-Z][a-zA-Z\s]+?)\s*:\s*["\'](.+?)["\']\.?$', line
    )
    if colon_match:
        return {
            "type": "dialogue",
            "speaker": colon_match.group(1).strip(),
            "text": colon_match.group(2).strip(),
        }

    # Pattern 3: Line contains quoted text — extract speaker from context
    quote_match = re.search(r'["\'](.+?)["\']', line)
    if quote_match:
        # Try to find speaker before the quote
        before_quote = line[:quote_match.start()].strip()
        speaker = _extract_speaker(before_quote)
        return {
            "type": "dialogue",
            "speaker": speaker,
            "text": quote_match.group(1).strip(),
        }

    # Pattern 4: Everything else is narration
    return {
        "type": "narration",
        "text": line.strip(),
        "speaker": None,
    }


def _extract_speaker(text: str) -> str:
    """Extract a speaker name from text preceding a quote."""
    # Remove trailing punctuation and common verbs
    text = re.sub(r'\s*(says?|shouts?|whispers?|yells?|screams?|replies?|asks?)\s*:?\s*$', '', text, flags=re.IGNORECASE)
    text = text.strip().rstrip(",.:;")

    # If what remains looks like a name (capitalized word), use it
    if text and text[0].isupper():
        return text.strip()

    return "Hero"


def get_voice_for_speaker(speaker: str, main_character: str = None) -> str:
    """Map a speaker name to a TTS voice profile."""
    speaker_lower = speaker.lower().strip()

    # Load character registry dynamically to read voice profiles
    import json
    import os
    registry_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "character_registry.json"
    )
    
    registry = {}
    if os.path.exists(registry_path):
        try:
            with open(registry_path, "r") as f:
                registry = json.load(f)
        except Exception:
            pass

    # If speaker is 'hero' and we have a main_character, treat speaker as main_character
    target_char = speaker_lower
    if speaker_lower == "hero" and main_character:
        target_char = main_character.lower().strip()

    # Look up target_char in registry
    if target_char in registry:
        return registry[target_char].get("voice", VOICE_PROFILES["default"])
        
    # Also check if target_char matches the name of any character in the registry
    for key, val in registry.items():
        if target_char == val.get("name", "").lower():
            return val.get("voice", VOICE_PROFILES["default"])

    if "narrator" in speaker_lower:
        return VOICE_PROFILES["narrator"]
    if any(v in speaker_lower for v in ["villain", "enemy", "dark"]):
        return VOICE_PROFILES["villain"]
    if any(c in speaker_lower for c in ["crowd", "people", "audience"]):
        return VOICE_PROFILES["crowd"]

    return VOICE_PROFILES.get(speaker_lower, VOICE_PROFILES["default"])


def generate_dialogue_timeline(script: str, character: str = "Hero") -> List[Dict[str, Any]]:
    """
    Full pipeline: parse script → assign voices → compute estimated durations.

    Returns timeline entries with voice and timing metadata:
      [
        {
          "type": "narration"|"dialogue",
          "text": "...",
          "speaker": "..." or None,
          "voice": "en-US-...",
          "estimated_duration": float,
          "scene_index": int,
        },
        ...
      ]
    """
    raw_timeline = parse_script(script)
    enriched = []
    scene_idx = 0

    for entry in raw_timeline:
        # Assign voice
        if entry["type"] == "dialogue":
            speaker = entry.get("speaker")
            if not speaker or speaker.lower() == "hero":
                speaker = character
            voice = get_voice_for_speaker(speaker, main_character=character)
        else:
            voice = VOICE_PROFILES["narrator"]
            speaker = None

        # Estimate duration: ~0.4s per word for narration, ~0.35s for dialogue
        word_count = len(entry["text"].split())
        if entry["type"] == "dialogue":
            est_dur = max(1.5, word_count * 0.35)
        else:
            est_dur = max(1.5, word_count * 0.4)

        enriched.append({
            "type": entry["type"],
            "text": entry["text"],
            "speaker": speaker,
            "voice": voice,
            "estimated_duration": round(est_dur, 2),
            "scene_index": scene_idx,
        })

        # Narration entries that describe actions bump the scene index
        text_lower = entry["text"].lower()
        if entry["type"] == "narration" and any(v in text_lower for v in ACTION_VERBS):
            scene_idx += 1


    return enriched
