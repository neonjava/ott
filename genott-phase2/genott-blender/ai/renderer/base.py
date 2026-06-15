# ai/renderer/base.py
from abc import ABC, abstractmethod
from ai.storyboard.models import ScenePlan

class VideoRenderer(ABC):
    @abstractmethod
    def render_scene(self, plan: ScenePlan, seed: int, output_path: str, generation_id: str = None) -> str:
        """Render consistent cinematic scene video based on scene configuration."""
        pass
