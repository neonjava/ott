# ai/lipsync/base.py
from abc import ABC, abstractmethod

class LipSyncProvider(ABC):
    @abstractmethod
    def run_lipsync(self, image_path: str, audio_path: str, output_path: str, generation_id: str = None) -> str:
        """Lip syncs face reference portrait image with target speech sound."""
        pass
