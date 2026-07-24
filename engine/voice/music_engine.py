# engine/voice/music_engine.py
import os
import wave
import struct
import math
import logging

logger = logging.getLogger(__name__)

class LocalMusicEngine:
    """
    Local Synthetic Background Music Engine for GenOTT V2.
    Synthesizes multi-tonal cinematic orchestral background audio score without external dependencies.
    """

    def synthesize_background_score(self, duration_sec: float = 120.0, output_path: str = "outputs/productions/background_music.wav") -> str:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        sample_rate = 44100
        n_samples = int(sample_rate * duration_sec)

        chords = [110.0, 130.81, 164.81, 196.0]  # A minor chord progression (A2, C3, E3, G3)

        with wave.open(output_path, "wb") as wav_file:
            wav_file.setnchannels(2)  # Stereo
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)

            for i in range(n_samples):
                t = i / sample_rate
                chord_idx = int(t / 8.0) % len(chords)
                base_freq = chords[chord_idx]

                # Ambient synth drone & rhythm harmonics
                val_left = int(7000 * math.sin(2 * math.pi * base_freq * t) + 3000 * math.sin(2 * math.pi * (base_freq * 1.5) * t))
                val_right = int(7000 * math.sin(2 * math.pi * (base_freq * 1.25) * t) + 3000 * math.sin(2 * math.pi * (base_freq * 2.0) * t))

                val_left = max(-32768, min(32767, val_left))
                val_right = max(-32768, min(32767, val_right))

                wav_file.writeframes(struct.pack("<hh", val_left, val_right))

        logger.info(f"[✓] Background music score synthesized successfully ({duration_sec}s) at {output_path}")
        return output_path
