# engine/routing/backend_router.py
import logging
from typing import Dict, Any, Optional
from engine.backends.plugin_framework import BackendRegistry, BackendPlugin

logger = logging.getLogger(__name__)

class BackendRouter:
    """
    Automated Generative Backend Router for GenOTT V2.
    Routes generation tasks dynamically between backends (WAN, CogVideoX, HunyuanVideo, LTX Video, Mochi)
    based on resolution, motion complexity, target latency, and VRAM budget.
    """

    def select_backend(
        self, 
        requested_backend: Optional[str] = None, 
        intent: str = "cinematic", 
        resolution: str = "1080p", 
        available_vram_gb: float = 16.0
    ) -> BackendPlugin:
        if requested_backend and requested_backend.lower() in BackendRegistry.list_registered():
            target = requested_backend.lower()
        else:
            # Automated Routing Logic
            if intent == "rapid_preview" or available_vram_gb < 10.0:
                target = "ltx-video" if "ltx-video" in BackendRegistry.list_registered() else "wan"
            elif intent == "fast_motion":
                target = "cogvideox" if "cogvideox" in BackendRegistry.list_registered() else "wan"
            elif resolution == "1080p" and available_vram_gb >= 16.0:
                target = "hunyuanvideo" if "hunyuanvideo" in BackendRegistry.list_registered() else "wan"
            else:
                target = "wan"

        logger.info(f"[BackendRouter] Auto-selected model backend '{target}' (Intent: {intent}, Res: {resolution})")
        return BackendRegistry.get_backend(target)
