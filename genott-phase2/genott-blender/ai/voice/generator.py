# ai/voice/generator.py
import os
import asyncio
import edge_tts
import time
import subprocess
from typing import List, Dict, Any

class VoiceSystem:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_silent_fallback(self, filepath: str, duration: float):
        """Generates a silent MP3 file of the specified duration locally using FFmpeg."""
        try:
            cmd = [
                "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000",
                "-t", str(duration), "-acodec", "libmp3lame", filepath
            ]
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return True
        except Exception as e:
            print(f"[VoiceSystem] Failed to generate silent fallback audio: {e}")
            # Write a dummy tiny empty file as a last resort
            with open(filepath, "wb") as f:
                f.write(b"")
            return False

    def synthesize_dialogue(self, text: str, voice: str) -> Dict[str, Any]:
        """Synthesize character speech dialogue."""
        filename = f"dialogue_{int(time.time())}_{os.urandom(4).hex()}.mp3"
        filepath = os.path.join(self.output_dir, filename)
        
        words = text.split()
        duration = max(1.5, round(len(words) * 0.4, 2))
        
        try:
            async def _speak():
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save(filepath)

            asyncio.run(_speak())
            success = os.path.exists(filepath) and os.path.getsize(filepath) > 0
        except Exception as e:
            print(f"[VoiceSystem] edge_tts synthesis failed: {e}. Generating silent fallback.")
            success = False
            
        if not success:
            self.generate_silent_fallback(filepath, duration)
        
        # Word timestamps stub (for animation keyframing integrations)
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
        duration = max(1.5, round(len(text.split()) * 0.4, 2))

        try:
            async def _speak():
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save(filepath)

            asyncio.run(_speak())
            success = os.path.exists(filepath) and os.path.getsize(filepath) > 0
        except Exception as e:
            print(f"[VoiceSystem] edge_tts narration failed: {e}. Generating silent fallback.")
            success = False

        if not success:
            self.generate_silent_fallback(filepath, duration)

        return {
            "audio_path": filepath,
            "filename": filename,
            "duration": duration
        }

