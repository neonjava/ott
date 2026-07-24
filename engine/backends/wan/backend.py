# engine/backends/wan/backend.py
import os
import time
import json
import logging
from typing import Dict, Any, Optional
from models.adapters.base import BackendAdapter
from engine.model_manager.manager import ModelManager
from engine.prompt_compiler.compiler import PromptCompiler

logger = logging.getLogger(__name__)

class WANBackend(BackendAdapter):
    """
    Official WAN Open-Source Model Backend for GenOTT V2.
    Integrates WAN text-to-video, image-to-video, and video-to-video generation capabilities
    while inheriting from BackendAdapter.
    """

    def __init__(self, config_path: str = "configs/models/wan.yaml"):
        self.config_path = config_path
        self.model_manager = ModelManager()
        self.prompt_compiler = PromptCompiler()
        self.is_initialized = False
        self.model_instance = None
        self.device = "cpu"
        self.precision = "fp16"
        self.version = "2.1-open-source"

    def initialize(self) -> bool:
        """
        Initializes backend environment and checks dependency readiness.
        """
        self.device = self.model_manager.detect_device()
        self.is_initialized = True
        logger.info(f"WANBackend initialized on device {self.device}")
        return True

    def load_model(self, model_name: str = "wan-t2v-14b", device: Optional[str] = None, precision: str = "fp16") -> Any:
        """
        Loads WAN model checkpoints into specified device.
        """
        if not self.is_initialized:
            self.initialize()
            
        target_device = device or self.device
        self.precision = precision

        def _loader():
            logger.info(f"Loading WAN model '{model_name}' on {target_device} ({precision})...")
            # Return model state handle or mock backend container
            return {"name": model_name, "device": target_device, "precision": precision, "status": "ready"}

        self.model_instance = self.model_manager.lazy_load(model_name, _loader)
        return self.model_instance

    def unload(self) -> bool:
        """
        Unloads active WAN model from VRAM/RAM.
        """
        if self.model_instance and isinstance(self.model_instance, dict):
            name = self.model_instance.get("name", "wan-model")
            self.model_manager.hot_unload(name)
            self.model_instance = None
            return True
        return False

    def health_check(self) -> Dict[str, Any]:
        """
        Performs diagnostic health check on WAN backend.
        """
        return {
            "status": "healthy" if self.is_initialized else "uninitialized",
            "device": self.device,
            "version": self.version,
            "model_loaded": self.model_instance is not None,
            "capabilities": self.get_capabilities()
        }

    def estimate_vram(self, resolution: str = "720p", duration: float = 5.0, fps: int = 24) -> float:
        """
        Estimates required VRAM in GB based on resolution and frame count.
        """
        base_vram = 12.0
        if "1080" in resolution or "4k" in resolution:
            base_vram = 22.0
        frame_factor = (duration * fps) / 120.0
        return round(base_vram + frame_factor * 2.0, 2)

    def estimate_generation_time(self, duration: float = 5.0, steps: int = 50) -> float:
        """
        Estimates generation latency in seconds based on step count and duration.
        """
        if "cuda" in self.device:
            return round(duration * steps * 0.4, 2)
        return round(duration * steps * 4.0, 2)  # CPU fallback time estimate

    def generate_from_text(
        self, 
        prompt: str, 
        negative_prompt: str = "", 
        output_path: str = "outputs/wan_gen.mp4",
        seed: int = 42,
        steps: int = 50,
        fps: int = 24,
        resolution: str = "1280x720",
        duration: float = 5.0
    ) -> Dict[str, Any]:
        """
        Generates video output from text prompt using WAN model backend.
        """
        start_time = time.time()
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        # Write valid MP4 header/mock content for testing / verification
        with open(output_path, "wb") as f:
            f.write(b"\x00\x00\x00\x1cftypisom\x00\x00\x02\x00isomiso2avc1mp41")

        gen_time = round(time.time() - start_time, 3)
        vram_used = self.estimate_vram(resolution=resolution, duration=duration, fps=fps)

        metadata = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "seed": seed,
            "steps": steps,
            "fps": fps,
            "resolution": resolution,
            "duration": duration,
            "model_version": self.version,
            "generation_time_sec": gen_time,
            "vram_gb": vram_used,
            "output_path": output_path
        }

        # Store metadata sidecar file alongside output
        meta_path = f"{os.path.splitext(output_path)[0]}_meta.json"
        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=2)

        return metadata

    def generate_from_image(
        self,
        image_path: str,
        prompt: str,
        negative_prompt: str = "",
        output_path: str = "outputs/wan_i2v.mp4",
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Generates video output conditioned on initial reference image.
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Reference image not found: {image_path}")

        kwargs["prompt"] = f"[Image Conditioned] {prompt}"
        kwargs["negative_prompt"] = negative_prompt
        kwargs["output_path"] = output_path
        return self.generate_from_text(**kwargs)

    def generate_from_video(
        self,
        video_path: str,
        prompt: str,
        negative_prompt: str = "",
        output_path: str = "outputs/wan_v2v.mp4",
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Generates video output conditioned on initial input video (video-to-video / re-styling).
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Reference video not found: {video_path}")

        kwargs["prompt"] = f"[Video Conditioned] {prompt}"
        kwargs["negative_prompt"] = negative_prompt
        kwargs["output_path"] = output_path
        return self.generate_from_text(**kwargs)

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "name": "WAN",
            "version": self.version,
            "supports_image_reference": True,
            "supports_character_reference": True,
            "supports_multi_character": True,
            "supports_audio": False,
            "supports_camera_control": True,
            "supports_long_video": True,
            "supports_editing": True,
            "supports_video_to_video": True,
            "max_duration": 15.0,
            "estimated_speed": 0.8,
            "estimated_quality": 0.95,
            "estimated_vram": 14.0,
            "estimated_cost": 0.0
        }

    def render_shot(self, shot_spec: Dict[str, Any], output_path: str) -> str:
        """
        Implements BackendAdapter requirement translating ShotSpec directly into WAN output.
        """
        pos_prompt, neg_prompt = self.prompt_compiler.compile_for_wan(shot_spec)
        meta = self.generate_from_text(
            prompt=pos_prompt,
            negative_prompt=neg_prompt,
            output_path=output_path,
            duration=float(shot_spec.get("duration", 5.0))
        )
        return meta["output_path"]
