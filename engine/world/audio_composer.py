# ai/audio_composer.py
import os
import subprocess
from typing import Dict, Any, List

class AudioComposer:
    """
    Subsystem: Spatial Audio Mixer & SFX Composer
    Simulates a sound mixing studio, layering spatial voices, background tracks, and contextual sound effects.
    """
    def __init__(self):
        # Mappings of script verbs to visual/audio sound effects
        self.sfx_catalog = {
            "attack": "assets/sfx/strike.wav",
            "strike": "assets/sfx/strike.wav",
            "leap": "assets/sfx/whoosh.wav",
            "jump": "assets/sfx/whoosh.wav",
            "walk": "assets/sfx/footsteps.wav",
            "run": "assets/sfx/footsteps.wav"
        }

    def compute_spatial_gain(self, camera_distance: float) -> float:
        """Calculates distance-based volume gain using inverse square law attenuation."""
        if camera_distance <= 0:
            return 1.0
        # Attenuate gain based on camera distance (clamped between 0.1 and 1.0)
        gain = 1.0 / (1.0 + 0.15 * (camera_distance ** 2))
        return max(0.1, min(1.0, round(gain, 3)))

    def compile_ffmpeg_mix_command(self, BGM_path: str, vocal_clips: List[Dict[str, Any]], sfx_clips: List[Dict[str, Any]], output_path: str) -> List[str]:
        """Compiles a complex multi-track audio overlay command string for FFmpeg."""
        cmd = ["ffmpeg", "-y"]
        
        # 1. Inputs
        cmd.extend(["-i", BGM_path]) # Input 0: BGM
        
        input_index = 1
        for clip in vocal_clips:
            cmd.extend(["-i", clip["path"]])
            clip["index"] = input_index
            input_index += 1
            
        for clip in sfx_clips:
            cmd.extend(["-i", clip["path"]])
            clip["index"] = input_index
            input_index += 1
            
        # 2. Filter Complex construction
        filter_str = ""
        mix_inputs = []
        
        # Mix BGM at lower ambient level (-18dB)
        filter_str += "[0:a]volume=0.15[bgm_mix]; "
        mix_inputs.append("[bgm_mix]")
        
        # Delay and gain adjust voice clips
        for clip in vocal_clips:
            idx = clip["index"]
            delay = int(clip.get("start", 0.0) * 1000)
            vol = clip.get("volume", 1.0)
            filter_str += f"[{idx}:a]adelay={delay}:all=1,volume={vol}[v_{idx}]; "
            mix_inputs.append(f"[v_{idx}]")
            
        # Delay and gain adjust SFX clips
        for clip in sfx_clips:
            idx = clip["index"]
            delay = int(clip.get("start", 0.0) * 1000)
            vol = clip.get("volume", 0.8)
            filter_str += f"[{idx}:a]adelay={delay}:all=1,volume={vol}[sfx_{idx}]; "
            mix_inputs.append(f"[sfx_{idx}]")
            
        # Mix all streams
        filter_str += "".join(mix_inputs)
        filter_str += f"amix=inputs={len(mix_inputs)}:normalize=0[aout]"
        
        cmd.extend([
            "-filter_complex", filter_str,
            "-map", "[aout]",
            output_path
        ])
        return cmd
