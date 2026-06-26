# ai/emotion_memory.py
from typing import Dict, Any, List

class EmotionMemoryEngine:
    """
    Subsystem: Emotion Memory Engine
    Tracks character baseline temperaments and computes vector updates based on narrative events and time decay.
    """
    def __init__(self):
        # Default baselines
        self.char_emotions = {}
        self.stimulus_rules = {
            "attack": {"anger": 0.4, "fear": 0.3, "happiness": -0.3},
            "gift": {"happiness": 0.5, "sadness": -0.2},
            "insult": {"anger": 0.5, "happiness": -0.2},
            "loss": {"sadness": 0.6, "anger": 0.2}
        }
        self.decay_rate = 0.05  # Decay amount per simulated second

    def get_profile(self, char_id: str) -> Dict[str, float]:
        """Retrieves or registers active emotional vectors for a target character."""
        key = char_id.lower().strip()
        if key not in self.char_emotions:
            self.char_emotions[key] = {
                "happiness": 0.5,
                "anger": 0.0,
                "sadness": 0.0,
                "fear": 0.0
            }
        return self.char_emotions[key]

    def process_stimulus(self, char_id: str, stimulus: str) -> Dict[str, float]:
        """Modulates active emotional vectors based on action or event triggers."""
        profile = self.get_profile(char_id)
        stim = stimulus.lower().strip()
        
        # Match keywords in the stimulus text
        for trigger, modifiers in self.stimulus_rules.items():
            if trigger in stim:
                for emo, val in modifiers.items():
                    profile[emo] = max(0.0, min(1.0, profile[emo] + val))
                    
        return profile

    def tick_decay(self, char_id: str, duration_sec: float) -> Dict[str, float]:
        """Applies time decay, pulling emotional levels back toward their baseline states."""
        profile = self.get_profile(char_id)
        decay = self.decay_rate * duration_sec
        
        # Happiness baseline is 0.5; others decay to 0.0
        for emo in ["anger", "sadness", "fear"]:
            if profile[emo] > 0.0:
                profile[emo] = max(0.0, profile[emo] - decay)
                
        if profile["happiness"] != 0.5:
            if profile["happiness"] > 0.5:
                profile["happiness"] = max(0.5, profile["happiness"] - decay)
            else:
                profile["happiness"] = min(0.5, profile["happiness"] + decay)
                
        return profile
