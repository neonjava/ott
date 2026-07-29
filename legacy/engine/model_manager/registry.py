# engine/model_manager/registry.py
import os
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

OFFICIAL_MODEL_SPECS: Dict[str, Dict[str, Any]] = {
    "wan": {
        "repo_url": "https://github.com/Wan-Video/Wan2.1.git",
        "weight_version": "2.1-open-source",
        "required_vram_gb": 14.0,
        "required_disk_gb": 28.0,
        "supported_resolutions": ["720p", "1080p"],
        "supported_fps": [24, 30],
        "supported_modes": ["text_to_video", "image_to_video", "video_to_video"],
        "official_weights_url": "https://huggingface.co/Wan-AI/Wan2.1-T2V-14B/resolve/main/Wan2.1_T2V_14B_fp16.safetensors",
        "checksum_sha256": None
    },
    "hunyuanvideo": {
        "repo_url": "https://github.com/Tencent/HunyuanVideo.git",
        "weight_version": "1.0.0",
        "required_vram_gb": 16.0,
        "required_disk_gb": 32.0,
        "supported_resolutions": ["720p", "1080p"],
        "supported_fps": [24, 30],
        "supported_modes": ["text_to_video", "image_to_video"],
        "official_weights_url": "https://huggingface.co/Tencent/HunyuanVideo/resolve/main/hunyuan_video.safetensors",
        "checksum_sha256": None
    },
    "cogvideox": {
        "repo_url": "https://github.com/THUDM/CogVideo.git",
        "weight_version": "5b",
        "required_vram_gb": 12.0,
        "required_disk_gb": 20.0,
        "supported_resolutions": ["720p"],
        "supported_fps": [24],
        "supported_modes": ["text_to_video", "image_to_video"],
        "official_weights_url": "https://huggingface.co/THUDM/CogVideoX-5b/resolve/main/cogvideox_5b.safetensors",
        "checksum_sha256": None
    },
    "ltx-video": {
        "repo_url": "https://github.com/Lightricks/LTX-Video.git",
        "weight_version": "0.9.1",
        "required_vram_gb": 8.0,
        "required_disk_gb": 14.0,
        "supported_resolutions": ["720p"],
        "supported_fps": [24],
        "supported_modes": ["text_to_video"],
        "official_weights_url": "https://huggingface.co/Lightricks/LTX-Video/resolve/main/ltx-video-2b-v0.9.1.safetensors",
        "checksum_sha256": None
    },
    "mochi": {
        "repo_url": "https://github.com/genmoai/mochi.git",
        "weight_version": "1-preview",
        "required_vram_gb": 18.0,
        "required_disk_gb": 35.0,
        "supported_resolutions": ["720p"],
        "supported_fps": [30],
        "supported_modes": ["text_to_video"],
        "official_weights_url": "https://huggingface.co/genmo/mochi-1-preview/resolve/main/mochi.safetensors",
        "checksum_sha256": None
    }
}

class ModelRegistry:
    """
    Maintains official metadata, installation status, health status, and directory layout
    for GenOTT V2 generative models.
    """

    def __init__(self, registry_file: str = "configs/models/registry.json", base_models_dir: str = "models", third_party_dir: str = "third_party"):
        self.registry_file = os.path.abspath(registry_file)
        self.base_models_dir = os.path.abspath(base_models_dir)
        self.third_party_dir = os.path.abspath(third_party_dir)
        self.registry_data: Dict[str, Dict[str, Any]] = {}
        self.load_registry()

    def load_registry(self):
        """
        Loads registry state from JSON or initializes from official specs.
        """
        os.makedirs(os.path.dirname(self.registry_file), exist_ok=True)
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, "r") as f:
                    self.registry_data = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load registry file {self.registry_file}: {e}")
                self.registry_data = {}

        # Merge defaults
        for key, spec in OFFICIAL_MODEL_SPECS.items():
            if key not in self.registry_data:
                self.registry_data[key] = {
                    **spec,
                    "installation_status": "uninstalled",
                    "health_status": "unknown",
                    "installed_version": None,
                    "local_weights_dir": os.path.join(self.base_models_dir, key),
                    "local_repo_dir": os.path.join(self.third_party_dir, key)
                }

    def save_registry(self):
        """
        Persists current registry metadata to disk.
        """
        os.makedirs(os.path.dirname(self.registry_file), exist_ok=True)
        with open(self.registry_file, "w") as f:
            json.dump(self.registry_data, f, indent=2)

    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        return self.registry_data.get(model_name)

    def list_all(self) -> Dict[str, Dict[str, Any]]:
        self.load_registry()
        return self.registry_data

    def update_status(self, model_name: str, install_status: str, health_status: str, version: Optional[str] = None):
        if model_name in self.registry_data:
            self.registry_data[model_name]["installation_status"] = install_status
            self.registry_data[model_name]["health_status"] = health_status
            if version:
                self.registry_data[model_name]["installed_version"] = version
            self.save_registry()
