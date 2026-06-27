# ai/voice/generator.py
import os
import asyncio
import edge_tts
import time
from typing import List, Dict, Any

class VoiceSystem:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def synthesize_dialogue(self, text: str, voice: str) -> Dict[str, Any]:
        """Synthesize character speech dialogue."""
        filename = f"dialogue_{int(time.time())}_{os.urandom(4).hex()}.mp3"
        filepath = os.path.join(self.output_dir, filename)
        
        async def _speak():
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(filepath)

        asyncio.run(_speak())
        
        # Word timestamps stub (for animation keyframing integrations)
        words = text.split()
        timestamps = []
        curr_time = 0.0
        for w in words:
            timestamps.append({
                "word": w.strip(".,!?\""),
                "start": round(curr_time, 2),
                "end": round(curr_time + 0.3, 2)
            })
            curr_time += 0.35

        return {
            "audio_path": filepath,
            "filename": filename,
            "timestamps": timestamps,
            "duration": round(curr_time, 2)
        }

    def synthesize_narration(self, text: str, voice: str = "en-US-GuyNeural") -> Dict[str, Any]:
        """Synthesize narrator background description overlay."""
        filename = f"narration_{int(time.time())}_{os.urandom(4).hex()}.mp3"
        filepath = os.path.join(self.output_dir, filename)

        async def _speak():
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(filepath)

        asyncio.run(_speak())

        return {
            "audio_path": filepath,
            "filename": filename,
            "duration": round(len(text.split()) * 0.4, 2)
        }
