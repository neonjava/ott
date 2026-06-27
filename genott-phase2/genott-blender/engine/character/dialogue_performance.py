# ai/dialogue_performance.py
import random
from typing import Dict, Any, List

class DialoguePerformanceAgent:
    """
    Subsystem: Dialogue Performance
    Calibrates speech pacing, eye saccades, breathing cycles, turn-taking, and facial micro-expressions.
    """
    def __init__(self):
        pass

    def calculate_pacing(self, line_text: str, emotion: str) -> Dict[str, Any]:
        """Calculates speaking rate (words per minute), pre/post pause offsets based on sentence mood."""
        word_count = len(line_text.split())
        base_wpm = 140.0
        
        # Pacing variations based on emotion
        emo = emotion.lower()
        if "angry" in emo or "fear" in emo:
            wpm_mod = 1.25  # Fast pacing
            pre_pause = 0.1
            post_pause = 0.3
        elif "sad" in emo or "mysterious" in emo:
            wpm_mod = 0.8  # Slow, dramatic pacing
            pre_pause = 0.5
            post_pause = 0.8
        else:
            wpm_mod = 1.0
            pre_pause = 0.2
            post_pause = 0.4
            
        speaking_rate = base_wpm * wpm_mod
        words_per_second = speaking_rate / 60.0
        calculated_duration = word_count / words_per_second if words_per_second > 0 else 1.0
        
        return {
            "wpm": speaking_rate,
            "duration": round(calculated_duration, 2),
            "pre_pause": pre_pause,
            "post_pause": post_pause
        }

    def generate_micro_expressions(self, duration: float) -> List[Dict[str, Any]]:
        """Generates timeline keyframes for eye blinks, micro-saccades, and breathing wiggles."""
        keyframes = []
        current_time = 0.0
        
        # 1. Add eye blinks (every 2.5 - 4 seconds)
        while current_time < duration:
            current_time += random.uniform(2.5, 4.0)
            if current_time < duration:
                keyframes.append({
                    "time": round(current_time, 2),
                    "type": "blink",
                    "value": 1.0,
                    "duration": 0.15
                })
                
        # 2. Add subtle eye saccades (every 0.8 - 1.5 seconds)
        current_time = 0.0
        while current_time < duration:
            current_time += random.uniform(0.8, 1.5)
            if current_time < duration:
                keyframes.append({
                    "time": round(current_time, 2),
                    "type": "saccade",
                    "offset_h": round(random.uniform(-0.05, 0.05), 3),
                    "offset_v": round(random.uniform(-0.03, 0.03), 3)
                })
                
        # Sort keyframes by time
        keyframes.sort(key=lambda x: x["time"])
        return keyframes

    def get_turn_taking_delay(self, speaker_rel: str) -> float:
        """Determines the pause between two speakers based on relationship/social cues."""
        rel = speaker_rel.lower()
        if "conflict" in rel or "fight" in rel:
            return 0.05  # Interrupting/fast responses
        elif "formal" in rel or "stranger" in rel:
            return 0.6  # High respect delay
        return 0.3  # Standard casual conversational gap
