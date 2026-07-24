# engine/backends/plugin_framework.py
import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Type

logger = logging.getLogger(__name__)

class BackendPlugin(ABC):
    """
    Universal Abstract Plugin Interface for all GenOTT V2 generative backends 
    (WAN, CogVideoX, HunyuanVideo, LTX Video, Mochi, Blender, etc.).
    """

    @abstractmethod
    def initialize(self) -> bool:
        pass

    @abstractmethod
    def shutdown(self) -> bool:
        pass

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def generate_text_to_video(self, prompt: str, negative_prompt: str = "", output_path: str = "output.mp4", **kwargs: Any) -> Dict[str, Any]:
        pass

    @abstractmethod
    def generate_image_to_video(self, image_path: str, prompt: str, negative_prompt: str = "", output_path: str = "output.mp4", **kwargs: Any) -> Dict[str, Any]:
        pass

    @abstractmethod
    def generate_video_to_video(self, video_path: str, prompt: str, negative_prompt: str = "", output_path: str = "output.mp4", **kwargs: Any) -> Dict[str, Any]:
        pass

    @abstractmethod
    def interrupt(self) -> bool:
        pass

    @abstractmethod
    def estimate_resources(self, resolution: str = "720p", duration: float = 5.0, fps: int = 24) -> Dict[str, Any]:
        pass

    @abstractmethod
    def report_metrics(self) -> Dict[str, Any]:
        pass


class BackendRegistry:
    """
    Global registry for backend plugins.
    """
    _backends: Dict[str, Type[BackendPlugin]] = {}
    _instances: Dict[str, BackendPlugin] = {}

    @classmethod
    def register_backend(cls, name: str, backend_cls: Type[BackendPlugin]):
        cls._backends[name.lower()] = backend_cls
        logger.info(f"Registered generative backend plugin: '{name}'")

    @classmethod
    def get_backend(cls, name: str, **kwargs: Any) -> BackendPlugin:
        name_lower = name.lower()
        if name_lower not in cls._instances:
            if name_lower not in cls._backends:
                raise ValueError(f"Backend plugin '{name}' is not registered. Available: {list(cls._backends.keys())}")
            cls._instances[name_lower] = cls._backends[name_lower](**kwargs)
        return cls._instances[name_lower]

    @classmethod
    def list_registered(cls) -> List[str]:
        return list(cls._backends.keys())
