# models/adapters/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class BackendAdapter(ABC):
    """
    Base Interface for Movie OS generative video and 3D rendering backends.
    All proprietary and open-source models (Blender, WAN, Hunyuan, CogVideo) must implement this.
    """
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Returns capability registry mapping:
        - name: str
        - version: str
        - supports_image_reference: bool
        - supports_character_reference: bool
        - supports_multi_character: bool
        - supports_audio: bool
        - supports_camera_control: bool
        - supports_long_video: bool
        - supports_editing: bool
        - max_duration: float (seconds)
        - estimated_speed: float (1.0 = realtime, lower is slower)
        - estimated_quality: float (0.0 to 1.0)
        - estimated_vram: float (GB)
        - estimated_cost: float (USD per minute)
        """
        pass

    @abstractmethod
    def render_shot(self, shot_spec: Dict[str, Any], output_path: str) -> str:
        """
        Executes rendering or generation for a single shot based on model-agnostic specs.
        Returns path to output video file.
        """
        pass
